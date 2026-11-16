# -*- coding: utf-8 -*-
"""
Módulos centrais do plugin GeoSIDRA para QGIS.
"""

from .sidra_client import SidraClient
from .ibge_api import IbgeMalhasClient
from .municipality_mapper import MunicipalityMapper
from .analytics_engine import AnalyticsEngine, AnalyticsReportBundle, StyledTableSpec
from .report_renderer import export_bundle, export_table_csv

try:
    from .layer_builder import GeoSidraLayerBuilder
    from .background_job import BackgroundJob
except ImportError:
    # Permite testes unitários de clientes e dados em ambiente Python padrão sem QGIS
    GeoSidraLayerBuilder = None
    BackgroundJob = None

__all__ = [
    "SidraClient",
    "IbgeMalhasClient",
    "MunicipalityMapper",
    "GeoSidraLayerBuilder",
    "AnalyticsEngine",
    "AnalyticsReportBundle",
    "StyledTableSpec",
    "export_bundle",
    "export_table_csv",
    "BackgroundJob",
]
