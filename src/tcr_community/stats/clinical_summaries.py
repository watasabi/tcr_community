"""Resumos clínicos agrupados para relatórios descritivos."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Final

import pandas as pd

from tcr_community.cleaning.standardize import (
    has_positive_indicator,
    normalize_text,
    parse_yes_no,
)
from tcr_community.schemas.columns import (
    COL_APACHE_II,
    COL_CAUSA_OBITO,
    COL_COMORBIDADES,
    COL_CUIDADOS_PALIATIVOS,
    COL_DESFECHO_PADRONIZADO,
    COL_DIAGNOSTICO,
    COL_DISPOSITIVO_INVASIVO,
    COL_DROGAS_VASOATIVAS,
    COL_HEMODIALISE,
    COL_PROCEDIMENTO_CIRURGICO,
    COL_SEDACAO,
    COL_TEMPO_UTI,
    COL_TRANSFUSAO,
    COL_VENTILACAO_MECANICA,
)

DIAGNOSIS_CATEGORIES: Final[list[str]] = [
    "Doenças respiratórias",
    "Doenças neurológicas",
    "Sepse e choque séptico",
    "Doenças cardiovasculares",
    "Doenças gastrointestinais/abdominais",
    "Doenças renais e metabólicas",
    "Infecções urinárias",
    "Doenças hepáticas",
    "Intoxicações exógenas",
    "Outros",
]

_CATEGORY_RULES: Final[list[tuple[str, tuple[str, ...]]]] = [
    (
        "Sepse e choque séptico",
        (
            "SEPSE",
            "SEPTICEMIA",
            "SEPTCEMIA",
            "CHOQUE_SEPTICO",
            "CHOQUE-SEPTICO",
            "CHQOUE_SEPTICO",
        ),
    ),
    (
        "Intoxicações exógenas",
        ("INTOXICACAO", "INTOXICAÇÃO"),
    ),
    (
        "Infecções urinárias",
        (
            "PIELONEFRITE",
            "INFECCAO_TRATO_URINARIO",
            "ITU",
            "FOCO_URINARIO",
            "TRATO_URINARIO",
            "CISTITE_AGUDA",
            "CISTITE AGUDA",
        ),
    ),
    (
        "Doenças hepáticas",
        (
            "CIRROSE",
            "ENCEFALOPATIA_HEPATICA",
            "ICTERICIA",
            "INSUFICIENCIA_HEPATICA",
            "COLANGITE",
            "HEPAT",
        ),
    ),
    (
        "Doenças renais e metabólicas",
        (
            "INSUFICIENCIA_RENAL",
            "INUFICIENCIA_RENAL",
            "DOENCA_RENAL",
            "DRC",
            "CETOACIDOSE",
            "ACIDOSE_METABOLICA",
            "HIPOGLICEMIA",
            "DIABET",
            "DM_",
            "DM2",
            "DMID",
            "RENAL",
        ),
    ),
    (
        "Doenças neurológicas",
        (
            "ACIDENTE_VASCULAR",
            "AVC_",
            "AVC",
            "ENCEFALOPATIA",
            "CRISE_CONVULSIVA",
            "REBAIXAMENTO",
            "DEMENCIA",
            "AVCI",
        ),
    ),
    (
        "Doenças cardiovasculares",
        (
            "INSUFICIENCIA_CARDIACA",
            "INUFICIENCIA_CARDIACA",
            "CHOQUE_CARDIOGEN",
            "CARDIOGENICO",
            "INFARTO",
            "IAM_",
            "IAM",
            "EDEMA_AGUDO",
            "TROMBOEMBOLISMO",
            "FLUTER",
            "FIBRILACAO",
            "DOR_TORACICA",
            "TAMPONAMENTO",
            "CHOQUE_NE",
            "CHOQUE_HIPOVOLEM",
            "CHOQUE_HEMORRAGIC",
        ),
    ),
    (
        "Doenças respiratórias",
        (
            "PNEUMON",
            "PNUEMON",
            "DPOC",
            "ASMA",
            "INSUFICIENCIA_RESPIRATORIA",
            "DISPNEIA",
            "TUBERCULOSE",
            "BRONQUIECTASIA",
            "BRONCOASPIRATIVA",
            "PULMONAR",
            "HIPOXEMIA",
        ),
    ),
    (
        "Doenças gastrointestinais/abdominais",
        (
            "ABDOME",
            "ABOME",
            "COLECIST",
            "PANCREAT",
            "PERITONITE",
            "HEMORRAGIA_DIGESTIVA",
            "MELENA",
            "OBSTRUCAO",
            "ISQUEMIA_MESENTERICA",
            "DOR_ABDOMINAL",
            "GASTROENTERITE",
            "DIARREIA",
            "CALCULOSE",
        ),
    ),
]

APACHE_MORTALITY_BANDS: Final[list[dict[str, object]]] = [
    {"faixa": "0-4", "min": 0, "max": 4, "mortalidade_estimada_pct": 4},
    {"faixa": "5-9", "min": 5, "max": 9, "mortalidade_estimada_pct": 8},
    {"faixa": "10-14", "min": 10, "max": 14, "mortalidade_estimada_pct": 15},
    {"faixa": "15-19", "min": 15, "max": 19, "mortalidade_estimada_pct": 25},
    {"faixa": "20-24", "min": 20, "max": 24, "mortalidade_estimada_pct": 40},
    {"faixa": "25-29", "min": 25, "max": 29, "mortalidade_estimada_pct": 55},
    {"faixa": "30-34", "min": 30, "max": 34, "mortalidade_estimada_pct": 75},
    {"faixa": "≥35", "min": 35, "max": 71, "mortalidade_estimada_pct": 85},
]

INTERVENTION_SPECS: Final[list[tuple[str, str]]] = [
    ("Ventilação mecânica", COL_VENTILACAO_MECANICA),
    ("Sedação", COL_SEDACAO),
    ("Drogas vasoativas", COL_DROGAS_VASOATIVAS),
    ("Hemodiálise", COL_HEMODIALISE),
    ("Transfusão sanguínea", COL_TRANSFUSAO),
    ("Procedimento cirúrgico", COL_PROCEDIMENTO_CIRURGICO),
    ("Dispositivos invasivos", COL_DISPOSITIVO_INVASIVO),
]

_NO_COMORBIDITY_TOKENS: Final[frozenset[str]] = frozenset(
    {"NAO", "N", "NEGA", "NEGOU", "SIM", "S"}
)

_COMORBIDITY_STOPWORDS: Final[frozenset[str]] = frozenset(
    {"DE", "DA", "DO", "E"}
)
_MIN_COMORBIDITY_TOKEN_LEN: Final = 2


@dataclass(frozen=True)
class ApacheBand:
    """Faixa de pontuação APACHE II com mortalidade de referência."""

    label: str
    min_score: int
    max_score: int
    estimated_mortality_pct: float


def _matches_keyword(text: str, keyword: str) -> bool:
    """Verifica keyword em tokens ou como fragmento composto."""
    tokens = text.split("_")
    if keyword in tokens:
        return True
    if " " in keyword:
        keyword = keyword.replace(" ", "_")
    padded = f"_{text}_"
    if "_" in keyword:
        return f"_{keyword}_" in padded
    return any(token.startswith(keyword) for token in tokens)


def classify_diagnosis(value: object) -> str:
    """Classifica diagnóstico principal em categoria clínica."""
    text = normalize_text(value)
    if text is None:
        return "Outros"
    for category, keywords in _CATEGORY_RULES:
        if any(_matches_keyword(text, keyword) for keyword in keywords):
            return category
    return "Outros"


def diagnosis_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Frequência de diagnósticos agrupados por categoria clínica."""
    if COL_DIAGNOSTICO not in df.columns:
        return pd.DataFrame(
            columns=["categoria", "absoluta", "relativa", "diagnosticos"]
        )
    categories = df[COL_DIAGNOSTICO].map(classify_diagnosis)
    counts = categories.value_counts()
    total = counts.sum()
    rows: list[dict[str, object]] = []
    for category in DIAGNOSIS_CATEGORIES:
        if category not in counts.index:
            continue
        mask = categories == category
        diagnoses = (
            df.loc[mask, COL_DIAGNOSTICO]
            .dropna()
            .astype(str)
            .value_counts()
            .head(5)
            .index.tolist()
        )
        rows.append(
            {
                "categoria": category,
                "absoluta": int(counts[category]),
                "relativa": counts[category] / total,
                "diagnosticos": "; ".join(diagnoses),
            }
        )
    return pd.DataFrame(rows)


def parse_comorbidity_tokens(value: object) -> list[str]:
    """Extrai tokens individuais de comorbidades compostas."""
    text = normalize_text(value)
    if text is None or text in _NO_COMORBIDITY_TOKENS:
        return []
    parts = re.split(r"[_,;,\s]+", text)
    tokens: list[str] = []
    for part in parts:
        token = part.strip()
        if (
            not token
            or token in _NO_COMORBIDITY_TOKENS
            or token in _COMORBIDITY_STOPWORDS
            or len(token) < _MIN_COMORBIDITY_TOKEN_LEN
        ):
            continue
        tokens.append(token)
    return tokens


def comorbidity_frequency(
    df: pd.DataFrame,
    *,
    top_n: int = 10,
    raw_col: str = COL_COMORBIDADES,
) -> pd.DataFrame:
    """Top comorbidades após parsing de campos compostos."""
    if raw_col not in df.columns:
        return pd.DataFrame(columns=["valor", "absoluta", "relativa"])
    counter: Counter[str] = Counter()
    for value in df[raw_col].dropna():
        counter.update(parse_comorbidity_tokens(value))
    if not counter:
        return pd.DataFrame(columns=["valor", "absoluta", "relativa"])
    total_patients = len(df)
    rows = counter.most_common(top_n)
    return pd.DataFrame(
        {
            "valor": [name for name, _ in rows],
            "absoluta": [count for _, count in rows],
            "relativa": [count / total_patients for _, count in rows],
        }
    )


def _intervention_is_yes(value: object) -> bool:
    """Indica uso de intervenção a partir de valor bruto ou padronizado."""
    text = normalize_text(value)
    if text is None:
        return False
    if text in {"CN", "AA"}:
        return True
    flag = parse_yes_no(text)
    if flag == "SIM":
        return True
    if flag == "NAO":
        return False
    return has_positive_indicator(text) == "SIM"


def interventions_table(df: pd.DataFrame) -> pd.DataFrame:
    """Tabela de suportes e intervenções terapêuticas (SIM/NAO)."""
    rows: list[dict[str, object]] = []
    total = len(df)
    for label, column in INTERVENTION_SPECS:
        if column not in df.columns:
            continue
        yes_count = int(df[column].map(_intervention_is_yes).sum())
        rows.append(
            {
                "intervencao": label,
                "sim": yes_count,
                "nao": total - yes_count,
                "pct_sim": yes_count / total if total else 0.0,
            }
        )
    return pd.DataFrame(rows)


def deaths_palliative_table(df: pd.DataFrame) -> pd.DataFrame:
    """Óbitos totais e quantos estavam em cuidados paliativos."""
    if COL_DESFECHO_PADRONIZADO not in df.columns:
        return pd.DataFrame()
    deaths = df[df[COL_DESFECHO_PADRONIZADO] == "OBITO"]
    total_deaths = len(deaths)
    if COL_CUIDADOS_PALIATIVOS not in deaths.columns:
        return pd.DataFrame(
            [{"metrica": "Total de óbitos", "valor": total_deaths}]
        )
    palliative = deaths[COL_CUIDADOS_PALIATIVOS].map(
        lambda v: (
            parse_yes_no(v) == "SIM" or has_positive_indicator(v) == "SIM"
        )
    )
    palliative_count = int(palliative.sum())
    return pd.DataFrame(
        [
            {"metrica": "Total de óbitos", "valor": total_deaths},
            {
                "metrica": "Óbitos em cuidados paliativos",
                "valor": palliative_count,
            },
            {
                "metrica": "Proporção em cuidados paliativos",
                "valor": (
                    palliative_count / total_deaths if total_deaths else 0.0
                ),
            },
        ]
    )


def death_causes_table(
    df: pd.DataFrame,
    *,
    top_n: int = 15,
) -> pd.DataFrame:
    """Principais causas de óbito entre pacientes com desfecho óbito."""
    required = {COL_CAUSA_OBITO, COL_DESFECHO_PADRONIZADO}
    if not required.issubset(df.columns):
        return pd.DataFrame(columns=["valor", "absoluta", "relativa"])
    deaths = df[df[COL_DESFECHO_PADRONIZADO] == "OBITO"]
    causes = deaths[COL_CAUSA_OBITO].map(normalize_text)
    causes = causes[causes.notna() & (causes != ".")]
    counts = causes.value_counts().head(top_n)
    total = len(deaths)
    return pd.DataFrame(
        {
            "valor": counts.index.astype(str),
            "absoluta": counts.values,
            "relativa": counts.values / total,
        }
    )


def apache_bands() -> list[ApacheBand]:
    """Faixas APACHE II com mortalidade estimada de referência."""
    return [
        ApacheBand(
            label=str(row["faixa"]),
            min_score=int(row["min"]),
            max_score=int(row["max"]),
            estimated_mortality_pct=float(row["mortalidade_estimada_pct"]),
        )
        for row in APACHE_MORTALITY_BANDS
    ]


def _apache_band_label(score: float) -> str | None:
    for band in apache_bands():
        if band.min_score <= score <= band.max_score:
            return band.label
    return None


def apache_mortality_table(df: pd.DataFrame) -> pd.DataFrame:
    """APACHE II por faixa: observado vs mortalidade estimada."""
    required = {COL_APACHE_II, COL_DESFECHO_PADRONIZADO}
    if not required.issubset(df.columns):
        return pd.DataFrame()
    subset = df[[COL_APACHE_II, COL_DESFECHO_PADRONIZADO]].dropna(
        subset=[COL_APACHE_II]
    )
    subset = subset.copy()
    subset["faixa_apache"] = subset[COL_APACHE_II].map(_apache_band_label)
    rows: list[dict[str, object]] = []
    for band in apache_bands():
        band_df = subset[subset["faixa_apache"] == band.label]
        n = len(band_df)
        deaths = int((band_df[COL_DESFECHO_PADRONIZADO] == "OBITO").sum())
        rows.append(
            {
                "faixa_apache": band.label,
                "mortalidade_estimada_pct": band.estimated_mortality_pct,
                "n_pacientes": n,
                "obitos_observados": deaths,
                "mortalidade_observada_pct": (
                    100.0 * deaths / n if n else 0.0
                ),
            }
        )
    return pd.DataFrame(rows)


def apache_vs_los_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Resumo da relação APACHE II × tempo de internação na UTI."""
    cols = [COL_APACHE_II, COL_TEMPO_UTI]
    if not all(col in df.columns for col in cols):
        return pd.DataFrame()
    subset = df[cols].dropna()
    if subset.empty:
        return pd.DataFrame()
    corr = subset[COL_APACHE_II].corr(subset[COL_TEMPO_UTI])
    return pd.DataFrame(
        [
            {"metrica": "n", "valor": len(subset)},
            {"metrica": "correlacao_pearson", "valor": corr},
            {
                "metrica": "apache_media",
                "valor": subset[COL_APACHE_II].mean(),
            },
            {
                "metrica": "tempo_uti_media_dias",
                "valor": subset[COL_TEMPO_UTI].mean(),
            },
        ]
    )


def apache_vs_los_points(df: pd.DataFrame) -> pd.DataFrame:
    """Pontos para scatter APACHE II × tempo de internação."""
    cols = [COL_APACHE_II, COL_TEMPO_UTI, COL_DESFECHO_PADRONIZADO]
    if not all(col in df.columns for col in cols[:2]):
        return pd.DataFrame()
    subset = df[cols].dropna(subset=[COL_APACHE_II, COL_TEMPO_UTI])
    return subset.rename(
        columns={
            COL_APACHE_II: "apache",
            COL_TEMPO_UTI: "tempo_uti",
            COL_DESFECHO_PADRONIZADO: "desfecho",
        }
    )
