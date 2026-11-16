# -*- coding: utf-8 -*-
"""
Construtor de camadas vetoriais e simbologias temáticas do GeoSIDRA (QGIS 3 / QGIS 4).
Suporta malhas municipais (N6), microrregiões (N9), mesorregiões (N8),
regiões metropolitanas/RIDE (N7/N14/N7_N6/N7_N14), estados (N3) e grandes regiões (N2).
"""

import colorsys
import json
import logging
import os
from typing import Dict, List, Optional, Tuple

from qgis.core import (
    QgsFeature,
    QgsFeatureRequest,
    QgsField,
    QgsFields,
    QgsFillSymbol,
    QgsGeometry,
    QgsGraduatedSymbolRenderer,
    QgsMarkerSymbol,
    QgsRendererRange,
    QgsSimpleFillSymbolLayer,
    QgsSingleSymbolRenderer,
    QgsVectorLayer,
)
from qgis.PyQt.QtGui import QColor

try:
    from qgis.PyQt.QtCore import QMetaType
    _HAS_QMETATYPE = hasattr(QMetaType, "Type")
except ImportError:
    _HAS_QMETATYPE = False
from qgis.PyQt.QtCore import QVariant

from .ibge_api import IBGE_MACRO_REGION_INFO, IbgeMalhasClient
from .municipality_mapper import MunicipalityMapper
from .sidra_client import UF_NUM_TO_SIGLA

LOGGER = logging.getLogger("GeoSIDRA")

PALETTES = {
    "green": ["#edf8e9", "#bae4b3", "#74c476", "#31a354", "#006d2c"],
    "amber": ["#fffbeb", "#fde68a", "#f59e0b", "#d97706", "#92400e"],
    "blue": ["#eff6ff", "#bfdbfe", "#60a5fa", "#2563eb", "#1e3a8a"],
    "ruby": ["#fee5d9", "#fcae91", "#fb6a4a", "#de2d26", "#a50f15"],
    "purple": ["#f5f3ff", "#ddd6fe", "#a78bfa", "#7c3aed", "#4c1d95"],
    "teal": ["#e0f2fe", "#7dd3fc", "#0284c7", "#0369a1", "#082f49"],
    "coral": ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"],
    "gray": ["#f8fafc", "#cbd5e1", "#94a3b8", "#475569", "#0f172a"],
}

CIRCLE_PALETTES = {
    "green": ["22,163,74,160", "21,128,61,180", "22,101,52,200", "20,83,45,220", "6,78,59,235"],
    "amber": ["245,158,11,165", "217,119,6,185", "180,83,9,205", "146,64,14,225", "120,53,15,240"],
    "blue": ["37,99,235,160", "29,78,216,180", "30,64,175,200", "30,58,138,220", "15,23,42,235"],
    "ruby": ["239,68,68,160", "220,38,38,180", "185,28,28,200", "153,27,27,220", "127,29,29,235"],
    "purple": ["147,51,234,160", "126,34,206,180", "107,33,168,200", "88,28,135,220", "59,7,100,235"],
    "teal": ["14,165,233,160", "2,132,199,180", "3,105,161,200", "7,89,133,220", "8,47,73,235"],
    "coral": ["245,158,11,160", "234,88,12,180", "225,29,72,200", "190,18,60,220", "136,19,55,235"],
    "gray": ["100,116,139,160", "71,85,105,180", "51,65,85,200", "30,41,59,220", "15,23,42,235"],
}


def _qgs_field(name: str, ftype: str) -> QgsField:
    if _HAS_QMETATYPE:
        t = {"int": QMetaType.Type.LongLong, "float": QMetaType.Type.Double}.get(ftype, QMetaType.Type.QString)
    else:
        t = {"int": QVariant.LongLong, "float": QVariant.Double}.get(ftype, QVariant.String)
    return QgsField(name, t)


def format_indicator_value(v: float, unit: str = "") -> str:
    """Formata valor numérico de acordo com a unidade retornada pelo SIDRA."""
    u_clean = (unit or "").strip()
    u_lower = u_clean.lower()
    a = abs(v)

    def _br(txt: str) -> str:
        return txt.replace(",", "X").replace(".", ",").replace("X", ".")

    if "por litro" in u_lower:
        return _br(f"R$ {v:,.2f}/L")

    if "mil r$" in u_lower or "mil reais" in u_lower:
        val_reais = v * 1000.0
        av = abs(val_reais)
        if av >= 1e9:
            return _br(f"R$ {val_reais / 1e9:,.2f} bi")
        if av >= 1e6:
            return _br(f"R$ {val_reais / 1e6:,.1f} mi")
        if av >= 1e3:
            return _br(f"R$ {val_reais / 1e3:,.0f} mil")
        return _br(f"R$ {val_reais:,.0f}")

    if "reais" in u_lower or u_clean == "R$":
        if a >= 1e6:
            return _br(f"R$ {v / 1e6:,.2f} mi")
        return _br(f"R$ {v:,.2f}" if a < 100 else f"R$ {v:,.0f}")

    if "salário" in u_lower or "salario" in u_lower:
        return _br(f"{v:,.2f} SM")

    if "%" in u_lower or "percentual" in u_lower:
        suf = "% a.a." if "a.a" in u_lower else "%"
        return _br(f"{v:,.2f}{suf}")

    if "‰" in u_lower or "por mil" in u_lower:
        return _br(f"{v:,.2f}‰")

    if "razão" in u_lower or "razao" in u_lower:
        return _br(f"{v:,.2f}")

    if u_lower in ("anos", "ano"):
        return _br(f"{v:,.1f} anos")

    if "filho" in u_lower:
        return _br(f"{v:,.2f} filhos")

    if "número-índice" in u_lower or "numero-indice" in u_lower:
        return _br(f"{v:,.1f}")

    if "índice" in u_lower or "indice" in u_lower or "gini" in u_lower:
        return _br(f"{v:,.3f}")

    if "hab/km" in u_lower:
        return _br(f"{v:,.1f} hab/km²")

    if "km²" in u_lower or "quadrad" in u_lower:
        return _br(f"{v:,.2f} km²" if a < 10 else f"{v:,.1f} km²")

    if "quilômetro" in u_lower or "quilometro" in u_lower or u_lower == "km":
        if a >= 1e3:
            return _br(f"{v / 1e3:,.2f} mil km")
        return _br(f"{v:,.1f} km" if a >= 10 else f"{v:,.2f} km")

    if any(tok in u_lower for tok in ("mil pessoas", "mil pessoa", "mil unidade", "mil domic")):
        scaled = v * 1000.0
        ap = abs(scaled)
        if ap >= 1e6:
            return _br(f"{scaled / 1e6:,.2f} mi")
        if ap >= 1e3:
            return _br(f"{scaled / 1e3:,.1f} mil")
        return _br(f"{scaled:,.0f}")

    if "mil litros" in u_lower:
        liters = v * 1000.0
        al = abs(liters)
        if al >= 1e6:
            return _br(f"{liters / 1e6:,.2f} mi L")
        return _br(f"{liters / 1e3:,.1f} mil L")

    if "mil dúzia" in u_lower or "mil duzia" in u_lower:
        duz = v * 1000.0
        ad = abs(duz)
        if ad >= 1e6:
            return _br(f"{duz / 1e6:,.2f} mi dúz.")
        return _br(f"{duz / 1e3:,.1f} mil dúz.")

    if u_lower == "t" or "tonelada" in u_lower:
        if a >= 1e6:
            return _br(f"{v / 1e6:,.2f} mi t")
        if a >= 1e3:
            return _br(f"{v / 1e3:,.1f} mil t")
        return _br(f"{v:,.1f} t")

    if "micrograma" in u_lower or "µg" in u_lower:
        return f"{_br(f'{v:,.1f}')} µg/m³"

    if "por 100 mil" in u_lower or "por 100.000" in u_lower:
        return f"{_br(f'{v:,.1f}')} / 100 mil hab."

    if "m³" in u_lower or "metro cúbico" in u_lower or "metros cúbicos" in u_lower:
        if a >= 1e6:
            return _br(f"{v / 1e6:,.2f} mi m³")
        if a >= 1e3:
            return _br(f"{v / 1e3:,.1f} mil m³")
        return _br(f"{v:,.0f} m³")

    if "kg/ha" in u_lower or "quilogramas por hectare" in u_lower:
        return _br(f"{v:,.0f} kg/ha")

    if "quilograma" in u_lower or u_lower == "kg":
        if a >= 1e6:
            return _br(f"{v / 1e6:,.2f} mi kg")
        if a >= 1e3:
            return _br(f"{v / 1e3:,.1f} mil kg")
        return _br(f"{v:,.0f} kg")

    if "cabe" in u_lower or "cab" in u_lower:
        if a >= 1e6:
            return _br(f"{v / 1e6:,.2f} mi cab.")
        if a >= 1e3:
            return _br(f"{v / 1e3:,.1f} mil cab.")
        return _br(f"{v:,.0f} cab.")

    if "hectare" in u_lower or u_lower == "ha":
        if a >= 1e6:
            return _br(f"{v / 1e6:,.2f} mi ha")
        if a >= 1e3:
            return _br(f"{v / 1e3:,.1f} mil ha")
        return _br(f"{v:,.0f} ha")

    if any(k in u_lower for k in ("pessoa", "domic", "estabel", "empres", "unid", "munic")):
        if a >= 1e6:
            return _br(f"{v / 1e6:,.2f} mi")
        if a >= 1e3:
            return _br(f"{v / 1e3:,.1f} mil")
        return _br(f"{v:,.0f}")

    if a >= 1e6:
        return _br(f"{v / 1e6:,.2f} mi")
    if a >= 1e3:
        return _br(f"{v / 1e3:,.1f} mil")
    return _br(f"{v:,.1f}")


def _quantile_breaks(vals: List[float], k: int) -> List[float]:
    vals = sorted(vals)
    lo, hi = vals[0], vals[-1]
    if hi <= lo:
        hi = lo + 1.0
    breaks = [lo]
    for i in range(1, k):
        b = vals[int(round(i / k * (len(vals) - 1)))]
        if b <= breaks[-1]:
            b = breaks[-1] + (hi - lo) / k
        breaks.append(min(hi, b))
    breaks.append(hi)
    return breaks


def _field_values(
    layer: QgsVectorLayer,
    field_name: str,
    positive_only: bool = False,
    check_has_reg: bool = False,
) -> List[float]:
    idx = layer.fields().indexFromName(field_name)
    idx_has = layer.fields().indexFromName("HAS_REG") if check_has_reg else -1
    out: List[float] = []
    if idx < 0:
        return out
    for feat in layer.getFeatures():
        if idx_has >= 0 and int(feat[idx_has] or 0) == 0:
            continue
        v = feat[idx]
        if v is None:
            continue
        try:
            fv = float(v)
        except (TypeError, ValueError):
            continue
        if positive_only and fv <= 0:
            continue
        out.append(fv)
    return out


class GeoSidraLayerBuilder:
    """Constrói camadas temáticas do SIDRA para todos os níveis territoriais IBGE suportados."""

    @staticmethod
    def _dissolve_polygon_geometry(geom: QgsGeometry) -> QgsGeometry:
        """Dissolve fronteiras internas de polígonos municipais componentes de uma RM/RIDE."""
        if geom is None or geom.isEmpty():
            return geom
        try:
            parts: List[QgsGeometry] = []
            if geom.isMultipart():
                for poly in geom.asMultiPolygon():
                    g_part = QgsGeometry.fromPolygonXY(poly)
                    if not g_part.isGeosValid():
                        g_part = g_part.makeValid()
                    if not g_part.isEmpty():
                        parts.append(g_part)
            else:
                g_part = geom if geom.isGeosValid() else geom.makeValid()
                if not g_part.isEmpty():
                    parts.append(g_part)
            if len(parts) <= 1:
                return parts[0] if parts else geom
            unioned = QgsGeometry.unaryUnion(parts)
            if unioned and not unioned.isEmpty():
                return unioned
        except Exception as exc:
            LOGGER.warning("Aviso ao dissolver geometria RM/RIDE: %s", exc)
        return geom

    @classmethod
    def _maybe_persist_dissolved_rm_cache(
        cls,
        dissolved_feats: Dict[str, Tuple[QgsGeometry, str, str, str]],
        malhas_client: IbgeMalhasClient,
    ) -> None:
        """Persiste GeoJSON dissolvido de N7/N14 para carregamentos futuros instantâneos."""
        if len(dissolved_feats) < 15:
            return
        out_path = malhas_client.get_dissolved_rm_cache_path()
        if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
            return
        features_json = []
        for code, (geom, nivel, nome, uf_val) in dissolved_feats.items():
            try:
                geom_dict = json.loads(geom.asJson(6))
            except Exception:
                continue
            features_json.append({
                "type": "Feature",
                "properties": {
                    "codarea": code,
                    "nivel": nivel,
                    "nome": nome,
                    "uf": uf_val,
                    "dissolved": True,
                },
                "geometry": geom_dict,
            })
        if features_json:
            tmp_path = f"{out_path}.part"
            try:
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump({"type": "FeatureCollection", "features": features_json}, f, ensure_ascii=False)
                os.replace(tmp_path, out_path)
            except Exception as exc:
                LOGGER.warning("Não foi possível salvar cache dissolvido de RMs: %s", exc)

    @classmethod
    def build_polygon_layer(
        cls,
        parsed_data: Dict,
        layer_name: str,
        territory: str = "BR",
        level: str = "N6",
        geojson_path: Optional[str] = None,
        ibge_field: str = "codarea",
    ) -> QgsVectorLayer:
        """Cria camada integrada com os dados do SIDRA."""
        lvl = (level or parsed_data.get("level") or "N6").upper()
        malhas_client = IbgeMalhasClient()
        by_mun = parsed_data.get("by_mun", {})

        if not geojson_path:
            cap_codes = [k for k in by_mun.keys() if len(str(k)) == 7] if lvl == "N7_N6" else None
            geojson_path = malhas_client.fetch_geojson_for_level(
                level=lvl,
                territory=territory,
                capital_codes=cap_codes,
            )

        source_layer = QgsVectorLayer(geojson_path, "ibge_malha_temp", "ogr")
        if not source_layer.isValid():
            try:
                os.remove(geojson_path)
            except OSError:
                pass
            raise RuntimeError("Falha ao carregar malha do IBGE. Verifique o cache ou conexão.")

        crs = source_layer.crs().authid() or "EPSG:4674"
        mem = QgsVectorLayer(f"MultiPolygon?crs={crs}", layer_name, "memory")
        prov = mem.dataProvider()

        field_specs = [
            ("CD_MUN", "str"),
            ("CD_GEO", "str"),
            ("NM_MUN", "str"),
            ("NM_LOCAL", "str"),
            ("UF", "str"),
            ("PRODUTO", "str"),
            ("UNIDADE", "str"),
            ("VALOR_PRINC", "float"),
            ("PART_PCT", "float"),
            ("RANKING", "int"),
            ("HAS_REG", "int"),
        ]

        for var_code in parsed_data.get("variables", []):
            field_specs.append((f"VAR_{var_code}", "float"))

        fields = QgsFields()
        for name, ftype in field_specs:
            fields.append(_qgs_field(name, ftype))
        prov.addAttributes(fields.toList())
        mem.updateFields()

        prod_name = parsed_data.get("product_name", "")
        unit_name = parsed_data.get("unit", "")
        mapper = MunicipalityMapper.instance()

        is_partial_sample = bool(parsed_data.get("partial_sample"))
        filter_to_matched = bool(by_mun) and (
            lvl in ("N7", "N14", "N7_N14", "N7_N6") or (lvl == "N6" and is_partial_sample)
        )
        src_field_names = {f.name() for f in source_layer.fields()}
        dissolved_rm_to_cache: Dict[str, Tuple[QgsGeometry, str, str, str]] = {}

        feats: List[QgsFeature] = []
        for src in source_layer.getFeatures():
            raw_code = str(src[ibge_field] or "").strip()
            src_geom = src.geometry()

            if lvl == "N1":
                code = raw_code.zfill(2)
                item_data = by_mun.get("BR")
                nm = "Brasil (Total Nacional)"
                uf = "BR"
            elif lvl == "N2":
                code = raw_code
                item_data = by_mun.get(code)
                reg_nm, reg_sigla = IBGE_MACRO_REGION_INFO.get(code, ("", "BR"))
                nm = item_data["nm_mun"] if item_data else reg_nm
                uf = item_data["uf"] if item_data else reg_sigla
            elif lvl == "N3":
                code = raw_code.zfill(2)
                item_data = by_mun.get(code)
                nm = item_data["nm_mun"] if item_data else ""
                uf = item_data["uf"] if item_data else UF_NUM_TO_SIGLA.get(code, "")
            elif lvl == "N8":
                code = raw_code.zfill(4)
                item_data = by_mun.get(code)
                nm = item_data["nm_mun"] if item_data else ""
                uf = item_data["uf"] if item_data else UF_NUM_TO_SIGLA.get(code[:2], "")
            elif lvl == "N9":
                code = raw_code.zfill(5)
                item_data = by_mun.get(code)
                nm = item_data["nm_mun"] if item_data else ""
                uf = item_data["uf"] if item_data else UF_NUM_TO_SIGLA.get(code[:2], "")
            elif lvl in ("N7", "N14", "N7_N14", "N7_N6"):
                code = raw_code.zfill(7) if len(raw_code) >= 6 else raw_code
                src_nivel = str(src["nivel"] or "") if "nivel" in src_field_names else (
                    "N6" if len(code) == 7 else ("N7" if len(code) == 4 else "N14")
                )
                is_rm_feat = src_nivel in ("N7", "N14")
                if lvl == "N7" and src_nivel != "N7":
                    continue
                if lvl == "N14" and src_nivel != "N14":
                    continue
                if filter_to_matched and code not in by_mun:
                    if is_rm_feat and "dissolved" in src_field_names and not bool(src["dissolved"]):
                        dissolved_g = cls._dissolve_polygon_geometry(src_geom)
                        rm_nm = str(src["nome"] or "") if "nome" in src_field_names else ""
                        rm_uf = str(src["uf"] or "") if "uf" in src_field_names else ""
                        dissolved_rm_to_cache[code] = (dissolved_g, src_nivel, rm_nm, rm_uf)
                    continue

                if is_rm_feat and "dissolved" in src_field_names and not bool(src["dissolved"]):
                    src_geom = cls._dissolve_polygon_geometry(src_geom)
                    rm_nm = str(src["nome"] or "") if "nome" in src_field_names else ""
                    rm_uf = str(src["uf"] or "") if "uf" in src_field_names else ""
                    dissolved_rm_to_cache[code] = (src_geom, src_nivel, rm_nm, rm_uf)

                item_data = by_mun.get(code)
                if item_data:
                    nm = item_data["nm_mun"]
                    uf = item_data["uf"]
                elif src_nivel == "N6":
                    info = mapper.get_by_ibge(code) or {}
                    nm = info.get("nome_municipio", "")
                    uf = info.get("uf", "")
                else:
                    nm = str(src["nome"] or "") if "nome" in src_field_names else ""
                    uf = str(src["uf"] or "") if "uf" in src_field_names else ""
            else:
                code = raw_code.zfill(7)
                if filter_to_matched and code not in by_mun and code[:6] not in by_mun:
                    continue
                info = mapper.get_by_ibge(code) or {}
                item_data = by_mun.get(code) or by_mun.get(code[:6])
                nm = item_data["nm_mun"] if item_data else info.get("nome_municipio", "")
                uf = item_data["uf"] if item_data else info.get("uf", "")

            attrs = []
            for name, ftype in field_specs:
                if name in ("CD_GEO", "CD_MUN"):
                    attrs.append(code)
                elif name in ("NM_LOCAL", "NM_MUN"):
                    attrs.append(nm)
                elif name == "UF":
                    attrs.append(uf)
                elif name == "PRODUTO":
                    attrs.append(prod_name)
                elif name == "UNIDADE":
                    attrs.append(unit_name)
                elif name == "VALOR_PRINC":
                    attrs.append(item_data["valor_principal"] if item_data else 0.0)
                elif name == "PART_PCT":
                    attrs.append(item_data.get("share_pct", 0.0) if item_data else 0.0)
                elif name == "RANKING":
                    attrs.append(item_data.get("ranking", 0) if item_data else 0)
                elif name == "HAS_REG":
                    attrs.append(1 if (item_data and item_data.get("has_record", False)) else 0)
                elif name.startswith("VAR_"):
                    vc = name[4:]
                    attrs.append(item_data["vars"].get(vc, 0.0) if item_data else 0.0)
                else:
                    attrs.append(0.0 if ftype == "float" else ("" if ftype == "str" else 0))

            f = QgsFeature(mem.fields())
            f.setGeometry(src_geom)
            f.setAttributes(attrs)
            feats.append(f)

        if dissolved_rm_to_cache:
            cls._maybe_persist_dissolved_rm_cache(dissolved_rm_to_cache, malhas_client)

        prov.addFeatures(feats)
        mem.updateExtents()
        return mem

    @classmethod
    def apply_base_polygon(cls, layer: QgsVectorLayer) -> None:
        sym = QgsFillSymbol()
        bg = QgsSimpleFillSymbolLayer()
        bg.setFillColor(QColor("#f8fafc"))
        bg.setStrokeColor(QColor("#cbd5e1"))
        bg.setStrokeWidth(0.18)
        sym.changeSymbolLayer(0, bg)
        layer.setRenderer(QgsSingleSymbolRenderer(sym))
        layer.triggerRepaint()

    @classmethod
    def apply_graduated(
        cls,
        layer: QgsVectorLayer,
        field_name: str = "VALOR_PRINC",
        scheme: str = "green",
        unit: str = "",
        allow_negative: bool = False,
        is_binary: bool = False,
    ) -> None:
        colors = PALETTES.get(scheme, PALETTES["green"])
        ranges: List[QgsRendererRange] = []

        if allow_negative:
            vals = _field_values(layer, field_name, positive_only=False, check_has_reg=True)
            if vals:
                unique_cnt = len(set(vals))
                if unique_cnt == 1:
                    sym = QgsFillSymbol.createSimple({"color": colors[-1], "outline_color": "#334155", "outline_width": "0.18"})
                    ranges.append(QgsRendererRange(vals[0], vals[0], sym, format_indicator_value(vals[0], unit)))
                else:
                    k = min(5, unique_cnt)
                    br = _quantile_breaks(vals, k)
                    for i in range(k):
                        sym = QgsFillSymbol.createSimple({"color": colors[i], "outline_color": "#334155", "outline_width": "0.18"})
                        lo, hi = br[i], br[i + 1]
                        lbl = f"{format_indicator_value(lo, unit)} a {format_indicator_value(hi, unit)}"
                        ranges.append(QgsRendererRange(lo, hi, sym, lbl))
            else:
                zero_sym = QgsFillSymbol.createSimple({"color": "#f1f5f9", "outline_color": "#94a3b8", "outline_width": "0.15"})
                ranges.append(QgsRendererRange(-1e18, 1e18, zero_sym, "Sem registro"))
        else:
            vals = _field_values(layer, field_name, positive_only=True)
            zero_lbl = "Não / Sem registro (0)" if is_binary else "Sem registro / Zero"
            zero_sym = QgsFillSymbol.createSimple({"color": "#f1f5f9", "outline_color": "#94a3b8", "outline_width": "0.15"})
            ranges.append(QgsRendererRange(-1e18, 0.0, zero_sym, zero_lbl))

            if vals:
                unique_cnt = len(set(vals))
                if unique_cnt == 1:
                    sym = QgsFillSymbol.createSimple({"color": colors[-1], "outline_color": "#334155", "outline_width": "0.18"})
                    pos_lbl = "Sim (Presença = 1)" if is_binary else format_indicator_value(vals[0], unit)
                    ranges.append(QgsRendererRange(1e-9, vals[0], sym, pos_lbl))
                else:
                    k = min(5, unique_cnt)
                    br = _quantile_breaks(vals, k)
                    for i in range(k):
                        sym = QgsFillSymbol.createSimple({"color": colors[i], "outline_color": "#334155", "outline_width": "0.18"})
                        lo = br[i] if i else 1e-9
                        hi = br[i + 1]
                        lbl = f"{format_indicator_value(lo, unit)} a {format_indicator_value(hi, unit)}"
                        ranges.append(QgsRendererRange(lo, hi, sym, lbl))

        renderer = QgsGraduatedSymbolRenderer(field_name, ranges)
        layer.setRenderer(renderer)
        layer.triggerRepaint()

    @classmethod
    def build_centroid_points(
        cls,
        poly_layer: QgsVectorLayer,
        field_name: str = "VALOR_PRINC",
        layer_name: str = "Pontos Proporcionais",
        allow_negative: bool = False,
    ) -> QgsVectorLayer:
        crs = poly_layer.crs().authid() or "EPSG:4674"
        pts = QgsVectorLayer(f"Point?crs={crs}", layer_name, "memory")
        prov = pts.dataProvider()
        prov.addAttributes(poly_layer.fields().toList())
        pts.updateFields()

        idx = poly_layer.fields().indexFromName(field_name)
        idx_has = poly_layer.fields().indexFromName("HAS_REG")
        out: List[QgsFeature] = []

        for feat in poly_layer.getFeatures():
            if allow_negative and idx_has >= 0 and int(feat[idx_has] or 0) == 0:
                continue
            try:
                raw_val = feat[idx]
                if raw_val is None:
                    continue
                fval = float(raw_val)
                if not allow_negative and fval <= 0:
                    continue
            except (TypeError, ValueError):
                continue

            geom = feat.geometry()
            if geom is None or geom.isEmpty():
                continue

            if geom.isMultipart():
                parts = geom.asGeometryCollection()
                geom = max(parts, key=lambda g: g.area()) if parts else geom

            pf = QgsFeature(pts.fields())
            pf.setGeometry(geom.pointOnSurface())
            pf.setAttributes(feat.attributes())
            out.append(pf)

        prov.addFeatures(out)
        pts.updateExtents()
        return pts

    @classmethod
    def apply_proportional_circles(
        cls,
        pt_layer: QgsVectorLayer,
        field_name: str = "VALOR_PRINC",
        scheme: str = "green",
        unit: str = "",
        allow_negative: bool = False,
    ) -> None:
        vals = _field_values(
            pt_layer,
            field_name,
            positive_only=not allow_negative,
            check_has_reg=allow_negative,
        )
        if not vals:
            return

        colors = CIRCLE_PALETTES.get(scheme, CIRCLE_PALETTES["green"])
        sizes = [4.0, 7.5, 12.0, 17.5, 24.0]
        unique_cnt = len(set(vals))
        ranges: List[QgsRendererRange] = []

        if unique_cnt == 1:
            color = "#dc2626" if (allow_negative and vals[0] < 0) else colors[-1]
            sym = QgsMarkerSymbol.createSimple({
                "name": "circle",
                "color": color,
                "outline_color": "#ffffff",
                "outline_width": "0.35",
                "size": "12.0",
            })
            ranges.append(QgsRendererRange(vals[0], vals[0], sym, format_indicator_value(vals[0], unit)))
        else:
            k = min(5, unique_cnt)
            br = _quantile_breaks(vals, k)
            max_abs = max((abs(v) for v in vals), default=1.0) or 1.0
            for i in range(k):
                lo = br[i] if (i or allow_negative) else 1e-9
                hi = br[i + 1]
                mid = 0.5 * (lo + hi)
                if allow_negative:
                    color = "#dc2626" if mid < 0 else colors[min(i, len(colors) - 1)]
                    size_val = round(4.5 + 17.5 * (abs(mid) / max_abs), 1)
                else:
                    color = colors[i]
                    size_val = sizes[i]
                sym = QgsMarkerSymbol.createSimple({
                    "name": "circle",
                    "color": color,
                    "outline_color": "#ffffff",
                    "outline_width": "0.35",
                    "size": str(size_val),
                })
                lbl = f"{format_indicator_value(lo, unit)} a {format_indicator_value(hi, unit)}"
                ranges.append(QgsRendererRange(lo, hi, sym, lbl))

        renderer = QgsGraduatedSymbolRenderer(field_name, ranges)
        renderer.setOrderBy(QgsFeatureRequest.OrderBy([QgsFeatureRequest.OrderByClause(field_name, False)]))
        renderer.setOrderByEnabled(True)
        pt_layer.setRenderer(renderer)
        pt_layer.triggerRepaint()
