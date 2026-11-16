# -*- coding: utf-8 -*-
"""
Motor de Análise e Relatórios Estatísticos do GeoSIDRA (IBGE / SIDRA).
Gera estruturas analíticas e payloads gráficos de alta resolução (300 DPI) para:
  1. Rankings Territoriais (Municípios ou Estados)
  2. Série Histórica e Evolução Temporal do Indicador
  3. Concentração Espacial (Curva de Lorenz e Coeficiente de Gini — para totais aditivos)
  4. Estrutura de Participação (Donut: Top 5, Top 10, Demais — para totais aditivos)
  5. Tabela Acadêmica de Publicação
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def fmt_int_br(val: float | int) -> str:
    """Formata inteiro no padrão brasileiro: 1.234.567."""
    v = int(round(float(val or 0)))
    return f"{v:,}".replace(",", ".")


def fmt_float_br(val: float, decimals: int = 1) -> str:
    """Formata decimal no padrão brasileiro: 128,9."""
    s = f"{float(val or 0.0):,.{decimals}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_currency_br(val: float, compact: bool = False) -> str:
    """Formata valores em R$, opcionalmente abreviados."""
    v = float(val or 0.0)
    if compact:
        av = abs(v)
        sign = "-" if v < 0 else ""
        if av >= 1e9:
            return f"{sign}R$ {fmt_float_br(av / 1e9, 2)} bi"
        if av >= 1e6:
            return f"{sign}R$ {fmt_float_br(av / 1e6, 1)} mi"
        if av >= 1e3:
            return f"{sign}R$ {fmt_float_br(av / 1e3, 0)} mil"
        return f"{sign}R$ {fmt_float_br(av, 0)}"
    return f"R$ {fmt_float_br(v, 2)}"


def fmt_volume_br(val: float, unit: str = "t") -> str:
    """Formata valores numéricos conforme a grandeza e unidade do SIDRA."""
    v = float(val or 0.0)
    u = (unit or "").strip()
    u_low = u.lower()

    if "por litro" in u_low:
        return f"R$ {fmt_float_br(v, 2)}/L"

    if "mil r$" in u_low or "mil reais" in u_low:
        return fmt_currency_br(v * 1000.0, compact=True)

    if "reais" in u_low or u == "R$":
        return fmt_currency_br(v, compact=(abs(v) >= 1e6))

    if "percentual" in u_low or "%" in u_low:
        suf = "% a.a." if "a.a" in u_low else "%"
        return f"{fmt_float_br(v, 2)}{suf}"

    if "‰" in u_low or "por mil" in u_low:
        return f"{fmt_float_br(v, 2)}‰"

    if "razão" in u_low or "razao" in u_low:
        return fmt_float_br(v, 2)

    if u_low in ("anos", "ano"):
        return f"{fmt_float_br(v, 1)} anos"

    if "filho" in u_low:
        return f"{fmt_float_br(v, 2)} filhos"

    if "número-índice" in u_low or "numero-indice" in u_low:
        return fmt_float_br(v, 1)

    if any(k in u_low for k in ("índice", "indice", "gini")):
        return fmt_float_br(v, 3)

    if any(k in u_low for k in ("salário", "salario", "hab/km")):
        return f"{fmt_float_br(v, 2)} {u}".strip()

    if "km²" in u_low or "quadrad" in u_low:
        return f"{fmt_float_br(v, 2 if abs(v) < 10 else 1)} km²"

    if "quilômetro" in u_low or "quilometro" in u_low or u_low == "km":
        if abs(v) >= 1e3:
            return f"{fmt_float_br(v / 1e3, 2)} mil km"
        return f"{fmt_float_br(v, 2 if abs(v) < 10 else 1)} km"

    if any(tok in u_low for tok in ("mil pessoas", "mil pessoa", "mil unidade", "mil domic")):
        scaled = v * 1000.0
        if abs(scaled) >= 1e6:
            return f"{fmt_float_br(scaled / 1e6, 2)} mi"
        if abs(scaled) >= 1e3:
            return f"{fmt_float_br(scaled / 1e3, 1)} mil"
        return fmt_int_br(scaled)

    if "micrograma" in u_low or "µg" in u_low:
        u_disp = "µg/m³"
    elif "por 100 mil" in u_low or "por 100.000" in u_low:
        u_disp = "/ 100 mil hab."
    elif "metros cúbicos" in u_low or "metro cúbico" in u_low or "m³" in u_low:
        u_disp = "m³"
    elif "mil litros" in u_low:
        liters = v * 1000.0
        if abs(liters) >= 1e6:
            return f"{fmt_float_br(liters / 1e6, 2)} mi L"
        return f"{fmt_float_br(liters / 1e3, 1)} mil L"
    elif "mil dúzia" in u_low or "mil duzia" in u_low:
        duz = v * 1000.0
        if abs(duz) >= 1e6:
            return f"{fmt_float_br(duz / 1e6, 2)} mi dúz."
        return f"{fmt_float_br(duz / 1e3, 1)} mil dúz."
    else:
        u_disp = u

    av = abs(v)
    if av >= 1e6:
        return f"{fmt_float_br(v / 1e6, 2)} mi {u_disp}".strip()
    if av >= 1e3:
        return f"{fmt_float_br(v / 1e3, 1)} mil {u_disp}".strip()
    if abs(v - round(v)) < 1e-6:
        return f"{fmt_int_br(v)} {u_disp}".strip()
    return f"{fmt_float_br(v, 1)} {u_disp}".strip()


@dataclass
class StyledTableSpec:
    """Especificação formal para geração de tabelas acadêmicas."""
    title: str
    subtitle: str
    headers: List[str]
    alignments: List[str]  # 'left', 'center', 'right'
    rows: List[List[str]]
    column_widths: Optional[List[float]] = None
    totals_row: Optional[List[str]] = None
    footnote: str = "Fonte: IBGE - SIDRA | Processamento: GeoSIDRA"


@dataclass
class AnalyticsReportBundle:
    """Pacote de relatório analítico contendo dados para gráficos e tabelas."""
    report_id: str
    category: str
    title: str
    subtitle: str
    chart_type: str  # 'bar_h', 'line', 'lorenz', 'donut', 'styled_table'
    data_points: List[Dict[str, Any]] = field(default_factory=list)
    table_spec: Optional[StyledTableSpec] = None
    summary_metrics: Dict[str, str] = field(default_factory=dict)
    axis_label_x: str = ""
    axis_label_y: str = ""
    footnote: str = "Fonte: IBGE - SIDRA | Processamento: GeoSIDRA"


class AnalyticsEngine:
    """Gera análises e relatórios padronizados a partir dos dados do SIDRA."""

    LEVEL_DISPLAY_META: Dict[str, tuple] = {
        "N1": ("Brasil", "Brasil"),
        "N2": ("Grandes Regiões", "Grande Região"),
        "N3": ("Estados / UFs", "UF"),
        "N6": ("Municípios", "Município"),
        "N7": ("Regiões Metropolitanas", "Região Metropolitana"),
        "N8": ("Mesorregiões Geográficas", "Mesorregião"),
        "N9": ("Microrregiões Geográficas", "Microrregião"),
        "N14": ("RIDEs", "RIDE"),
        "N7_N14": ("RMs e RIDE", "RM / RIDE"),
        "N7_N6": ("RMs e Capitais", "RM / Capital"),
    }

    @staticmethod
    def _format_unit_chart_label(item: Dict[str, Any], level: str) -> str:
        nm = str(item.get("nm_mun") or "").strip()
        uf = str(item.get("uf") or "").strip()
        if level in ("N1", "N2", "N3") or not uf:
            return nm
        if nm.endswith(" (RM)"):
            return f"{nm[:-5]} - {uf} (RM)"
        if nm.endswith(" (RIDE)"):
            return f"{nm[:-7]} - {uf} (RIDE)"
        return f"{nm} ({uf})"

    @classmethod
    def compute_gini(cls, values: List[float]) -> float:
        """Calcula o coeficiente de Gini para distribuição espacial."""
        clean = [float(v) for v in values if float(v or 0) > 0]
        if len(clean) < 2:
            return 0.0
        clean.sort()
        n = len(clean)
        cum = 0.0
        for i, val in enumerate(clean, start=1):
            cum += i * val
        total = sum(clean)
        if total == 0:
            return 0.0
        gini = (2.0 * cum) / (n * total) - (n + 1.0) / n
        return max(0.0, min(1.0, gini))

    @classmethod
    def generate_all_reports(
        cls,
        parsed_data: Dict,
        territory_label: str = "Brasil",
    ) -> List[AnalyticsReportBundle]:
        """Gera a lista completa de relatórios analíticos para os dados do SIDRA."""
        bundles: List[AnalyticsReportBundle] = []

        prod_name = parsed_data.get("product_name") or parsed_data.get("variable_name") or "Indicador SIDRA"
        var_name = parsed_data.get("variable_name") or "Indicador"
        unit_name = parsed_data.get("unit") or ""
        years = parsed_data.get("years", [])
        if len(years) > 6:
            period_str = f"({years[0]} a {years[-1]} - {len(years)} períodos)"
        elif years:
            period_str = f"({', '.join(years)})"
        else:
            period_str = ""
        top_producers = parsed_data.get("top_producers", [])
        total_val = parsed_data.get("total", 0.0)
        mean_val = parsed_data.get("mean_value", 0.0)
        agg_mode = (parsed_data.get("agg_mode") or "sum").lower()
        allow_negative = bool(parsed_data.get("allow_negative", False))
        is_binary = bool(parsed_data.get("is_binary", False))
        level = (parsed_data.get("level") or "N6").upper()

        unit_label = f" ({unit_name})" if unit_name else ""
        ter_word, ter_col = cls.LEVEL_DISPLAY_META.get(level, ("Municípios", "Município"))
        is_additive = (agg_mode != "mean") and (not allow_negative) and (not is_binary) and (total_val > 0)

        # -------------------------------------------------------------
        # 1. Ranking Territorial (Top 15)
        # -------------------------------------------------------------
        top15 = top_producers[:15]
        bar_pts = []
        for item in reversed(top15):
            val = item["valor_principal"]
            pct = item.get("share_pct", 0.0)
            label = cls._format_unit_chart_label(item, level)
            txt = (
                f"{fmt_volume_br(val, unit_name)} ({fmt_float_br(pct, 1)}%)"
                if is_additive
                else fmt_volume_br(val, unit_name)
            )
            bar_pts.append({
                "label": label,
                "value": val,
                "share": pct,
                "unit": unit_name,
                "text": txt,
            })

        top15_sum = sum(p["value"] for p in bar_pts)
        top15_share = (top15_sum / total_val * 100.0) if (is_additive and total_val > 0) else 0.0

        summary_1 = (
            {
                "Total Apurado": fmt_volume_br(total_val, unit_name),
                "Top 15 Participação": f"{fmt_float_br(top15_share, 1)}%",
                "Unidades com Registro": fmt_int_br(len(top_producers)),
            }
            if is_additive
            else (
                {
                    "Municípios com Sim (= 1)": fmt_int_br(total_val),
                    "Exibidos no Ranking": fmt_int_br(len(top15)),
                }
                if is_binary
                else {
                    "Média do Recorte": fmt_volume_br(mean_val, unit_name),
                    "Unidades com Registro": fmt_int_br(len(top_producers)),
                }
            )
        )

        bundles.append(AnalyticsReportBundle(
            report_id="ranking_top_producers",
            category=f"Rankings ({ter_word})",
            title=f"Principais {ter_word}: {prod_name}",
            subtitle=f"{var_name} | Recorte: {territory_label} {period_str} | Top {len(top15)}",
            chart_type="bar_h",
            data_points=bar_pts,
            axis_label_x=f"{var_name}{unit_label}",
            axis_label_y=f"{ter_col}",
            summary_metrics=summary_1,
        ))

        # -------------------------------------------------------------
        # 2. Evolução Temporal (Série Histórica)
        # -------------------------------------------------------------
        time_series = parsed_data.get("time_series", {})
        if len(time_series) > 1:
            line_pts = [{"year": str(yr), "value": val, "unit": unit_name} for yr, val in time_series.items()]
            vals = list(time_series.values())
            crescimento = ((vals[-1] - vals[0]) / vals[0] * 100.0) if vals[0] != 0 else 0.0
            agg_desc = "Média territorial" if agg_mode == "mean" else "Evolução temporal"
            bundles.append(AnalyticsReportBundle(
                report_id="timeseries_evolution",
                category="Série Histórica",
                title=f"{agg_desc}: {prod_name}",
                subtitle=f"{var_name} | Recorte: {territory_label} | Variação: {fmt_float_br(crescimento, 1)}%",
                chart_type="line",
                data_points=line_pts,
                axis_label_x="Ano",
                axis_label_y=f"{var_name}{unit_label}",
                summary_metrics={
                    "Ano Inicial": f"{list(time_series.keys())[0]} ({fmt_volume_br(vals[0], unit_name)})",
                    "Ano Final": f"{list(time_series.keys())[-1]} ({fmt_volume_br(vals[-1], unit_name)})",
                    "Variação no Período": f"{fmt_float_br(crescimento, 1)}%",
                },
            ))

        # -------------------------------------------------------------
        # 3. Concentração Espacial (Curva de Lorenz & Gini) — apenas aditivos
        # -------------------------------------------------------------
        all_vals = [p["valor_principal"] for p in top_producers if p["valor_principal"] > 0]
        if is_additive and len(all_vals) >= 5:
            gini = cls.compute_gini(all_vals)
            sorted_v = sorted(all_vals)
            n = len(sorted_v)
            cum_vals = [0.0]
            cum_share = 0.0
            for v in sorted_v:
                cum_share += v / total_val
                cum_vals.append(cum_share)

            step = max(1, n // 50)
            lorenz_pts = []
            for i in range(0, n + 1, step):
                lorenz_pts.append({
                    "pct_mun": (i / n) * 100.0,
                    "pct_prod": cum_vals[min(i, n)] * 100.0,
                })
            if lorenz_pts[-1]["pct_mun"] < 100.0:
                lorenz_pts.append({"pct_mun": 100.0, "pct_prod": 100.0})

            bundles.append(AnalyticsReportBundle(
                report_id="lorenz_concentration",
                category="Concentração Espacial",
                title=f"Curva de Lorenz e Concentração: {prod_name}",
                subtitle=f"Desigualdade Espacial ({var_name}) | Coeficiente de Gini: {fmt_float_br(gini, 3)}",
                chart_type="lorenz",
                data_points=lorenz_pts,
                axis_label_x=f"% Acumulado de {ter_word}",
                axis_label_y="% Acumulado do Total",
                summary_metrics={
                    "Índice de Gini": fmt_float_br(gini, 3),
                    "Classificação": "Altíssima Concentração" if gini > 0.7 else ("Moderada" if gini > 0.4 else "Disperso"),
                    "Unidades Ativas": fmt_int_br(n),
                },
            ))

        # -------------------------------------------------------------
        # 4. Estrutura de Participação (Donut) — apenas aditivos
        # -------------------------------------------------------------
        if is_additive and len(top_producers) >= 5:
            top5_v = sum(p["valor_principal"] for p in top_producers[:5])
            top6_10_v = sum(p["valor_principal"] for p in top_producers[5:10])
            top11_20_v = sum(p["valor_principal"] for p in top_producers[10:20])
            demais_v = max(0.0, total_val - (top5_v + top6_10_v + top11_20_v))

            donut_pts = [
                {"label": "Top 1 a 5 Líderes", "value": top5_v, "share": (top5_v / total_val * 100.0)},
                {"label": "6º ao 10º Colocados", "value": top6_10_v, "share": (top6_10_v / total_val * 100.0)},
                {"label": "11º ao 20º Colocados", "value": top11_20_v, "share": (top11_20_v / total_val * 100.0)},
                {"label": f"Demais {ter_word}", "value": demais_v, "share": (demais_v / total_val * 100.0)},
            ]
            bundles.append(AnalyticsReportBundle(
                report_id="donut_structure",
                category="Estrutura de Concentração",
                title=f"Concentração por Faixas de Liderança: {prod_name}",
                subtitle=f"Participação sobre o total do recorte ({var_name})",
                chart_type="donut",
                data_points=donut_pts,
                summary_metrics={
                    "Top 5 Concentram": f"{fmt_float_br(top5_v / total_val * 100.0, 1)}%",
                    "Top 10 Concentram": f"{fmt_float_br((top5_v + top6_10_v) / total_val * 100.0, 1)}%",
                },
            ))

        # -------------------------------------------------------------
        # 5. Tabela Acadêmica de Desempenho Territorial (Padrão ABNT)
        # -------------------------------------------------------------
        if is_additive:
            t_headers = ["Pos.", ter_col, "UF", f"{var_name}{unit_label}", "Part. Relativa (%)", "Acumulado (%)"]
            t_align = ["center", "left", "center", "right", "right", "right"]
            t_rows = []
            cum_pct = 0.0
            for item in top_producers[:20]:
                pct = item.get("share_pct", 0.0)
                cum_pct += pct
                val_raw = item.get("valor_principal", 0.0)
                val_str = fmt_int_br(val_raw) if abs(val_raw - round(val_raw)) < 1e-6 else fmt_float_br(val_raw, 2)
                t_rows.append([
                    str(item.get("ranking", "")),
                    item.get("nm_mun", ""),
                    item.get("uf", ""),
                    val_str,
                    f"{fmt_float_br(pct, 2)}%",
                    f"{fmt_float_br(cum_pct, 2)}%",
                ])
            tot_str = fmt_int_br(total_val) if abs(total_val - round(total_val)) < 1e-6 else fmt_float_br(total_val, 2)
            totals = ["-", "TOTAL GERAL", "-", tot_str, "100,00%", "100,00%"]
        else:
            t_headers = ["Pos.", ter_col, "UF", f"{var_name}{unit_label}"]
            t_align = ["center", "left", "center", "right"]
            t_rows = []
            for item in top_producers[:20]:
                val_raw = item.get("valor_principal", 0.0)
                t_rows.append([
                    str(item.get("ranking", "")),
                    item.get("nm_mun", ""),
                    item.get("uf", ""),
                    fmt_int_br(val_raw) if is_binary else fmt_float_br(val_raw, 2),
                ])
            totals = (
                ["-", "TOTAL SIM (VALOR = 1)", "-", fmt_int_br(total_val)]
                if is_binary
                else ["-", "MÉDIA DO RECORTE", "-", fmt_float_br(mean_val, 2)]
            )

        table_spec = StyledTableSpec(
            title=f"Tabela 1: {prod_name} - Principais {ter_word}",
            subtitle=f"{var_name} | Recorte: {territory_label} {period_str} | IBGE - SIDRA",
            headers=t_headers,
            alignments=t_align,
            rows=t_rows,
            totals_row=totals,
            footnote="Fonte: IBGE (SIDRA) | Processamento: GeoSIDRA.",
        )
        bundles.append(AnalyticsReportBundle(
            report_id="table_academic_summary",
            category="Tabelas Acadêmicas",
            title=table_spec.title,
            subtitle=table_spec.subtitle,
            chart_type="styled_table",
            table_spec=table_spec,
            summary_metrics={
                "Líder": (
                    f"{top_producers[0]['nm_mun']} ({fmt_float_br(top_producers[0].get('share_pct', 0), 1)}%)"
                    if (top_producers and is_additive)
                    else (top_producers[0]["nm_mun"] if top_producers else "N/A")
                ),
                "Valor do Líder": fmt_volume_br(top_producers[0]["valor_principal"], unit_name) if top_producers else "0",
            },
        ))

        return bundles
