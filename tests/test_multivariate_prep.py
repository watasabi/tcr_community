"""Testes de preparo de features multivariadas."""

import numpy as np
import pandas as pd

from tcr_community.multivariate.prep import prepare_clustering_frame


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "comorbidades": ["SIM", "NAO", "SIM", None],
            "genero": ["M", "F", "M", "F"],
            "escala_apache_ii": [10, 15, np.nan, 20],
            "tempo_internacao_uti": [3, 5, 7, 9],
        }
    )


def test_prepare_clustering_frame_dtypes() -> None:
    df = _sample_df()
    frame = prepare_clustering_frame(
        df,
        categorical_cols=["comorbidades", "genero"],
        numeric_cols=["escala_apache_ii", "tempo_internacao_uti"],
    )
    assert frame.data["comorbidades"].dtype == object
    assert frame.data["genero"].dtype == object
    assert frame.data["escala_apache_ii"].dtype == np.float64
    assert frame.data["tempo_internacao_uti"].dtype == np.float64


def test_prepare_clustering_frame_dropna_removes_missing_rows() -> None:
    df = _sample_df()
    frame = prepare_clustering_frame(
        df,
        categorical_cols=["comorbidades", "genero"],
        numeric_cols=["escala_apache_ii", "tempo_internacao_uti"],
    )
    expected_rows = 2
    assert frame.data.isna().sum().sum() == 0
    assert len(frame.data) == expected_rows
    assert list(frame.patient_index) == [0, 1]


def test_prepare_clustering_frame_categorical_idx_order() -> None:
    df = _sample_df()
    frame = prepare_clustering_frame(
        df,
        categorical_cols=["comorbidades", "genero"],
        numeric_cols=["escala_apache_ii", "tempo_internacao_uti"],
    )
    assert frame.categorical_idx == [0, 1]
    assert list(frame.data.columns)[:2] == ["comorbidades", "genero"]
