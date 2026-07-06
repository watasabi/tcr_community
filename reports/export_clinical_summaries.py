#!/usr/bin/env python3
"""Exporta tabelas e figuras da análise descritiva clínica agrupada."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from tcr_community.io.loaders import load_tcr_excel
from tcr_community.pipeline.prepare_data import PROCESSED_PATH, prepare_data
from tcr_community.stats.clinical_summaries import (
    apache_mortality_table,
    apache_vs_los_points,
    apache_vs_los_summary,
    comorbidity_frequency,
    death_causes_table,
    deaths_palliative_table,
    diagnosis_by_category,
    interventions_table,
)
from tcr_community.stats.descriptive import export_report

ROOT = Path(__file__).resolve().parents[1]
DESCRIPTIVE_DIR = ROOT / "reports" / "descriptive"
FIGURES_DIR = ROOT / "reports" / "figures"


@dataclass(frozen=True)
class BarChartSpec:
    """Configuração de gráfico de barras."""

    label_col: str
    value_col: str
    title: str
    filename: str
    horizontal: bool = True


def _load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not Path(PROCESSED_PATH).exists():
        prepare_data()
    clean = pd.read_parquet(PROCESSED_PATH)
    raw = load_tcr_excel()
    return clean, raw


def export_tables(clean: pd.DataFrame, raw: pd.DataFrame) -> list[Path]:
    """Exporta CSVs agrupados para reports/descriptive/."""
    tables = {
        "clin_diagnostico_por_categoria": diagnosis_by_category(clean),
        "clin_comorbidades_top10": comorbidity_frequency(raw, top_n=10),
        "clin_causa_obito_top": death_causes_table(clean, top_n=15),
        "clin_intervencoes": interventions_table(clean),
        "clin_obitos_cuidados_paliativos": deaths_palliative_table(clean),
        "clin_apache_mortalidade_faixas": apache_mortality_table(clean),
        "clin_apache_tempo_internacao": apache_vs_los_summary(clean),
    }
    return export_report(tables, DESCRIPTIVE_DIR)


def _save_bar(df: pd.DataFrame, spec: BarChartSpec) -> Path:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / spec.filename
    plot_df = df.sort_values(spec.value_col, ascending=True)
    fig, ax = plt.subplots(figsize=(10, max(4, 0.4 * len(plot_df))))
    if spec.horizontal:
        ax.barh(
            plot_df[spec.label_col],
            plot_df[spec.value_col],
            color="steelblue",
        )
        ax.set_xlabel("Frequência absoluta")
    else:
        ax.bar(
            plot_df[spec.label_col],
            plot_df[spec.value_col],
            color="steelblue",
        )
        ax.set_ylabel("Frequência absoluta")
        plt.xticks(rotation=45, ha="right")
    ax.set_title(spec.title)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def export_figures(clean: pd.DataFrame, raw: pd.DataFrame) -> list[Path]:
    """Gera figuras PNG em reports/figures/."""
    paths: list[Path] = []

    cat_df = diagnosis_by_category(clean)
    if not cat_df.empty:
        paths.append(
            _save_bar(
                cat_df,
                BarChartSpec(
                    label_col="categoria",
                    value_col="absoluta",
                    title="Diagnósticos por categoria clínica",
                    filename="diagnostico_por_categoria.png",
                ),
            )
        )

    comorb_df = comorbidity_frequency(raw, top_n=10)
    if not comorb_df.empty:
        paths.append(
            _save_bar(
                comorb_df,
                BarChartSpec(
                    label_col="valor",
                    value_col="absoluta",
                    title="10 comorbidades mais frequentes",
                    filename="comorbidades_top10.png",
                ),
            )
        )

    death_df = death_causes_table(clean, top_n=15)
    if not death_df.empty:
        paths.append(
            _save_bar(
                death_df,
                BarChartSpec(
                    label_col="valor",
                    value_col="absoluta",
                    title="Principais causas de óbito",
                    filename="causa_obito_top15.png",
                ),
            )
        )

    scatter_df = apache_vs_los_points(clean)
    if not scatter_df.empty:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        path = FIGURES_DIR / "apache_vs_tempo_internacao.png"
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.scatterplot(
            data=scatter_df,
            x="apache",
            y="tempo_uti",
            hue="desfecho",
            alpha=0.7,
            ax=ax,
        )
        ax.set_xlabel("APACHE II")
        ax.set_ylabel("Tempo de internação na UTI (dias)")
        ax.set_title("APACHE II × tempo de internação")
        fig.tight_layout()
        fig.savefig(path, dpi=120)
        plt.close(fig)
        paths.append(path)

    apache_df = apache_mortality_table(clean)
    if not apache_df.empty:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        path = FIGURES_DIR / "apache_mortalidade_observada_vs_estimada.png"
        fig, ax = plt.subplots(figsize=(9, 5))
        x = range(len(apache_df))
        width = 0.35
        ax.bar(
            [i - width / 2 for i in x],
            apache_df["mortalidade_estimada_pct"],
            width,
            label="Estimada (referência)",
            color="lightgray",
        )
        ax.bar(
            [i + width / 2 for i in x],
            apache_df["mortalidade_observada_pct"],
            width,
            label="Observada",
            color="crimson",
        )
        ax.set_xticks(list(x))
        ax.set_xticklabels(apache_df["faixa_apache"], rotation=0)
        ax.set_ylabel("Mortalidade (%)")
        ax.set_xlabel("Faixa APACHE II")
        ax.set_title("Mortalidade estimada vs observada por faixa APACHE II")
        ax.legend()
        fig.tight_layout()
        fig.savefig(path, dpi=120)
        plt.close(fig)
        paths.append(path)

    return paths


def main() -> None:
    clean, raw = _load_data()
    csv_paths = export_tables(clean, raw)
    fig_paths = export_figures(clean, raw)
    print(f"Exportados {len(csv_paths)} CSVs em {DESCRIPTIVE_DIR}")
    print(f"Exportadas {len(fig_paths)} figuras em {FIGURES_DIR}")


if __name__ == "__main__":
    main()
