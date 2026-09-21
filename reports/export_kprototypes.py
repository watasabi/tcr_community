#!/usr/bin/env python3
"""Exporta clustering K-Prototypes (categórico + numérico)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from tcr_community.multivariate.kprototypes import (
    cluster_profile_table,
    cluster_vs_outcome_table,
    cost_by_k,
    fit_kprototypes,
)
from tcr_community.multivariate.prep import prepare_clustering_frame
from tcr_community.pipeline.prepare_data import PROCESSED_PATH, prepare_data
from tcr_community.schemas.columns import COL_DESFECHO_PADRONIZADO
from tcr_community.stats.descriptive import export_report

ROOT = Path(__file__).resolve().parents[1]
MULTIVARIATE_DIR = ROOT / "reports" / "multivariate"
FIGURES_DIR = ROOT / "reports" / "figures"

# k escolhido por inspeção visual da curva de custo/cotovelo: o ganho de
# custo cai claramente entre k=3 e k=4, e se torna incremental depois de
# k=4 (ver cluster_kprototypes_cost_by_k.csv).
CHOSEN_K = 4
K_RANGE = list(range(2, 8))


def _load_data() -> pd.DataFrame:
    if not Path(PROCESSED_PATH).exists():
        prepare_data()
    return pd.read_parquet(PROCESSED_PATH)


def _plot_elbow(costs: pd.DataFrame) -> Path:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / "cluster_kprototypes_elbow.png"
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(costs["k"], costs["cost"], marker="o")
    ax.axvline(CHOSEN_K, color="red", linestyle="--", alpha=0.6)
    ax.set_xlabel("k (número de clusters)")
    ax.set_ylabel("custo K-Prototypes")
    ax.set_title("Curva de custo por k (método do cotovelo)")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def main() -> None:
    df = _load_data()
    frame = prepare_clustering_frame(df)

    costs = cost_by_k(frame, K_RANGE)
    result = fit_kprototypes(frame, CHOSEN_K)

    profile = cluster_profile_table(frame, result.labels)
    outcome = cluster_vs_outcome_table(
        df, frame, result.labels, target=COL_DESFECHO_PADRONIZADO
    )

    assignments = pd.DataFrame(
        {
            "patient_index": frame.patient_index,
            "cluster": result.labels,
            COL_DESFECHO_PADRONIZADO: df.loc[
                frame.patient_index, COL_DESFECHO_PADRONIZADO
            ].to_numpy(),
        }
    )

    export_report(
        {
            "cluster_kprototypes_cost_by_k": costs,
            "cluster_kprototypes_profile": profile.reset_index(),
            "cluster_kprototypes_vs_outcome": outcome.reset_index(),
            "cluster_kprototypes_assignments": assignments,
        },
        MULTIVARIATE_DIR,
    )
    elbow_path = _plot_elbow(costs)

    print(f"k escolhido: {CHOSEN_K} (custo final: {result.cost:.1f})")
    print(f"n pacientes no clustering: {len(frame.patient_index)}")
    print(f"CSVs em: {MULTIVARIATE_DIR}")
    print(f"Figura: {elbow_path}")


if __name__ == "__main__":
    main()
