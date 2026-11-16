# -*- coding: utf-8 -*-
"""
Renderizador de Tabelas Acadêmicas e Gráficos de Alta Resolução (300 DPI)
para o plugin GeoSIDRA (IBGE / SIDRA).
Gera imagens PNG com padrão visual de publicação científica, tabelas CSV
e relatórios autônomos em HTML.
"""

from __future__ import annotations

import base64
import csv
import os
from typing import Any, Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .analytics_engine import AnalyticsReportBundle, StyledTableSpec, fmt_float_br, fmt_int_br

THEME_COLORS = {
    "green": "#1b5e20",
    "forest": "#2e7d32",
    "light_green": "#4caf50",
    "navy": "#0f2c59",
    "amber": "#b45309",
    "wine": "#7a1c1c",
}

SERIES_PALETTE = [
    "#1b5e20",
    "#2e7d32",
    "#0f2c59",
    "#b45309",
    "#7a1c1c",
    "#0e7490",
    "#5b21b6",
    "#475569",
    "#2563eb",
    "#16a34a",
]


def render_styled_table_png(table_spec: StyledTableSpec, out_path: str, dpi: int = 240) -> str:
    """Renderiza uma StyledTableSpec como imagem PNG de alta resolução com cabeçalho institucional e zebrado."""
    n_rows = len(table_spec.rows) + (1 if table_spec.totals_row else 0)
    fig_height = max(4.0, 1.8 + (n_rows * 0.35))
    fig, ax = plt.subplots(figsize=(11.5, fig_height), dpi=dpi)
    ax.axis("off")

    # Título e Subtítulo
    fig.text(0.05, 0.95, table_spec.title, fontsize=12, fontweight="bold", color="#0f172a", ha="left")
    fig.text(0.05, 0.91, table_spec.subtitle, fontsize=9.5, color="#475569", ha="left")

    table_data = list(table_spec.rows)
    if table_spec.totals_row:
        table_data.append(table_spec.totals_row)

    col_widths = table_spec.column_widths or [1.0 / len(table_spec.headers)] * len(table_spec.headers)
    table = ax.table(
        cellText=table_data,
        colLabels=table_spec.headers,
        colWidths=col_widths,
        loc="upper center",
        bbox=[0.05, 0.08, 0.90, 0.78],
    )

    table.auto_set_font_size(False)
    table.set_fontsize(8.5)

    # Estiliza cabeçalho
    for col_idx in range(len(table_spec.headers)):
        cell = table[0, col_idx]
        cell.set_facecolor("#1b5e20")
        cell.get_text().set_color("#ffffff")
        cell.get_text().set_weight("bold")
        cell.get_text().set_fontsize(9)
        cell.set_edgecolor("#ffffff")
        cell.set_linewidth(1.0)
        cell.set_height(0.055)

    # Estiliza linhas de dados (zebrado)
    for row_idx, row in enumerate(table_spec.rows, start=1):
        bg = "#ffffff" if row_idx % 2 != 0 else "#f8fafc"
        for col_idx in range(len(row)):
            cell = table[row_idx, col_idx]
            cell.set_facecolor(bg)
            cell.set_edgecolor("#e2e8f0")
            cell.set_linewidth(0.5)
            align = table_spec.alignments[col_idx] if col_idx < len(table_spec.alignments) else "left"
            cell.get_text().set_horizontalalignment(align)
            cell.get_text().set_color("#1e293b")

    # Estiliza linha de total
    if table_spec.totals_row:
        tot_row_idx = len(table_spec.rows) + 1
        for col_idx in range(len(table_spec.totals_row)):
            cell = table[tot_row_idx, col_idx]
            cell.set_facecolor("#e2e8f0")
            cell.set_edgecolor("#cbd5e1")
            cell.set_linewidth(1.0)
            cell.get_text().set_weight("bold")
            cell.get_text().set_color("#0f172a")
            align = table_spec.alignments[col_idx] if col_idx < len(table_spec.alignments) else "left"
            cell.get_text().set_horizontalalignment(align)

    # Rodapé
    fig.text(0.05, 0.03, table_spec.footnote, fontsize=8, color="#64748b", ha="left")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor="#ffffff", edgecolor="none")
    plt.close(fig)
    return out_path


def render_horizontal_bar_chart(
    bundle: AnalyticsReportBundle,
    out_path: str,
    custom_title: Optional[str] = None,
    custom_subtitle: Optional[str] = None,
    dpi: int = 300,
) -> str:
    """Renderiza gráfico de barras horizontais em 300 DPI com rótulos diretos."""
    pts = bundle.data_points
    if not pts:
        return ""

    labels = [p["label"] for p in pts]
    values = [p["value"] for p in pts]
    texts = [p.get("text", "") for p in pts]

    n_bars = len(labels)
    fig_height = max(4.5, 1.8 + (n_bars * 0.38))
    fig, ax = plt.subplots(figsize=(10.5, fig_height), dpi=dpi)

    y_pos = np.arange(len(labels))
    bars = ax.barh(y_pos, values, color="#2e7d32", edgecolor="#1b5e20", height=0.65, alpha=0.92)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=8.5, color="#1e293b")
    ax.set_xlabel(bundle.axis_label_x, fontsize=9.5, fontweight="bold", color="#334155", labelpad=8)

    # Rótulos nas barras (suporta valores positivos e negativos)
    max_v = max(values) if values else 1.0
    min_v = min(values) if values else 0.0
    span = max(abs(max_v - min_v), abs(max_v), abs(min_v), 1.0)
    for bar, txt in zip(bars, texts):
        w = bar.get_width()
        if w >= 0:
            x_text = w + (span * 0.015)
            ha = "left"
        else:
            x_text = w - (span * 0.015)
            ha = "right"
        ax.text(x_text, bar.get_y() + bar.get_height() / 2, txt, va="center", ha=ha, fontsize=8, color="#0f172a", fontweight="bold")

    if min_v < 0:
        ax.axvline(0, color="#64748b", linewidth=0.9)
        ax.set_xlim(min_v - span * 0.30, max(0.0, max_v) + span * 0.30)
    else:
        ax.set_xlim(0, max(max_v, 1e-6) * 1.30)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cbd5e1")
    ax.spines["bottom"].set_color("#cbd5e1")
    ax.xaxis.grid(True, linestyle="--", alpha=0.45, color="#cbd5e1")
    ax.set_axisbelow(True)

    # Títulos
    title = custom_title if custom_title is not None else bundle.title
    subtitle = custom_subtitle if custom_subtitle is not None else bundle.subtitle
    fig.text(0.04, 0.96, title, fontsize=12, fontweight="bold", color="#0f172a")
    fig.text(0.04, 0.92, subtitle, fontsize=9, color="#475569")
    fig.text(0.04, 0.015, bundle.footnote, fontsize=7.5, color="#64748b")

    plt.tight_layout(rect=[0.02, 0.04, 0.98, 0.90])
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor="#ffffff")
    plt.close(fig)
    return out_path


def render_line_chart(
    bundle: AnalyticsReportBundle,
    out_path: str,
    custom_title: Optional[str] = None,
    custom_subtitle: Optional[str] = None,
    dpi: int = 300,
) -> str:
    """Renderiza gráfico de evolução temporal em linha com pontos e sombreamento."""
    pts = bundle.data_points
    if not pts:
        return ""

    years = [p["year"] for p in pts]
    values = [p["value"] for p in pts]
    unit = pts[0].get("unit", "")

    fig, ax = plt.subplots(figsize=(10.5, 5.2), dpi=dpi)

    ax.plot(years, values, marker="o", color="#1b5e20", linewidth=2.5, markersize=7, markerfacecolor="#4caf50", markeredgecolor="#1b5e20", label=bundle.axis_label_y or "Série Histórica")
    ax.fill_between(range(len(years)), 0, values, color="#81c784", alpha=0.18)

    # Rótulo de valores sobre os pontos
    unit_low = unit.lower()
    dec = 2 if any(k in unit_low for k in ("%", "índice", "indice", "hab/km")) else 1
    for x, y in enumerate(values):
        ax.annotate(
            f"{fmt_float_br(y, dec)} {unit}".strip(),
            (x, y),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontsize=8,
            fontweight="bold",
            color="#0f172a",
        )

    ax.set_ylabel(bundle.axis_label_y, fontsize=9.5, fontweight="bold", color="#334155")
    ax.set_xlabel(bundle.axis_label_x, fontsize=9.5, fontweight="bold", color="#334155")
    min_v = min(values) if values else 0.0
    max_v = max(values) if values else 1.0
    if min_v < 0:
        ax.set_ylim(min_v * 1.18, max(0.0, max_v) * 1.18)
    else:
        ax.set_ylim(0, max(max_v, 1e-6) * 1.18)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, linestyle="--", alpha=0.45, color="#cbd5e1")
    ax.set_axisbelow(True)

    title = custom_title if custom_title is not None else bundle.title
    subtitle = custom_subtitle if custom_subtitle is not None else bundle.subtitle
    fig.text(0.04, 0.95, title, fontsize=12, fontweight="bold", color="#0f172a")
    fig.text(0.04, 0.91, subtitle, fontsize=9, color="#475569")
    fig.text(0.04, 0.015, bundle.footnote, fontsize=7.5, color="#64748b")

    plt.tight_layout(rect=[0.02, 0.04, 0.98, 0.89])
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor="#ffffff")
    plt.close(fig)
    return out_path


def render_lorenz_curve(
    bundle: AnalyticsReportBundle,
    out_path: str,
    custom_title: Optional[str] = None,
    custom_subtitle: Optional[str] = None,
    dpi: int = 300,
) -> str:
    """Renderiza a Curva de Lorenz com diagonal de perfeita igualdade e destaque do Gini."""
    pts = bundle.data_points
    if not pts:
        return ""

    x_mun = [p["pct_mun"] for p in pts]
    y_prod = [p["pct_prod"] for p in pts]

    fig, ax = plt.subplots(figsize=(7.5, 6.0), dpi=dpi)

    # Diagonal de perfeita igualdade
    ax.plot([0, 100], [0, 100], linestyle="--", color="#94a3b8", linewidth=1.5, label="Equidistribuição (Gini = 0)")

    # Curva empírica
    ax.plot(x_mun, y_prod, color="#1b5e20", linewidth=2.5, label="Distribuição Espacial Observada")
    ax.fill_between(x_mun, y_prod, x_mun, color="#a5d6a7", alpha=0.35, label="Área de Desigualdade")

    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xlabel(bundle.axis_label_x, fontsize=9, fontweight="bold", color="#334155")
    ax.set_ylabel(bundle.axis_label_y, fontsize=9, fontweight="bold", color="#334155")
    ax.legend(loc="upper left", fontsize=8.5, frameon=True, facecolor="#ffffff", framealpha=0.9)
    ax.grid(True, linestyle=":", alpha=0.5, color="#cbd5e1")

    # Caixa com Gini
    gini_val = bundle.summary_metrics.get("Índice de Gini", "N/A")
    ax.text(
        0.95, 0.10,
        f"Índice de Gini: {gini_val}",
        transform=ax.transAxes,
        fontsize=9.5,
        fontweight="bold",
        color="#0f172a",
        ha="right",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#f1f5f9", edgecolor="#cbd5e1"),
    )

    title = custom_title if custom_title is not None else bundle.title
    subtitle = custom_subtitle if custom_subtitle is not None else bundle.subtitle
    fig.text(0.06, 0.95, title, fontsize=11.5, fontweight="bold", color="#0f172a")
    fig.text(0.06, 0.91, subtitle, fontsize=8.5, color="#475569")
    fig.text(0.06, 0.015, bundle.footnote, fontsize=7.5, color="#64748b")

    plt.tight_layout(rect=[0.03, 0.04, 0.97, 0.89])
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor="#ffffff")
    plt.close(fig)
    return out_path


def render_donut_chart(
    bundle: AnalyticsReportBundle,
    out_path: str,
    custom_title: Optional[str] = None,
    custom_subtitle: Optional[str] = None,
    dpi: int = 300,
) -> str:
    """Renderiza gráfico de donut para estrutura de concentração de mercado."""
    pts = bundle.data_points
    if not pts:
        return ""

    labels = [f"{p['label']} ({fmt_float_br(p['share'], 1)}%)" for p in pts]
    values = [p["value"] for p in pts]
    colors = ["#1b5e20", "#388e3c", "#81c784", "#cbd5e1"]

    fig, ax = plt.subplots(figsize=(7.5, 5.5), dpi=dpi)
    wedges, _ = ax.pie(
        values,
        labels=None,
        startangle=140,
        colors=colors[:len(values)],
        wedgeprops=dict(width=0.45, edgecolor="#ffffff", linewidth=1.5),
    )

    ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(0.85, 0.5), fontsize=8.5, frameon=False)

    title = custom_title if custom_title is not None else bundle.title
    subtitle = custom_subtitle if custom_subtitle is not None else bundle.subtitle
    fig.text(0.06, 0.95, title, fontsize=11.5, fontweight="bold", color="#0f172a")
    fig.text(0.06, 0.91, subtitle, fontsize=8.5, color="#475569")
    fig.text(0.06, 0.015, bundle.footnote, fontsize=7.5, color="#64748b")

    plt.tight_layout(rect=[0.03, 0.04, 0.97, 0.89])
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor="#ffffff")
    plt.close(fig)
    return out_path


def export_bundle(
    bundle: AnalyticsReportBundle,
    out_dir: str,
    custom_title: Optional[str] = None,
    custom_subtitle: Optional[str] = None,
    dpi: int = 300,
) -> str:
    """Despacha a renderização do bundle para o método apropriado."""
    os.makedirs(out_dir, exist_ok=True)
    filename = f"{bundle.report_id}.png"
    out_path = os.path.join(out_dir, filename)

    if bundle.chart_type == "styled_table" and bundle.table_spec:
        return render_styled_table_png(bundle.table_spec, out_path, dpi=240)
    if bundle.chart_type == "bar_h":
        return render_horizontal_bar_chart(bundle, out_path, custom_title, custom_subtitle, dpi=dpi)
    if bundle.chart_type == "line":
        return render_line_chart(bundle, out_path, custom_title, custom_subtitle, dpi=dpi)
    if bundle.chart_type == "lorenz":
        return render_lorenz_curve(bundle, out_path, custom_title, custom_subtitle, dpi=dpi)
    if bundle.chart_type == "donut":
        return render_donut_chart(bundle, out_path, custom_title, custom_subtitle, dpi=dpi)

    return ""


def export_table_csv(table_spec: StyledTableSpec, out_path: str) -> str:
    """Exporta a especificação da tabela em CSV com codificação UTF-8 com BOM para Excel."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(table_spec.headers)
        for row in table_spec.rows:
            writer.writerow(row)
        if table_spec.totals_row:
            writer.writerow(table_spec.totals_row)
    return out_path
