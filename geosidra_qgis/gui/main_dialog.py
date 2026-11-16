# -*- coding: utf-8 -*-
"""
Janela principal do plugin GeoSIDRA para QGIS 3 / QGIS 4.
Interface sóbria e padronizada:
  1. Dados e Filtros (PAM, Censo Agro 2017, PPM/Aquicultura, PEVS, PIB, CEMPRE, PIA, População e Censo 2022)
  2. Mapa e Simbologia (Círculos e Coroplético)
  3. Relatórios, Tabelas e Gráficos (300 DPI, preview amplo sem espremer)
  4. Log e Diagnóstico
"""

from __future__ import annotations

import csv
import logging
import os
import unicodedata
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from qgis.core import QgsProject, QgsVectorLayer
from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtGui import QColor, QDesktopServices, QIcon, QPainter, QPixmap
from qgis.PyQt.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..core.analytics_engine import (
    AnalyticsEngine,
    AnalyticsReportBundle,
    fmt_float_br,
    fmt_int_br,
)
from ..core.background_job import BackgroundJob
from ..core.ibge_api import IbgeMalhasClient
from ..core.layer_builder import GeoSidraLayerBuilder
from ..core.report_renderer import (
    export_bundle,
    export_table_csv,
    render_styled_table_png,
)
from ..core.sidra_client import SidraClient
from ..data.catalog import (
    BRAZIL_UFS,
    SURVEY_GROUPS,
    SURVEYS,
    TERRITORIAL_LEVEL_LABELS,
    get_survey_by_id,
    get_survey_categories,
    get_survey_extra_classifications,
    get_survey_supported_levels,
    get_survey_valid_years,
    get_survey_year_label,
    get_variable_info,
    get_variable_slug,
    resolve_table_queries,
)

LOGGER = logging.getLogger("GeoSIDRA")


def _enum(owner: Any, scope: str, name: str) -> Any:
    """Acessa enums de forma compatível com Qt5 e Qt6."""
    scoped = getattr(owner, scope, None)
    if scoped is not None and hasattr(scoped, name):
        return getattr(scoped, name)
    return getattr(owner, name)


def make_compact_button(text: str, primary: bool = False) -> QPushButton:
    """Cria botão compacto com estilo padronizado sóbrio."""
    btn = QPushButton(text)
    if hasattr(QSizePolicy, "Policy"):
        btn.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    else:
        btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
    if primary:
        btn.setMinimumHeight(30)
        btn.setStyleSheet(
            "QPushButton { background-color: #0f2c59; color: #ffffff; font-weight: bold; "
            "padding: 5px 14px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #1e3a8a; }"
            "QPushButton:disabled { background-color: #94a3b8; }"
        )
    else:
        btn.setStyleSheet("padding: 3px 10px;")
    return btn


PALETTES_INFO = [
    ("Verde agro e florestal (Greens)", "green", ["#edf8e9", "#bae4b3", "#74c476", "#31a354", "#006d2c"]),
    ("Âmbar e dourado (Cereais / Grãos)", "amber", ["#fffbeb", "#fde68a", "#f59e0b", "#d97706", "#92400e"]),
    ("Azul clássico (Blues)", "blue", ["#eff6ff", "#bfdbfe", "#60a5fa", "#2563eb", "#1e3a8a"]),
    ("Rubi e carmim (Carnes / Frutas)", "ruby", ["#fee5d9", "#fcae91", "#fb6a4a", "#de2d26", "#a50f15"]),
    ("Roxo uva e café (Purples)", "purple", ["#f5f3ff", "#ddd6fe", "#a78bfa", "#7c3aed", "#4c1d95"]),
    ("Teal / Oceânico", "teal", ["#e0f2fe", "#7dd3fc", "#0284c7", "#0369a1", "#082f49"]),
    ("Coral / Laranja", "coral", ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"]),
    ("Cinza neutro", "gray", ["#f8fafc", "#cbd5e1", "#94a3b8", "#475569", "#0f172a"]),
]

STANDARD_UI_YEARS = list(range(2026, 2000, -1))
AVAILABLE_YEARS = list(range(2026, 1973, -1))


class GeoSidraDialog(QDialog):
    """Diálogo principal do GeoSIDRA."""

    def __init__(self, iface, parent=None):
        super().__init__(parent or (iface.mainWindow() if iface else None))
        self.iface = iface
        self.setWindowTitle("GeoSIDRA - Espacializador Estatístico do IBGE (SIDRA)")
        self.resize(900, 740)
        self.setMinimumSize(820, 640)

        self.sidra_client = SidraClient()
        self.last_parsed_data: Optional[Dict] = None
        self.last_reports: List[AnalyticsReportBundle] = []
        self.current_preview_bundle: Optional[AnalyticsReportBundle] = None
        self.last_rendered_png: Optional[str] = None
        self.active_job: Optional[BackgroundJob] = None
        self._warned_surveys: Set[str] = set()
        self._suppress_survey_popup: bool = True
        self._prev_single_year_survey: bool = False
        self._prev_subannual_survey: bool = False
        self._extra_clf_combos: List[Tuple[int, str, QComboBox, int]] = []

        self._build_ui()
        self._populate_initial_data()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(6)

        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)

        # 1. Aba Dados e Filtros
        tab_dados = QWidget()
        self._build_tab_filters(tab_dados)
        self.tabs.addTab(tab_dados, "1. Dados e Filtros")

        # 2. Aba Mapa e Simbologia
        tab_map = QWidget()
        self._build_tab_map(tab_map)
        self.tabs.addTab(tab_map, "2. Mapa e Simbologia")

        # 3. Aba Relatórios, Tabelas e Gráficos
        tab_reports = QWidget()
        self._build_tab_reports(tab_reports)
        self.tabs.addTab(tab_reports, "3. Relatórios, Tabelas e Gráficos")

        # 4. Aba Log
        tab_log = QWidget()
        self._build_tab_log(tab_log)
        self.tabs.addTab(tab_log, "4. Log e Diagnóstico")

        # Barra de Progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(18)
        self.progress_bar.setTextVisible(True)
        root.addWidget(self.progress_bar)

        # Rodapé Sóbrio
        h_footer = QHBoxLayout()
        h_footer.setContentsMargins(0, 4, 0, 0)
        h_footer.setSpacing(8)

        n_groups = sum(1 for gid, _ in SURVEY_GROUPS if gid != "ALL")
        src = QLabel(f"Fonte: IBGE (SIDRA - {len(SURVEYS)} pesquisas em {n_groups} áreas temáticas) | Malha: IBGE")
        src.setStyleSheet("color: #64748b; font-size: 10px;")
        h_footer.addWidget(src)

        self.lbl_status = QLabel("Pronto")
        self.lbl_status.setStyleSheet("color: #475569; font-size: 11px;")
        h_footer.addWidget(self.lbl_status)
        h_footer.addStretch(1)

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self._cancel_active_job)
        h_footer.addWidget(self.btn_cancel)

        self.btn_execute = QPushButton("Consultar SIDRA e gerar camada no QGIS")
        self.btn_execute.setMinimumHeight(32)
        self.btn_execute.setStyleSheet("font-weight: bold;")
        self.btn_execute.clicked.connect(self._run_sidra_query_and_layer)
        h_footer.addWidget(self.btn_execute)

        root.addLayout(h_footer)

    # --------------------------------------------------------------------------
    # ABA 1: DADOS E FILTROS
    # --------------------------------------------------------------------------
    def _build_tab_filters(self, parent: QWidget) -> None:
        tab_outer = QVBoxLayout(parent)
        tab_outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea(parent)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(_enum(QFrame, "Shape", "NoFrame"))
        tab_outer.addWidget(scroll)

        page = QWidget()
        scroll.setWidget(page)
        v_dados = QVBoxLayout(page)
        v_dados.setContentsMargins(8, 8, 8, 8)
        v_dados.setSpacing(8)

        # 1. Pesquisa Estatística Oficial do IBGE
        grp_survey = QGroupBox("1. Pesquisa Estatística Oficial do IBGE (SIDRA)")
        v_survey = QVBoxLayout(grp_survey)
        v_survey.setContentsMargins(10, 8, 10, 8)
        v_survey.setSpacing(6)

        f_survey = QFormLayout()
        f_survey.setContentsMargins(0, 0, 0, 0)
        f_survey.setVerticalSpacing(6)

        self.cmb_group = QComboBox()
        for gid, gname in SURVEY_GROUPS:
            self.cmb_group.addItem(gname, gid)
        self.cmb_group.currentIndexChanged.connect(self._on_group_changed)
        f_survey.addRow("Área Temática:", self.cmb_group)

        self.txt_filter_survey = QLineEdit()
        self.txt_filter_survey.setPlaceholderText(
            "Buscar pesquisa ou nº da tabela SIDRA (ex: 6588, abate, censo, pnad, munic, 5457)..."
        )
        self.txt_filter_survey.textChanged.connect(self._on_survey_filter_changed)
        f_survey.addRow("Filtrar pesquisa:", self.txt_filter_survey)

        self.cmb_survey = QComboBox()
        self.cmb_survey.currentIndexChanged.connect(self._on_survey_changed)
        f_survey.addRow("Pesquisa / Tabela:", self.cmb_survey)
        v_survey.addLayout(f_survey)

        # Banner de pontos de atenção e restrições da tabela selecionada
        self.frame_notice = QFrame()
        self.frame_notice.setObjectName("noticeBanner")
        v_notice = QVBoxLayout(self.frame_notice)
        v_notice.setContentsMargins(8, 6, 8, 6)
        v_notice.setSpacing(2)

        self.lbl_notice_title = QLabel("")
        self.lbl_notice_title.setWordWrap(True)
        v_notice.addWidget(self.lbl_notice_title)

        self.lbl_notice = QLabel("")
        self.lbl_notice.setWordWrap(True)
        v_notice.addWidget(self.lbl_notice)

        self.frame_notice.setVisible(False)
        v_survey.addWidget(self.frame_notice)

        v_dados.addWidget(grp_survey)

        # 2. Recorte Territorial e Temporal
        grp_geo_time = QGroupBox("2. Recorte Territorial e Temporal")
        grid_gt = QGridLayout(grp_geo_time)
        grid_gt.setContentsMargins(10, 8, 10, 8)
        grid_gt.setHorizontalSpacing(10)
        grid_gt.setVerticalSpacing(6)

        grid_gt.addWidget(QLabel("Nível territorial (mapa):"), 0, 0)
        self.cmb_level = QComboBox()
        self.cmb_level.setToolTip(
            "Recorte geográfico de agregação no mapa (Municípios N6, Microrregiões N9, Mesorregiões N8, "
            "RMs N7/N14, Estados N3 ou Grandes Regiões N2, conforme suporte oficial da pesquisa no SIDRA)."
        )
        self.cmb_level.currentIndexChanged.connect(self._on_level_changed)
        grid_gt.addWidget(self.cmb_level, 0, 1)

        grid_gt.addWidget(QLabel("UF / Território:"), 1, 0)
        self.cmb_territory = QComboBox()
        for uf_sigla, uf_nome, _ in BRAZIL_UFS:
            self.cmb_territory.addItem(f"{uf_sigla} - {uf_nome}", uf_sigla)
        self.cmb_territory.setCurrentIndex(0)
        grid_gt.addWidget(self.cmb_territory, 1, 1)

        grid_gt.addWidget(QLabel("Ano(s) / Período(s):"), 2, 0, _enum(Qt, "AlignmentFlag", "AlignTop"))

        box_years = QVBoxLayout()
        box_years.setSpacing(4)
        self.list_years = QListWidget()
        self.list_years.setSelectionMode(_enum(QAbstractItemView, "SelectionMode", "NoSelection"))
        self.list_years.setMaximumHeight(130)
        user_role = _enum(Qt, "ItemDataRole", "UserRole")
        for yr in STANDARD_UI_YEARS:
            item = QListWidgetItem(str(yr))
            item.setData(user_role, yr)
            item.setFlags(item.flags() | _enum(Qt, "ItemFlag", "ItemIsUserCheckable"))
            item.setCheckState(_enum(Qt, "CheckState", "Checked" if yr in (2025, 2024) else "Unchecked"))
            self.list_years.addItem(item)
        box_years.addWidget(self.list_years)

        # Botões de Anos
        row_y_btns = QHBoxLayout()
        row_y_btns.setSpacing(4)
        btn_y_clear = make_compact_button("Limpar")
        btn_y_clear.clicked.connect(lambda: self._set_checked_years([]))

        btn_y_latest = make_compact_button("Último Disponível")
        btn_y_latest.clicked.connect(lambda: self._select_preset_years("latest"))

        btn_y_2022 = make_compact_button("Censo 2022")
        btn_y_2022.clicked.connect(lambda: self._select_preset_years("2022"))

        btn_y_3 = make_compact_button("Últimos 3 Anos")
        btn_y_3.clicked.connect(lambda: self._select_preset_years("last3"))

        btn_y_5 = make_compact_button("Últimos 5 Anos")
        btn_y_5.clicked.connect(lambda: self._select_preset_years("last5"))

        btn_y_all = make_compact_button("Todos Válidos")
        btn_y_all.clicked.connect(lambda: self._select_preset_years("all"))

        row_y_btns.addWidget(btn_y_clear)
        row_y_btns.addWidget(btn_y_latest)
        row_y_btns.addWidget(btn_y_2022)
        row_y_btns.addWidget(btn_y_3)
        row_y_btns.addWidget(btn_y_5)
        row_y_btns.addWidget(btn_y_all)
        row_y_btns.addStretch(1)
        box_years.addLayout(row_y_btns)

        grid_gt.addLayout(box_years, 2, 1)
        v_dados.addWidget(grp_geo_time)

        # 3. Categoria / Produto / Tema e Variável
        grp_prod = QGroupBox("3. Produto / Atividade / Tema e Variável Mapeada")
        grid_p = QGridLayout(grp_prod)
        grid_p.setContentsMargins(10, 8, 10, 8)
        grid_p.setHorizontalSpacing(10)
        grid_p.setVerticalSpacing(6)

        grid_p.addWidget(QLabel("Filtrar categoria / item:"), 0, 0)
        self.txt_filter_prod = QLineEdit()
        self.txt_filter_prod.setPlaceholderText("Digite para filtrar (ex: Soja, Tilápia, Eucalipto, Comércio, Alfabetização)...")
        self.txt_filter_prod.textChanged.connect(self._filter_products_dropdown)
        grid_p.addWidget(self.txt_filter_prod, 0, 1)

        grid_p.addWidget(QLabel("Categoria / Item:"), 1, 0)
        self.cmb_product = QComboBox()
        grid_p.addWidget(self.cmb_product, 1, 1)

        grid_p.addWidget(QLabel("Variável mapeada:"), 2, 0)
        self.cmb_variable = QComboBox()
        self.cmb_variable.currentIndexChanged.connect(self._on_variable_changed)
        grid_p.addWidget(self.cmb_variable, 2, 1)

        # Subfiltros opcionais (classificações secundárias antes travadas no Total)
        self.pnl_extra_clfs = QWidget()
        self.form_extra_clfs = QFormLayout(self.pnl_extra_clfs)
        self.form_extra_clfs.setContentsMargins(0, 4, 0, 0)
        self.form_extra_clfs.setVerticalSpacing(5)
        self.pnl_extra_clfs.setVisible(False)
        grid_p.addWidget(self.pnl_extra_clfs, 3, 0, 1, 2)

        v_dados.addWidget(grp_prod)
        v_dados.addStretch(1)

    # --------------------------------------------------------------------------
    # ABA 2: MAPA E SIMBOLOGIA
    # --------------------------------------------------------------------------
    def _build_tab_map(self, parent: QWidget) -> None:
        v_map = QVBoxLayout(parent)
        v_map.setContentsMargins(10, 10, 10, 10)
        v_map.setSpacing(10)

        grp_symb = QGroupBox("Configurações Cartográficas e Temáticas")
        f_symb = QFormLayout(grp_symb)
        f_symb.setContentsMargins(12, 12, 12, 12)
        f_symb.setVerticalSpacing(10)

        self.cmb_symb = QComboBox()
        self.cmb_symb.addItem("Círculos proporcionais no centroide (ordenação decrescente)", "circles")
        self.cmb_symb.addItem("Mapa coroplético (quantis nos polígonos)", "choropleth")
        f_symb.addRow("Técnica de representação:", self.cmb_symb)

        self.cmb_palette = QComboBox()
        for label, code, colors in PALETTES_INFO:
            icon_pix = self._create_palette_pixmap(colors)
            self.cmb_palette.addItem(QIcon(icon_pix), label, code)
        f_symb.addRow("Paleta de cores:", self.cmb_palette)

        self.chk_base_poly = QCheckBox("Adicionar camada base neutra de contexto (círculos e recortes regionais)")
        self.chk_base_poly.setToolTip(
            "Adiciona limites neutros sob os círculos proporcionais e a malha das 27 UFs sob recortes parciais (RMs, Capitais ou RIDE)."
        )
        self.chk_base_poly.setChecked(True)
        f_symb.addRow("", self.chk_base_poly)

        self.chk_zoom_layer = QCheckBox("Ajustar zoom automaticamente na extensão da camada gerada")
        self.chk_zoom_layer.setChecked(True)
        f_symb.addRow("", self.chk_zoom_layer)

        v_map.addWidget(grp_symb)
        v_map.addStretch(1)

    # --------------------------------------------------------------------------
    # ABA 3: RELATÓRIOS, TABELAS E GRÁFICOS
    # --------------------------------------------------------------------------
    def _build_tab_reports(self, parent: QWidget) -> None:
        rep_scroll = QScrollArea(parent)
        rep_scroll.setWidgetResizable(True)
        rep_scroll.setFrameShape(_enum(QFrame, "Shape", "NoFrame"))

        rep_page = QWidget()
        v_rep = QVBoxLayout(rep_page)
        v_rep.setContentsMargins(6, 6, 6, 6)
        v_rep.setSpacing(8)

        # 1. Seleção do Relatório
        grp_rep_sel = QGroupBox("1. Seleção de Gráficos e Tabelas Acadêmicas")
        f_rep_sel = QFormLayout(grp_rep_sel)
        f_rep_sel.setContentsMargins(10, 8, 10, 8)
        self.cmb_report = QComboBox()
        self.cmb_report.currentIndexChanged.connect(self._on_report_selected)
        f_rep_sel.addRow("Item analítico:", self.cmb_report)
        v_rep.addWidget(grp_rep_sel)

        # 2. Edição de Título e Subtítulo
        grp_titles = QGroupBox("2. Título e Subtítulo Personalizados")
        grid_t = QGridLayout(grp_titles)
        grid_t.setContentsMargins(10, 8, 10, 8)
        grid_t.setHorizontalSpacing(8)
        grid_t.setVerticalSpacing(5)

        grid_t.addWidget(QLabel("Título:"), 0, 0)
        self.txt_custom_title = QLineEdit()
        grid_t.addWidget(self.txt_custom_title, 0, 1)

        grid_t.addWidget(QLabel("Subtítulo:"), 1, 0)
        self.txt_custom_subtitle = QLineEdit()
        grid_t.addWidget(self.txt_custom_subtitle, 1, 1)

        btn_restore_title = make_compact_button("Restaurar Padrão")
        btn_restore_title.clicked.connect(self._restore_default_report_title)
        grid_t.addWidget(btn_restore_title, 0, 2, 2, 1)
        v_rep.addWidget(grp_titles)

        # 3. Exportação
        grp_exp = QGroupBox("3. Exportação")
        vbox_exp = QVBoxLayout(grp_exp)
        vbox_exp.setContentsMargins(8, 6, 8, 6)
        vbox_exp.setSpacing(6)

        row_dir = QHBoxLayout()
        row_dir.setSpacing(6)
        default_dir = os.path.join(os.path.expanduser("~"), "GeoSIDRA_Relatorios")
        row_dir.addWidget(QLabel("Pasta:"))
        self.txt_out_dir = QLineEdit(default_dir)
        btn_browse_dir = make_compact_button("Procurar...")
        btn_browse_dir.clicked.connect(self._browse_out_dir)
        btn_open_dir = make_compact_button("Abrir Pasta")
        btn_open_dir.clicked.connect(self._open_out_dir)

        row_dir.addWidget(self.txt_out_dir, stretch=1)
        row_dir.addWidget(btn_browse_dir)
        row_dir.addWidget(btn_open_dir)
        vbox_exp.addLayout(row_dir)

        row_act = QHBoxLayout()
        row_act.setSpacing(8)
        self.chk_export_html = QCheckBox("Salvar também em página HTML")
        self.chk_export_html.setChecked(False)
        row_act.addWidget(self.chk_export_html)

        row_act.addStretch(1)

        self.btn_gen_report = make_compact_button("Gerar Item Selecionado (300 DPI)", primary=True)
        self.btn_gen_report.clicked.connect(self._generate_selected_report)
        row_act.addWidget(self.btn_gen_report)

        vbox_exp.addLayout(row_act)
        v_rep.addWidget(grp_exp)

        # 4. Pré-visualização Ampla
        grp_prev = QGroupBox("4. Pré-visualização do Resultado")
        grp_prev.setMinimumHeight(450)
        prev_layout = QVBoxLayout(grp_prev)
        prev_layout.setContentsMargins(8, 8, 8, 8)
        prev_layout.setSpacing(6)

        btn_box = QHBoxLayout()
        self.btn_open_full = make_compact_button("Abrir em Tamanho Real (300 DPI)")
        self.btn_open_full.setEnabled(False)
        self.btn_open_full.clicked.connect(self._open_preview_image_external)
        btn_box.addWidget(self.btn_open_full)
        btn_box.addStretch(1)
        prev_layout.addLayout(btn_box)

        self.prev_scroll = QScrollArea()
        self.prev_scroll.setWidgetResizable(True)
        self.prev_scroll.setMinimumHeight(400)
        self.lbl_preview_img = QLabel("Consulte os dados no SIDRA para habilitar a pré-visualização dos gráficos.")
        self.lbl_preview_img.setAlignment(_enum(Qt, "AlignmentFlag", "AlignCenter"))
        self.lbl_preview_img.setStyleSheet("background: #f8fafc; color: #64748b; font-size: 11px;")
        self.prev_scroll.setWidget(self.lbl_preview_img)
        prev_layout.addWidget(self.prev_scroll, 1)

        v_rep.addWidget(grp_prev, 1)
        rep_scroll.setWidget(rep_page)

        parent_layout = QVBoxLayout(parent)
        parent_layout.setContentsMargins(0, 0, 0, 0)
        parent_layout.addWidget(rep_scroll)

    # --------------------------------------------------------------------------
    # ABA 4: LOG E DIAGNÓSTICO
    # --------------------------------------------------------------------------
    def _build_tab_log(self, parent: QWidget) -> None:
        v_log = QVBoxLayout(parent)
        v_log.setContentsMargins(8, 8, 8, 8)
        v_log.setSpacing(6)

        self.txt_log = QPlainTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet("background: #0f172a; color: #f8fafc; font-family: Consolas, monospace; font-size: 10pt;")
        v_log.addWidget(self.txt_log)

        btn_box = QHBoxLayout()
        btn_clear = make_compact_button("Limpar Log")
        btn_clear.clicked.connect(self.txt_log.clear)
        btn_box.addStretch(1)
        btn_box.addWidget(btn_clear)
        v_log.addLayout(btn_box)

    # --------------------------------------------------------------------------
    # MÉTODOS DE DADOS E EVENTOS
    # --------------------------------------------------------------------------
    def _log(self, msg: str) -> None:
        self.txt_log.appendPlainText(msg)
        LOGGER.info(msg)

    def _create_palette_pixmap(self, colors: List[str]) -> QPixmap:
        pix = QPixmap(80, 14)
        pix.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pix)
        w = 80 // len(colors)
        for i, c in enumerate(colors):
            painter.fillRect(i * w, 0, w, 14, QColor(c))
        painter.end()
        return pix

    def _item_year(self, item: QListWidgetItem) -> int:
        val = item.data(_enum(Qt, "ItemDataRole", "UserRole"))
        if val is not None:
            return int(val)
        return int(str(item.text()).split()[0])

    def _set_checked_years(self, years: List[int]) -> None:
        year_set = set(years)
        enabled_flag = _enum(Qt, "ItemFlag", "ItemIsEnabled")
        checked = _enum(Qt, "CheckState", "Checked")
        unchecked = _enum(Qt, "CheckState", "Unchecked")
        for i in range(self.list_years.count()):
            item = self.list_years.item(i)
            yr = self._item_year(item)
            if (item.flags() & enabled_flag) and yr in year_set:
                item.setCheckState(checked)
            else:
                item.setCheckState(unchecked)

    def _get_selected_years(self) -> List[int]:
        res = []
        enabled_flag = _enum(Qt, "ItemFlag", "ItemIsEnabled")
        checked = _enum(Qt, "CheckState", "Checked")
        for i in range(self.list_years.count()):
            item = self.list_years.item(i)
            if (item.flags() & enabled_flag) and item.checkState() == checked:
                res.append(self._item_year(item))
        return sorted(res)

    def _get_current_survey(self) -> Dict[str, Any]:
        survey_id = self.cmb_survey.currentData()
        return get_survey_by_id(survey_id) or SURVEYS[0]

    def _select_preset_years(self, mode: str) -> None:
        survey = self._get_current_survey()
        var_id = self.cmb_variable.currentData()
        is_subannual = survey.get("periodicity") in ("quarterly", "monthly", "semiannual")
        valid_years = get_survey_valid_years(survey, None, variable_id=var_id)
        if not valid_years:
            return

        annual_pool = [y for y in valid_years if y <= 9999] if is_subannual else valid_years

        if mode == "latest":
            self._set_checked_years([valid_years[0]])
        elif mode == "last3":
            self._set_checked_years((annual_pool or valid_years)[:3])
        elif mode == "last5":
            self._set_checked_years((annual_pool or valid_years)[:5])
        elif mode == "all":
            self._set_checked_years(valid_years)
        elif mode == "2022":
            if 2022 in valid_years:
                self._set_checked_years([2022])
            elif is_subannual:
                q2022 = [y for y in valid_years if 202200 <= y <= 202299]
                if q2022:
                    self._set_checked_years(q2022)
                    return
                QMessageBox.information(
                    self,
                    "Ano indisponível",
                    f"O ano 2022 não está disponível para a pesquisa selecionada:\n{survey.get('name', 'Pesquisa')}",
                )
            else:
                QMessageBox.information(
                    self,
                    "Ano indisponível",
                    f"O ano 2022 não está disponível para a pesquisa selecionada:\n{survey.get('name', 'Pesquisa')}",
                )

    def _update_years_availability(
        self,
        survey: Dict[str, Any],
        var_id: Optional[int],
        force_default: bool = False,
    ) -> None:
        is_subannual = survey.get("periodicity") in ("quarterly", "monthly", "semiannual")
        valid_years = get_survey_valid_years(survey, None, variable_id=var_id)
        valid_set = set(valid_years)
        prev_checked = self._get_selected_years()

        if is_subannual:
            desired_ids = valid_years
        else:
            floor_year = min([2001] + [y for y in valid_years if y <= 9999])
            desired_ids = list(range(2026, floor_year - 1, -1))
        current_ids = [self._item_year(self.list_years.item(i)) for i in range(self.list_years.count())]

        enabled_flag = _enum(Qt, "ItemFlag", "ItemIsEnabled")
        checkable_flag = _enum(Qt, "ItemFlag", "ItemIsUserCheckable")
        unchecked = _enum(Qt, "CheckState", "Unchecked")
        user_role = _enum(Qt, "ItemDataRole", "UserRole")

        if current_ids != desired_ids:
            self.list_years.clear()
            for yr in desired_ids:
                item = QListWidgetItem(str(yr))
                item.setData(user_role, yr)
                item.setFlags(item.flags() | checkable_flag)
                item.setCheckState(unchecked)
                self.list_years.addItem(item)

        for i in range(self.list_years.count()):
            item = self.list_years.item(i)
            yr = self._item_year(item)
            if yr in valid_set:
                item.setText(get_survey_year_label(survey, yr, variable_id=var_id))
                item.setFlags(item.flags() | enabled_flag | checkable_flag)
                fnt = item.font()
                fnt.setBold(is_subannual and yr <= 9999)
                item.setFont(fnt)
            else:
                item.setText(f"{yr} (indisponível nesta tabela)")
                item.setCheckState(unchecked)
                item.setFlags((item.flags() | checkable_flag) & ~enabled_flag)

        kept = [y for y in prev_checked if y in valid_set]
        if force_default or not kept:
            defaults = [y for y in survey.get("default_years", []) if y in valid_set]
            target = defaults or (valid_years[:1] if valid_years else [])
        else:
            target = kept

        self._set_checked_years(target)

    def _update_survey_notice(self, survey: Dict[str, Any]) -> None:
        title = (survey.get("notice_title") or "").strip()
        text = (survey.get("notice_text") or "").strip()
        severity = (survey.get("notice_severity") or "info").lower()

        if not title and not text:
            self.frame_notice.setVisible(False)
            return

        if severity == "caution":
            bg, border, title_col, text_col, prefix = "#fef2f2", "#dc2626", "#991b1b", "#7f1d1d", "PONTO DE ATENÇÃO: "
        elif severity == "warning":
            bg, border, title_col, text_col, prefix = "#fffbeb", "#d97706", "#92400e", "#78350f", "AVISO DA TABELA: "
        else:
            bg, border, title_col, text_col, prefix = "#f0f9ff", "#0284c7", "#0c4a6e", "#075985", "NOTA METODOLÓGICA: "

        self.frame_notice.setStyleSheet(
            f"#noticeBanner {{ background-color: {bg}; border: 1px solid {border}; "
            f"border-left: 4px solid {border}; border-radius: 4px; }}"
        )
        self.lbl_notice_title.setStyleSheet(f"color: {title_col}; font-weight: bold; font-size: 11px;")
        self.lbl_notice.setStyleSheet(f"color: {text_col}; font-size: 11px;")
        self.lbl_notice_title.setText(f"{prefix}{title}" if title else prefix.rstrip(": "))
        self.lbl_notice.setText(text)
        self.frame_notice.setVisible(True)

    def _populate_initial_data(self) -> None:
        self._suppress_survey_popup = True
        try:
            self._on_group_changed(0)
        finally:
            self._suppress_survey_popup = False

    @staticmethod
    def _normalize_search_text(text: str) -> str:
        """Remove acentos e converte texto para minúsculas na busca de pesquisas."""
        nfkd = unicodedata.normalize("NFKD", text or "")
        return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()

    def _populate_surveys_combo(self, preserve_id: Optional[str] = None) -> None:
        group_id = self.cmb_group.currentData() or "ALL"
        pool = SURVEYS if group_id == "ALL" else [s for s in SURVEYS if s.get("group") == group_id]
        if not pool:
            pool = SURVEYS

        q = self._normalize_search_text(self.txt_filter_survey.text())
        if q:
            terms = [t for t in q.split() if t]
            filtered = []
            for s in pool:
                tbls = [str(s.get("table", ""))] + [
                    str(seg.get("table", "")) for seg in (s.get("table_series") or [])
                ]
                haystack = self._normalize_search_text(
                    f"{s['name']} {s['id']} {' '.join(tbls)}"
                )
                if all(t in haystack for t in terms):
                    filtered.append(s)
        else:
            filtered = pool

        self.cmb_survey.blockSignals(True)
        self.cmb_survey.clear()
        if not filtered:
            self.cmb_survey.addItem("Nenhuma pesquisa encontrada para o filtro informado", None)
            self.cmb_survey.setCurrentIndex(0)
            self.cmb_survey.blockSignals(False)
            self.btn_execute.setEnabled(False)
            return

        self.btn_execute.setEnabled(True)
        for s in filtered:
            self.cmb_survey.addItem(s["name"], s["id"])
        target_idx = 0
        if preserve_id:
            idx_prev = self.cmb_survey.findData(preserve_id)
            if idx_prev >= 0:
                target_idx = idx_prev
        self.cmb_survey.setCurrentIndex(target_idx)
        self.cmb_survey.blockSignals(False)
        self._on_survey_changed(target_idx)

    def _on_group_changed(self, index: int) -> None:
        if self.txt_filter_survey.text():
            self.txt_filter_survey.blockSignals(True)
            self.txt_filter_survey.clear()
            self.txt_filter_survey.blockSignals(False)
        self._populate_surveys_combo(preserve_id=None)

    def _on_survey_filter_changed(self) -> None:
        prev_suppress = self._suppress_survey_popup
        self._suppress_survey_popup = True
        try:
            self._populate_surveys_combo(preserve_id=self.cmb_survey.currentData())
        finally:
            self._suppress_survey_popup = prev_suppress

    def _rebuild_extra_classifications(self, survey: Dict[str, Any]) -> None:
        while self.form_extra_clfs.rowCount() > 0:
            self.form_extra_clfs.removeRow(0)
        self._extra_clf_combos = []

        specs = get_survey_extra_classifications(survey)
        if not specs:
            self.pnl_extra_clfs.setVisible(False)
            return

        for spec in specs:
            cmb = QComboBox()
            for cid_val, cname in spec["categories"]:
                cmb.addItem(cname, cid_val)
            def_idx = cmb.findData(spec["default"])
            if def_idx >= 0:
                cmb.setCurrentIndex(def_idx)
            short_name = spec["name"]
            if len(short_name) > 48:
                short_name = short_name[:45] + "..."
            lbl = QLabel(f"Subfiltro ({short_name}):")
            lbl.setToolTip(spec["name"])
            self.form_extra_clfs.addRow(lbl, cmb)
            self._extra_clf_combos.append((spec["id"], spec["name"], cmb, spec["default"]))

        self.pnl_extra_clfs.setVisible(True)

    def _update_territory_for_level(self, survey: Dict[str, Any], level: str) -> None:
        policy = {
            "N1": (False, "Pesquisa disponível apenas em nível nacional (Brasil - N1)."),
            "N2": (False, "Grandes Regiões (N2): exibe as 5 macrorregiões do Brasil (fixado em BR)."),
            "N14": (False, "RIDE - Grande Teresina (N14): abrangência interestadual PI/MA (fixado em BR)."),
            "N7_N14": (False, "Regiões Metropolitanas + RIDE Grande Teresina (N7 + N14): exibe todas as 21 áreas (fixado em BR)."),
            "N7_N6": (False, "Recorte combinado RMs + Capitais Isoladas (N7 + N6, ex.: IPCA/INPC): fixado em BR."),
            "N3": (True, "Unidades da Federação (Estados - N3). Selecione BR para todas as UFs ou filtre uma UF."),
            "N8": (True, "Mesorregiões Geográficas (N8). Selecione BR para todo o país ou filtre uma UF."),
            "N9": (True, "Microrregiões Geográficas (N9). Selecione BR para todo o país ou filtre uma UF."),
            "N7": (True, "Regiões Metropolitanas (N7 - 20 RMs oficiais). Recomenda-se BR; UFs sem RM retornam erro no SIDRA."),
        }
        if level in policy:
            enabled, tooltip = policy[level]
        elif survey.get("partial_n6"):
            enabled = True
            tooltip = (
                "Nível municipal (N6) restrito aos municípios pesquisados "
                "(ex.: capitais estaduais na PNAD/IPCA). Selecione BR ou uma UF."
            )
        else:
            enabled = True
            tooltip = "Pesquisa em nível municipal (N6). Selecione BR ou uma UF específica."

        self.cmb_territory.setEnabled(enabled)
        if not enabled:
            self.cmb_territory.setCurrentIndex(0)  # Brasil
        self.cmb_territory.setToolTip(tooltip)

    def _on_level_changed(self, _index: int) -> None:
        if self.cmb_survey.currentData() is None:
            return
        current_survey = self._get_current_survey()
        selected_level = self.cmb_level.currentData() or current_survey.get("level", "N6")
        self._update_territory_for_level(current_survey, selected_level)

    def _on_survey_changed(self, index: int) -> None:
        if self.cmb_survey.currentData() is None:
            return
        current_survey = self._get_current_survey()
        survey_id = current_survey.get("id", "")

        self.cmb_variable.blockSignals(True)
        self.cmb_variable.clear()
        default_var = current_survey.get("default_var")
        selected_idx = 0
        for idx, v in enumerate(current_survey.get("variables", [])):
            self.cmb_variable.addItem(f"{v['name']} ({v['unit']})", v["id"])
            if default_var is not None and v["id"] == default_var:
                selected_idx = idx
        self.cmb_variable.setCurrentIndex(selected_idx)
        self.cmb_variable.blockSignals(False)

        var_id = self.cmb_variable.currentData()

        supported_levels = get_survey_supported_levels(current_survey)
        default_level = current_survey.get("level", "N6")
        self.cmb_level.blockSignals(True)
        self.cmb_level.clear()
        level_idx = 0
        for idx, lvl in enumerate(supported_levels):
            self.cmb_level.addItem(TERRITORIAL_LEVEL_LABELS.get(lvl, lvl), lvl)
            if lvl == default_level:
                level_idx = idx
        self.cmb_level.setCurrentIndex(level_idx)
        self.cmb_level.blockSignals(False)

        selected_level = self.cmb_level.currentData() or default_level
        self._update_territory_for_level(current_survey, selected_level)

        is_subannual = current_survey.get("periodicity") in ("quarterly", "monthly", "semiannual")
        new_valid = get_survey_valid_years(current_survey, None, variable_id=var_id)
        is_single = len(new_valid) == 1
        has_pre2001 = any(y < 2001 for y in new_valid if y <= 9999)
        force_default = (
            self._prev_single_year_survey
            or self._prev_subannual_survey
            or is_single
            or is_subannual
            or has_pre2001
            or bool(current_survey.get("valid_years"))
        )
        self._prev_single_year_survey = is_single
        self._prev_subannual_survey = is_subannual
        self._update_years_availability(current_survey, var_id, force_default=force_default)

        self.txt_filter_prod.blockSignals(True)
        self.txt_filter_prod.clear()
        self.txt_filter_prod.blockSignals(False)
        self._refresh_products_list()
        self._rebuild_extra_classifications(current_survey)
        self._update_survey_notice(current_survey)

        if (
            not self._suppress_survey_popup
            and current_survey.get("popup_notice")
            and survey_id not in self._warned_surveys
        ):
            self._warned_surveys.add(survey_id)
            QMessageBox.warning(
                self,
                current_survey.get("notice_title") or "Aviso sobre a tabela selecionada",
                current_survey.get("notice_text") or "Esta tabela possui restrições de recorte ou série histórica.",
            )

    def _on_variable_changed(self, index: int) -> None:
        current_survey = self._get_current_survey()
        var_id = self.cmb_variable.currentData()
        self._update_years_availability(current_survey, var_id, force_default=False)

    def _refresh_products_list(self) -> None:
        current_survey = self._get_current_survey()
        cats = get_survey_categories(current_survey)
        filter_txt = self.txt_filter_prod.text().strip().lower()

        self.cmb_product.clear()
        matches = [
            (cid, cname)
            for cid, cname in cats
            if not filter_txt or filter_txt in str(cname).lower() or filter_txt == str(cid)
        ]

        limit = 500 if not filter_txt else 1500
        for cid, cname in matches[:limit]:
            self.cmb_product.addItem(cname, cid)

        default_cat = current_survey.get("default_cat")
        if not filter_txt and default_cat is not None:
            idx_def = self.cmb_product.findData(default_cat)
            if idx_def >= 0:
                self.cmb_product.setCurrentIndex(idx_def)

        has_many = len(cats) > 1
        self.txt_filter_prod.setEnabled(has_many)
        if not has_many:
            self.txt_filter_prod.setPlaceholderText("Esta tabela utiliza categoria única (Total).")
        elif len(matches) > limit and not filter_txt:
            self.txt_filter_prod.setPlaceholderText(
                f"Exibindo {limit} de {len(cats)} categorias. Digite aqui para filtrar todas..."
            )
        else:
            self.txt_filter_prod.setPlaceholderText(
                "Digite para filtrar (ex: Soja, Tilápia, Comércio, Renda, Plano Diretor, Religião)..."
            )

    def _filter_products_dropdown(self) -> None:
        self._refresh_products_list()

    # --------------------------------------------------------------------------
    # EXECUÇÃO DE CONSULTA SIDRA E CRIAÇÃO DE CAMADA
    # --------------------------------------------------------------------------
    def _run_sidra_query_and_layer(self) -> None:
        if self.cmb_survey.currentData() is None:
            QMessageBox.warning(self, "Aviso", "Selecione uma pesquisa válida antes de executar a consulta.")
            return

        years = self._get_selected_years()
        if not years:
            QMessageBox.warning(self, "Aviso", "Selecione pelo menos um ano ou período de referência disponível na tabela.")
            return

        current_survey = self._get_current_survey()
        survey_id = current_survey["id"]
        variable_id = self.cmb_variable.currentData()
        var_info = get_variable_info(survey_id, variable_id) or {}
        var_slug = get_variable_slug(survey_id, variable_id)
        category = self.cmb_product.currentData()

        table_plans, skipped_years = resolve_table_queries(
            current_survey, years, variable_id, category_id=category
        )
        if not table_plans:
            valid_years = get_survey_valid_years(current_survey, None, variable_id=variable_id)
            valid_preview = ", ".join(str(y) for y in valid_years[:8])
            QMessageBox.warning(
                self,
                "Anos indisponíveis",
                f"Nenhum dos anos selecionados ({years}) está disponível para a tabela/variável escolhida.\n\n"
                f"Anos válidos disponíveis: {valid_preview}"
                + (" ..." if len(valid_years) > 8 else ""),
            )
            return

        if skipped_years:
            self._log(
                f"AVISO: Anos ignorados por não existirem na tabela/variável selecionada: {skipped_years}"
            )

        classification = current_survey.get("classification")
        extra_classifications = dict(current_survey.get("extra_classifications") or {})
        active_sublabels: List[str] = []
        for cid, _cname, cmb, def_val in self._extra_clf_combos:
            sel_val = cmb.currentData()
            if sel_val is not None:
                extra_classifications[int(cid)] = int(sel_val)
                if int(sel_val) != int(def_val):
                    active_sublabels.append(cmb.currentText())
        if not extra_classifications:
            extra_classifications = None

        prod_label = self.cmb_product.currentText()
        if active_sublabels:
            prod_label = f"{prod_label} | {' | '.join(active_sublabels)}"
        territory = self.cmb_territory.currentData()
        scheme = self.cmb_palette.currentData()
        level = self.cmb_level.currentData() or current_survey.get("level", "N6")
        partial_sample = (level in ("N7", "N14", "N7_N14", "N7_N6")) or (
            level == "N6" and bool(current_survey.get("partial_n6"))
        )
        capital_codes = current_survey.get("capital_codes")
        agg_mode = var_info.get("agg_mode", "sum")
        allow_negative = bool(var_info.get("allow_negative", False))
        is_binary = bool(var_info.get("is_binary", False))

        is_circles = (self.cmb_symb.currentData() == "circles")
        create_base = self.chk_base_poly.isChecked()
        zoom_layer = self.chk_zoom_layer.isChecked()
        tables_desc = ", ".join(f"{p.get('table', '')} ({p.get('years', [])})" for p in table_plans)

        survey_name_label = current_survey.get("name", survey_id)
        self._log(f"--- Iniciando consulta SIDRA: {survey_name_label} ---")
        self._log(f"Tabela(s): {tables_desc} | Nível: {level} | Território: {territory} | Categoria: {prod_label}")
        self._log(f"Variável: {variable_id} ({var_info.get('name', var_slug)}) | Modo: {agg_mode}")

        self.btn_execute.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setValue(5)
        self.lbl_status.setText("Consultando API SIDRA do IBGE...")

        def _worker_task(report: Callable[[int, str], None]):
            report(10, f"Consultando API SIDRA/IBGE ({level})...")
            raw_data = self.sidra_client.query_series(
                table_plans=table_plans,
                territory=territory,
                level=level,
                classification=classification,
                category=category,
                extra_classifications=extra_classifications,
                progress_callback=report,
            )

            report(60, "Processando e estruturando registros...")
            parsed = self.sidra_client.parse_records(
                raw_data,
                primary_var=variable_id,
                agg_mode=agg_mode,
                allow_negative=allow_negative,
            )
            parsed["product_name"] = prod_label
            parsed["level"] = level
            parsed["partial_sample"] = partial_sample
            parsed["survey_id"] = survey_id
            parsed["survey_name"] = current_survey.get("name", survey_id)
            parsed["agg_mode"] = agg_mode
            parsed["allow_negative"] = allow_negative
            parsed["is_binary"] = is_binary
            if not parsed.get("variable_name") and var_info.get("name"):
                parsed["variable_name"] = var_info["name"]
            if not parsed.get("unit") and var_info.get("unit"):
                parsed["unit"] = var_info["unit"]

            report(80, "Obtendo malha vetorial oficial do IBGE...")
            malhas_client = IbgeMalhasClient()
            geojson_path = malhas_client.fetch_geojson_for_level(
                level=level,
                territory=territory,
                capital_codes=capital_codes,
                progress_callback=report,
            )
            base_geojson_path = None
            if create_base and partial_sample:
                base_geojson_path = malhas_client.fetch_states_geojson(progress_callback=report)

            report(95, "Criando camadas vetoriais no QGIS...")
            return {
                "parsed": parsed,
                "geojson_path": geojson_path,
                "base_geojson_path": base_geojson_path,
                "territory": territory,
                "level": level,
                "partial_sample": partial_sample,
                "is_circles": is_circles,
                "create_base": create_base,
                "scheme": scheme,
                "zoom_layer": zoom_layer,
                "prod_label": prod_label,
                "var_slug": var_slug,
                "allow_negative": allow_negative,
                "is_binary": is_binary,
            }

        self.active_job = BackgroundJob(_worker_task)
        self.active_job.progress.connect(self._on_job_progress)
        self.active_job.succeeded.connect(self._on_sidra_job_succeeded)
        self.active_job.failed.connect(self._on_job_failed)
        self.active_job.cancelled.connect(self._on_job_cancelled)
        self.active_job.start()

    def _on_job_progress(self, pct: int, msg: str) -> None:
        self.progress_bar.setValue(pct)
        self.lbl_status.setText(msg)
        self._log(f"[{pct}%] {msg}")

    def _on_job_cancelled(self) -> None:
        self.btn_execute.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.progress_bar.setValue(0)
        self.lbl_status.setText("Tarefa cancelada.")
        self._log("Tarefa cancelada pelo usuário.")

    def _on_job_failed(self, err_msg: str) -> None:
        self.btn_execute.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.progress_bar.setValue(0)
        self.lbl_status.setText("Erro na execução.")
        self._log(f"ERRO: {err_msg}")
        QMessageBox.critical(self, "Erro no GeoSIDRA", f"Falha ao executar consulta: {err_msg}")

    def _cancel_active_job(self) -> None:
        if self.active_job:
            self.active_job.request_cancel()
            self.lbl_status.setText("Cancelando...")

    def _on_sidra_job_succeeded(self, result: Dict) -> None:
        self.btn_execute.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.progress_bar.setValue(100)
        self.lbl_status.setText("Camada criada com sucesso!")

        parsed = result["parsed"]
        self.last_parsed_data = parsed
        geojson_path = result["geojson_path"]
        territory = result["territory"]
        level = result["level"]
        scheme = result["scheme"]
        prod_label = result["prod_label"]
        var_slug = result.get("var_slug", "indicador")
        unit = parsed.get("unit", "")

        poly_layer_name = f"GeoSIDRA [{level}] - {prod_label[:28]} - {var_slug} ({territory})"
        poly_layer = GeoSidraLayerBuilder.build_polygon_layer(
            parsed_data=parsed,
            layer_name=poly_layer_name,
            territory=territory,
            level=level,
            geojson_path=geojson_path,
        )

        project = QgsProject.instance()

        base_geojson_path = result.get("base_geojson_path")
        if base_geojson_path and result.get("create_base"):
            ctx_layer = QgsVectorLayer(
                base_geojson_path,
                f"GeoSIDRA [Contexto UF] - Estados ({territory})",
                "ogr",
            )
            if ctx_layer.isValid():
                GeoSidraLayerBuilder.apply_base_polygon(ctx_layer)
                project.addMapLayer(ctx_layer)

        is_circles = result["is_circles"]
        allow_negative = bool(result.get("allow_negative", parsed.get("allow_negative", False)))
        is_binary = bool(result.get("is_binary", parsed.get("is_binary", False)))

        if is_circles:
            if result["create_base"]:
                base_layer_name = f"GeoSIDRA [Base] - {prod_label[:28]} ({territory})"
                poly_layer.setName(base_layer_name)
                GeoSidraLayerBuilder.apply_base_polygon(poly_layer)
                project.addMapLayer(poly_layer)

            pt_layer_name = f"GeoSIDRA [Círculos] - {prod_label[:28]} - {var_slug} ({territory})"
            pt_layer = GeoSidraLayerBuilder.build_centroid_points(
                poly_layer=poly_layer,
                field_name="VALOR_PRINC",
                layer_name=pt_layer_name,
                allow_negative=allow_negative,
            )
            GeoSidraLayerBuilder.apply_proportional_circles(
                pt_layer=pt_layer,
                field_name="VALOR_PRINC",
                scheme=scheme,
                unit=unit,
                allow_negative=allow_negative,
            )
            project.addMapLayer(pt_layer)
            target_layer = pt_layer
        else:
            GeoSidraLayerBuilder.apply_graduated(
                layer=poly_layer,
                field_name="VALOR_PRINC",
                scheme=scheme,
                unit=unit,
                allow_negative=allow_negative,
                is_binary=is_binary,
            )
            project.addMapLayer(poly_layer)
            target_layer = poly_layer

        if result["zoom_layer"] and self.iface:
            self.iface.setActiveLayer(target_layer)
            self.iface.zoomToActiveLayer()

        agg_mode = (parsed.get("agg_mode") or "sum").lower()
        n_units = len(parsed.get("top_producers", []))
        self._log(f"Camada adicionada ao QGIS com sucesso: {target_layer.name()}")
        if is_binary:
            self._log(
                f"Indicador binário municipal: {parsed.get('total', 0):,.0f} municípios com registro 'Sim (= 1)' "
                f"({n_units} unidades cadastradas)."
            )
        elif agg_mode == "mean" or allow_negative:
            self._log(
                f"Média apurada entre unidades territoriais: {parsed.get('mean_value', 0.0):,.2f} {unit} "
                f"({n_units} unidades territoriais)."
            )
        else:
            self._log(f"Total apurado: {parsed.get('total', 0):,.1f} {unit} ({n_units} unidades territoriais).")

        self._populate_reports_tab(parsed, territory_label=territory)

    # --------------------------------------------------------------------------
    # GERAÇÃO DE RELATÓRIOS E PRÉ-VISUALIZAÇÃO (ABA 3)
    # --------------------------------------------------------------------------
    def _populate_reports_tab(self, parsed: Dict, territory_label: str) -> None:
        self.last_reports = AnalyticsEngine.generate_all_reports(parsed, territory_label=territory_label)
        self.cmb_report.clear()
        for idx, bundle in enumerate(self.last_reports):
            self.cmb_report.addItem(f"[{bundle.category}] {bundle.title}", idx)

        if self.last_reports:
            self.cmb_report.setCurrentIndex(0)
            self._render_current_preview()

    def _on_report_selected(self, index: int) -> None:
        if index < 0 or index >= len(self.last_reports):
            return
        bundle = self.last_reports[index]
        self.current_preview_bundle = bundle
        self.txt_custom_title.setText(bundle.title)
        self.txt_custom_subtitle.setText(bundle.subtitle)
        self._render_current_preview()

    def _restore_default_report_title(self) -> None:
        if self.current_preview_bundle:
            self.txt_custom_title.setText(self.current_preview_bundle.title)
            self.txt_custom_subtitle.setText(self.current_preview_bundle.subtitle)
            self._render_current_preview()

    def _render_current_preview(self) -> None:
        idx = self.cmb_report.currentIndex()
        if idx < 0 or idx >= len(self.last_reports):
            return

        bundle = self.last_reports[idx]
        out_dir = self.txt_out_dir.text().strip() or os.path.join(os.path.expanduser("~"), "GeoSIDRA_Relatorios")
        title = self.txt_custom_title.text().strip() or bundle.title
        subtitle = self.txt_custom_subtitle.text().strip() or bundle.subtitle

        png_path = export_bundle(bundle, out_dir=out_dir, custom_title=title, custom_subtitle=subtitle, dpi=180)
        self.last_rendered_png = png_path

        if os.path.exists(png_path):
            pix = QPixmap(png_path)
            target_w = max(400, self.prev_scroll.viewport().width() - 20)
            scaled = pix.scaledToWidth(target_w, _enum(Qt, "TransformationMode", "SmoothTransformation"))
            self.lbl_preview_img.setPixmap(scaled)
            self.btn_open_full.setEnabled(True)

    def _open_preview_image_external(self) -> None:
        if self.last_rendered_png and os.path.exists(self.last_rendered_png):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.last_rendered_png))

    def _browse_out_dir(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Exportação", self.txt_out_dir.text())
        if d:
            self.txt_out_dir.setText(d)

    def _open_out_dir(self) -> None:
        d = self.txt_out_dir.text().strip()
        if not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(d))

    def _generate_selected_report(self) -> None:
        idx = self.cmb_report.currentIndex()
        if idx < 0 or idx >= len(self.last_reports):
            QMessageBox.warning(self, "Aviso", "Nenhum relatório selecionado.")
            return

        bundle = self.last_reports[idx]
        out_dir = self.txt_out_dir.text().strip()
        title = self.txt_custom_title.text().strip() or bundle.title
        subtitle = self.txt_custom_subtitle.text().strip() or bundle.subtitle

        png_path = export_bundle(bundle, out_dir=out_dir, custom_title=title, custom_subtitle=subtitle, dpi=300)
        if bundle.table_spec:
            csv_path = os.path.join(out_dir, f"{bundle.report_id}.csv")
            export_table_csv(bundle.table_spec, csv_path)

        self._render_current_preview()
        QMessageBox.information(self, "Sucesso", f"Relatório gerado em alta resolução (300 DPI) em:\n{png_path}")
