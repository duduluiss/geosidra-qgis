# -*- coding: utf-8 -*-
"""
GeoSIDRA - Espacializador Estatístico do IBGE (SIDRA) para QGIS 4 / QGIS 3
Autor: Luís Eduardo Araújo de Souza
"""

import importlib
import logging
import sys

LOGGER = logging.getLogger("GeoSIDRA")


def _reload_submodules() -> None:
    order = [
        "geosidra_qgis.data.catalog",
        "geosidra_qgis.core.municipality_mapper",
        "geosidra_qgis.core.ibge_api",
        "geosidra_qgis.core.sidra_client",
        "geosidra_qgis.core.layer_builder",
        "geosidra_qgis.core.analytics_engine",
        "geosidra_qgis.core.report_renderer",
        "geosidra_qgis.core.background_job",
        "geosidra_qgis.gui.main_dialog",
        "geosidra_qgis.plugin",
    ]
    for mod_name in order:
        mod_obj = sys.modules.get(mod_name)
        if mod_obj is not None:
            try:
                importlib.reload(mod_obj)
            except Exception as exc:
                LOGGER.debug("Submódulo não recarregado (%s): %s", mod_name, exc)


def classFactory(iface):
    _reload_submodules()
    from .plugin import GeoSidraPlugin
    return GeoSidraPlugin(iface)
