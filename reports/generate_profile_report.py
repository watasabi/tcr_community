#!/usr/bin/env python3
"""Gera um relatório HTML simples com plots client-side a partir dos CSVs em reports/.

Usage:
    python3 reports/generate_profile_report.py

Creates `reports/profile_report.html`.
"""

from __future__ import annotations

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

CLINICAL_SUMMARY_FILES = {
    "Diagnósticos por categoria": "clin_diagnostico_por_categoria.csv",
    "10 comorbidades mais frequentes": "clin_comorbidades_top10.csv",
    "Principais causas de óbito": "clin_causa_obito_top.csv",
    "Suportes e intervenções": "clin_intervencoes.csv",
    "Óbitos e cuidados paliativos": "clin_obitos_cuidados_paliativos.csv",
    "APACHE II × mortalidade por faixa": "clin_apache_mortalidade_faixas.csv",
    "APACHE II × tempo de internação": "clin_apache_tempo_internacao.csv",
}

CLINICAL_FIGURES = [
    ("diagnostico_por_categoria.png", "Diagnósticos por categoria clínica"),
    ("comorbidades_top10.png", "10 comorbidades mais frequentes"),
    ("causa_obito_top15.png", "Principais causas de óbito"),
    ("apache_vs_tempo_internacao.png", "APACHE II × tempo de internação"),
    (
        "apache_mortalidade_observada_vs_estimada.png",
        "Mortalidade observada vs estimada (APACHE II)",
    ),
]


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


def render_report(out_path: Path):
    parts: list[str] = []
    parts.append(
        f"<h1>Relatório de Dados — gerado {datetime.datetime.now().isoformat(sep=' ', timespec='seconds')}</h1>"
    )

    # Association results
    parts.append('<div class="section">')
    parts.append("<h2>Association results</h2>")
    if ASSOC_FILE.exists():
        try:
            assoc = pd.read_csv(ASSOC_FILE)
            parts.append(
                f'<div class="meta">Fonte: {html_escape(str(ASSOC_FILE.relative_to(ROOT)))}, linhas: {len(assoc)}</div>'
            )
            parts.append('<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>')
            parts.append('<details open><summary class="small">Preview, estatísticas e plots (client-side)</summary>')
            parts.append('<h3 class="small">Preview (primeiras linhas)</h3>')
            parts.append(df_to_html_preview(assoc))
            parts.append('<h3 class="small">Estatísticas sumarizadas</h3>')
            parts.append(describe_df_html(assoc))

            # p-value bar chart data for client-side Plotly
            try:
                if "p_value" in assoc.columns and "variable" in assoc.columns:
                    dfp = assoc.copy()
                    dfp["p_value"] = pd.to_numeric(dfp["p_value"], errors="coerce")
                    missing_mask = dfp["p_value"].isna()
                    dfp.loc[missing_mask, "p_value"] = 1.0
                    dfp = dfp.sort_values(by="p_value", ascending=True).reset_index(drop=True)
                    dfp["-log10_p"] = [-math.log10(max(v, 1e-300)) for v in dfp["p_value"]]
                    dfp["significant"] = (dfp["p_value"] < 0.05).astype(int)

                    vars_full = dfp["variable"].astype(str).tolist()
                    vars_short = [(v if len(v) <= 40 else v[:37] + "...") for v in vars_full]
                    vals = dfp["-log10_p"].tolist()
                    sig = dfp["significant"].astype(int).tolist()
                    missing = missing_mask.astype(int).tolist()

                    # colors: missing -> lightgray, significant -> crimson, else steelblue
                    colors = [
                        ("lightgray" if m else ("crimson" if s else "steelblue"))
                        for m, s in zip(missing, sig)
                    ]

                    plot_id = "assoc-plot"
                    parts.append(f'<div id="{plot_id}" class="plot"></div>')
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
  })
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
                    parts.append('<div class="note">p_value ou variable ausente no CSV de associação — sem gráfico.</div>')
            except Exception:
                parts.append('<div class="note">Erro ao preparar gráfico de p-values.</div>')

            parts.append("</details>")
        except Exception as e:
            parts.append(f'<div class="note">Erro ao ler {html_escape(ASSOC_FILE.name)}: {html_escape(str(e))}</div>')
    else:
        parts.append(f'<div class="note">Arquivo {html_escape(ASSOC_FILE.name)} não encontrado.</div>')

    parts.append("</div>")

    # Clinical summaries (categorized)
    parts.append('<div class="section">')
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

    for fig_name, caption in CLINICAL_FIGURES:
        fig_path = FIGURES_DIR / fig_name
        if not fig_path.exists():
            continue
        has_clinical = True
        rel = fig_path.relative_to(REPORTS_DIR)
        parts.append(f'<h3 class="small">{html_escape(caption)}</h3>')
        parts.append(
            f'<img src="{html_escape(str(rel))}" alt="{html_escape(caption)}" '
            'style="max-width:100%;height:auto;" />'
        )

    if not has_clinical:
        parts.append(
            '<div class="note">Execute '
            "<code>uv run python reports/export_clinical_summaries.py</code> "
            "para gerar tabelas e figuras desta seção.</div>"
        )
    parts.append("</div>")

    # Descriptive CSVs
    parts.append('<div class="section">')
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
  })
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
  })
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
  })
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
    parts.append('<div class="section small">Gerado por generate_profile_report.py</div>')

    html_doc = f"""
<html>
<head>
  <meta charset="utf-8" />
  <title>Relatório de Dados</title>
  <style>{CSS}</style>
</head>
<body>
{"".join(parts)}
</body>
</html>
"""

    out_path.write_text(html_doc, encoding="utf-8")


def html_escape(s: str) -> str:
    return (s or "").replace("<", "&lt;").replace(">", "&gt;")


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
    out = REPORTS_DIR / "profile_report.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    render_report(out)
    print(f"Gerado: {out}")


if __name__ == "__main__":
    main()
