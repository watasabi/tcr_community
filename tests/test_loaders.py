"""Testes de leitura do Excel TCR."""

from pathlib import Path

import pandas as pd

from tcr_community.io.loaders import DEFAULT_EXCEL_PATH, load_tcr_excel
from tcr_community.schemas.columns import (
    COL_DESFECHO,
    COL_GENERO,
    COL_PACIENTE,
)

EXCEL = Path(DEFAULT_EXCEL_PATH)
EXPECTED_PATIENT_COUNT = 205


def test_excel_exists() -> None:
    assert EXCEL.exists()


def test_load_transpose_shape() -> None:
    df = load_tcr_excel(EXCEL)
    assert len(df) == EXPECTED_PATIENT_COUNT
    assert COL_PACIENTE in df.columns
    assert COL_GENERO in df.columns
    assert COL_DESFECHO in df.columns


def test_no_section_headers_as_columns() -> None:
    df = load_tcr_excel(EXCEL)
    assert "Variaveis demograficas" not in df.columns
    assert "Variaveis Clinicas" not in df.columns


def test_patient_codes_unique() -> None:
    df = load_tcr_excel(EXCEL)
    codes = pd.to_numeric(df[COL_PACIENTE], errors="coerce")
    assert codes.notna().all()
    assert codes.nunique() == len(df)
