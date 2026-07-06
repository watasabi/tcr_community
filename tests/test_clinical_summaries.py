"""Testes de resumos clínicos agrupados."""

import pandas as pd

from tcr_community.stats.clinical_summaries import (
    classify_diagnosis,
    comorbidity_frequency,
    diagnosis_by_category,
    interventions_table,
    parse_comorbidity_tokens,
)


def test_classify_diagnosis_respiratory() -> None:
    assert classify_diagnosis("PNEUMONIA_NE") == "Doenças respiratórias"


def test_classify_diagnosis_sepsis() -> None:
    assert classify_diagnosis("CHOQUE_SEPTICO_FOCO_PULMONAR") == (
        "Sepse e choque séptico"
    )


def test_classify_diagnosis_neurological() -> None:
    assert classify_diagnosis("ACIDENTE_VASCULAR_CEREBRAL_ISQUEMICO") == (
        "Doenças neurológicas"
    )


def test_parse_comorbidity_tokens() -> None:
    tokens = parse_comorbidity_tokens("HAS_DM2_ICC")
    assert tokens == ["HAS", "DM2", "ICC"]


def test_diagnosis_by_category_counts() -> None:
    df = pd.DataFrame(
        {
            "diagnostico_principal": [
                "PNEUMONIA",
                "SEPSE",
                "PNEUMONIA",
            ]
        }
    )
    table = diagnosis_by_category(df)
    resp = table.loc[
        table["categoria"] == "Doenças respiratórias", "absoluta"
    ].iloc[0]
    sepse = table.loc[
        table["categoria"] == "Sepse e choque séptico", "absoluta"
    ].iloc[0]
    expected_resp = 2
    expected_sepse = 1
    assert resp == expected_resp
    assert sepse == expected_sepse


def test_comorbidity_frequency_top() -> None:
    df = pd.DataFrame(
        {
            "comorbidades": [
                "HAS_DM",
                "HAS",
                "NAO",
            ]
        }
    )
    table = comorbidity_frequency(df, top_n=5)
    assert table.iloc[0]["valor"] == "HAS"
    expected_has_count = 2
    assert table.iloc[0]["absoluta"] == expected_has_count


def test_classify_diagnosis_urinary_not_colecistite() -> None:
    assert classify_diagnosis("COLECISTITE_AGUDA") == (
        "Doenças gastrointestinais/abdominais"
    )
    assert classify_diagnosis("CISTITE_AGUDA") == "Infecções urinárias"
    df = pd.DataFrame(
        {
            "ventilacao_mecanica": ["SIM", "NAO", "CN"],
            "sedacao": ["FENTANIL", "NAO", "NAO"],
            "drogas_vasoativas": ["SIM", "NAO", "SIM"],
            "hemodialise": ["NAO", "SIM", "NAO"],
            "transfusao_sanguinea": ["NAO", "NAO", "SIM"],
            "procedimento_cirurgico": ["NAO", "NAO", "NAO"],
            "dispositivo_invasivo": ["CVC_IOT", "NAO", "SVD"],
        }
    )
    table = interventions_table(df)
    vent = table.loc[
        table["intervencao"] == "Ventilação mecânica", "sim"
    ].iloc[0]
    expected_vent_count = 2
    assert vent == expected_vent_count
