"""Preparo de features para clustering, MCA e árvore de decisão."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from tcr_community.cleaning.standardize import simplify_for_association
from tcr_community.schemas.columns import (
    CLUSTERING_CATEGORICAL_COLS,
    CLUSTERING_NUMERIC_COLS,
)


@dataclass
class ClusteringFrame:
    """Frame pronto para K-Prototypes/MCA + índices de colunas categóricas.

    Attributes:
        data: DataFrame com preditoras, categóricas como ``object``
            (strings) e numéricas como ``float64``, linhas com qualquer
            valor ausente nas colunas selecionadas removidas.
        categorical_idx: Posições (0-based) das colunas categóricas em
            ``data.columns``, na ordem exigida pelo argumento
            ``categorical=`` de ``KPrototypes.fit``.
        patient_index: Índice original de ``data`` no df de entrada,
            preservado para religar clusters aos pacientes/desfecho depois.
    """

    data: pd.DataFrame
    categorical_idx: list[int]
    patient_index: pd.Index


def prepare_clustering_frame(
    df: pd.DataFrame,
    categorical_cols: list[str] | None = None,
    numeric_cols: list[str] | None = None,
    *,
    dropna: bool = True,
) -> ClusteringFrame:
    """Prepara features mistas para K-Prototypes/MCA.

    Simplifica categóricas (``simplify_for_association``), converte
    numéricas via ``pd.to_numeric``, força dtypes simples
    (object/float64) para compatibilidade com kmodes/prince/sklearn, e
    remove linhas com qualquer valor ausente nas colunas selecionadas.

    Args:
        df: Dataset limpo (ex.: ``tcr_patients_clean.parquet``).
        categorical_cols: Preditoras categóricas (default:
            ``CLUSTERING_CATEGORICAL_COLS``).
        numeric_cols: Preditoras numéricas (default:
            ``CLUSTERING_NUMERIC_COLS``).
        dropna: Se True, remove linhas com qualquer NA nas colunas
            selecionadas (kmodes/prince exigem dados completos).

    Returns:
        ClusteringFrame com dados tipados, índices categóricos e o
        índice original das linhas mantidas.
    """
    cat_cols = [
        c
        for c in (categorical_cols or CLUSTERING_CATEGORICAL_COLS)
        if c in df.columns
    ]
    num_cols = [
        c for c in (numeric_cols or CLUSTERING_NUMERIC_COLS) if c in df.columns
    ]

    work = pd.DataFrame(index=df.index)
    for col in cat_cols:
        work[col] = df[col].map(simplify_for_association).astype(object)
    for col in num_cols:
        work[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")

    if dropna:
        work = work.dropna(axis=0, how="any")

    return ClusteringFrame(
        data=work,
        categorical_idx=list(range(len(cat_cols))),
        patient_index=work.index,
    )
