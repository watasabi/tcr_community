"""MCA (redução dimensional categórica) + clustering hierárquico/k-means."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import prince
from scipy.cluster.hierarchy import linkage
from sklearn.cluster import AgglomerativeClustering, KMeans

from tcr_community.multivariate.prep import ClusteringFrame
from tcr_community.schemas.columns import COL_DESFECHO_PADRONIZADO


@dataclass
class MCAResult:
    """Resultado do ajuste MCA.

    Attributes:
        coordinates: Coordenadas dos pacientes nas dimensões MCA
            (colunas ``dim_1``, ``dim_2``, ...), índice =
            ``frame.patient_index``.
        explained_inertia: Série com % de inércia (variância) explicada
            por dimensão.
        model: Objeto ``prince.MCA`` ajustado (para reuso).
    """

    coordinates: pd.DataFrame
    explained_inertia: pd.Series
    model: prince.MCA


def fit_mca(
    frame: ClusteringFrame,
    *,
    n_components: int = 5,
    random_state: int = 42,
) -> MCAResult:
    """Ajusta MCA sobre as colunas categóricas do frame.

    Usa apenas ``frame.categorical_idx`` (MCA não lida com numéricas
    diretamente); numéricas ficam fora da redução dimensional.

    Args:
        frame: Saída de ``prepare_clustering_frame`` (categóricas
            primeiro, ver ``categorical_idx``).
        n_components: Número de dimensões MCA a reter.
        random_state: Semente para reprodutibilidade.

    Returns:
        MCAResult com coordenadas, inércia explicada e modelo ajustado.
    """
    cat_cols = frame.data.columns[frame.categorical_idx]
    cat_data = frame.data[cat_cols]

    model = prince.MCA(n_components=n_components, random_state=random_state)
    model = model.fit(cat_data)

    coords = model.row_coordinates(cat_data)
    coords.columns = [f"dim_{i + 1}" for i in range(coords.shape[1])]
    coords.index = frame.patient_index

    variance = model.percentage_of_variance_
    inertia = pd.Series(
        variance,
        index=[f"dim_{i + 1}" for i in range(len(variance))],
        name="pct_variance",
    )

    return MCAResult(
        coordinates=coords, explained_inertia=inertia, model=model
    )


def hierarchical_linkage_matrix(
    coordinates: pd.DataFrame,
    *,
    method: str = "ward",
) -> np.ndarray:
    """Calcula matriz de ligação para dendrograma (scipy linkage).

    Args:
        coordinates: Coordenadas MCA (ou outras features numéricas).
        method: Método de ligação (default ``ward``).

    Returns:
        Matriz de ligação no formato esperado por
        ``scipy.cluster.hierarchy.dendrogram``.
    """
    return linkage(coordinates.values, method=method)


def fit_hierarchical_clusters(
    coordinates: pd.DataFrame,
    n_clusters: int,
    *,
    method: str = "ward",
) -> np.ndarray:
    """Corta o dendrograma em n_clusters via AgglomerativeClustering.

    Args:
        coordinates: Coordenadas MCA.
        n_clusters: Número de clusters desejado.
        method: Linkage (``ward``, ``complete``, ``average``).

    Returns:
        Array de rótulos de cluster, mesma ordem de ``coordinates``.
    """
    model = AgglomerativeClustering(n_clusters=n_clusters, linkage=method)
    return model.fit_predict(coordinates.values).astype(int)


def fit_kmeans_on_mca(
    coordinates: pd.DataFrame,
    n_clusters: int,
    *,
    random_state: int = 42,
) -> np.ndarray:
    """K-means "clássico" sobre as coordenadas MCA.

    Args:
        coordinates: Coordenadas MCA.
        n_clusters: Número de clusters.
        random_state: Semente.

    Returns:
        Array de rótulos de cluster.
    """
    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    return model.fit_predict(coordinates.values).astype(int)


def mca_scatter_frame(
    df: pd.DataFrame,
    frame: ClusteringFrame,
    mca_result: MCAResult,
    *,
    cluster_labels: dict[str, np.ndarray] | None = None,
    target: str = COL_DESFECHO_PADRONIZADO,
) -> pd.DataFrame:
    """Monta frame para o scatter 2D: dim_1, dim_2, desfecho, clusters.

    Args:
        df: Dataset original (para juntar o desfecho por índice).
        frame: ClusteringFrame usado no MCA.
        mca_result: Resultado de ``fit_mca``.
        cluster_labels: Mapa opcional nome_da_coluna -> rótulos de
            cluster (mesma ordem de ``frame.patient_index``), ex.
            ``{"cluster_hierarquico": h_labels, "cluster_kmeans": k_labels}``.
        target: Coluna de desfecho a incluir para colorir o scatter.

    Returns:
        DataFrame pronto para plot: ``dim_1``, ``dim_2``, ``desfecho``,
        e uma coluna por entrada de ``cluster_labels``, se fornecido.
    """
    out = mca_result.coordinates[["dim_1", "dim_2"]].copy()
    out["desfecho"] = df.loc[frame.patient_index, target].to_numpy()

    for name, labels in (cluster_labels or {}).items():
        out[name] = labels

    return out
