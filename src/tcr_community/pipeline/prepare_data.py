"""Pipeline de preparação de dados."""

from pathlib import Path

import pandas as pd

from tcr_community.cleaning.standardize import clean_and_standardize
from tcr_community.io.loaders import DEFAULT_EXCEL_PATH, load_tcr_excel

INTERIM_PATH = Path("/home/rwp/code/tcr_community/data/external/COLETA_DE_DADOS_TCR.xlsx")
PROCESSED_PATH = Path("/home/rwp/code/tcr_community/data/processed/tcr_patients_clean.parquet")


def _stringify_objects(df: pd.DataFrame) -> pd.DataFrame:
    """Converte colunas object mistas para string para parquet."""
    out = df.copy()
    for col in out.select_dtypes(include=["object", "string"]).columns:
        out[col] = out[col].astype("string")
    return out


def prepare_data(
    excel_path: Path | str = DEFAULT_EXCEL_PATH,
    interim_path: Path | str = INTERIM_PATH,
    processed_path: Path | str = PROCESSED_PATH,
) -> pd.DataFrame:
    """Executa ingestão, transposição e limpeza; salva parquet.

    Args:
        excel_path: Caminho ao Excel externo.
        interim_path: Destino do parquet bruto transposto.
        processed_path: Destino do parquet limpo.

    Returns:
        DataFrame processado.
    """
    interim_path = Path(interim_path)
    processed_path = Path(processed_path)
    interim_path.parent.mkdir(parents=True, exist_ok=True)
    processed_path.parent.mkdir(parents=True, exist_ok=True)

    raw = load_tcr_excel(excel_path)
    raw = _stringify_objects(raw)
    raw.to_parquet(interim_path, index=False)

    clean = clean_and_standardize(raw)
    clean = _stringify_objects(clean)
    clean.to_parquet(processed_path, index=False)

    return clean


if __name__ == "__main__":
    df = prepare_data()
    print(f"Processados {len(df)} pacientes -> {PROCESSED_PATH}")
