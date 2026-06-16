"""Testes de padronização."""

from tcr_community.cleaning.standardize import (
    clean_and_standardize,
    has_positive_indicator,
    normalize_text,
    parse_yes_no,
    standardize_desfecho,
    standardize_genero,
)
from tcr_community.io.loaders import DEFAULT_EXCEL_PATH, load_tcr_excel
from tcr_community.schemas.columns import (
    COL_DESFECHO_PADRONIZADO,
    COL_GENERO,
)


def test_normalize_text_strips_and_upper() -> None:
    assert normalize_text("  não ") == "NAO"
    assert normalize_text("F ") == "F"


def test_parse_yes_no() -> None:
    assert parse_yes_no("SIM") == "SIM"
    assert parse_yes_no("NÃO") == "NAO"
    assert parse_yes_no("NAO ") == "NAO"
    assert parse_yes_no("SIM_CVC") == "SIM"


def test_standardize_genero() -> None:
    assert standardize_genero("M") == "M"
    assert standardize_genero("F ") == "F"
    assert standardize_genero(3) == "OUTRO"


def test_standardize_desfecho() -> None:
    assert standardize_desfecho("OBITO") == "OBITO"
    assert standardize_desfecho("ALTA/TRANSFERENCIA") == "ALTA"
    assert standardize_desfecho("TRANSFERENCIA_HT") == "TRANSFERENCIA"


def test_has_positive_indicator() -> None:
    assert has_positive_indicator("NAO") == "NAO"
    assert has_positive_indicator("HAS_DM2") == "SIM"


def test_clean_adds_desfecho_padronizado() -> None:
    raw = load_tcr_excel(DEFAULT_EXCEL_PATH)
    clean = clean_and_standardize(raw)
    assert COL_DESFECHO_PADRONIZADO in clean.columns
    assert COL_GENERO in clean.columns
    assert clean[COL_DESFECHO_PADRONIZADO].notna().any()
