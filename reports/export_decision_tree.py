#!/usr/bin/env python3
"""Exporta árvore de decisão interpretável para o desfecho."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.tree import plot_tree

from tcr_community.multivariate.decision_tree import (
    TreeFitResult,
    classification_report_table,
    feature_importance_table,
    fit_decision_tree,
    prepare_tree_features,
    tree_text_rules,
)
from tcr_community.pipeline.prepare_data import PROCESSED_PATH, prepare_data
from tcr_community.stats.descriptive import export_report

ROOT = Path(__file__).resolve().parents[1]
MULTIVARIATE_DIR = ROOT / "reports" / "multivariate"
FIGURES_DIR = ROOT / "reports" / "figures"

MAX_DEPTH = 4


def _load_data() -> pd.DataFrame:
    if not Path(PROCESSED_PATH).exists():
        prepare_data()
    return pd.read_parquet(PROCESSED_PATH)


def _plot_tree(result: TreeFitResult) -> Path:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / "tree_decision_tree.png"
    fig, ax = plt.subplots(figsize=(18, 10))
    plot_tree(
        result.model,
        feature_names=result.feature_names,
        class_names=result.class_names,
        filled=True,
        rounded=True,
        fontsize=8,
        ax=ax,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def main() -> None:
    df = _load_data()
    x, y = prepare_tree_features(df)
    result = fit_decision_tree(x, y, max_depth=MAX_DEPTH)

    importance = feature_importance_table(result)
    class_report = classification_report_table(result)
    rules = tree_text_rules(result)
    metrics = pd.DataFrame(
        {
            "metric": [
                "n_train",
                "n_test",
                "train_accuracy",
                "test_accuracy",
                "max_depth",
            ],
            "value": [
                result.n_train,
                result.n_test,
                round(result.train_accuracy, 4),
                round(result.test_accuracy, 4),
                MAX_DEPTH,
            ],
        }
    )

    export_report(
        {
            "tree_feature_importance": importance,
            "tree_metrics": metrics,
            "tree_classification_report": class_report,
        },
        MULTIVARIATE_DIR,
    )
    MULTIVARIATE_DIR.mkdir(parents=True, exist_ok=True)
    (MULTIVARIATE_DIR / "tree_rules.txt").write_text(rules)
    tree_path = _plot_tree(result)

    print(f"train_accuracy={result.train_accuracy:.3f}")
    print(f"test_accuracy={result.test_accuracy:.3f}")
    print(f"n_train={result.n_train} n_test={result.n_test}")
    print(f"CSVs em: {MULTIVARIATE_DIR}")
    print(f"Figura: {tree_path}")


if __name__ == "__main__":
    main()
