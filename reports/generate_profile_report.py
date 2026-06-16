#!/usr/bin/env python3
"""Gera um relatório HTML simples a partir dos CSVs em reports/.

Uso:
    python reports/generate_profile_report.py

Gera `reports/profile_report.html`.
"""

from __future__ import annotations

import datetime
from pathlib import Path
import pandas as pd
import html


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
DESCRIPTIVE_DIR = REPORTS_DIR / "descriptive"
ASSOC_FILE = REPORTS_DIR / "association_results.csv"


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
"""


def df_to_html_preview(df: pd.DataFrame, max_rows: int = 10) -> str:
    return df.head(max_rows).to_html(
        classes="preview-table", index=False, border=0
    )


def describe_df_html(df: pd.DataFrame) -> str:
    # Use describe for numeric and object (include='all')
    desc = df.describe(include="all", datetime_is_numeric=False).T
    # sanitize
    desc_html = desc.to_html(classes="desc-table")
    return desc_html


def render_report(out_path: Path):
    parts = []
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
                f'<div class="meta">Fonte: {html.escape(str(ASSOC_FILE.relative_to(ROOT)))}, linhas: {len(assoc)}</div>'
            )
            parts.append(
                '<details open><summary class="small">Preview e estatísticas</summary>'
            )
            parts.append('<h3 class="small">Preview (primeiras linhas)</h3>')
            parts.append(df_to_html_preview(assoc))
            parts.append('<h3 class="small">Estatísticas sumarizadas</h3>')
            parts.append(describe_df_html(assoc))
            parts.append("</details>")
        except Exception as e:
            parts.append(
                f'<div class="small">Erro ao ler {ASSOC_FILE.name}: {html.escape(str(e))}</div>'
            )
    else:
        parts.append(
            f'<div class="small">Arquivo {ASSOC_FILE.name} não encontrado.</div>'
        )
    parts.append("</div>")

    # Descriptive CSVs
    parts.append('<div class="section">')
    parts.append("<h2>Descriptive CSVs</h2>")
    if DESCRIPTIVE_DIR.exists() and any(DESCRIPTIVE_DIR.iterdir()):
        for p in sorted(DESCRIPTIVE_DIR.glob("*.csv")):
            try:
                df = pd.read_csv(p)
                parts.append(f"<h3>{html.escape(p.name)}</h3>")
                parts.append(
                    f'<div class="meta">linhas: {len(df)}, colunas: {len(df.columns)}</div>'
                )
                parts.append(
                    '<details><summary class="small">Preview e estatísticas</summary>'
                )
                parts.append(df_to_html_preview(df))
                parts.append(describe_df_html(df))
                parts.append("</details>")
            except Exception as e:
                parts.append(
                    f'<div class="small">Erro lendo {p.name}: {html.escape(str(e))}</div>'
                )
    else:
        parts.append(
            '<div class="small">Nenhum CSV descritivo encontrado em reports/descriptive/</div>'
        )
    parts.append("</div>")

    # Footer
    parts.append(
        '<div class="section small">Gerado por `generate_profile_report.py`</div>'
    )

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


def main():
    out = REPORTS_DIR / "profile_report.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    render_report(out)
    print(f"Gerado: {out}")


if __name__ == "__main__":
    main()
