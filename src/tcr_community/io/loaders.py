"""Leitura de dados externos TCR."""

from pathlib import Path

import pandas as pd

from tcr_community.schemas.columns import (
    EXCEL_ROW_MAP,
    SECTION_HEADERS,
)

DEFAULT_EXCEL_PATH = Path("data/external/COLETA_DE_DADOS_TCR.xlsx")
DEFAULT_SHEET = "Planilha1"


def load_tcr_excel(
    path: Path | str = DEFAULT_EXCEL_PATH,
    sheet_name: str = DEFAULT_SHEET,
) -> pd.DataFrame:
    """Lê o Excel transposto e retorna pacientes como linhas.

    O arquivo original tem variáveis nas linhas e pacientes nas colunas.
    A função transpõe para o formato paciente × variável.

    Args:
        path: Caminho ao arquivo Excel.
        sheet_name: Nome da aba a ler.

    Returns:
        DataFrame com uma linha por paciente e colunas normalizadas.
    """
    path = Path(path)
    raw = pd.read_excel(path, sheet_name=sheet_name, header=None)

    labels = raw.iloc[:, 0].astype(str).str.strip()
    patient_data = raw.iloc[:, 1:].T
    patient_data.columns = labels.tolist()
    patient_data = patient_data.reset_index(drop=True)

    # Remove linhas de seção e colunas não mapeadas
    keep_labels = [label for label in labels if label not in SECTION_HEADERS]
    patient_data = patient_data[keep_labels]

    rename_map = {
        label: EXCEL_ROW_MAP[label]
        for label in keep_labels
        if label in EXCEL_ROW_MAP
    }
    patient_data = patient_data.rename(columns=rename_map)

    return patient_data
