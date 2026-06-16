"""Normalização e limpeza do dataset TCR."""

import re
import unicodedata
from datetime import datetime

import pandas as pd

from tcr_community.schemas.columns import (
    COL_APACHE_II,
    COL_COMORBIDADES,
    COL_DATA_ADMISSAO,
    COL_DATA_ALTA_OBITO,
    COL_DESFECHO,
    COL_DESFECHO_PADRONIZADO,
    COL_DROGAS_VASOATIVAS,
    COL_FAIXA_ETARIA,
    COL_FERIDAS_LPP,
    COL_GENERO,
    COL_HEMODIALISE,
    COL_LOCAL_RESIDENCIA,
    COL_PACIENTE,
    COL_PROCEDIMENTO_CIRURGICO,
    COL_TEMPO_UTI,
    COL_TRANSFUSAO,
    COL_UTI,
    COL_VENTILACAO_MECANICA,
)

YES_TOKENS = frozenset({"SIM", "S"})
NO_TOKENS = frozenset({"NAO", "NÃO", "N", "NEGA", "NEGOU"})
MAX_LABEL_LEN = 50


def normalize_text(value: object) -> str | None:
    """Normaliza texto: trim, maiúsculas, sem acentos."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if not text or text == ".":
        return None
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.upper()


def parse_yes_no(value: object) -> str | None:
    """Converte respostas SIM/NAO em categoria padronizada."""
    text = normalize_text(value)
    if text is None:
        return None
    if text in YES_TOKENS:
        return "SIM"
    if text in NO_TOKENS:
        return "NAO"
    if text.startswith("SIM"):
        return "SIM"
    if text.startswith("NAO") or text.startswith("NÃO"):
        return "NAO"
    return text


def has_positive_indicator(value: object) -> str:
    """Deriva flag SIM/NAO para campos compostos (comorbidades, etc.)."""
    text = normalize_text(value)
    if text is None:
        return "NAO"
    flag = parse_yes_no(text)
    if flag == "SIM":
        return "SIM"
    if flag == "NAO":
        return "NAO"
    return "SIM"


def standardize_genero(value: object) -> str | None:
    """Padroniza gênero em M/F/OUTRO."""
    text = normalize_text(value)
    if text is None:
        return None
    if text in {"M", "MASCULINO"}:
        return "M"
    if text in {"F", "FEMININO"}:
        return "F"
    return "OUTRO"


def standardize_desfecho(value: object) -> str | None:
    """Padroniza desfecho clínico em 3 categorias."""
    text = normalize_text(value)
    if text is None:
        return None
    result = "OUTRO"
    if text.startswith("ALTA"):
        result = "ALTA"
    elif "OBITO" in text:
        result = "OBITO"
    elif "TRANSFERENCIA" in text:
        result = "TRANSFERENCIA"
    elif "ALTA" in text:
        result = "ALTA"
    elif text in NO_TOKENS:
        result = "DESCONHECIDO"
    return result


def parse_date(value: object) -> pd.Timestamp | None:
    """Converte datas mistas (datetime ou string) em Timestamp."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, datetime):
        return pd.Timestamp(value)
    if isinstance(value, pd.Timestamp):
        return value
    text = str(value).strip().rstrip(".")
    if re.match(r"^\d{4}-\d{2}-\d{2}", text):
        parsed = pd.to_datetime(text, errors="coerce")
    else:
        parsed = pd.to_datetime(text, dayfirst=True, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed


def clean_and_standardize(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica limpeza e padronização ao dataset transposto.

    Args:
        df: DataFrame bruto após load_tcr_excel.

    Returns:
        DataFrame limpo pronto para análise.
    """
    out = df.copy()

    if COL_GENERO in out.columns:
        out[COL_GENERO] = out[COL_GENERO].map(standardize_genero)

    if COL_LOCAL_RESIDENCIA in out.columns:
        out[COL_LOCAL_RESIDENCIA] = out[COL_LOCAL_RESIDENCIA].map(
            normalize_text
        )

    numeric_cols = [COL_FAIXA_ETARIA, COL_APACHE_II, COL_TEMPO_UTI, COL_UTI]
    for col in numeric_cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    date_cols = [COL_DATA_ADMISSAO, COL_DATA_ALTA_OBITO]
    for col in date_cols:
        if col in out.columns:
            out[col] = out[col].map(parse_date)

    yes_no_cols = [
        COL_HEMODIALISE,
        COL_PROCEDIMENTO_CIRURGICO,
        COL_VENTILACAO_MECANICA,
    ]
    for col in yes_no_cols:
        if col in out.columns:
            out[col] = out[col].map(parse_yes_no)

    flag_cols = [
        COL_COMORBIDADES,
        COL_DROGAS_VASOATIVAS,
        COL_TRANSFUSAO,
        COL_FERIDAS_LPP,
    ]
    for col in flag_cols:
        if col in out.columns:
            out[col] = out[col].map(has_positive_indicator)

    if COL_DESFECHO in out.columns:
        out[COL_DESFECHO] = out[COL_DESFECHO].map(normalize_text)
        out[COL_DESFECHO_PADRONIZADO] = out[COL_DESFECHO].map(
            standardize_desfecho
        )

    if COL_PACIENTE in out.columns:
        out[COL_PACIENTE] = pd.to_numeric(out[COL_PACIENTE], errors="coerce")

    return out


def simplify_for_association(value: object) -> str | None:
    """Simplifica variáveis categóricas para testes de associação."""
    text = normalize_text(value)
    if text is None:
        return None
    flag = parse_yes_no(text)
    if flag in {"SIM", "NAO"}:
        return flag
    return text[:MAX_LABEL_LEN] if len(text) > MAX_LABEL_LEN else text
