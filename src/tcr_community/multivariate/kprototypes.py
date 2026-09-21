"""K-Prototypes: clustering misto (categórico + numérico)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from kmodes.kprototypes import KPrototypes

from tcr_community.multivariate.prep import ClusteringFrame
from tcr_community.schemas.columns import COL_DESFECHO_PADRONIZADO


@dataclass
class KPrototypesFitResult:
    """Resultado de um ajuste K-Prototypes.

    Attributes:
        k: Número de clusters usado.
        cost: Custo final (soma de dissimilaridades) do modelo.
        labels: Rótulo de cluster por linha (mesma ordem de
            ``frame.patient_index``).
    """

    k: int
    cost: float
    labels: np.ndarray


def cost_by_k(
    frame: ClusteringFrame,
    k_values: list[int],
    *,
    random_state: int = 42,
    n_init: int = 5,
) -> pd.DataFrame:
    """Calcula o custo K-Prototypes para uma faixa de k (método do cotovelo).

    Args:
        frame: Saída de ``prepare_clustering_frame``.
        k_values: Valores de k a testar (ex.: ``range(2, 8)``).
        random_state: Semente para reprodutibilidade.
        n_init: Número de inicializações por k (kmodes ``n_init``).

    Returns:
        DataFrame com colunas ``k`` e ``cost``, uma linha por valor de k.
    """
    costs: list[dict[str, float]] = []
    for k in k_values:
        model = KPrototypes(
            n_clusters=k,
            init="Cao",
            n_init=n_init,
            random_state=random_state,
        )
        model.fit(
            frame.data.values,
            categorical=frame.categorical_idx,
        )
        costs.append({"k": k, "cost": float(model.cost_)})
    return pd.DataFrame(costs)


def fit_kprototypes(
    frame: ClusteringFrame,
    k: int,
    *,
    random_state: int = 42,
    n_init: int = 10,
) -> KPrototypesFitResult:
    """Ajusta K-Prototypes com k fixo.

    Args:
        frame: Saída de ``prepare_clustering_frame``.
        k: Número de clusters.
        random_state: Semente para reprodutibilidade.
        n_init: Número de inicializações.

    Returns:
        KPrototypesFitResult com rótulos e custo final.
    """
    model = KPrototypes(
        n_clusters=k,
        init="Cao",
        n_init=n_init,
        random_state=random_state,
    )
    labels = model.fit_predict(
        frame.data.values,
        categorical=frame.categorical_idx,
    )
    return KPrototypesFitResult(
        k=k,
        cost=float(model.cost_),
        labels=labels.astype(int),
    )


def cluster_profile_table(
    frame: ClusteringFrame,
    labels: np.ndarray,
) -> pd.DataFrame:
    """Perfil de cada cluster: moda das categóricas, média das numéricas.

    Args:
        frame: ClusteringFrame usado no ajuste.
        labels: Rótulos de cluster (mesma ordem de ``frame.data``).

    Returns:
        DataFrame indexado por cluster, uma coluna por preditora com a
        moda (categóricas) ou média (numéricas), mais coluna ``n``.
    """
    data = frame.data.copy()
    data["cluster"] = labels
    cat_cols = data.columns[frame.categorical_idx]
    num_cols = [c for c in frame.data.columns if c not in set(cat_cols)]

    rows: list[dict[str, object]] = []
    for cluster_id, group in data.groupby("cluster"):
        row: dict[str, object] = {"cluster": cluster_id, "n": len(group)}
        for col in cat_cols:
            mode = group[col].mode()
            row[col] = mode.iat[0] if not mode.empty else None
        for col in num_cols:
            row[col] = group[col].mean()
        rows.append(row)

    return pd.DataFrame(rows).set_index("cluster").sort_index()


def cluster_vs_outcome_table(
    df: pd.DataFrame,
    frame: ClusteringFrame,
    labels: np.ndarray,
    target: str = COL_DESFECHO_PADRONIZADO,
) -> pd.DataFrame:
    """Crosstab cluster × desfecho (contagem e percentual por linha).

    Args:
        df: Dataset original contendo ``target``, mesmo índice do df
            passado a ``prepare_clustering_frame``.
        frame: ClusteringFrame usado no ajuste.
        labels: Rótulos de cluster.
        target: Coluna de desfecho.

    Returns:
        DataFrame crosstab (linhas=cluster, colunas=categorias do
        desfecho) com contagens absolutas seguidas das colunas
        percentuais ``pct_<categoria>``.
    """
    cluster_series = pd.Series(
        labels, index=frame.patient_index, name="cluster"
    )
    outcome = df.loc[frame.patient_index, target]
    counts = pd.crosstab(cluster_series, outcome)
    pct = counts.div(counts.sum(axis=1), axis=0)
    pct.columns = [f"pct_{c}" for c in pct.columns]
    return pd.concat([counts, pct], axis=1)
