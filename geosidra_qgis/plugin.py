# -*- coding: utf-8 -*-
"""
Classe principal do plugin GeoSIDRA - Espacializador Estatístico do IBGE (SIDRA).
Autor: Luís Eduardo Araújo de Souza
"""

import os
from qgis.PyQt.QtGui import QIcon

try:
    from qgis.PyQt.QtGui import QAction
except ImportError:
    from qgis.PyQt.QtWidgets import QAction

from . import _reload_submodules
from .data.catalog import SURVEY_GROUPS, SURVEYS


class GeoSidraPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
        self.action = None
        self.dialog = None
        self.menu_name = "&GeoSIDRA - IBGE"

    def initGui(self) -> None:
        icon_path = os.path.join(self.plugin_dir, "icon.png")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(self.plugin_dir, "icon.svg")

        self.action = QAction(
            QIcon(icon_path),
            "GeoSIDRA - Espacializador Estatístico do IBGE (SIDRA)...",
            self.iface.mainWindow(),
        )
        n_surveys = len(SURVEYS)
        n_groups = max(1, len(SURVEY_GROUPS) - 1)
        self.action.setToolTip(
            f"Ingestão, análise e espacialização temática de {n_surveys} pesquisas oficiais em {n_groups} áreas temáticas do IBGE/SIDRA"
        )
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToVectorMenu(self.menu_name, self.action)

    def unload(self) -> None:
        if self.action is not None:
            self.iface.removePluginVectorMenu(self.menu_name, self.action)
            self.iface.removeToolBarIcon(self.action)
            self.action = None

    def run(self) -> None:
        _reload_submodules()
        from .gui.main_dialog import GeoSidraDialog
        self.dialog = GeoSidraDialog(self.iface)
        self.dialog.exec()
