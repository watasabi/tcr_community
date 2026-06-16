"""Estatística descritiva para o dataset TCR."""

from pathlib import Path

import pandas as pd

from tcr_community.schemas.columns import (
    CLINICAL_CATEGORICAL_COLS,
    CLINICAL_NUMERIC_COLS,
    DEMOGRAPHIC_COLS,
)


def frequency_table(
    series: pd.Series,
    dropna: bool = True,
) -> pd.DataFrame:
    """Tabela de frequência absoluta e relativa.

    Args:
        series: Série categórica ou discreta.
        dropna: Se True, ignora valores nulos.

    Returns:
        DataFrame com colunas valor, absoluta, relativa.
    """
    counts = series.value_counts(dropna=dropna)
    total = counts.sum()
    return pd.DataFrame(
        {
            "valor": counts.index.astype(str),
            "absoluta": counts.values,
            "relativa": counts.values / total,
        }
    )


def numeric_summary(series: pd.Series) -> pd.DataFrame:
    """Resumo de variável quantitativa.

    Args:
        series: Série numérica.

    Returns:
        DataFrame com média, mediana, min, max e desvio padrão.
    """
    clean = pd.to_numeric(series, errors="coerce").dropna()
    return pd.DataFrame(
        {
            "n": [len(clean)],
            "media": [clean.mean()],
            "mediana": [clean.median()],
            "min": [clean.min()],
            "max": [clean.max()],
            "desvio_padrao": [clean.std(ddof=1) if len(clean) > 1 else 0.0],
        }
    )


def descriptive_report(
    df: pd.DataFrame,
    categorical_cols: list[str] | None = None,
    numeric_cols: list[str] | None = None,
) -> dict[str, pd.DataFrame]:
    """Gera tabelas descritivas para colunas categóricas e numéricas.

    Args:
        df: Dataset de pacientes.
        categorical_cols: Colunas para frequências.
        numeric_cols: Colunas para resumo numérico.

    Returns:
        Dicionário nome_coluna -> tabela descritiva.
    """
    cat_cols = categorical_cols or []
    num_cols = numeric_cols or []
    report: dict[str, pd.DataFrame] = {}

    for col in cat_cols:
        if col in df.columns:
            report[col] = frequency_table(df[col])

    for col in num_cols:
        if col in df.columns:
            report[col] = numeric_summary(df[col])

    return report


def demographic_report(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Tabelas descritivas demográficas."""
    return descriptive_report(
        df,
        categorical_cols=[c for c in DEMOGRAPHIC_COLS if c != "faixa_etaria"],
        numeric_cols=["faixa_etaria"],
    )


def clinical_report(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Tabelas descritivas clínicas."""
    return descriptive_report(
        df,
        categorical_cols=CLINICAL_CATEGORICAL_COLS,
        numeric_cols=CLINICAL_NUMERIC_COLS,
    )


def export_report(
    report: dict[str, pd.DataFrame],
    output_dir: Path | str,
    prefix: str = "",
) -> list[Path]:
    """Exporta tabelas descritivas como CSV.

    Args:
        report: Dicionário de tabelas.
        output_dir: Diretório de destino.
        prefix: Prefixo nos nomes dos arquivos.

    Returns:
        Lista de caminhos exportados.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    for name, table in report.items():
        path = output_dir / f"{prefix}{name}.csv"
        table.to_csv(path, index=False)
        paths.append(path)

    return paths
