#!/usr/bin/env python3
"""Gera relatório HTML a partir dos CSVs em reports/.

Usage:
    python3 reports/generate_profile_report.py

Creates:
  - ``reports/profile_report.html`` (clássico)
  - ``reports/profile_report_minimal.html`` (tema Apple/minimal)
"""

from __future__ import annotations

import base64
import datetime
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
DESCRIPTIVE_DIR = REPORTS_DIR / "descriptive"
FIGURES_DIR = REPORTS_DIR / "figures"
ASSOC_FILE = REPORTS_DIR / "association_results.csv"
PHIK_MATRIX_FILE = REPORTS_DIR / "association_phik_matrix.csv"
PHIK_FIGURE_FILE = FIGURES_DIR / "association_phik_matrix.png"

# O alias plotly-latest está congelado na v1, que ignora texttemplate.
PLOTLY_CDN = "https://cdn.plot.ly/plotly-3.0.1.min.js"

CLINICAL_SUMMARY_FILES = {
    "Diagnósticos por categoria": "clin_diagnostico_por_categoria.csv",
    "10 comorbidades mais frequentes": "clin_comorbidades_top10.csv",
    "Principais causas de óbito": "clin_causa_obito_top.csv",
    "Suportes e intervenções": "clin_intervencoes.csv",
    "Dispositivos invasivos por tipo": (
        "clin_dispositivos_invasivos_por_tipo.csv"
    ),
    "Ventilação mecânica (SIM/NÃO)": "clin_ventilacao_mecanica_resumo.csv",
    "Óbitos e cuidados paliativos": "clin_obitos_cuidados_paliativos.csv",
    "APACHE II × mortalidade por faixa": "clin_apache_mortalidade_faixas.csv",
    "APACHE II × tempo de internação": "clin_apache_tempo_internacao.csv",
}

FIGURE_CAPTIONS: dict[str, str] = {
    "sexo_bar.png": "Distribuição por gênero",
    "faixa_etaria_hist.png": "Histograma de faixa etária",
    "diagnostico_top20.png": "Top 20 diagnósticos principais",
    "diagnostico_por_categoria.png": "Diagnósticos por categoria clínica",
    "desfecho_pie.png": "Composição de desfechos clínicos",
    "comorbidades_top10.png": "10 comorbidades mais frequentes",
    "causa_obito_top15.png": "Principais causas de óbito",
    "procedencia_top20.png": "Principais procedências de entrada",
    "apache_by_desfecho.png": "APACHE II por desfecho",
    "apache_vs_tempo_internacao.png": "APACHE II × tempo de internação",
    "apache_mortalidade_observada_vs_estimada.png": (
        "Mortalidade observada vs estimada (APACHE II)"
    ),
    "tempo_internacao_por_desfecho.png": (
        "Tempo médio de internação por desfecho"
    ),
    "tempo_internacao_por_ventilacao.png": (
        "Tempo de internação por ventilação mecânica"
    ),
    "tempo_internacao_por_feridas_lpp.png": (
        "Tempo de internação × feridas LPP"
    ),
    "tempo_internacao_por_dispositivo_invasivo.png": (
        "Tempo de internação × dispositivo invasivo"
    ),
    "obito_por_ventilacao.png": "Desfecho por ventilação mecânica",
    "obito_por_drogas_vasoativas.png": "Desfecho por drogas vasoativas",
    "obito_por_hemodialise.png": "Desfecho por hemodiálise",
    "obito_por_procedimento_cirurgico.png": (
        "Desfecho por procedimento cirúrgico"
    ),
    "obito_por_transfusao.png": "Desfecho por transfusão sanguínea",
    "obito_por_comorbidades.png": "Desfecho por comorbidades",
    "obito_por_vicios_top.png": "Desfecho por principais vícios",
    "rcp_vs_cuidados_paliativos.png": "RCP × cuidados paliativos",
    "association_phik_matrix.png": "Matriz de associação PhiK",
}


CSS = """
body{font-family: Arial, Helvetica, sans-serif; margin:20px}
h1,h2{color:#222}
.section{margin-bottom:28px}
table{border-collapse:collapse;width:100%;margin-top:8px}
th,td{border:1px solid #ddd;padding:6px 8px;text-align:left}
th{background:#f7f7f7}
.small{font-size:0.9em;color:#555}
.meta{font-size:0.9em;color:#666;margin-bottom:6px}
.preview{max-height:240px;overflow:auto;border:1px solid #eee;padding:8px;background:#fafafa}
.plot{margin-top:12px;margin-bottom:12px}
.note{font-size:0.9em;color:#666}
img{max-width:100%;height:auto;display:block;margin:8px 0 16px}
.figure-card{margin-bottom:20px}
.figure-card h3{margin-bottom:6px}
"""

# Minimal / Apple-inspired theme (legibility-first)
CSS_MINIMAL = """
:root {
  --bg: #f5f5f7;
  --surface: #ffffff;
  --text: #1d1d1f;
  --muted: #6e6e73;
  --line: rgba(0, 0, 0, 0.08);
  --accent: #0071e3;
  --radius: 16px;
  --shadow: 0 1px 2px rgba(0, 0, 0, 0.04),
            0 8px 24px rgba(0, 0, 0, 0.04);
}

* { box-sizing: border-box; }

html { scroll-behavior: smooth; }

body {
  margin: 0;
  color: var(--text);
  background: var(--bg);
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text",
    "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-size: 15px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

.page {
  max-width: 920px;
  margin: 0 auto;
  padding: 48px 24px 80px;
}

.hero {
  margin-bottom: 40px;
  padding-bottom: 28px;
  border-bottom: 1px solid var(--line);
}

.hero .eyebrow {
  margin: 0 0 8px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.hero h1 {
  margin: 0 0 8px;
  font-size: clamp(28px, 4vw, 40px);
  font-weight: 600;
  letter-spacing: -0.03em;
  line-height: 1.15;
}

.hero .subtitle {
  margin: 0;
  color: var(--muted);
  font-size: 16px;
}

.toc {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 20px 0 0;
}

.toc a {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 980px;
  background: var(--surface);
  border: 1px solid var(--line);
  color: var(--text);
  text-decoration: none;
  font-size: 13px;
  transition: border-color 0.15s ease, color 0.15s ease;
}

.toc a:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.section {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 28px 28px 24px;
  margin-bottom: 24px;
}

.section > h2 {
  margin: 0 0 6px;
  font-size: 22px;
  font-weight: 600;
  letter-spacing: -0.02em;
}

.section > h3,
details h3 {
  margin: 28px 0 10px;
  font-size: 17px;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.section > h3:first-of-type {
  margin-top: 18px;
}

.meta, .note, .small {
  color: var(--muted);
  font-size: 13px;
}

.meta { margin: 0 0 14px; }

.note {
  margin: 10px 0;
}

table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  margin-top: 8px;
  font-size: 13.5px;
  overflow: hidden;
  border-radius: 12px;
  border: 1px solid var(--line);
}

th, td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid var(--line);
  vertical-align: top;
}

th {
  background: #fafafa;
  color: var(--muted);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

tr:last-child td,
tr:last-child th {
  border-bottom: none;
}

tbody tr:hover td {
  background: #fbfbfd;
}

.preview-table,
.desc-table {
  display: block;
  max-height: 320px;
  overflow: auto;
}

details {
  margin-top: 12px;
}

details > summary {
  cursor: pointer;
  list-style: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: 980px;
  border: 1px solid var(--line);
  background: #fafafa;
  color: var(--text);
  font-size: 13px;
  font-weight: 500;
  user-select: none;
}

details > summary::-webkit-details-marker { display: none; }

details > summary::before {
  content: "";
  width: 6px;
  height: 6px;
  border-right: 1.5px solid var(--muted);
  border-bottom: 1.5px solid var(--muted);
  transform: rotate(-45deg);
  transition: transform 0.15s ease;
}

details[open] > summary::before {
  transform: rotate(45deg);
}

details[open] > summary {
  margin-bottom: 14px;
}

.plot {
  margin: 16px 0;
  padding: 8px;
  border-radius: 12px;
  background: #fafafa;
  border: 1px solid var(--line);
}

img {
  display: block;
  width: 100%;
  height: auto;
  margin: 8px 0 4px;
  border-radius: 12px;
  border: 1px solid var(--line);
  background: #fff;
}

.figure-card {
  margin: 0 0 28px;
}

.figure-card h3 {
  margin: 0 0 10px;
  font-size: 17px;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.figure-grid {
  display: grid;
  gap: 8px;
}

code {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.92em;
  background: #f0f0f2;
  padding: 1px 6px;
  border-radius: 6px;
}

.footer {
  margin-top: 8px;
  color: var(--muted);
  font-size: 12px;
  text-align: center;
}

@media (max-width: 640px) {
  .page { padding: 28px 16px 56px; }
  .section { padding: 20px 16px; }
  th, td { padding: 8px 10px; }
}
"""


def df_to_html_preview(df: pd.DataFrame, max_rows: int = 10) -> str:
    df2 = df.head(max_rows).copy()
    df2 = df2.fillna("")
    return df2.to_html(classes="preview-table", index=False, border=0)


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def df_table_html(df: pd.DataFrame) -> str:
    return df.fillna("").to_html(index=False, border=0)


def format_clinical_table(df: pd.DataFrame) -> pd.DataFrame:
    """Formata colunas percentuais para exibição HTML."""
    display = df.copy()
    if "relativa" in display.columns:
        display["relativa"] = display["relativa"].map(pct)
    if "pct_sim" in display.columns:
        display["pct_sim"] = display["pct_sim"].map(pct)
    if "metrica" in display.columns and "valor" in display.columns:
        mask = display["metrica"] == "Proporção em cuidados paliativos"
        if mask.any():
            display["valor"] = display["valor"].astype(object)
            display.loc[mask, "valor"] = display.loc[mask, "valor"].map(pct)
    if "mortalidade_observada_pct" in display.columns:
        display["mortalidade_observada_pct"] = display[
            "mortalidade_observada_pct"
        ].map(lambda v: f"{v:.1f}%")
    return display


def describe_df_html(df: pd.DataFrame) -> str:
    try:
        desc = df.describe(include="all", datetime_is_numeric=False).T
    except TypeError:
        desc = df.describe(include="all").T
    desc_html = desc.fillna("").to_html(classes="desc-table")
    return desc_html


def export_phik_matrix() -> pd.DataFrame | None:
    """Calcula, salva CSV/PNG e devolve a matriz PhiK.

    Returns:
        Matriz PhiK ou None se dados/cálculo indisponíveis.
    """
    try:
        from tcr_community.pipeline.prepare_data import (
            PROCESSED_PATH,
            prepare_data,
        )
        from tcr_community.stats.association import phik_association_matrix
    except ImportError as exc:
        print(f"Aviso: PhiK indisponível ({exc})")
        return None

    path = Path(PROCESSED_PATH)
    if not path.exists():
        try:
            prepare_data()
        except Exception as exc:  # noqa: BLE001
            print(f"Aviso: não foi possível preparar dados ({exc})")
            return None

    try:
        df = pd.read_parquet(path)
        matrix = phik_association_matrix(df)
    except Exception as exc:  # noqa: BLE001
        print(f"Aviso: falha ao calcular PhiK ({exc})")
        return None

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    matrix.round(4).to_csv(PHIK_MATRIX_FILE)

    try:
        import matplotlib.pyplot as plt
        import seaborn as sns

        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        n = len(matrix)
        fig_w = max(7.0, 0.7 * n + 2)
        fig, ax = plt.subplots(figsize=(fig_w, fig_w * 0.85))
        sns.heatmap(
            matrix.astype(float),
            annot=True,
            fmt=".2f",
            cmap="Blues",
            vmin=0.0,
            vmax=1.0,
            square=True,
            linewidths=0.4,
            linecolor="#ffffff",
            cbar_kws={"label": "PhiK", "shrink": 0.8},
            ax=ax,
        )
        ax.set_title("Matriz de associação PhiK")
        plt.xticks(rotation=45, ha="right")
        plt.yticks(rotation=0)
        fig.tight_layout()
        fig.savefig(PHIK_FIGURE_FILE, dpi=150, bbox_inches="tight")
        plt.close(fig)
    except Exception as exc:  # noqa: BLE001
        print(f"Aviso: figura PhiK não gerada ({exc})")

    return matrix


def load_phik_matrix() -> pd.DataFrame | None:
    """Carrega matriz PhiK do CSV, se existir."""
    if not PHIK_MATRIX_FILE.exists():
        return None
    try:
        return pd.read_csv(PHIK_MATRIX_FILE, index_col=0)
    except Exception:  # noqa: BLE001
        return None


def phik_heatmap_html(
    matrix: pd.DataFrame,
    *,
    plot_id: str,
    theme: str,
) -> str:
    """Monta heatmap Plotly da matriz PhiK."""
    labels = [str(c) for c in matrix.columns]
    z = matrix.astype(float).values.tolist()
    text = [[f"{v:.2f}" for v in row] for row in z]
    n = len(labels)
    height = max(420, min(900, 48 * n + 160))
    colorscale = (
        [[0, "#f5f5f7"], [0.5, "#64b5f6"], [1, "#0071e3"]]
        if theme == "minimal"
        else "Blues"
    )
    paper = "rgba(0,0,0,0)" if theme == "minimal" else "white"
    font_color = "#1d1d1f" if theme == "minimal" else "#222"
    return f"""
<script>
  (function(){{
    const labels = {json.dumps(labels)};
    const z = {json.dumps(z)};
    const text = {json.dumps(text)};
    const data = [{{
      z: z,
      x: labels,
      y: labels,
      type: 'heatmap',
      colorscale: {json.dumps(colorscale)},
      zmin: 0,
      zmax: 1,
      text: text,
      texttemplate: '%{{text}}',
      textfont: {{size: 11}},
      hovertemplate:
        '%{{y}} × %{{x}}<br>PhiK=%{{z:.3f}}<extra></extra>',
      colorbar: {{title: 'PhiK', thickness: 14}}
    }}];
    const layout = {{
      title: 'Matriz de associação PhiK',
      height: {height},
      margin: {{l: 140, r: 40, t: 60, b: 120}},
      xaxis: {{tickangle: -40, side: 'bottom'}},
      yaxis: {{autorange: 'reversed'}},
      paper_bgcolor: '{paper}',
      plot_bgcolor: '{paper}',
      font: {{color: '{font_color}', size: 12}}
    }};
    Plotly.newPlot('{plot_id}', data, layout, {{responsive: true}});
  }})();
</script>
"""


def render_report(
    out_path: Path,
    *,
    theme: str = "classic",
) -> None:
    """Render HTML report.

    Args:
        out_path: Destination HTML path.
        theme: ``classic`` or ``minimal`` (Apple-inspired).
    """
    generated_at = datetime.datetime.now().isoformat(
        sep=" ", timespec="seconds"
    )
    parts: list[str] = []

    if theme == "minimal":
        parts.append('<div class="page">')
        parts.append('<header class="hero">')
        parts.append('<p class="eyebrow">tcr_community</p>')
        parts.append("<h1>Relatório de Dados</h1>")
        parts.append(
            f'<p class="subtitle">Gerado em {html_escape(generated_at)}</p>'
        )
        parts.append('<nav class="toc" aria-label="Seções">')
        parts.append('<a href="#associacao">Associações</a>')
        parts.append('<a href="#clinica">Análise clínica</a>')
        parts.append('<a href="#figuras">Figuras</a>')
        parts.append('<a href="#descritivos">CSVs descritivos</a>')
        parts.append("</nav>")
        parts.append("</header>")
    else:
        parts.append(
            f"<h1>Relatório de Dados — gerado {generated_at}</h1>"
        )

    # Association results
    section_id = ' id="associacao"' if theme == "minimal" else ""
    parts.append(f'<div class="section"{section_id}>')
    parts.append("<h2>Association results</h2>")

    phik = load_phik_matrix()
    if phik is not None and not phik.empty:
        parts.append("<h3>Matriz de associação PhiK</h3>")
        parts.append(
            '<p class="note">Coeficiente PhiK (0–1) entre preditoras '
            "clínicas e o desfecho. Funciona com variáveis categóricas "
            "e numéricas (equivalente a uma matriz de correlação para "
            "dados mistos).</p>"
        )
        parts.append(
            f'<div class="meta">Fonte: '
            f"{html_escape(str(PHIK_MATRIX_FILE.relative_to(ROOT)))}"
            f"</div>"
        )
        plot_id = "phik-heatmap"
        parts.append(f'<div id="{plot_id}" class="plot"></div>')
        parts.append(phik_heatmap_html(phik, plot_id=plot_id, theme=theme))
        parts.append(
            '<details><summary class="small">'
            "Tabela da matriz PhiK</summary>"
        )
        parts.append(
            phik.round(3)
            .fillna("")
            .to_html(classes="preview-table", border=0)
        )
        parts.append("</details>")
    else:
        parts.append(
            '<div class="note">Matriz PhiK não disponível. '
            "Execute o gerador com dados processados para calculá-la."
            "</div>"
        )

    if ASSOC_FILE.exists():
        try:
            assoc = pd.read_csv(ASSOC_FILE)
            parts.append(
                f'<div class="meta">Fonte: '
                f"{html_escape(str(ASSOC_FILE.relative_to(ROOT)))}, "
                f"linhas: {len(assoc)}</div>"
            )
            parts.append(
                '<details open><summary class="small">'
                "Preview, estatísticas e plots (client-side)</summary>"
            )
            parts.append(
                '<h3 class="small">Preview (primeiras linhas)</h3>'
            )
            parts.append(df_to_html_preview(assoc))
            parts.append(
                '<h3 class="small">Estatísticas sumarizadas</h3>'
            )
            parts.append(describe_df_html(assoc))

            # p-value bar chart data for client-side Plotly
            try:
                if (
                    "p_value" in assoc.columns
                    and "variable" in assoc.columns
                ):
                    dfp = assoc.copy()
                    dfp["p_value"] = pd.to_numeric(
                        dfp["p_value"], errors="coerce"
                    )
                    missing_mask = dfp["p_value"].isna()
                    dfp.loc[missing_mask, "p_value"] = 1.0
                    dfp = dfp.sort_values(
                        by="p_value", ascending=True
                    ).reset_index(drop=True)
                    dfp["-log10_p"] = [
                        -math.log10(max(v, 1e-300))
                        for v in dfp["p_value"]
                    ]
                    dfp["significant"] = (
                        dfp["p_value"] < 0.05
                    ).astype(int)

                    vars_full = dfp["variable"].astype(str).tolist()
                    vars_short = [
                        (v if len(v) <= 40 else v[:37] + "...")
                        for v in vars_full
                    ]
                    vals = dfp["-log10_p"].tolist()
                    sig = dfp["significant"].astype(int).tolist()
                    missing = missing_mask.astype(int).tolist()

                    # colors: missing -> lightgray, significant -> accent/red
                    if theme == "minimal":
                        colors = [
                            (
                                "#c7c7cc"
                                if m
                                else ("#ff3b30" if s else "#0071e3")
                            )
                            for m, s in zip(missing, sig, strict=True)
                        ]
                    else:
                        colors = [
                            (
                                "lightgray"
                                if m
                                else ("crimson" if s else "steelblue")
                            )
                            for m, s in zip(missing, sig, strict=True)
                        ]

                    plot_id = "assoc-plot"
                    parts.append(
                        f'<div id="{plot_id}" class="plot"></div>'
                    )
                    height = max(300, min(1200, 50 * len(vars_short)))

                    js = (
                        """
<script>
  (function(){
    const vars = %s;
    const varsFull = %s;
    const vals = %s;
    const colors = %s;
    const data = [{
      x: vars,
      y: vals,
      type: 'bar',
      marker: {color: colors},
      hovertemplate: '%%{customdata[0]}<br>-log10(p)=%%{y}<extra></extra>',
      customdata: varsFull.map(v => [v])
    }];
    const layout = {title: '-log10(p-value) por variável', xaxis: {tickangle: -45}, yaxis: {title: '-log10(p-value)'}, height: %d, margin: {b: 150}};
    Plotly.newPlot('%s', data, layout, {responsive: true});
  })();
</script>
"""
                        % (
                            json.dumps(vars_short),
                            json.dumps(vars_full),
                            json.dumps(vals),
                            json.dumps(colors),
                            height,
                            plot_id,
                        )
                    )
                    parts.append(js)
                else:
                    parts.append(
                        '<div class="note">p_value ou variable ausente '
                        "no CSV de associação — sem gráfico.</div>"
                    )
            except Exception:
                parts.append(
                    '<div class="note">Erro ao preparar gráfico '
                    "de p-values.</div>"
                )

            parts.append("</details>")
        except Exception as e:
            parts.append(
                f'<div class="note">Erro ao ler '
                f"{html_escape(ASSOC_FILE.name)}: "
                f"{html_escape(str(e))}</div>"
            )
    else:
        parts.append(
            f'<div class="note">Arquivo '
            f"{html_escape(ASSOC_FILE.name)} não encontrado.</div>"
        )

    parts.append("</div>")

    # Clinical summaries (categorized)
    section_id = ' id="clinica"' if theme == "minimal" else ""
    parts.append(f'<div class="section"{section_id}>')
    parts.append("<h2>Análise descritiva clínica</h2>")
    parts.append(
        '<p class="note">Diagnósticos agrupados por categoria, '
        "comorbidades, causas de óbito, intervenções e APACHE II.</p>"
    )
    has_clinical = False
    for title, filename in CLINICAL_SUMMARY_FILES.items():
        path = DESCRIPTIVE_DIR / filename
        if not path.exists():
            continue
        has_clinical = True
        df = pd.read_csv(path)
        parts.append(f"<h3>{html_escape(title)}</h3>")
        parts.append(df_table_html(format_clinical_table(df)))

    if not has_clinical:
        parts.append(
            '<div class="note">Execute '
            "<code>uv run python reports/export_clinical_summaries.py</code> "
            "para gerar tabelas e figuras desta seção.</div>"
        )
    parts.append("</div>")

    # All figures from reports/figures/
    section_id = ' id="figuras"' if theme == "minimal" else ""
    parts.append(f'<div class="section"{section_id}>')
    parts.append("<h2>Figuras</h2>")
    figure_files = list_figure_files()
    if figure_files:
        parts.append(
            f'<p class="note">Todas as imagens em '
            f"<code>reports/figures/</code> "
            f"({len(figure_files)} arquivos), embutidas neste arquivo: "
            f"continuam visíveis após download ou envio por e-mail.</p>"
        )
        img_style = (
            ""
            if theme == "minimal"
            else ' style="max-width:100%;height:auto;"'
        )
        for fig_path in figure_files:
            caption = figure_caption(fig_path.name)
            parts.append('<div class="figure-card">')
            parts.append(f"<h3>{html_escape(caption)}</h3>")
            parts.append(
                f'<div class="meta">{html_escape(fig_path.name)}</div>'
            )
            parts.append(
                f'<img src="{figure_data_uri(fig_path)}" '
                f'alt="{html_escape(caption)}"{img_style} />'
            )
            parts.append("</div>")
    else:
        parts.append(
            '<div class="note">Nenhuma figura PNG encontrada em '
            "<code>reports/figures/</code>.</div>"
        )
    parts.append("</div>")

    # Descriptive CSVs
    section_id = ' id="descritivos"' if theme == "minimal" else ""
    parts.append(f'<div class="section"{section_id}>')
    parts.append("<h2>Descriptive CSVs</h2>")
    if DESCRIPTIVE_DIR.exists() and any(DESCRIPTIVE_DIR.iterdir()):
        for p in sorted(DESCRIPTIVE_DIR.glob("*.csv")):
            try:
                df = pd.read_csv(p)
                parts.append(f"<h3>{html_escape(p.name)}</h3>")
                parts.append(f'<div class="meta">linhas: {len(df)}, colunas: {len(df.columns)}</div>')
                parts.append('<details><summary class="small">Preview, estatísticas e plots</summary>')
                parts.append(df_to_html_preview(df))
                parts.append(describe_df_html(df))

                # simple client-side plots
                try:
                    nums = df.select_dtypes(include='number').columns.tolist()
                    cats = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
                    if nums:
                        coln = nums[0]
                        series = df[coln].dropna()
                        if len(series) > 0:
                            if series.nunique() <= 10:
                                vc = series.astype(str).value_counts().sort_values(ascending=False)
                                labels = vc.index.tolist()
                                values = vc.values.tolist()
                                pid = f"plot-{p.name}-num"
                                parts.append(f'<div id="{pid}" class="plot"></div>')
                                js = (
                                    """
<script>
  (function(){
    const labels = %s;
    const vals = %s;
    const data = [{x: labels, y: vals, type: 'bar'}];
    const layout = {title: 'Contagem de %s', xaxis: {tickangle: -45}, yaxis: {title: 'count'}};
    Plotly.newPlot('%s', data, layout, {responsive: true});
  })();
</script>
"""
                                    % (json.dumps(labels), json.dumps(values), html_escape(coln), pid)
                                )
                                parts.append(js)
                            else:
                                counts, bins = np.histogram(series, bins=20)
                                centers = ((bins[:-1] + bins[1:]) / 2).tolist()
                                counts = counts.tolist()
                                pid = f"plot-{p.name}-num"
                                parts.append(f'<div id="{pid}" class="plot"></div>')
                                js = (
                                    """
<script>
  (function(){
    const x = %s;
    const y = %s;
    const data = [{x: x, y: y, type: 'bar'}];
    const layout = {title: 'Histograma de %s', xaxis: {title: '%s'}, yaxis: {title: 'count'}};
    Plotly.newPlot('%s', data, layout, {responsive: true});
  })();
</script>
"""
                                    % (json.dumps(centers), json.dumps(counts), html_escape(coln), html_escape(coln), pid)
                                )
                                parts.append(js)
                    if cats:
                        colc = cats[0]
                        vc = df[colc].astype(str).value_counts().nlargest(20)
                        labels = vc.index.tolist()
                        values = vc.values.tolist()
                        pid2 = f"plot-{p.name}-cat"
                        parts.append(f'<div id="{pid2}" class="plot"></div>')
                        js2 = (
                            """
<script>
  (function(){
    const labels = %s;
    const vals = %s;
    const data = [{x: labels, y: vals, type: 'bar'}];
    const layout = {title: 'Contagem de %s', xaxis: {tickangle: -45}, yaxis: {title: 'count'}};
    Plotly.newPlot('%s', data, layout, {responsive: true});
  })();
</script>
"""
                            % (json.dumps(labels), json.dumps(values), html_escape(colc), pid2)
                        )
                        parts.append(js2)
                except Exception:
                    parts.append('<div class="note">Erro ao gerar plots para este CSV.</div>')

                parts.append("</details>")
            except Exception as e:
                parts.append(f'<div class="note">Erro lendo {html_escape(p.name)}: {html_escape(str(e))}</div>')
        else:
            parts.append('<div class="note">Nenhum CSV descritivo encontrado em reports/descriptive/</div>')

    parts.append("</div>")

    # Footer
    if theme == "minimal":
        parts.append(
            '<p class="footer">Gerado por generate_profile_report.py</p>'
        )
        parts.append("</div>")  # .page
    else:
        parts.append(
            '<div class="section small">'
            "Gerado por generate_profile_report.py</div>"
        )

    css = CSS_MINIMAL if theme == "minimal" else CSS
    title = (
        "Relatório de Dados — Minimal"
        if theme == "minimal"
        else "Relatório de Dados"
    )
    html_doc = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <script src="{PLOTLY_CDN}" charset="utf-8"></script>
  <style>{css}</style>
</head>
<body>
{"".join(parts)}
</body>
</html>
"""

    out_path.write_text(html_doc, encoding="utf-8")


def html_escape(s: str) -> str:
    return (s or "").replace("<", "&lt;").replace(">", "&gt;")


def figure_caption(filename: str) -> str:
    """Retorna legenda amigável para um PNG em figures/."""
    if filename in FIGURE_CAPTIONS:
        return FIGURE_CAPTIONS[filename]
    stem = Path(filename).stem.replace("_", " ").strip()
    return stem[:1].upper() + stem[1:] if stem else filename


def figure_data_uri(path: Path) -> str:
    """Converte PNG em data URI para o HTML ficar autocontido."""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def list_figure_files() -> list[Path]:
    """Lista PNGs em reports/figures/, ordenados por nome."""
    if not FIGURES_DIR.exists():
        return []
    return sorted(
        p
        for p in FIGURES_DIR.glob("*.png")
        if p.is_file() and p.stat().st_size > 0
    )


def main() -> None:
    import subprocess
    import sys

    script = Path(__file__).parent / "export_clinical_summaries.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(
            "Aviso: exportação clínica não executada: "
            f"{result.stderr.strip() or result.stdout.strip()}"
        )

    phik = export_phik_matrix()
    if phik is not None:
        print(f"Gerado: {PHIK_MATRIX_FILE}")
        if PHIK_FIGURE_FILE.exists():
            print(f"Gerado: {PHIK_FIGURE_FILE}")

    out_dir = REPORTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    # Classic kept for compatibility; minimal is the Apple-inspired version.
    classic = out_dir / "profile_report.html"
    minimal = out_dir / "profile_report_minimal.html"
    render_report(classic, theme="classic")
    render_report(minimal, theme="minimal")
    print(f"Gerado (clássico): {classic}")
    print(f"Gerado (minimal):  {minimal}")


if __name__ == "__main__":
    main()
