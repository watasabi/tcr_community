#!/usr/bin/env python3
"""Exporta MCA + clustering hierárquico e k-means sobre coordenadas MCA."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram

from tcr_community.multivariate.mca_hierarchical import (
    fit_hierarchical_clusters,
    fit_kmeans_on_mca,
    fit_mca,
    hierarchical_linkage_matrix,
    mca_scatter_frame,
)
from tcr_community.multivariate.prep import prepare_clustering_frame
from tcr_community.pipeline.prepare_data import PROCESSED_PATH, prepare_data
from tcr_community.schemas.columns import COL_DESFECHO_PADRONIZADO
from tcr_community.stats.descriptive import export_report

ROOT = Path(__file__).resolve().parents[1]
MULTIVARIATE_DIR = ROOT / "reports" / "multivariate"
FIGURES_DIR = ROOT / "reports" / "figures"

# Mesmo n_clusters usado no K-Prototypes (§ export_kprototypes.py),
# para permitir comparação entre os dois métodos de agrupamento.
N_CLUSTERS = 4


def _load_data() -> pd.DataFrame:
    if not Path(PROCESSED_PATH).exists():
        prepare_data()
    return pd.read_parquet(PROCESSED_PATH)


def _plot_scatter(scatter: pd.DataFrame, hue: str, filename: str) -> Path:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / filename
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.scatterplot(
        data=scatter, x="dim_1", y="dim_2", hue=hue, ax=ax, palette="tab10"
    )
    ax.set_xlabel("Dimensão MCA 1")
    ax.set_ylabel("Dimensão MCA 2")
    ax.set_title(f"Pacientes no espaço MCA, coloridos por {hue}")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def _plot_dendrogram(linkage_matrix: np.ndarray) -> Path:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / "mca_dendrogram.png"
    fig, ax = plt.subplots(figsize=(10, 5))
    dendrogram(linkage_matrix, ax=ax, no_labels=True)
    ax.set_xlabel("Pacientes")
    ax.set_ylabel("Distância (Ward)")
    ax.set_title("Dendrograma (clustering hierárquico sobre coordenadas MCA)")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def main() -> None:
    df = _load_data()
    frame = prepare_clustering_frame(df)

    mca_result = fit_mca(frame)
    coords_2d = mca_result.coordinates[["dim_1", "dim_2"]]

    linkage_matrix = hierarchical_linkage_matrix(coords_2d)
    hierarchical_labels = fit_hierarchical_clusters(coords_2d, N_CLUSTERS)
    kmeans_labels = fit_kmeans_on_mca(coords_2d, N_CLUSTERS)

    scatter = mca_scatter_frame(
        df,
        frame,
        mca_result,
        cluster_labels={
            "cluster_hierarquico": hierarchical_labels,
            "cluster_kmeans": kmeans_labels,
        },
        target=COL_DESFECHO_PADRONIZADO,
    )

    inertia_table = mca_result.explained_inertia.reset_index().rename(
        columns={"index": "dimensao"}
    )
    export_report(
        {
            "mca_coordinates": mca_result.coordinates.reset_index(
                names="patient_index"
            ),
            "mca_explained_inertia": inertia_table,
            "cluster_hierarchical_assignments": pd.DataFrame(
                {
                    "patient_index": frame.patient_index,
                    "cluster": hierarchical_labels,
                }
            ),
            "cluster_kmeans_mca_assignments": pd.DataFrame(
                {
                    "patient_index": frame.patient_index,
                    "cluster": kmeans_labels,
                }
            ),
        },
        MULTIVARIATE_DIR,
    )

    scatter_desfecho = _plot_scatter(
        scatter, "desfecho", "mca_scatter_by_desfecho.png"
    )
    scatter_cluster = _plot_scatter(
        scatter, "cluster_hierarquico", "mca_scatter_by_cluster.png"
    )
    dendrogram_path = _plot_dendrogram(linkage_matrix)

    print(f"n pacientes: {len(frame.patient_index)}")
    print(
        "inércia explicada (top 5): "
        f"{mca_result.explained_inertia.round(2).to_dict()}"
    )
    print(f"CSVs em: {MULTIVARIATE_DIR}")
    print(f"Figuras: {scatter_desfecho}, {scatter_cluster}, {dendrogram_path}")


if __name__ == "__main__":
    main()
