# -*- coding: utf-8 -*-
"""
Catálogo completo de pesquisas, tabelas, variáveis e classificações do SIDRA/IBGE.
Inclui pesquisas oficiais curadas organizadas em 12 áreas temáticas com múltiplos níveis
territoriais suportados (N6 Municípios, N9 Microrregiões, N8 Mesorregiões, N7 RMs,
N14 RIDE, N7+N6 Inflação Regional, N3 UFs, N2 Grandes Regiões e N1 Brasil).
"""

import json
import os
import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

from .phase2_categories import PHASE2_STATIC_CATEGORIES
from .phase3_categories import PHASE3_STATIC_CATEGORIES
from .phase3_surveys import build_phase3_surveys
from .phase4_categories import PHASE4_STATIC_CATEGORIES
from .phase4_surveys import build_phase4_surveys
from .phase5_categories import PHASE5_STATIC_CATEGORIES
from .phase5_surveys import build_phase5_surveys
from .phase6_categories import PHASE6_STATIC_CATEGORIES
from .phase6_surveys import build_phase6_surveys
from .phase7_categories import PHASE7_STATIC_CATEGORIES
from .phase7_surveys import build_phase7_surveys
from .phase8_categories import PHASE8_STATIC_CATEGORIES
from .phase8_surveys import build_phase8_surveys
from .phase9_categories import PHASE9_STATIC_CATEGORIES
from .phase9_surveys import build_phase9_surveys
from .phase10_categories import PHASE10_STATIC_CATEGORIES
from .phase10_surveys import build_phase10_surveys
from .phase11_categories import PHASE11_STATIC_CATEGORIES
from .phase11_surveys import build_phase11_surveys
from .phase12_categories import PHASE12_STATIC_CATEGORIES
from .phase12_surveys import build_phase12_surveys
from .phase13_categories import PHASE13_STATIC_CATEGORIES
from .phase13_surveys import build_phase13_surveys
from .phase14_categories import PHASE14_STATIC_CATEGORIES
from .phase14_surveys import build_phase14_surveys


def _build_quarterly_periods(
    years: List[int],
    latest_year: int = 2026,
    latest_quarter: int = 2,
    missing_quarters: Optional[set] = None,
) -> Tuple[List[int], Dict[int, Any], Dict[int, str]]:
    """
    Constrói códigos, mapeamentos e rótulos para pesquisas trimestrais:
      - Para anos completos (4 trimestres disponíveis): inclui o código anual `YYYY`
        mapeado para `['YYYY01', 'YYYY02', 'YYYY03', 'YYYY04']` (Total/Consolidado Anual)
        seguido pelos 4 trimestres individuais em ordem decrescente (`4T`..`1T`).
      - Para anos parciais (como 2026 até 2T ou anos com lacunas): inclui somente
        os trimestres publicados em ordem decrescente.
    """
    missing = missing_quarters or set()
    valid_periods: List[int] = []
    pmap: Dict[int, Any] = {}
    plabels: Dict[int, str] = {}

    for y in sorted(set(years), reverse=True):
        max_q = latest_quarter if y == latest_year else 4
        qs_avail = [q for q in range(1, max_q + 1) if f"{y}0{q}" not in missing]
        if not qs_avail:
            continue

        if len(qs_avail) == 4:
            valid_periods.append(y)
            pmap[y] = [f"{y}0{q}" for q in qs_avail]
            plabels[y] = f"{y} - Consolidado Anual (1T a 4T)"

        for q in reversed(qs_avail):
            code_str = f"{y}0{q}"
            code_int = int(code_str)
            valid_periods.append(code_int)
            pmap[code_int] = code_str
            plabels[code_int] = f"{q}º Trimestre / {y} ({code_str})"

    return valid_periods, pmap, plabels


def _build_monthly_periods(
    start_year: int = 2006,
    start_month: int = 1,
    end_year: int = 2026,
    end_month: int = 9,
    latest_suffix: str = "",
) -> Tuple[List[int], Dict[int, str], Dict[int, str]]:
    """
    Constrói períodos válidos, mapa e rótulos mensais/anuais do SIDRA:
      - Para anos encerrados: código anual YYYY mapeado ao fechamento de dezembro (YYYY12),
        seguido pelos meses individuais (Nov..Jan ou Nov..start_month no ano inicial).
      - Para o ano em curso (end_month < 12): meses individuais publicados (end_month..start_month).
    """
    months_pt = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
    }
    valid_periods: List[int] = []
    pmap: Dict[int, str] = {}
    plabels: Dict[int, str] = {}

    for y in range(end_year, start_year - 1, -1):
        min_m = start_month if y == start_year else 1
        if y == end_year and end_month < 12:
            for m in range(end_month, min_m - 1, -1):
                code_str = f"{y}{m:02d}"
                code_int = int(code_str)
                valid_periods.append(code_int)
                pmap[code_int] = code_str
                suffix = latest_suffix if (y == end_year and m == end_month) else ""
                plabels[code_int] = f"{months_pt[m]} / {y} ({code_str}{suffix})"
        else:
            valid_periods.append(y)
            pmap[y] = f"{y}12"
            plabels[y] = f"{y} - Fechamento Anual (Dez/{y})"
            for m in range(11, min_m - 1, -1):
                code_str = f"{y}{m:02d}"
                code_int = int(code_str)
                valid_periods.append(code_int)
                pmap[code_int] = code_str
                plabels[code_int] = f"{months_pt[m]} / {y} ({code_str})"

    return valid_periods, pmap, plabels


def _build_lspa_periods(
    start_year: int = 2006,
    end_year: int = 2026,
    end_month: int = 9,
) -> Tuple[List[int], Dict[int, str], Dict[int, str]]:
    """
    Constrói períodos válidos, mapa e rótulos mensais/anuais do LSPA (Tabela 6588):
      - Para anos encerrados (2006..2025): código anual YYYY mapeado ao fechamento
        de dezembro (YYYY12), seguido pelos meses individuais (Nov..Jan, ou Set..Nov em 2006).
      - Para 2026 (safra em acompanhamento): meses individuais publicados (Set/2026..Jan/2026).
    """
    return _build_monthly_periods(
        start_year=start_year,
        start_month=9,
        end_year=end_year,
        end_month=end_month,
        latest_suffix=" - Previsão Atual",
    )


def _build_semiannual_periods(
    start_year: int = 2007,
    start_semester: int = 2,
    end_year: int = 2025,
    end_semester: int = 2,
) -> Tuple[List[int], Dict[int, str], Dict[int, str]]:
    """
    Constrói períodos semestrais válidos, mapa e rótulos para a Pesquisa de Estoques:
      - Para anos com 2º semestre publicado: código YYYY mapeado para YYYY02 (fechamento anual).
      - Para anos com 1º semestre publicado: código YYYY01 mapeado para YYYY01.
    """
    valid_periods: List[int] = []
    pmap: Dict[int, str] = {}
    plabels: Dict[int, str] = {}

    for y in range(end_year, start_year - 1, -1):
        min_s = start_semester if y == start_year else 1
        max_s = end_semester if y == end_year else 2
        if max_s >= 2:
            valid_periods.append(y)
            pmap[y] = f"{y}02"
            plabels[y] = f"{y} - Fechamento Anual (2º Semestre / {y}02)"
        if min_s <= 1:
            code_str = f"{y}01"
            code_int = int(code_str)
            valid_periods.append(code_int)
            pmap[code_int] = code_str
            plabels[code_int] = f"1º Semestre / {y} ({code_str})"

    return valid_periods, pmap, plabels


_LSPA_VALID_PERIODS, _LSPA_PERIOD_MAP, _LSPA_PERIOD_LABELS = _build_lspa_periods(2006, 2026, 9)
_QUARTERLY_2001_2026_VALID, _QUARTERLY_2001_2026_MAP, _QUARTERLY_2001_2026_LABELS = _build_quarterly_periods(
    list(range(2001, 2027)), latest_year=2026, latest_quarter=2
)
_PNAD_DES_VALID, _PNAD_DES_MAP, _PNAD_DES_LABELS = _build_quarterly_periods(
    list(range(2012, 2027)), latest_year=2026, latest_quarter=2
)
_PNAD_REND_MISSING = {
    "202002", "202003", "202004",
    "202101", "202102", "202103", "202104",
    "202201",
}
_PNAD_REND_VALID_YEARS, _PNAD_REND_MAP, _PNAD_REND_LABELS = _build_quarterly_periods(
    list(range(2012, 2027)),
    latest_year=2026,
    latest_quarter=2,
    missing_quarters=_PNAD_REND_MISSING,
)

SURVEY_GROUPS = [
    ("ALL", "Todas as áreas temáticas"),
    ("AGRO_VEGETAL", "Agropecuária, Lavouras, Safras e Censo Agro (PAM / LSPA / Censo Agro)"),
    ("PECUARIA_AQUI", "Pecuária, Abate Trimestral, Couro e Aquicultura (PPM / Leite / Ovos)"),
    ("FLORESTAL", "Silvicultura e Extração Vegetal (PEVS)"),
    ("ECONOMIA_EMPRESAS", "Economia, Indústria, Comércio, Serviços e MEIs (PIB, CEMPRE, PIA, PAC, PAS)"),
    ("SISTEMA_FINANCEIRO_CREDITO", "Sistema Financeiro, Bancarização e Crédito (BACEN / ESTBAN / ODS)"),
    ("FINANCAS_PUBLICAS", "Finanças Públicas, Receitas e Despesas Municipais (FINBRA / Siconfi)"),
    ("TRABALHO_RENDA", "Trabalho, Rendimento, Deslocamento e Segurança Alimentar (Censo / PNAD / EBIA)"),
    ("DEMOGRAFIA_EDUCACAO", "Demografia, População, Censos e Assistência Social (Estimativas / Projeções / SUAS)"),
    ("INFANCIA_JUVENTUDE_ESCOLAS", "Infância, Juventude, Educação e Saúde do Escolar (PeNSE / Censo / MUNIC)"),
    ("SAUDE_PNS", "Saúde Pública, Doenças Crônicas e Hábitos (PNS)"),
    ("SEGURANCA_DEFESA_SOCIAL", "Segurança Pública, Vitimização, Defesa Social e Direitos Humanos (MUNIC / PNAD)"),
    ("CULTURA_TURISMO_ESPORTE", "Cultura, Patrimônio Histórico, Turismo e Esporte (MUNIC / PSH / PNAD)"),
    ("TRANSPORTE_MOBILIDADE", "Transporte, Mobilidade Urbana e Frota de Veículos (SENATRAN / MUNIC)"),
    ("INOVACAO_GOV_DIGITAL", "Inovação Tecnológica, P&D e Governo Digital (PINTEC / MUNIC / ODS)"),
    ("HABITACAO_FAVELAS", "Habitação, Favelas, Condições de Moradia e Entorno Urbano (Censo 2022)"),
    ("SANEAMENTO_GESTAO_URBANA", "Saneamento Básico, Resíduos Sólidos e Gestão Urbana (PNSB / Censo / PNAD)"),
    ("MEIO_AMBIENTE_CLIMA_ODS", "Meio Ambiente, Clima, Biodiversidade e Recursos Naturais (IDS / ODS)"),
    ("RISCOS_DESASTRES_DEFESA_CIVIL", "Riscos Geológicos, Desastres Naturais e Defesa Civil (CEMADEN / PNSB / MUNIC)"),
    ("TERRITORIOS_TRADICIONAIS_INDIGENAS_QUILOMBOLAS", "Terras Indígenas e Comunidades Quilombolas em Territórios Delimitados (Censo 2022)"),
    ("CONJUNTURA_MENSAL", "Preços, Inflação Regional e Construção Civil (IPCA / INPC / SINAPI / PIM / PMC / PMS)"),
    ("REGISTRO_CIVIL", "Estatísticas Vitais do Registro Civil (Nascimentos, Casamentos, Óbitos, Divórcios)"),
]

# Pesquisas Oficiais do IBGE disponíveis via API SIDRA
SURVEYS: List[Dict[str, Any]] = [
    # ------------------------------------------------------------------
    # 1. AGROPECUÁRIA E PRODUÇÃO VEGETAL
    # ------------------------------------------------------------------
    {
        "id": "PAM",
        "group": "AGRO_VEGETAL",
        "name": "PAM - Produção Agrícola Municipal (85 Lavouras Temporárias e Permanentes)",
        "table": 5457,
        "classification": 782,
        "category_source": "PAM_CATEGORIES",
        "level": "N6",
        "min_year": 1974,
        "max_year": 2025,
        "default_years": [2025, 2024],
        "default_var": 214,
        "notice_severity": "info",
        "popup_notice": False,
        "notice_title": "PAM - Série histórica até 2025",
        "notice_text": (
            "Dados municipais (N6) disponíveis de 1974 a 2025. O ano de 2026 ainda não foi publicado pelo IBGE para a PAM."
        ),
        "variables": [
            {"id": 214, "name": "Quantidade Produzida", "slug": "quantidade_produzida", "unit": "t", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 215, "name": "Valor da Produção", "slug": "valor_producao", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
            {"id": 216, "name": "Área Colhida", "slug": "area_colhida", "unit": "ha", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 8331, "name": "Área Plantada / Destinada à Colheita", "slug": "area_plantada", "unit": "ha", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 112, "name": "Rendimento Médio", "slug": "rendimento_medio", "unit": "kg/ha", "multiplier": 1.0, "agg_mode": "mean"},
        ],
    },
    {
        "id": "PAM_MILHO",
        "group": "AGRO_VEGETAL",
        "name": "PAM Safras - Milho (1ª e 2ª Safras / Safrinha)",
        "table": 839,
        "classification": 81,
        "category_source": "PAM_MILHO_CATEGORIES",
        "level": "N6",
        "min_year": 2003,
        "max_year": 2025,
        "default_years": [2025],
        "default_var": 214,
        "notice_severity": "info",
        "popup_notice": False,
        "notice_title": "PAM Safras (Milho) - Série 2003 a 2025",
        "notice_text": (
            "Permite separar a 1ª safra (verão) da 2ª safra (safrinha) em nível municipal (N6). Disponível de 2003 a 2025."
        ),
        "variables": [
            {"id": 214, "name": "Quantidade Produzida", "slug": "quantidade_produzida", "unit": "t", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 109, "name": "Área Plantada", "slug": "area_plantada", "unit": "ha", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 216, "name": "Área Colhida", "slug": "area_colhida", "unit": "ha", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 112, "name": "Rendimento Médio", "slug": "rendimento_medio", "unit": "kg/ha", "multiplier": 1.0, "agg_mode": "mean"},
        ],
    },
    {
        "id": "PAM_FEIJAO",
        "group": "AGRO_VEGETAL",
        "name": "PAM Safras - Feijão (1ª, 2ª e 3ª Safras)",
        "table": 1002,
        "classification": 81,
        "category_source": "PAM_FEIJAO_CATEGORIES",
        "level": "N6",
        "min_year": 2003,
        "max_year": 2025,
        "default_years": [2025],
        "default_var": 214,
        "notice_severity": "info",
        "popup_notice": False,
        "notice_title": "PAM Safras (Feijão) - Série 2003 a 2025",
        "notice_text": "Desagrega a produção municipal de feijão por 1ª, 2ª e 3ª safras (2003 a 2025).",
        "variables": [
            {"id": 214, "name": "Quantidade Produzida", "slug": "quantidade_produzida", "unit": "t", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 109, "name": "Área Plantada", "slug": "area_plantada", "unit": "ha", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 216, "name": "Área Colhida", "slug": "area_colhida", "unit": "ha", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 112, "name": "Rendimento Médio", "slug": "rendimento_medio", "unit": "kg/ha", "multiplier": 1.0, "agg_mode": "mean"},
        ],
    },
    {
        "id": "PAM_BATATA",
        "group": "AGRO_VEGETAL",
        "name": "PAM Safras - Batata-inglesa (1ª, 2ª e 3ª Safras)",
        "table": 1001,
        "classification": 81,
        "category_source": "PAM_BATATA_CATEGORIES",
        "level": "N6",
        "min_year": 2003,
        "max_year": 2025,
        "default_years": [2025],
        "default_var": 214,
        "notice_severity": "info",
        "popup_notice": False,
        "notice_title": "PAM Safras (Batata-inglesa) - Série 2003 a 2025",
        "notice_text": "Desagrega a produção municipal de batata-inglesa por 1ª, 2ª e 3ª safras (2003 a 2025).",
        "variables": [
            {"id": 214, "name": "Quantidade Produzida", "slug": "quantidade_produzida", "unit": "t", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 109, "name": "Área Plantada", "slug": "area_plantada", "unit": "ha", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 216, "name": "Área Colhida", "slug": "area_colhida", "unit": "ha", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 112, "name": "Rendimento Médio", "slug": "rendimento_medio", "unit": "kg/ha", "multiplier": 1.0, "agg_mode": "mean"},
        ],
    },
    {
        "id": "PAM_AMENDOIM",
        "group": "AGRO_VEGETAL",
        "name": "PAM Safras - Amendoim (1ª e 2ª Safras)",
        "table": 1000,
        "classification": 81,
        "category_source": "PAM_AMENDOIM_CATEGORIES",
        "level": "N6",
        "min_year": 2003,
        "max_year": 2025,
        "default_years": [2025],
        "default_var": 214,
        "notice_severity": "info",
        "popup_notice": False,
        "notice_title": "PAM Safras (Amendoim) - Série 2003 a 2025",
        "notice_text": "Desagrega a produção municipal de amendoim por 1ª e 2ª safras (2003 a 2025).",
        "variables": [
            {"id": 214, "name": "Quantidade Produzida", "slug": "quantidade_produzida", "unit": "t", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 109, "name": "Área Plantada", "slug": "area_plantada", "unit": "ha", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 216, "name": "Área Colhida", "slug": "area_colhida", "unit": "ha", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 112, "name": "Rendimento Médio", "slug": "rendimento_medio", "unit": "kg/ha", "multiplier": 1.0, "agg_mode": "mean"},
        ],
    },
    {
        "id": "CENSO_AGRO_TIPOLOGIA",
        "group": "AGRO_VEGETAL",
        "name": "Censo Agropecuário 2017 - Agricultura Familiar e Tipologia (Tabela 6878)",
        "table": 6878,
        "classification": 829,
        "extra_classifications": {12517: 113601, 12564: 41145, 12771: 45951, 218: 46502},
        "category_source": "CENSO_AGRO_TIPOLOGIA_CATEGORIES",
        "level": "N6",
        "min_year": 2017,
        "max_year": 2017,
        "valid_years": [2017],
        "default_years": [2017],
        "default_var": 183,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Agropecuário (Somente 2017)",
        "notice_text": (
            "Levantamento censitário estrutural com dados disponíveis exclusivamente para o ano de 2017 "
            "(nível municipal N6). As dimensões secundárias (atividade, sexo, idade e condição do produtor) "
            "estão fixadas em 'Total'."
        ),
        "variables": [
            {"id": 183, "name": "Número de Estabelecimentos Agropecuários", "slug": "estabelecimentos_agropecuarios", "unit": "Estabelecimentos", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 184, "name": "Área dos Estabelecimentos Agropecuários", "slug": "area_estabelecimentos", "unit": "ha", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "CENSO_AGRO_TERRAS",
        "group": "AGRO_VEGETAL",
        "name": "Censo Agropecuário 2017 - Utilização das Terras nos Estabelecimentos (Tabela 6881)",
        "table": 6881,
        "classification": 222,
        "extra_classifications": {829: 46302, 218: 46502, 12517: 113601, 12567: 41151},
        "category_source": "CENSO_AGRO_TERRAS_CATEGORIES",
        "level": "N6",
        "min_year": 2017,
        "max_year": 2017,
        "valid_years": [2017],
        "default_years": [2017],
        "default_var": 184,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Agropecuário (Somente 2017)",
        "notice_text": (
            "Levantamento censitário estrutural disponível exclusivamente para 2017 (nível municipal N6). "
            "Permite mapear áreas de lavouras, pastagens, matas/florestas e sistemas agroflorestais."
        ),
        "variables": [
            {"id": 184, "name": "Área das Terras", "slug": "area_utilizacao_terras", "unit": "ha", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 9587, "name": "Número de Estabelecimentos com Área", "slug": "estabelecimentos_area", "unit": "Estabelecimentos", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },

    # ------------------------------------------------------------------
    # 2. PECUÁRIA E AQUICULTURA (PPM)
    # ------------------------------------------------------------------
    {
        "id": "PPM_REBANHO",
        "group": "PECUARIA_AQUI",
        "name": "PPM - Pecuária Municipal (Efetivo dos Rebanhos)",
        "table": 3939,
        "classification": 79,
        "category_source": "PPM_REBANHOS_CATEGORIES",
        "level": "N6",
        "min_year": 1974,
        "max_year": 2025,
        "default_years": [2025],
        "default_var": 105,
        "notice_severity": "info",
        "popup_notice": False,
        "notice_title": "PPM Rebanhos - Indicador de estoque (até 2025)",
        "notice_text": (
            "Série municipal (N6) de 1974 a 2025 (sem 2026). Por ser estoque anual de rebanho em 31/12, "
            "quando múltiplos anos são marcados o mapa exibe o efetivo do último ano e o gráfico mostra a evolução."
        ),
        "variables": [
            {"id": 105, "name": "Efetivo do Rebanho", "slug": "efetivo_rebanho", "unit": "Cabeças", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "PPM_PRODUTO",
        "group": "PECUARIA_AQUI",
        "name": "PPM - Pecuária Municipal (Produtos de Origem Animal: Leite, Ovos, Mel)",
        "table": 74,
        "classification": 80,
        "category_source": "PPM_PRODUTOS_CATEGORIES",
        "level": "N6",
        "min_year": 1974,
        "max_year": 2025,
        "default_years": [2025, 2024],
        "default_var": 106,
        "notice_severity": "info",
        "popup_notice": False,
        "notice_title": "PPM Produtos Animais - Série até 2025",
        "notice_text": (
            "Série municipal (N6) de 1974 a 2025 (sem 2026). Utilize a categoria 'Total' apenas para 'Valor da Produção', "
            "pois os produtos individuais têm unidades físicas distintas (litros, dúzias, kg)."
        ),
        "variables": [
            {"id": 106, "name": "Quantidade Produzida", "slug": "quantidade_produzida", "unit": "Unidade específica", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 215, "name": "Valor da Produção", "slug": "valor_producao", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
        ],
    },
    {
        "id": "PPM_AQUICULTURA",
        "group": "PECUARIA_AQUI",
        "name": "PPM - Aquicultura Municipal (Peixes, Tilápia, Camarão, Ostras - Tabela 3940)",
        "table": 3940,
        "classification": 654,
        "category_source": "PPM_AQUICULTURA_CATEGORIES",
        "level": "N6",
        "min_year": 2013,
        "max_year": 2025,
        "default_years": [2025, 2024],
        "default_var": 4146,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "PPM Aquicultura - Série iniciada em 2013 (2013 a 2025)",
        "notice_text": (
            "A produção aquícola municipal começou a ser pesquisada na PPM em 2013 e vai até 2025. "
            "Não existem dados municipais de aquicultura no SIDRA para 2006–2012 nem para 2026."
        ),
        "variables": [
            {"id": 4146, "name": "Produção da Aquicultura", "slug": "producao_aquicultura", "unit": "kg / milheiros", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 215, "name": "Valor da Produção", "slug": "valor_producao", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
        ],
    },
    {
        "id": "PPM_VACAS_ORDENHADAS",
        "group": "PECUARIA_AQUI",
        "name": "PPM - Vacas Ordenhadas por Município (Tabela 94)",
        "table": 94,
        "classification": None,
        "level": "N6",
        "min_year": 1974,
        "max_year": 2025,
        "default_years": [2025],
        "default_var": 107,
        "notice_severity": "info",
        "popup_notice": False,
        "notice_title": "PPM Vacas Ordenhadas - Série até 2025",
        "notice_text": "Série municipal (N6) de 1974 a 2025 (sem 2026). Efetivo anual (usa último ano no mapa).",
        "variables": [
            {"id": 107, "name": "Vacas Ordenhadas", "slug": "vacas_ordenhadas", "unit": "Cabeças", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "PPM_OVINOS_TOSQUIADOS",
        "group": "PECUARIA_AQUI",
        "name": "PPM - Ovinos Tosquiados por Município (Tabela 95)",
        "table": 95,
        "classification": None,
        "level": "N6",
        "min_year": 1974,
        "max_year": 2025,
        "default_years": [2025],
        "default_var": 108,
        "notice_severity": "info",
        "popup_notice": False,
        "notice_title": "PPM Ovinos Tosquiados - Série até 2025",
        "notice_text": "Série municipal (N6) de 1974 a 2025 (sem 2026). Efetivo anual (usa último ano no mapa).",
        "variables": [
            {"id": 108, "name": "Ovinos Tosquiados", "slug": "ovinos_tosquiados", "unit": "Cabeças", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },

    # ------------------------------------------------------------------
    # 3. EXTRAÇÃO VEGETAL E SILVICULTURA (PEVS)
    # ------------------------------------------------------------------
    {
        "id": "PEVS_EXTRACAO",
        "group": "FLORESTAL",
        "name": "PEVS - Extração Vegetal (Erva-mate, Açaí, Pinhão, Madeira Nativa - Tabela 289)",
        "table": 289,
        "classification": 193,
        "category_source": "PEVS_EXTRACAO_CATEGORIES",
        "level": "N6",
        "min_year": 1986,
        "max_year": 2025,
        "default_years": [2025, 2024],
        "default_var": 144,
        "notice_severity": "info",
        "popup_notice": False,
        "notice_title": "PEVS Extração Vegetal - Série até 2025",
        "notice_text": (
            "Dados municipais (N6) disponíveis de 1986 a 2025 (sem 2026). As unidades de quantidade variam "
            "conforme o produto (toneladas, m³ ou árvores) e são gravadas na coluna UNIDADE."
        ),
        "variables": [
            {"id": 144, "name": "Quantidade Produzida na Extração Vegetal", "slug": "quantidade_produzida_extracao", "unit": "t / m³", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 145, "name": "Valor da Produção na Extração Vegetal", "slug": "valor_producao_extracao", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
        ],
    },
    {
        "id": "PEVS_SILVICULTURA",
        "group": "FLORESTAL",
        "name": "PEVS - Silvicultura (Florestas Plantadas: Tora, Celulose, Lenha, Carvão - Tabela 291)",
        "table": 291,
        "classification": 194,
        "category_source": "PEVS_SILVICULTURA_CATEGORIES",
        "level": "N6",
        "min_year": 1986,
        "max_year": 2025,
        "default_years": [2025, 2024],
        "default_var": 142,
        "notice_severity": "info",
        "popup_notice": False,
        "notice_title": "PEVS Silvicultura - Série até 2025",
        "notice_text": (
            "Dados municipais (N6) de 1986 a 2025 (sem 2026). Madeira em tora e lenha são medidas em m³; "
            "carvão vegetal, resina, folha de eucalipto e casca de acácia em toneladas."
        ),
        "variables": [
            {"id": 142, "name": "Quantidade Produzida na Silvicultura", "slug": "quantidade_produzida_silvicultura", "unit": "m³ / t", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 143, "name": "Valor da Produção na Silvicultura", "slug": "valor_producao_silvicultura", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
        ],
    },
    {
        "id": "PEVS_AREA",
        "group": "FLORESTAL",
        "name": "PEVS - Área Existente da Silvicultura por Espécie Florestal (Tabela 5930)",
        "table": 5930,
        "classification": 734,
        "category_source": "PEVS_AREA_CATEGORIES",
        "level": "N6",
        "min_year": 2013,
        "max_year": 2025,
        "default_years": [2025],
        "default_var": 6549,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "PEVS Área da Silvicultura - Série 2013 a 2025",
        "notice_text": (
            "O levantamento de área plantada por espécie (Eucalipto, Pinus, Acácia, Teca etc.) iniciou em 2013 e vai até 2025 "
            "(sem dados para 2006–2012 e 2026). Por ser estoque em 31/12, o mapa utiliza o último ano selecionado."
        ),
        "variables": [
            {"id": 6549, "name": "Área Total Existente em 31/12", "slug": "area_silvicultura", "unit": "ha", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },

    # ------------------------------------------------------------------
    # 4. CONTAS REGIONAIS, INDÚSTRIA E EMPRESAS (PIB / CEMPRE / PIA)
    # ------------------------------------------------------------------
    {
        "id": "PIB_MUN",
        "group": "ECONOMIA_EMPRESAS",
        "name": "PIB Municipal - Contas Econômicas e Valor Adicionado (Tabelas 21/5938 - 1999–2023)",
        "table": 5938,
        "table_series": [
            {"min_year": 1999, "max_year": 2001, "table": 21, "var_overrides": {6575: None}},
            {"min_year": 2002, "max_year": 2023, "table": 5938},
        ],
        "classification": None,
        "level": "N6",
        "min_year": 1999,
        "max_year": 2023,
        "default_years": [2023],
        "default_var": 37,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "PIB Municipal - Série Unificada 1999 a 2023 (Ref. 2002 + Ref. 2010)",
        "notice_text": (
            "Combina automaticamente 1999–2001 (Tabela 21 - Ref. 2002) e 2002–2023 (Tabela 5938 - Ref. 2010), "
            "com defasagem oficial até 2023. VAB Serviços excl. Administração Pública (6575) inicia em 2002."
        ),
        "variables": [
            {"id": 37, "name": "Produto Interno Bruto (PIB)", "slug": "pib", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
            {"id": 513, "name": "VAB Agropecuária", "slug": "vab_agropecuaria", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
            {"id": 517, "name": "VAB Indústria", "slug": "vab_industria", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
            {"id": 6575, "name": "VAB Serviços (excl. Adm. Pública)", "slug": "vab_servicos", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum", "min_year": 2002},
            {"id": 525, "name": "VAB Administração Pública", "slug": "vab_administracao_publica", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
            {"id": 498, "name": "Valor Adicionado Bruto Total", "slug": "vab_total", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
            {"id": 543, "name": "Impostos Líquidos sobre Produtos", "slug": "impostos_liquidos", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
        ],
    },
    {
        "id": "PIB_GINI_UF",
        "group": "ECONOMIA_EMPRESAS",
        "name": "PIB Estadual - Índice de Gini da Distribuição do PIB/VAB (Tabelas 599/5939 - N3 - 1999–2023)",
        "table": 5939,
        "table_series": [
            {"min_year": 1999, "max_year": 2001, "table": 599, "var_overrides": {6568: None}},
            {"min_year": 2002, "max_year": 2023, "table": 5939},
        ],
        "classification": None,
        "level": "N3",
        "min_year": 1999,
        "max_year": 2023,
        "default_years": [2023],
        "default_var": 529,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Índice de Gini do PIB - Nível Estadual (N3) e Série 1999 a 2023",
        "notice_text": (
            "Disponível somente em nível Estadual (N3 - UFs) até 2023 (combina Tabela 599 Ref. 2002 em 1999–2001 "
            "com Tabela 5939 Ref. 2010 em 2002–2023). O DF não possui índice por ser município único; Gini VAB Serviços (6568) inicia em 2002."
        ),
        "variables": [
            {"id": 529, "name": "Índice de Gini do PIB", "slug": "gini_pib", "unit": "Índice", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 531, "name": "Índice de Gini do VAB Agropecuária", "slug": "gini_vab_agro", "unit": "Índice", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 532, "name": "Índice de Gini do VAB Indústria", "slug": "gini_vab_industria", "unit": "Índice", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 6568, "name": "Índice de Gini do VAB Serviços", "slug": "gini_vab_servicos", "unit": "Índice", "multiplier": 1.0, "agg_mode": "mean", "min_year": 2002},
            {"id": 534, "name": "Índice de Gini do VAB Administração Pública", "slug": "gini_vab_adm_publica", "unit": "Índice", "multiplier": 1.0, "agg_mode": "mean"},
        ],
    },
    {
        "id": "CEMPRE_TOTAIS",
        "group": "ECONOMIA_EMPRESAS",
        "name": "CEMPRE - Empresas, Unidades Locais e Pessoal Ocupado Municipal (Tabelas 1685 / 9509)",
        "table": 9509,
        "table_series": [
            {"min_year": 2006, "max_year": 2021, "table": 1685},
            {"min_year": 2022, "max_year": 2024, "table": 9509},
        ],
        "classification": None,
        "level": "N6",
        "min_year": 2006,
        "max_year": 2024,
        "default_years": [2024],
        "default_var": 706,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "CEMPRE Totais - Série até 2024 e quebra metodológica em 2022",
        "notice_text": (
            "Dados municipais (N6) publicados até 2024 (sem 2025/2026). O plugin alterna automaticamente entre "
            "a série encerrada (2006–2021, Tabela 1685) e a série nova (2022–2024, Tabela 9509). "
            "Atenção: houve revisão metodológica do IBGE a partir de 2022."
        ),
        "variables": [
            {"id": 706, "name": "Número de Unidades Locais", "slug": "unidades_locais", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 367, "name": "Número de Empresas Atuantes", "slug": "empresas_atuantes", "unit": "Empresas", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 707, "name": "Pessoal Ocupado Total", "slug": "pessoal_ocupado_total", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 708, "name": "Pessoal Ocupado Assalariado", "slug": "pessoal_ocupado_assalariado", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 5944, "name": "Pessoal Assalariado Médio", "slug": "pessoal_assalariado_medio", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 662, "name": "Salários e Outras Remunerações", "slug": "salarios_remuneracoes", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
            {"id": 10143, "name": "Salário Médio Mensal (em Reais)", "slug": "salario_medio_reais", "unit": "R$", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 1606, "name": "Salário Médio Mensal (Salários Mínimos)", "slug": "salario_medio_sm", "unit": "Salários mínimos", "multiplier": 1.0, "agg_mode": "mean"},
        ],
    },
    {
        "id": "CEMPRE_CNAE",
        "group": "ECONOMIA_EMPRESAS",
        "name": "CEMPRE Setorial - Empresas e Emprego por CNAE 2.0 Municipal (Tabelas 6450 / 9528)",
        "table": 9528,
        "table_series": [
            {"min_year": 2006, "max_year": 2021, "table": 6450},
            {"min_year": 2022, "max_year": 2024, "table": 9528},
        ],
        "classification": 12762,
        "category_source": "CEMPRE_CNAE",
        "level": "N6",
        "min_year": 2006,
        "max_year": 2024,
        "default_years": [2024],
        "default_var": 706,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "CEMPRE por CNAE 2.0 - Quebra em 2022, limite 2024 e sigilo pontual",
        "notice_text": (
            "Cobre 1.067 seções, divisões, grupos e classes CNAE 2.0 em nível municipal (N6) até 2024. "
            "Integra Tabela 6450 (2006–2021) e Tabela 9528 (2022–2024), havendo quebra metodológica em 2022. "
            "Classes com poucas empresas no município podem vir desidentificadas ('X' / '-')."
        ),
        "variables": [
            {"id": 706, "name": "Número de Unidades Locais", "slug": "unidades_locais", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 707, "name": "Pessoal Ocupado Total", "slug": "pessoal_ocupado_total", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 708, "name": "Pessoal Ocupado Assalariado", "slug": "pessoal_ocupado_assalariado", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 662, "name": "Salários e Outras Remunerações", "slug": "salarios_remuneracoes", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
        ],
    },
    {
        "id": "PIA_PRODUTO",
        "group": "ECONOMIA_EMPRESAS",
        "name": "PIA-Produto - Produção Física e Vendas Industriais (Prodlist - Nível Brasil N1)",
        "table": 7752,
        "table_recent": 10476,
        "table_series": [
            {"min_year": 2014, "max_year": 2023, "table": 7752},
            {"min_year": 2024, "max_year": 2024, "table": 10476},
        ],
        "classification": 1264,
        "category_source": "PIA_PRODLIST",
        "level": "N1",
        "min_year": 2014,
        "max_year": 2024,
        "default_years": [2024, 2023],
        "default_var": 215,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "PIA-Produto - Apenas Nível Brasil (N1) por Sigilo Estatístico",
        "notice_text": (
            "Devido à Lei de Sigilo Estatístico (Lei nº 5.534/1968), o IBGE divulga a PIA-Produto apenas em nível "
            "Brasil (N1), sem abertura por estado ou município. Série disponível de 2014 a 2024 "
            "(integra Tabela 7752 até 2023 e Tabela 10476 para 2024)."
        ),
        "variables": [
            {"id": 215, "name": "Valor da Produção", "slug": "valor_producao", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
            {"id": 214, "name": "Quantidade Produzida", "slug": "quantidade_produzida", "unit": "Unidade específica", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 864, "name": "Receita Líquida de Vendas", "slug": "receita_vendas", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
            {"id": 1982, "name": "Quantidade Vendida", "slug": "quantidade_vendida", "unit": "Unidade específica", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 362, "name": "Número de Informações / Registros", "slug": "numero_empresas", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "PIA_EMPRESA_UF",
        "group": "ECONOMIA_EMPRESAS",
        "name": "PIA-Empresa - Estrutura Industrial por Estado/UF (Divisões CNAE 2.0 - N3)",
        "table": 1849,
        "table_recent": 10457,
        "table_series": [
            {"min_year": 2007, "max_year": 2023, "table": 1849, "var_overrides": {2086: None}},
            {"min_year": 2024, "max_year": 2024, "table": 10457, "var_overrides": {706: 13816}},
        ],
        "classification": 12762,
        "category_source": "PIA_CNAE_CATEGORIES",
        "level": "N3",
        "min_year": 2007,
        "max_year": 2024,
        "default_years": [2024, 2023],
        "default_var": 811,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "PIA-Empresa - Apenas Nível Estadual (N3) e até 2024",
        "notice_text": (
            "Dados divulgados somente por Estado/UF (N3) para empresas industriais com 5 ou mais pessoas ocupadas, "
            "de 2007 a 2024 (Tabela 1849 até 2023 e Tabela 10457 para 2024). Observação: a variável "
            "'Número de Empresas (>= 5 pessoas)' passou a existir apenas a partir de 2024."
        ),
        "variables": [
            {"id": 811, "name": "Valor da Transformação Industrial (VTI)", "slug": "vti", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
            {"id": 810, "name": "Valor Bruto da Produção Industrial (VBPI)", "slug": "vbpi", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
            {"id": 836, "name": "Receita Líquida de Vendas Industriais", "slug": "receita_liquida_vendas", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
            {"id": 631, "name": "Pessoal Ocupado (31/12)", "slug": "pessoal_ocupado", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 673, "name": "Salários e Outras Remunerações", "slug": "salarios_remuneracoes", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
            {"id": 706, "name": "Número de Unidades Locais", "slug": "unidades_locais", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 2086, "name": "Número de Empresas (>= 5 pessoas - apenas 2024)", "slug": "numero_empresas", "unit": "Empresas", "multiplier": 1.0, "agg_mode": "last", "min_year": 2024},
        ],
    },

    # ------------------------------------------------------------------
    # 5. DEMOGRAFIA, EDUCAÇÃO E SANEAMENTO
    # ------------------------------------------------------------------
    {
        "id": "POP_ESTIMADA",
        "group": "DEMOGRAFIA_EDUCACAO",
        "name": "Estimativas de População Residente Municipal (2001–2026 - Tabela 6579)",
        "table": 6579,
        "classification": None,
        "level": "N6",
        "min_year": 2001,
        "max_year": 2026,
        "valid_years": [2006, 2008, 2009, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2024, 2025, 2026],
        "default_years": [2026],
        "default_var": 9324,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Estimativas de População - Sem anos censitários (2010, 2022 e 2023)",
        "notice_text": (
            "Única pesquisa do catálogo com dados de 2026. Porém, esta tabela NÃO publica estimativas para os "
            "anos censitários/contagens (2007, 2010, 2022 e 2023). Para 2022, utilize as tabelas do Censo Demográfico 2022."
        ),
        "variables": [
            {"id": 9324, "name": "População Residente Estimada", "slug": "populacao_estimada", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "CENSO22_POP_DENS",
        "group": "DEMOGRAFIA_EDUCACAO",
        "name": "Censo 2022 - População, Área Territorial e Densidade Demográfica (Tabela 4714)",
        "table": 4714,
        "classification": None,
        "level": "N6",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 93,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Demográfico 2022 (Somente ano 2022)",
        "notice_text": (
            "Tabela do Censo Demográfico 2022 com dados disponíveis apenas para o ano de 2022 (nível municipal N6)."
        ),
        "variables": [
            {"id": 93, "name": "População Residente", "slug": "populacao_residente", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 614, "name": "Densidade Demográfica", "slug": "densidade_demografica", "unit": "hab/km²", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 6318, "name": "Área da Unidade Territorial", "slug": "area_territorial", "unit": "km²", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "CENSO22_CRESCIMENTO",
        "group": "DEMOGRAFIA_EDUCACAO",
        "name": "Censo 2022 - Variação Populacional e Crescimento 2010–2022 (Tabela 4709)",
        "table": 4709,
        "classification": None,
        "level": "N6",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 10605,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Demográfico 2022 - Valores negativos permitidos (Somente 2022)",
        "notice_text": (
            "Tabela censitária única (ano 2022). Municípios com redução populacional entre 2010 e 2022 apresentam "
            "valores negativos na variação absoluta e na taxa de crescimento geométrico."
        ),
        "variables": [
            {"id": 10605, "name": "Taxa de Crescimento Geométrico (2010–2022)", "slug": "taxa_crescimento_geometrico", "unit": "% a.a.", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
            {"id": 5936, "name": "Variação Absoluta da População (2010–2022)", "slug": "variacao_populacional", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
            {"id": 93, "name": "População Residente (2022)", "slug": "populacao_residente", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "CENSO22_URB_RURAL",
        "group": "DEMOGRAFIA_EDUCACAO",
        "name": "Censo 2022 - População Urbana vs. Rural (Tabela 9923)",
        "table": 9923,
        "classification": 1,
        "category_source": "CENSO22_SITUACAO_CATEGORIES",
        "level": "N6",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 93,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Demográfico 2022 (Somente ano 2022)",
        "notice_text": "População residente municipal por situação do domicílio (Urbana, Rural ou Total), apenas para 2022.",
        "variables": [
            {"id": 93, "name": "População Residente", "slug": "populacao_situacao", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 1000093, "name": "Percentual da População Total", "slug": "pct_populacao_situacao", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
        ],
    },
    {
        "id": "CENSO22_ALFABETIZACAO",
        "group": "DEMOGRAFIA_EDUCACAO",
        "name": "Censo 2022 - Taxa de Alfabetização (15 anos ou mais - Tabela 9543)",
        "table": 9543,
        "classification": 2,
        "extra_classifications": {86: 95251, 287: 100362},
        "category_source": "CENSO22_SEXO_CATEGORIES",
        "level": "N6",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 2513,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Demográfico 2022 (Somente ano 2022)",
        "notice_text": (
            "Taxa percentual de alfabetização da população com 15 anos ou mais no Censo 2022 (por sexo ou Total, "
            "considerando total de cor/raça e idades >= 15 anos)."
        ),
        "variables": [
            {"id": 2513, "name": "Taxa de Alfabetização (15 anos ou mais)", "slug": "taxa_alfabetizacao", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
        ],
    },
    {
        "id": "CENSO22_ESGOTAMENTO",
        "group": "SANEAMENTO_GESTAO_URBANA",
        "name": "Censo 2022 - Domicílios por Tipo de Esgotamento Sanitário (Tabela 6805)",
        "table": 6805,
        "classification": 11558,
        "category_source": "CENSO22_ESGOTAMENTO_CATEGORIES",
        "level": "N6",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 1000381,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Demográfico 2022 (Somente ano 2022)",
        "notice_text": "Domicílios particulares permanentes ocupados por tipo de esgotamento sanitário (somente 2022).",
        "variables": [
            {"id": 1000381, "name": "Percentual dos Domicílios (%)", "slug": "pct_domicilios_esgoto", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 381, "name": "Quantidade de Domicílios", "slug": "domicilios_esgoto", "unit": "Domicílios", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "CENSO22_AGUA",
        "group": "SANEAMENTO_GESTAO_URBANA",
        "name": "Censo 2022 - Domicílios por Abastecimento de Água (Tabela 6804)",
        "table": 6804,
        "classification": 301,
        "extra_classifications": {1817: 72125},
        "category_source": "CENSO22_AGUA_CATEGORIES",
        "level": "N6",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 1000381,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Demográfico 2022 (Somente ano 2022)",
        "notice_text": "Domicílios por principal forma de abastecimento de água (total de canalização), apenas para 2022.",
        "variables": [
            {"id": 1000381, "name": "Percentual dos Domicílios (%)", "slug": "pct_domicilios_agua", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 381, "name": "Quantidade de Domicílios", "slug": "domicilios_agua", "unit": "Domicílios", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "CENSO22_LIXO",
        "group": "SANEAMENTO_GESTAO_URBANA",
        "name": "Censo 2022 - Domicílios por Destino do Lixo (Tabela 6892)",
        "table": 6892,
        "classification": 67,
        "category_source": "CENSO22_LIXO_CATEGORIES",
        "level": "N6",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 1000381,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Demográfico 2022 (Somente ano 2022)",
        "notice_text": "Domicílios por destino do lixo coletado/queimado/enterrado (somente 2022).",
        "variables": [
            {"id": 1000381, "name": "Percentual dos Domicílios (%)", "slug": "pct_domicilios_lixo", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 381, "name": "Quantidade de Domicílios", "slug": "domicilios_lixo", "unit": "Domicílios", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },

    # ------------------------------------------------------------------
    # EXPANSÃO FASE 2: LSPA E CENSO AGROPECUÁRIO 2017 COMPLEMENTAR
    # ------------------------------------------------------------------
    {
        "id": "LSPA_SAFRA_UF",
        "group": "AGRO_VEGETAL",
        "name": "LSPA - Previsão Mensal (Jan–Dez) e Fechamento Anual de Safra por UF (2006–Set/2026 - Tabela 6588)",
        "table": 6588,
        "classification": 48,
        "category_source": "LSPA_PRODUTOS_CATEGORIES",
        "default_cat": 39443,
        "level": "N3",
        "periodicity": "monthly",
        "min_year": 2006,
        "max_year": 2026,
        "valid_years": _LSPA_VALID_PERIODS,
        "period_map": _LSPA_PERIOD_MAP,
        "period_labels": _LSPA_PERIOD_LABELS,
        "default_years": [202609, 2025],
        "default_var": 35,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "LSPA (Nível UF - N3) - Série Mensal Completa (Set/2006 a Set/2026)",
        "notice_text": (
            "Levantamento Sistemático da Produção Agrícola divulgado apenas por Estado/UF (N3). "
            "Permite escolher o fechamento anual de dezembro (YYYY) ou qualquer mês individual (Set/2006 a Set/2026). "
            "Por serem revisões mensais da safra anual, múltiplos períodos aplicam o último valor (ou média no rendimento)."
        ),
        "variables": [
            {"id": 35, "name": "Produção Estimada da Safra", "slug": "producao_lspa", "unit": "t", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 109, "name": "Área Plantada", "slug": "area_plantada_lspa", "unit": "ha", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 216, "name": "Área Colhida", "slug": "area_colhida_lspa", "unit": "ha", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 36, "name": "Rendimento Médio", "slug": "rendimento_medio_lspa", "unit": "kg/ha", "multiplier": 1.0, "agg_mode": "mean"},
        ],
    },
    {
        "id": "CAGRO_VALOR_PROD",
        "group": "AGRO_VEGETAL",
        "name": "Censo Agropecuário 2017 - Valor da Produção Rural por Origem (Tabela 6897)",
        "table": 6897,
        "classification": 12547,
        "extra_classifications": {829: 46302, 218: 46502, 12517: 113601},
        "category_source": "CAGRO_TIPO_PROD_CATEGORIES",
        "level": "N6",
        "min_year": 2017,
        "max_year": 2017,
        "valid_years": [2017],
        "default_years": [2017],
        "default_var": 1999,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Agropecuário (Somente 2017)",
        "notice_text": (
            "Dados censitários municipais (N6) disponíveis exclusivamente para 2017. "
            "Permite mapear o valor da produção animal, vegetal, horticultura, silvicultura e extração."
        ),
        "variables": [
            {"id": 1999, "name": "Valor da Produção dos Estabelecimentos", "slug": "valor_producao_cagro", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "last"},
            {"id": 40, "name": "Estabelecimentos com Produção", "slug": "estab_com_producao", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "CAGRO_IRRIGACAO",
        "group": "AGRO_VEGETAL",
        "name": "Censo Agropecuário 2017 - Irrigação e Área Irrigada por Método (Tabela 6857)",
        "table": 6857,
        "classification": 12604,
        "extra_classifications": {829: 46302, 12564: 41145, 12771: 45951, 309: 10969},
        "category_source": "CAGRO_IRRIG_METODO_CATEGORIES",
        "level": "N6",
        "min_year": 2017,
        "max_year": 2017,
        "valid_years": [2017],
        "default_years": [2017],
        "default_var": 2373,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Agropecuário (Somente 2017)",
        "notice_text": (
            "Dados censitários municipais (N6) disponíveis apenas para 2017. "
            "Células com baixa ocorrência municipal ou sem uso do método podem constar como sem registro (-)."
        ),
        "variables": [
            {"id": 2373, "name": "Área Irrigada", "slug": "area_irrigada", "unit": "ha", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 2372, "name": "Estabelecimentos com Uso de Irrigação", "slug": "estab_irrigacao", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "CAGRO_PESSOAL",
        "group": "AGRO_VEGETAL",
        "name": "Censo Agropecuário 2017 - Pessoal Ocupado no Campo e Laço Familiar (Tabela 6884)",
        "table": 6884,
        "classification": 12517,
        "extra_classifications": {829: 46302, 2: 6794, 223: 46571, 218: 46502},
        "category_source": "CAGRO_ATIVIDADE_CATEGORIES",
        "level": "N6",
        "min_year": 2017,
        "max_year": 2017,
        "valid_years": [2017],
        "default_years": [2017],
        "default_var": 185,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Agropecuário (Somente 2017)",
        "notice_text": (
            "Pessoal ocupado nos estabelecimentos agropecuários por grupo de atividade econômica (apenas 2017, N6)."
        ),
        "variables": [
            {"id": 185, "name": "Pessoal Ocupado nos Estabelecimentos", "slug": "pessoal_ocupado_campo", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 10099, "name": "Estabelecimentos com Pessoal Ocupado", "slug": "estab_pessoal_ocupado", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 2002, "name": "Pessoal Ocupado com Laço Familiar", "slug": "pessoal_laco_familiar", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 2052, "name": "Estabelecimentos com Laço Familiar", "slug": "estab_laco_familiar", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "CAGRO_AGROTOXICOS",
        "group": "AGRO_VEGETAL",
        "name": "Censo Agropecuário 2017 - Uso de Agrotóxicos nos Estabelecimentos (Tabela 6851)",
        "table": 6851,
        "classification": 12521,
        "extra_classifications": {829: 46302, 12564: 41145, 218: 46502, 800: 41147, 12598: 41141},
        "category_source": "CAGRO_AGROTOXICOS_CATEGORIES",
        "default_cat": 111611,
        "level": "N6",
        "min_year": 2017,
        "max_year": 2017,
        "valid_years": [2017],
        "default_years": [2017],
        "default_var": 183,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Agropecuário (Somente 2017)",
        "notice_text": (
            "Número de estabelecimentos agropecuários segundo declaração de uso de agrotóxicos (apenas 2017, N6)."
        ),
        "variables": [
            {"id": 183, "name": "Número de Estabelecimentos Agropecuários", "slug": "estab_agrotoxicos", "unit": "Estabelecimentos", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "CAGRO_TRATORES",
        "group": "AGRO_VEGETAL",
        "name": "Censo Agropecuário 2017 - Tratores e Mecanização Agropecuária (Tabela 6869)",
        "table": 6869,
        "classification": 12605,
        "extra_classifications": {829: 46302, 12564: 41145, 12771: 45951},
        "category_source": "CAGRO_TRATORES_CATEGORIES",
        "level": "N6",
        "min_year": 2017,
        "max_year": 2017,
        "valid_years": [2017],
        "default_years": [2017],
        "default_var": 1862,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Agropecuário (Somente 2017)",
        "notice_text": (
            "Frota de tratores e estabelecimentos mecanizados por faixa de potência (cv), apenas em 2017 (N6)."
        ),
        "variables": [
            {"id": 1862, "name": "Número de Tratores Existentes", "slug": "numero_tratores", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 1918, "name": "Estabelecimentos com Tratores", "slug": "estab_com_tratores", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "CAGRO_ENERGIA",
        "group": "AGRO_VEGETAL",
        "name": "Censo Agropecuário 2017 - Energia Elétrica no Meio Rural (Tabela 6778)",
        "table": 6778,
        "classification": 309,
        "extra_classifications": {829: 46302, 218: 46502, 12553: 46523, 12517: 113601, 220: 110085},
        "category_source": "CAGRO_ENERGIA_CATEGORIES",
        "default_cat": 3011,
        "level": "N6",
        "min_year": 2017,
        "max_year": 2017,
        "valid_years": [2017],
        "default_years": [2017],
        "default_var": 183,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Agropecuário (Somente 2017)",
        "notice_text": (
            "Número de estabelecimentos agropecuários por existência de energia elétrica (apenas 2017, N6)."
        ),
        "variables": [
            {"id": 183, "name": "Número de Estabelecimentos Agropecuários", "slug": "estab_energia", "unit": "Estabelecimentos", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },

    # ------------------------------------------------------------------
    # EXPANSÃO FASE 2: PECUÁRIA TRIMESTRAL (N3 - ATÉ 2T/2026)
    # ------------------------------------------------------------------
    {
        "id": "ABATE_BOVINOS_UF",
        "group": "PECUARIA_AQUI",
        "name": "Abate Trimestral de Bovinos - Cabeças e Carcaças por UF (N3 - 2001–2T/2026 - Tabela 1092)",
        "table": 1092,
        "classification": 18,
        "extra_classifications": {12716: 115236, 12529: 118225},
        "category_source": "ABATE_BOVINO_CATEGORIES",
        "level": "N3",
        "periodicity": "quarterly",
        "min_year": 2001,
        "max_year": 2026,
        "valid_years": _QUARTERLY_2001_2026_VALID,
        "period_map": _QUARTERLY_2001_2026_MAP,
        "period_labels": _QUARTERLY_2001_2026_LABELS,
        "default_years": [2025],
        "default_var": 284,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Pesquisa Trimestral de Abate (Nível UF - Trimestres 1T a 4T e Total)",
        "notice_text": (
            "Divulgado em nível Estadual (N3) até o 2º Trimestre de 2026 (202602). Você pode selecionar "
            "trimestres avulsos (1T, 2T, 3T, 4T) ou o Total Anual consolidado (soma dos 4 trimestres do ano) "
            "para abate e peso de carcaças. UFs com poucos informantes podem ter sigilo estatístico (-)."
        ),
        "variables": [
            {"id": 284, "name": "Animais Abatidos", "slug": "abate_bovinos_cabecas", "unit": "Cabeças", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 285, "name": "Peso Total das Carcaças", "slug": "abate_bovinos_carcacas", "unit": "kg", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 151, "name": "Número de Estabelecimentos Informantes", "slug": "informantes_abate_bovinos", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "ABATE_SUINOS_UF",
        "group": "PECUARIA_AQUI",
        "name": "Abate Trimestral de Suínos - Cabeças e Carcaças por UF (N3 - 2001–2T/2026 - Tabela 1093)",
        "table": 1093,
        "classification": 12529,
        "extra_classifications": {12716: 115236},
        "category_source": "INSPECAO_SAN_CATEGORIES",
        "level": "N3",
        "periodicity": "quarterly",
        "min_year": 2001,
        "max_year": 2026,
        "valid_years": _QUARTERLY_2001_2026_VALID,
        "period_map": _QUARTERLY_2001_2026_MAP,
        "period_labels": _QUARTERLY_2001_2026_LABELS,
        "default_years": [2025],
        "default_var": 284,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Pesquisa Trimestral de Abate (Nível UF - Trimestres 1T a 4T e Total)",
        "notice_text": (
            "Divulgado em nível Estadual (N3) por tipo de inspeção sanitária até o 2º Trimestre de 2026. "
            "Permite consultar cada trimestre (1T a 4T) separadamente ou o Total Anual (soma de 1T a 4T)."
        ),
        "variables": [
            {"id": 284, "name": "Animais Abatidos", "slug": "abate_suinos_cabecas", "unit": "Cabeças", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 285, "name": "Peso Total das Carcaças", "slug": "abate_suinos_carcacas", "unit": "kg", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 151, "name": "Número de Estabelecimentos Informantes", "slug": "informantes_abate_suinos", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "ABATE_FRANGOS_UF",
        "group": "PECUARIA_AQUI",
        "name": "Abate Trimestral de Frangos - Cabeças e Carcaças por UF (N3 - 2001–2T/2026 - Tabela 1094)",
        "table": 1094,
        "classification": 12529,
        "extra_classifications": {12716: 115236},
        "category_source": "INSPECAO_SAN_CATEGORIES",
        "level": "N3",
        "periodicity": "quarterly",
        "min_year": 2001,
        "max_year": 2026,
        "valid_years": _QUARTERLY_2001_2026_VALID,
        "period_map": _QUARTERLY_2001_2026_MAP,
        "period_labels": _QUARTERLY_2001_2026_LABELS,
        "default_years": [2025],
        "default_var": 284,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Pesquisa Trimestral de Abate (Nível UF - Trimestres 1T a 4T e Total)",
        "notice_text": (
            "Divulgado em nível Estadual (N3) por tipo de inspeção sanitária até o 2º Trimestre de 2026. "
            "Permite consultar cada trimestre (1T a 4T) separadamente ou o Total Anual (soma de 1T a 4T)."
        ),
        "variables": [
            {"id": 284, "name": "Animais Abatidos", "slug": "abate_frangos_cabecas", "unit": "Cabeças", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 285, "name": "Peso Total das Carcaças", "slug": "abate_frangos_carcacas", "unit": "kg", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 151, "name": "Número de Estabelecimentos Informantes", "slug": "informantes_abate_frangos", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "LEITE_TRIMESTRAL_UF",
        "group": "PECUARIA_AQUI",
        "name": "Pesquisa Trimestral do Leite - Volume Adquirido e Preço por UF (N3 - 2001–2T/2026 - Tabela 1086)",
        "table": 1086,
        "classification": 12529,
        "extra_classifications": {12716: 115236},
        "category_source": "INSPECAO_SAN_CATEGORIES",
        "level": "N3",
        "periodicity": "quarterly",
        "min_year": 2001,
        "max_year": 2026,
        "valid_years": _QUARTERLY_2001_2026_VALID,
        "period_map": _QUARTERLY_2001_2026_MAP,
        "period_labels": _QUARTERLY_2001_2026_LABELS,
        "default_years": [2025],
        "default_var": 282,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Pesquisa Trimestral do Leite (Nível UF - Trimestres 1T a 4T e Total)",
        "notice_text": (
            "Divulgado por UF (N3) para laticínios sob inspeção até o 2º Trimestre de 2026. Permite escolher "
            "trimestres individuais (1T a 4T) ou o Total Anual (soma dos volumes no ano; média para preço ao produtor)."
        ),
        "variables": [
            {"id": 282, "name": "Leite Cru Adquirido", "slug": "leite_adquirido", "unit": "Mil litros", "multiplier": 1000.0, "agg_mode": "sum"},
            {"id": 283, "name": "Leite Cru Industrializado", "slug": "leite_industrializado", "unit": "Mil litros", "multiplier": 1000.0, "agg_mode": "sum"},
            {"id": 2522, "name": "Preço Médio Pago ao Produtor", "slug": "preco_medio_leite", "unit": "Reais por litro", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 151, "name": "Estabelecimentos Laticínios Informantes", "slug": "informantes_leite", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "OVOS_TRIMESTRAL_UF",
        "group": "PECUARIA_AQUI",
        "name": "Produção Trimestral de Ovos de Galinha e Poedeiras por UF (N3 - 2001–2T/2026 - Tabela 7524)",
        "table": 7524,
        "classification": 1835,
        "extra_classifications": {12716: 115236},
        "category_source": "OVOS_FINALIDADE_CATEGORIES",
        "level": "N3",
        "periodicity": "quarterly",
        "min_year": 2001,
        "max_year": 2026,
        "valid_years": _QUARTERLY_2001_2026_VALID,
        "period_map": _QUARTERLY_2001_2026_MAP,
        "period_labels": _QUARTERLY_2001_2026_LABELS,
        "default_years": [2025],
        "default_var": 29,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Produção de Ovos de Galinha (Nível UF - Trimestres 1T a 4T e Total)",
        "notice_text": (
            "Divulgado por UF (N3) para granjas com 10 mil ou mais poedeiras até o 2º Trimestre de 2026. "
            "Permite escolher trimestres avulsos (1T a 4T) ou o Total Anual (soma dos 4 trimestres de produção)."
        ),
        "variables": [
            {"id": 29, "name": "Quantidade de Ovos Produzidos", "slug": "producao_ovos_trim", "unit": "Mil dúzias", "multiplier": 1000.0, "agg_mode": "sum"},
            {"id": 1988, "name": "Número de Galinhas Poedeiras", "slug": "galinhas_poedeiras", "unit": "Cabeças", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 151, "name": "Número de Estabelecimentos Informantes", "slug": "informantes_ovos", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },

    # ------------------------------------------------------------------
    # EXPANSÃO FASE 2: COMÉRCIO (PAC), SERVIÇOS (PAS), FASFIL E MEIs (N3)
    # ------------------------------------------------------------------
    {
        "id": "PAC_COMERCIO_UF",
        "group": "ECONOMIA_EMPRESAS",
        "name": "PAC - Pesquisa Anual de Comércio por Estado/UF (N3 - Tabelas 1407/10653 - 2007–2024)",
        "table": 10653,
        "table_series": [
            {
                "min_year": 2007,
                "max_year": 2023,
                "table": 1407,
                "uf_classification": 12354,
                "var_overrides": {310: None},
                "cat_overrides": {
                    83357: 106644,
                    83358: 7137,
                    83359: 7138,
                    83360: 7142,
                    83361: 7143,
                    83362: 7139,
                    83363: 7141,
                    83364: 7140,
                    83365: 7144,
                    83366: 90085,
                    83367: 106648,
                    83368: 106649,
                    83369: 90086,
                    83370: 106650,
                    90088: 7146,
                    83371: 7145,
                    83372: 90087,
                    83373: 7147,
                },
            },
            {"min_year": 2024, "max_year": 2024, "table": 10653},
        ],
        "classification": 11066,
        "category_source": "PAC_COMERCIO_CATEGORIES",
        "level": "N3",
        "min_year": 2007,
        "max_year": 2024,
        "default_years": [2024, 2023],
        "default_var": 866,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "PAC Regionalizada - Nível Estadual (N3) e Série 2007–2024 (1407 + 10653)",
        "notice_text": (
            "Integra a série encerrada 2007–2023 (Tabela 1407, adaptando UFs da c12354) com a série nova 2024 "
            "(Tabela 10653, sem recorte municipal N6). A variável Número de Empresas Comerciais (310) existe apenas em 2024."
        ),
        "variables": [
            {"id": 866, "name": "Receita Bruta de Revenda de Mercadorias", "slug": "receita_revenda_pac", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
            {"id": 503, "name": "Margem de Comercialização", "slug": "margem_comercializacao_pac", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
            {"id": 310, "name": "Número de Empresas Comerciais", "slug": "empresas_comerciais", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last", "min_year": 2024, "max_year": 2024},
            {"id": 312, "name": "Pessoal Ocupado em 31/12", "slug": "pessoal_ocupado_pac", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 314, "name": "Salários, Retiradas e Outras Remunerações", "slug": "salarios_pac", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
        ],
    },
    {
        "id": "PAS_SERVICOS_UF",
        "group": "ECONOMIA_EMPRESAS",
        "name": "PAS - Pesquisa Anual de Serviços por Estado/UF (N3 - Tabelas 2715/10762 - 2007–2024)",
        "table": 10762,
        "table_series": [
            {
                "min_year": 2007,
                "max_year": 2023,
                "table": 2715,
                "uf_classification": 12354,
                "var_overrides": {857: 673},
                "cat_overrides": {58296: 106869},
            },
            {"min_year": 2024, "max_year": 2024, "table": 10762},
        ],
        "classification": 12355,
        "category_source": "PAS_SERVICOS_CATEGORIES",
        "level": "N3",
        "min_year": 2007,
        "max_year": 2024,
        "default_years": [2024, 2023],
        "default_var": 672,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "PAS Regionalizada - Nível Estadual (N3) e Série 2007–2024 (2715 + 10762)",
        "notice_text": (
            "Integra a série 2007–2023 (Tabela 2715, adaptando UFs da c12354) com a série nova 2024 "
            "(Tabela 10762, sem recorte municipal N6) para todas as atividades de serviços não-financeiros."
        ),
        "variables": [
            {"id": 672, "name": "Receita Bruta de Serviços", "slug": "receita_servicos_pas", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
            {"id": 630, "name": "Número de Empresas de Serviços", "slug": "empresas_servicos", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 631, "name": "Pessoal Ocupado em 31/12", "slug": "pessoal_ocupado_pas", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 857, "name": "Gastos com Pessoal (Salários e Retiradas)", "slug": "salarios_pas", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
        ],
    },
    {
        "id": "FASFIL_ONG_UF",
        "group": "ECONOMIA_EMPRESAS",
        "name": "FASFIL - Fundações Privadas e Associações Sem Fins Lucrativos (N3 - 2022–2023 - Tabela 10415)",
        "table": 10415,
        "classification": 510,
        "extra_classifications": {12386: 114485, 370: 9504},
        "category_source": "FASFIL_CATEGORIES",
        "level": "N3",
        "min_year": 2022,
        "max_year": 2023,
        "default_years": [2023],
        "default_var": 2129,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "FASFIL - Apenas Nível Estadual (N3) e Anos 2022–2023",
        "notice_text": (
            "Mapeia entidades do terceiro setor (saúde, educação, assistência social, religião, associações) "
            "por Estado/UF (N3) para os anos de 2022 e 2023."
        ),
        "variables": [
            {"id": 2129, "name": "Unidades Locais Sem Fins Lucrativos", "slug": "unidades_fasfil", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 2130, "name": "Pessoal Ocupado Assalariado (31/12)", "slug": "pessoal_assalariado_fasfil", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 2131, "name": "Salários e Outras Remunerações", "slug": "salarios_fasfil", "unit": "mil R$", "multiplier": 1000.0, "agg_mode": "sum"},
            {"id": 13621, "name": "Salário Médio Mensal (em Reais)", "slug": "salario_medio_reais_fasfil", "unit": "Reais", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 2132, "name": "Salário Médio Mensal (Salários Mínimos)", "slug": "salario_medio_sm_fasfil", "unit": "Salários mínimos", "multiplier": 1.0, "agg_mode": "mean"},
        ],
    },
    {
        "id": "MEI_EMPREGO",
        "group": "ECONOMIA_EMPRESAS",
        "name": "MEI - Microempreendedores Individuais e Empregados por Seção CNAE (N3 - 2020–2022 - Tabela 9590)",
        "table": 9590,
        "classification": 956,
        "extra_classifications": {1719: 71430, 1760: 60187, 1724: 60096, 1726: 60099},
        "category_source": "MEI_SECAO_CNAE_CATEGORIES",
        "level": "N3",
        "min_year": 2020,
        "max_year": 2022,
        "default_years": [2022, 2021],
        "default_var": 8862,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Estatísticas MEI - Nível Estadual (N3 - 27 UFs) e Anos 2020–2022",
        "notice_text": (
            "Neste recorte do SIDRA, todos os 27 estados (N3) têm cobertura completa; "
            "no recorte N6 o IBGE publica somente as 27 capitais. Série disponível para 2020 a 2022."
        ),
        "variables": [
            {"id": 8862, "name": "Número de MEIs", "slug": "numero_meis", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 8865, "name": "Empregados dos MEIs", "slug": "empregados_meis", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "MEI_DINAMICA",
        "group": "ECONOMIA_EMPRESAS",
        "name": "MEI - Dinâmica de Entradas, Saídas e Saldo por Seção CNAE (N3 - 2022 - Tabela 9597)",
        "table": 9597,
        "classification": 956,
        "category_source": "MEI_SECAO_CNAE_CATEGORIES",
        "level": "N3",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 8894,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Dinâmica MEI - Nível Estadual (N3), Ano 2022 e Saldo Negativo Permitido",
        "notice_text": (
            "Divulgado integralmente por UF (N3) apenas para 2022 (N6 contempla somente capitais). "
            "O saldo e a variação relativa permitem valores negativos quando há encerramento líquido."
        ),
        "variables": [
            {"id": 8894, "name": "Saldo de MEIs (Entradas - Saídas)", "slug": "saldo_meis", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last", "allow_negative": True},
            {"id": 8895, "name": "Variação Relativa do Saldo (%)", "slug": "variacao_saldo_meis", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
            {"id": 8890, "name": "Entradas de MEIs", "slug": "entradas_meis", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 8891, "name": "Taxa de Entrada de MEIs (%)", "slug": "taxa_entrada_meis", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 8892, "name": "Saídas de MEIs", "slug": "saidas_meis", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 8893, "name": "Taxa de Saída de MEIs (%)", "slug": "taxa_saida_meis", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 8862, "name": "Estoque Total de MEIs", "slug": "estoque_meis", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "MEI_CNAE",
        "group": "ECONOMIA_EMPRESAS",
        "name": "MEI Detalhado - 674 Classes CNAE 2.0 por Estado/UF (N3 - 2022 - Tabela 9594)",
        "table": 9594,
        "classification": 1761,
        "extra_classifications": {1719: 71430, 1760: 60187, 1724: 60096, 1726: 60099},
        "category_source": "MEI_CNAE",
        "level": "N3",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 8862,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "MEI por Classe CNAE 2.0 - Nível Estadual (N3) e Somente 2022",
        "notice_text": (
            "Cobre 674 classes CNAE 2.0 em nível Estadual (N3 - todas as 27 UFs) apenas para 2022. "
            "Classes muito específicas podem apresentar sigilo estatístico pontual (-)."
        ),
        "variables": [
            {"id": 8862, "name": "Número de MEIs", "slug": "numero_meis_cnae", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 8865, "name": "Empregados dos MEIs", "slug": "empregados_meis_cnae", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },

    # ------------------------------------------------------------------
    # EXPANSÃO FASE 2: TRABALHO, RENDIMENTO E DESLOCAMENTO
    # ------------------------------------------------------------------
    {
        "id": "CENSO22_RENDA_PC",
        "group": "TRABALHO_RENDA",
        "name": "Censo 2022 - Rendimento Domiciliar Per Capita por Cor ou Raça (Tabela 10295)",
        "table": 10295,
        "classification": 86,
        "extra_classifications": {2: 6794, 58: 95253},
        "category_source": "CENSO22_COR_RACA_CATEGORIES",
        "level": "N6",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 13431,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Demográfico 2022 (Somente 2022 - Indicador Não-Aditivo)",
        "notice_text": (
            "Rendimento nominal mensal domiciliar per capita médio e mediano em Reais (apenas 2022, N6). "
            "Como indicador de média/mediana, os relatórios utilizam média do recorte e desativam Lorenz."
        ),
        "variables": [
            {"id": 13431, "name": "Rendimento Domiciliar Per Capita Médio", "slug": "renda_pc_media", "unit": "Reais", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 13534, "name": "Rendimento Domiciliar Per Capita Mediano", "slug": "renda_pc_mediana", "unit": "Reais", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 13604, "name": "Moradores Considerados", "slug": "moradores_renda_pc", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "CENSO22_TRAB_CNAE",
        "group": "TRABALHO_RENDA",
        "name": "Censo 2022 - Ocupados e Rendimento do Trabalho por Seção CNAE (Tabela 10286)",
        "table": 10286,
        "classification": 11805,
        "extra_classifications": {2: 6794, 526: 15349},
        "category_source": "CENSO22_CNAE_CATEGORIES",
        "level": "N6",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 13536,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Demográfico 2022 (Somente ano 2022)",
        "notice_text": (
            "Rendimento mensal nominal médio/mediano de todos os trabalhos e total de pessoas de 14+ anos "
            "ocupadas por seção de atividade econômica (dados censitários da amostra, apenas 2022)."
        ),
        "variables": [
            {"id": 13536, "name": "Rendimento Médio Mensal do Trabalho", "slug": "renda_trabalho_media", "unit": "Reais", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 13537, "name": "Rendimento Mediano Mensal do Trabalho", "slug": "renda_trabalho_mediana", "unit": "Reais", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 13535, "name": "Pessoas Ocupadas com Rendimento", "slug": "ocupados_com_rendimento", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 1013535, "name": "Participação (%) na Seção CNAE", "slug": "pct_ocupados_cnae", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
        ],
    },
    {
        "id": "CENSO22_FORCA_TRAB",
        "group": "TRABALHO_RENDA",
        "name": "Censo 2022 - Força de Trabalho, Ocupação e Desocupação 14+ (Tabela 9517)",
        "table": 9517,
        "classification": 629,
        "extra_classifications": {2: 6794, 86: 95251, 1568: 120704},
        "category_source": "CENSO22_FORCA_CATEGORIES",
        "default_cat": 32387,
        "level": "N6",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 1641,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Demográfico 2022 (Somente ano 2022)",
        "notice_text": (
            "População de 14 anos ou mais segundo condição na força de trabalho (ocupada, desocupada "
            "ou fora da força de trabalho) no Censo Demográfico 2022 (nível municipal N6)."
        ),
        "variables": [
            {"id": 1641, "name": "Pessoas de 14 Anos ou Mais", "slug": "pessoas_forca_trabalho", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 1001641, "name": "Participação (%) no Total 14+", "slug": "pct_forca_trabalho", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
        ],
    },
    {
        "id": "CENSO22_DESLOCAMENTO",
        "group": "TRABALHO_RENDA",
        "name": "Censo 2022 - Tempo de Deslocamento Casa-Trabalho (Tabela 10331)",
        "table": 10331,
        "classification": 537,
        "extra_classifications": {2: 6794, 86: 95251, 386: 9680},
        "category_source": "CENSO22_DESLOCAMENTO_CATEGORIES",
        "default_cat": 19431,
        "level": "N6",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 1013556,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Demográfico 2022 - Mobilidade (Somente 2022)",
        "notice_text": (
            "Tempo habitual de deslocamento do domicílio até o trabalho principal para pessoas de 10+ anos "
            "que trabalhavam fora de casa (apenas 2022, N6)."
        ),
        "variables": [
            {"id": 1013556, "name": "Percentual dos Trabalhadores na Faixa (%)", "slug": "pct_deslocamento", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 13556, "name": "Pessoas na Faixa de Deslocamento", "slug": "pessoas_deslocamento", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "PNAD_DESOCUPACAO_UF",
        "group": "TRABALHO_RENDA",
        "name": "PNAD Contínua - Taxa de Desocupação e Subutilização por UF (N3 - 2012–2T/2026 - Tabela 4099)",
        "table": 4099,
        "classification": None,
        "level": "N3",
        "partial_n6": True,
        "periodicity": "quarterly",
        "min_year": 2012,
        "max_year": 2026,
        "valid_years": _PNAD_DES_VALID,
        "period_map": _PNAD_DES_MAP,
        "period_labels": _PNAD_DES_LABELS,
        "default_years": [202602],
        "default_var": 4099,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "PNAD Contínua Trimestral (Nível Estadual N3 - 1T a 4T até 2T/2026)",
        "notice_text": (
            "Pesquisa amostral divulgada integralmente apenas em nível Estadual (N3 - 27 UFs; "
            "em N6 contempla só capitais). Disponibiliza todos os trimestres (1T a 4T até 2T/2026) "
            "além da média anual consolidada (1T a 4T) para cada ano fechado."
        ),
        "variables": [
            {"id": 4099, "name": "Taxa de Desocupação (%)", "slug": "taxa_desocupacao", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 4114, "name": "Taxa Combinada de Desocupação e Subocupação (%)", "slug": "taxa_desocup_subocup", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 4116, "name": "Taxa Combinada Desocupação + Força Potencial (%)", "slug": "taxa_forca_potencial", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 4118, "name": "Taxa Composta de Subutilização (%)", "slug": "taxa_subutilizacao", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
        ],
    },
    {
        "id": "PNAD_RENDIMENTO_UF",
        "group": "TRABALHO_RENDA",
        "name": "PNAD Contínua - Rendimento Médio Real do Trabalho por UF (N3 - Até 2T/2026 - Tabela 5436)",
        "table": 5436,
        "classification": 2,
        "category_source": "CENSO22_SEXO_CATEGORIES",
        "level": "N3",
        "partial_n6": True,
        "periodicity": "quarterly",
        "min_year": 2012,
        "max_year": 2026,
        "valid_years": _PNAD_REND_VALID_YEARS,
        "period_map": _PNAD_REND_MAP,
        "period_labels": _PNAD_REND_LABELS,
        "default_years": [202602],
        "default_var": 5933,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "PNAD Contínua Rendimento Real (N3 - Lacuna Pandemia 2T/2020 a 1T/2022)",
        "notice_text": (
            "Divulgado em nível Estadual (N3 - 27 UFs) em Reais reais deflacionados, com trimestres 1T a 4T até 2T/2026 "
            "(202602) e média anual nos anos completos. Os trimestres de 2T/2020 a 1T/2022 não foram publicados nesta "
            "tabela durante a pandemia (permanecem disponíveis 1T/2020 e de 2T/2022 em diante)."
        ),
        "variables": [
            {"id": 5933, "name": "Rendimento Médio Real Habitual (Todos os Trabalhos)", "slug": "renda_real_todos_hab", "unit": "Reais", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 5932, "name": "Rendimento Médio Real Habitual (Trabalho Principal)", "slug": "renda_real_princ_hab", "unit": "Reais", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 5935, "name": "Rendimento Médio Real Efetivo (Todos os Trabalhos)", "slug": "renda_real_todos_efet", "unit": "Reais", "multiplier": 1.0, "agg_mode": "mean"},
        ],
    },

    # ------------------------------------------------------------------
    # EXPANSÃO FASE 2: DEMOGRAFIA, EDUCAÇÃO, POVOS E INCLUSÃO SOCIAL
    # ------------------------------------------------------------------
    {
        "id": "CENSO22_ENVELHECIMENTO",
        "group": "DEMOGRAFIA_EDUCACAO",
        "name": "Censo 2022 - Índice de Envelhecimento, Idade Mediana e Razão de Sexo (Tabela 9515)",
        "table": 9515,
        "classification": None,
        "level": "N6",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 10612,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Demográfico 2022 - Estrutura Etária (Somente 2022)",
        "notice_text": (
            "Indicadores sintéticos municipais (N6) disponíveis apenas para 2022: Índice de Envelhecimento "
            "(idosos 60+/65+ por 100 crianças), Idade Mediana (em anos) e Razão de Sexo (homens por 100 mulheres)."
        ),
        "variables": [
            {"id": 10612, "name": "Índice de Envelhecimento", "slug": "indice_envelhecimento", "unit": "Razão", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 10613, "name": "Idade Mediana da População", "slug": "idade_mediana", "unit": "Anos", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 8845, "name": "Razão de Sexo", "slug": "razao_sexo", "unit": "Razão", "multiplier": 1.0, "agg_mode": "mean"},
        ],
    },
    {
        "id": "CENSO22_COR_RACA",
        "group": "DEMOGRAFIA_EDUCACAO",
        "name": "Censos 2010 e 2022 - População Residente por Cor ou Raça (Tabela 9605)",
        "table": 9605,
        "classification": 86,
        "category_source": "CENSO22_COR_RACA_CATEGORIES",
        "level": "N6",
        "min_year": 2010,
        "max_year": 2022,
        "valid_years": [2022, 2010],
        "default_years": [2022],
        "default_var": 1000093,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censos Demográficos - Apenas 2010 e 2022",
        "notice_text": (
            "Composição étnico-racial da população municipal disponível exclusivamente nos anos censitários de 2010 e 2022."
        ),
        "variables": [
            {"id": 1000093, "name": "Percentual da População Total (%)", "slug": "pct_cor_raca", "unit": "Percentual", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 93, "name": "População Residente", "slug": "pop_cor_raca", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "CENSO22_INSTRUCAO",
        "group": "DEMOGRAFIA_EDUCACAO",
        "name": "Censo 2022 - Nível de Instrução da População de 18+ Anos (Tabela 10061)",
        "table": 10061,
        "classification": 1568,
        "extra_classifications": {58: 95253, 2: 6794, 86: 95251},
        "category_source": "CENSO22_INSTRUCAO_CATEGORIES",
        "default_cat": 99713,
        "level": "N6",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 1002667,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Demográfico 2022 - Escolaridade (Somente 2022)",
        "notice_text": (
            "Distribuição educacional das pessoas com 18 anos ou mais (do ensino sem instrução ao superior completo) "
            "para o ano de 2022 (nível municipal N6)."
        ),
        "variables": [
            {"id": 1002667, "name": "Percentual da População 18+ (%)", "slug": "pct_instrucao_18mais", "unit": "Percentual", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 2667, "name": "Pessoas de 18 Anos ou Mais", "slug": "pessoas_instrucao_18mais", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "CENSO22_ANOS_ESTUDO",
        "group": "DEMOGRAFIA_EDUCACAO",
        "name": "Censo 2022 - Anos Médios de Estudo por Faixa Etária (Tabela 10062)",
        "table": 10062,
        "classification": 58,
        "extra_classifications": {2: 6794, 86: 95251},
        "category_source": "CENSO22_IDADE_ESTUDO_CATEGORIES",
        "default_cat": 108866,
        "level": "N6",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 13285,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Demográfico 2022 (Somente 2022)",
        "notice_text": (
            "Número médio de anos de estudo concluídos com aprovação pelas pessoas de 11 anos ou mais "
            "(categoria padrão: 25 anos ou mais) em 2022 (N6)."
        ),
        "variables": [
            {"id": 13285, "name": "Número Médio de Anos de Estudo", "slug": "anos_medios_estudo", "unit": "Anos", "multiplier": 1.0, "agg_mode": "mean"},
        ],
    },
    {
        "id": "CENSO22_INDIGENAS",
        "group": "DEMOGRAFIA_EDUCACAO",
        "name": "Censo 2022 - População Indígena por Critério de Declaração (Tabela 9718)",
        "table": 9718,
        "classification": 1714,
        "extra_classifications": {2661: 32776},
        "category_source": "CENSO22_INDIGENA_CATEGORIES",
        "level": "N6",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 350,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo 2022 - População Indígena (Somente 2022 / Ocorrência Local)",
        "notice_text": (
            "Dados do Censo 2022 (N6). Municípios sem população indígena identificada ou com valores zerados "
            "podem aparecer sem preenchimento (-) no SIDRA."
        ),
        "variables": [
            {"id": 350, "name": "Pessoas Indígenas", "slug": "pessoas_indigenas", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 4727, "name": "Percentual na População Residente (%)", "slug": "pct_indigenas", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
        ],
    },
    {
        "id": "CENSO22_QUILOMBOLAS",
        "group": "DEMOGRAFIA_EDUCACAO",
        "name": "Censo 2022 - População Quilombola por Localização (Tabela 9578)",
        "table": 9578,
        "classification": 2661,
        "category_source": "CENSO22_QUILOMBOLA_LOC_CATEGORIES",
        "level": "N6",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 4709,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo 2022 - População Quilombola (Somente 2022 / Cobertura Esparsa)",
        "notice_text": (
            "Levantamento inédito do Censo 2022 (N6). Apenas municípios onde foram identificadas localidades "
            "quilombolas possuem registros; os demais permanecem sem preenchimento (-)."
        ),
        "variables": [
            {"id": 4709, "name": "Pessoas Quilombolas", "slug": "pessoas_quilombolas", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 4728, "name": "Percentual na População Residente (%)", "slug": "pct_quilombolas", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
        ],
    },
    {
        "id": "CENSO22_RELIGIAO",
        "group": "DEMOGRAFIA_EDUCACAO",
        "name": "Censo 2022 - População Residente 10+ Anos por Religião (Tabela 9537)",
        "table": 9537,
        "classification": 133,
        "extra_classifications": {2: 6794, 58: 95253},
        "category_source": "CENSO22_RELIGIAO_CATEGORIES",
        "default_cat": 95263,
        "level": "N6",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 13495,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Demográfico 2022 - Religiões (Somente 2022)",
        "notice_text": (
            "Distribuição da população de 10 anos ou mais por grupo religioso no Censo 2022 (apenas 2022, N6)."
        ),
        "variables": [
            {"id": 13495, "name": "Percentual por Religião (%)", "slug": "pct_religiao", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 140, "name": "Pessoas de 10 Anos ou Mais", "slug": "pessoas_religiao", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "CENSO22_PCD",
        "group": "DEMOGRAFIA_EDUCACAO",
        "name": "Censo 2022 - Pessoas com Deficiência 2+ Anos (Tabela 10125)",
        "table": 10125,
        "classification": 2,
        "extra_classifications": {58: 95253},
        "category_source": "CENSO22_SEXO_CATEGORIES",
        "level": "N6",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 13403,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Demográfico 2022 - Pessoas com Deficiência (Somente 2022)",
        "notice_text": (
            "Prevalência e contingente de pessoas de 2 anos ou mais com deficiência funcional nos municípios (apenas 2022, N6)."
        ),
        "variables": [
            {"id": 13403, "name": "Percentual com Deficiência (%)", "slug": "pct_pcd", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 12785, "name": "Pessoas com Deficiência", "slug": "pessoas_pcd", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },

    # ------------------------------------------------------------------
    # EXPANSÃO FASE 2: SANEAMENTO (PNSB), HABITAÇÃO E GESTÃO MUNICIPAL
    # ------------------------------------------------------------------
    {
        "id": "AREAS_URBANIZADAS",
        "group": "SANEAMENTO_GESTAO_URBANA",
        "name": "Áreas Urbanizadas do Brasil - Mancha Urbana e Vazios (2019 e 2022 - Tabela 10763)",
        "table": 10763,
        "classification": None,
        "level": "N6",
        "min_year": 2019,
        "max_year": 2022,
        "valid_years": [2022, 2019],
        "default_years": [2022],
        "default_var": 14214,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Áreas Urbanizadas (IBGE - Somente 2019 e 2022)",
        "notice_text": (
            "Mapeamento morfológico por imagem orbital em km² por município (N6), publicado para 2019 e 2022. "
            "Separa mancha densa, pouco densa, loteamentos vazios e vazios intraurbanos."
        ),
        "variables": [
            {"id": 14214, "name": "Áreas Urbanizadas, Equipamentos e Vazios (Total)", "slug": "area_urbanizada_total", "unit": "km²", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 12749, "name": "Áreas Urbanizadas (Propriamente Ditas)", "slug": "area_urbanizada_pura", "unit": "km²", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 14211, "name": "Áreas Urbanizadas Densas", "slug": "area_urb_densa", "unit": "km²", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 14212, "name": "Áreas Urbanizadas Pouco Densas", "slug": "area_urb_pouco_densa", "unit": "km²", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 12750, "name": "Loteamentos Vazios", "slug": "loteamentos_vazios", "unit": "km²", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 12753, "name": "Vazios Intraurbanos", "slug": "vazios_intraurbanos", "unit": "km²", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 12752, "name": "Outros Equipamentos Urbanos", "slug": "outros_equip_urbanos", "unit": "km²", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "CENSO22_FAVELAS_NUM",
        "group": "HABITACAO_FAVELAS",
        "name": "Censo 2022 - Número de Favelas e Comunidades Urbanas (Tabela 9883)",
        "table": 9883,
        "classification": None,
        "level": "N6",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 9910,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Favelas e Comunidades Urbanas - Apenas Municípios Ocorrentes (2022)",
        "notice_text": (
            "O IBGE publica nesta tabela (2022, N6) exclusivamente os municípios em que foram identificadas "
            "favelas e comunidades urbanas; os demais municípios permanecem com valor zero na malha."
        ),
        "variables": [
            {"id": 9910, "name": "Número de Favelas e Comunidades Urbanas", "slug": "numero_favelas", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "CENSO22_FAVELAS_POP",
        "group": "HABITACAO_FAVELAS",
        "name": "Censo 2022 - População em Favelas e Comunidades Urbanas (Tabela 9884)",
        "table": 9884,
        "classification": 86,
        "extra_classifications": {2: 6794, 58: 95253},
        "category_source": "CENSO22_COR_RACA_CATEGORIES",
        "level": "N6",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 9612,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "População em Favelas - Apenas Municípios Ocorrentes (2022)",
        "notice_text": (
            "Somente municípios com favelas identificadas no Censo 2022 possuem contagem positiva nesta tabela (N6)."
        ),
        "variables": [
            {"id": 9612, "name": "População Residente em Favelas", "slug": "pop_favelas", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 1009612, "name": "Percentual por Cor/Raça em Favelas (%)", "slug": "pct_cor_favelas", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
        ],
    },
    {
        "id": "CENSO22_DOMICILIOS_OCUP",
        "group": "HABITACAO_FAVELAS",
        "name": "Censo 2022 - Domicílios por Condição de Ocupação (Próprio, Alugado, Cedido - Tabela 9930)",
        "table": 9930,
        "classification": 63,
        "extra_classifications": {65: 95810, 125: 2932},
        "category_source": "CENSO22_OCUP_DOM_CATEGORIES",
        "default_cat": 1055,
        "level": "N6",
        "min_year": 2022,
        "max_year": 2022,
        "valid_years": [2022],
        "default_years": [2022],
        "default_var": 1000381,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Censo Demográfico 2022 - Posse Domiciliar (Somente 2022)",
        "notice_text": (
            "Domicílios particulares permanentes ocupados segundo condição de posse (próprio quitado, financiando, "
            "alugado, cedido) exclusivamente para 2022 (N6)."
        ),
        "variables": [
            {"id": 1000381, "name": "Percentual dos Domicílios (%)", "slug": "pct_cond_ocupacao", "unit": "Percentual", "multiplier": 1.0, "agg_mode": "mean"},
            {"id": 381, "name": "Quantidade de Domicílios", "slug": "domicilios_cond_ocupacao", "unit": "Domicílios", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "PNSB_AGUA",
        "group": "SANEAMENTO_GESTAO_URBANA",
        "name": "PNSB 2017 - Volume e Ligações de Abastecimento de Água (Tabela 7499)",
        "table": 7499,
        "classification": 988,
        "category_source": "PNSB_AGUA_LIG_CATEGORIES",
        "level": "N6",
        "min_year": 2017,
        "max_year": 2017,
        "valid_years": [2017],
        "default_years": [2017],
        "default_var": 448,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "PNSB Saneamento Básico (Somente 2017)",
        "notice_text": (
            "Pesquisa Nacional de Saneamento Básico com dados de engenharia sanitária (m³/dia, ligações e "
            "micromedição) divulgados exclusivamente para o ano de 2017 (N6)."
        ),
        "variables": [
            {"id": 448, "name": "Volume de Água Consumido por Dia", "slug": "vol_agua_consumido_dia", "unit": "Metros cúbicos", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 10739, "name": "Volume de Água Faturado por Dia", "slug": "vol_agua_faturado_dia", "unit": "Metros cúbicos", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 10711, "name": "Ligações Ativas Abastecidas", "slug": "ligacoes_ativas_agua", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 10738, "name": "Ligações Ativas Micromedidas", "slug": "ligacoes_micromedidas_agua", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 339, "name": "Economias Ativas Abastecidas", "slug": "economias_ativas_agua", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "PNSB_ESGOTO",
        "group": "SANEAMENTO_GESTAO_URBANA",
        "name": "PNSB 2017 - Coleta de Esgoto Sanitário (Volume m³/dia e Ligações - Tabela 7510)",
        "table": 7510,
        "classification": 988,
        "category_source": "PNSB_ESGOTO_LIG_CATEGORIES",
        "level": "N6",
        "min_year": 2017,
        "max_year": 2017,
        "valid_years": [2017],
        "default_years": [2017],
        "default_var": 768,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "PNSB Esgotamento Sanitário (Somente 2017 - Rede Coletora Pública)",
        "notice_text": (
            "Dados da PNSB disponíveis exclusivamente para 2017 (N6). Municípios sem serviço de coleta pública "
            "de esgoto por rede geral aparecem sem registro (-) na tabela."
        ),
        "variables": [
            {"id": 768, "name": "Volume de Esgoto Coletado por Dia", "slug": "vol_esgoto_coletado_dia", "unit": "Metros cúbicos", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 10751, "name": "Volume de Esgoto Faturado por Dia", "slug": "vol_esgoto_faturado_dia", "unit": "Metros cúbicos", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 10748, "name": "Ligações Ativas Esgotadas", "slug": "ligacoes_esgotadas", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
            {"id": 446, "name": "Economias Ativas Esgotadas", "slug": "economias_esgotadas", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
        ],
    },
    {
        "id": "MUNIC_PLANO_DIRETOR",
        "group": "SANEAMENTO_GESTAO_URBANA",
        "name": "MUNIC 2021 - Existência de Plano Diretor Municipal (Tabela 5882)",
        "table": 5882,
        "classification": 1480,
        "extra_classifications": {12446: 47692},
        "category_source": "MUNIC_PLANO_DIRETOR_CATEGORIES",
        "default_cat": 58279,
        "level": "N6",
        "min_year": 2021,
        "max_year": 2021,
        "valid_years": [2021],
        "default_years": [2021],
        "default_var": 603,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "MUNIC Cadastral Binária (Somente 2021)",
        "notice_text": (
            "Pesquisa cadastral com indicador binário (N6, ano 2021): valor 1 indica municípios que atendem à condição "
            "(ex.: Com Plano Diretor); municípios sem o instrumento retornam '-' e ficam na classe Não/Sem registro."
        ),
        "variables": [
            {"id": 603, "name": "Município Enquadrado (Indicador Sim = 1)", "slug": "munic_plano_diretor", "unit": "Municípios", "multiplier": 1.0, "agg_mode": "last", "is_binary": True},
        ],
    },
    {
        "id": "MUNIC_ALAGAMENTOS",
        "group": "RISCOS_DESASTRES_DEFESA_CIVIL",
        "name": "MUNIC 2020 - Municípios Atingidos por Alagamentos nos Últimos 4 Anos (Tabela 8535)",
        "table": 8535,
        "classification": 1195,
        "extra_classifications": {12446: 47692, 1196: 50808},
        "category_source": "MUNIC_ALAGAMENTO_CATEGORIES",
        "default_cat": 50806,
        "level": "N6",
        "min_year": 2020,
        "max_year": 2020,
        "valid_years": [2020],
        "default_years": [2020],
        "default_var": 603,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "MUNIC Cadastral Binária - Riscos Ambientais (Somente 2020)",
        "notice_text": (
            "Pesquisa cadastral com indicador binário (N6, ano 2020): valor 1 identifica municípios atingidos por alagamentos "
            "nos 4 anos anteriores (categoria padrão); demais constam na classe Não/Sem registro."
        ),
        "variables": [
            {"id": 603, "name": "Município Atingido (Indicador Sim = 1)", "slug": "munic_alagamentos", "unit": "Municípios", "multiplier": 1.0, "agg_mode": "last", "is_binary": True},
        ],
    },
    {
        "id": "MUNIC_COMPRAS_AF",
        "group": "AGRO_VEGETAL",
        "name": "MUNIC 2023 - Compras Públicas da Agricultura Familiar (PNAE/PAA - Tabela 10384)",
        "table": 10384,
        "classification": 2094,
        "extra_classifications": {12446: 47692},
        "category_source": "MUNIC_AAF_PROG_CATEGORIES",
        "default_cat": 79300,
        "level": "N6",
        "min_year": 2023,
        "max_year": 2023,
        "valid_years": [2023],
        "default_years": [2023],
        "default_var": 13191,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "MUNIC Cadastral Binária (Somente 2023)",
        "notice_text": (
            "Indicador binário municipal (N6, ano 2023): valor 1 identifica prefeituras que declararam compras da "
            "agricultura familiar (Total = pelo menos um programa; ou filtre PNAE, PAA, estaduais ou próprios)."
        ),
        "variables": [
            {"id": 13191, "name": "Município com Compras (Indicador Sim = 1)", "slug": "munic_compras_af", "unit": "Municípios", "multiplier": 1.0, "agg_mode": "last", "is_binary": True},
        ],
    },

    # ------------------------------------------------------------------
    # EXPANSÃO FASE 2: REGISTRO CIVIL (2003–2024)
    # ------------------------------------------------------------------
    {
        "id": "RC_NASCIDOS_VIVOS",
        "group": "REGISTRO_CIVIL",
        "name": "Registro Civil - Nascidos Vivos por Município de Residência da Mãe (2003–2024 - Tabela 2609)",
        "table": 2609,
        "classification": 240,
        "extra_classifications": {232: 0, 2: 0},
        "category_source": "RC_IDADE_MAE_CATEGORIES",
        "level": "N6",
        "min_year": 2003,
        "max_year": 2024,
        "default_years": [2024, 2023],
        "default_var": 217,
        "notice_severity": "info",
        "popup_notice": False,
        "notice_title": "Estatísticas do Registro Civil - Série 2003 a 2024",
        "notice_text": (
            "Registros de nascidos vivos por município de residência da mãe (N6), disponíveis de 2003 a 2024 "
            "(com abertura opcional por grupo de idade da mãe na ocasião do parto)."
        ),
        "variables": [
            {"id": 217, "name": "Nascidos Vivos Registrados", "slug": "nascidos_vivos", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "sum"},
        ],
    },
    {
        "id": "RC_OBITOS",
        "group": "REGISTRO_CIVIL",
        "name": "Registro Civil - Óbitos Ocorridos por Natureza e Residência do Falecido (2003–2024 - Tabela 2654)",
        "table": 2654,
        "classification": 1836,
        "extra_classifications": {244: 0, 2: 0, 260: 0, 257: 0},
        "category_source": "RC_OBITO_NAT_CATEGORIES",
        "level": "N6",
        "min_year": 2003,
        "max_year": 2024,
        "default_years": [2024, 2023],
        "default_var": 343,
        "notice_severity": "info",
        "popup_notice": False,
        "notice_title": "Registro Civil (Óbitos) - Série 2003 a 2024",
        "notice_text": (
            "Óbitos por município de residência do falecido (N6) entre 2003 e 2024, segmentados por natureza "
            "(Total, Natural ou Não natural/causas externas)."
        ),
        "variables": [
            {"id": 343, "name": "Número de Óbitos Ocorridos", "slug": "numero_obitos", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "sum"},
        ],
    },
    {
        "id": "RC_CASAMENTOS",
        "group": "REGISTRO_CIVIL",
        "name": "Registro Civil - Casamentos por Município do Registro (2013–2024 - Tabela 4412)",
        "table": 4412,
        "classification": 664,
        "extra_classifications": {244: 0, 665: 0, 666: 0, 667: 0},
        "category_source": "RC_ESTADO_CIVIL_CATEGORIES",
        "level": "N6",
        "min_year": 2013,
        "max_year": 2024,
        "default_years": [2024, 2023],
        "default_var": 4993,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Registro Civil (Casamentos) - Série Iniciada em 2013 (2013 a 2024)",
        "notice_text": (
            "Tabela com casamentos civis segundo local do cartório de registro (N6) disponível apenas de 2013 a 2024 "
            "(inclui recorte por arranjo conjugal entre cônjuges)."
        ),
        "variables": [
            {"id": 4993, "name": "Número Total de Casamentos", "slug": "numero_casamentos", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 221, "name": "Casamentos entre Cônjuges Masculino e Feminino", "slug": "casamentos_masc_fem", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 4373, "name": "Casamentos entre Cônjuges Masculinos", "slug": "casamentos_masc_masc", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "sum"},
            {"id": 4374, "name": "Casamentos entre Cônjuges Femininos", "slug": "casamentos_fem_fem", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "sum"},
        ],
    },
]

SURVEYS.extend(
    build_phase3_surveys(
        _build_monthly_periods,
        _build_quarterly_periods,
        _build_semiannual_periods,
    )
)
SURVEYS.extend(build_phase4_surveys())
SURVEYS.extend(build_phase5_surveys())
SURVEYS.extend(build_phase6_surveys())
SURVEYS.extend(build_phase7_surveys())
SURVEYS.extend(build_phase8_surveys())
SURVEYS.extend(build_phase9_surveys())
SURVEYS.extend(build_phase10_surveys())
SURVEYS.extend(build_phase11_surveys())
SURVEYS.extend(build_phase12_surveys())
SURVEYS.extend(build_phase13_surveys())
SURVEYS.extend(build_phase14_surveys())

# --------------------------------------------------------------------------
# Reorganização taxonômica canônica em 21 áreas temáticas puras (+ ALL = 22)
# Elimina sobreposições (Urbano x Habitação x Favelas), separa Vulnerabilidade
# Territorial/Riscos do Sistema Financeiro/Bancarização e devolve Crédito Rural ao Agro.
# --------------------------------------------------------------------------
CANONICAL_SURVEY_GROUP_REMAP: Dict[str, str] = {
    # 1. Antigo URBANO_SANEAMENTO_GESTAO desmembrado e redistribuído
    "CENSO22_ENTORNO_URBANISTICO": "HABITACAO_FAVELAS",
    "CENSO22_DOMICILIOS_OCUP": "HABITACAO_FAVELAS",
    "CENSO22_FAVELAS_NUM": "HABITACAO_FAVELAS",
    "CENSO22_FAVELAS_POP": "HABITACAO_FAVELAS",
    "MUNIC_COMPRAS_AF": "AGRO_VEGETAL",
    "MUNIC_MEIO_AMBIENTE": "MEIO_AMBIENTE_CLIMA_ODS",
    "MUNIC_ALAGAMENTOS": "RISCOS_DESASTRES_DEFESA_CIVIL",
    "MUNIC_SECA_ESTIAGEM": "RISCOS_DESASTRES_DEFESA_CIVIL",
    "MUNIC_SEGURANCA_ALIMENTAR": "TRABALHO_RENDA",
    "MUNIC_MULHERES_ABRIGO": "SEGURANCA_DEFESA_SOCIAL",
    "MUNIC_SEGURANCA_PUBLICA": "SEGURANCA_DEFESA_SOCIAL",
    "MUNIC_PRIMEIRA_INFANCIA": "INFANCIA_JUVENTUDE_ESCOLAS",
    "MUNIC_CRECHES": "INFANCIA_JUVENTUDE_ESCOLAS",
    "MUNIC_CONSELHO_TUTELAR": "INFANCIA_JUVENTUDE_ESCOLAS",
    "MUNIC_REDE_SUAS_CRAS": "DEMOGRAFIA_EDUCACAO",
    "MUNIC_BENEFICIOS_EVENTUAIS": "DEMOGRAFIA_EDUCACAO",
    "MUNIC_CONSELHO_ASSISTENCIA": "DEMOGRAFIA_EDUCACAO",
    "MUNIC_TRANSPORTE_ONIBUS": "TRANSPORTE_MOBILIDADE",
    "MUNIC_CULTURA_PLANO": "CULTURA_TURISMO_ESPORTE",
    "MUNIC_FUNDOS_CULTURA_SAUDE": "CULTURA_TURISMO_ESPORTE",
    "MUNIC_ESPORTE_INSTALACOES": "CULTURA_TURISMO_ESPORTE",
    "CENSO22_ESGOTAMENTO": "SANEAMENTO_GESTAO_URBANA",
    "CENSO22_AGUA": "SANEAMENTO_GESTAO_URBANA",
    "CENSO22_LIXO": "SANEAMENTO_GESTAO_URBANA",
    "AREAS_URBANIZADAS": "SANEAMENTO_GESTAO_URBANA",
    "PNSB_AGUA": "SANEAMENTO_GESTAO_URBANA",
    "PNSB_ESGOTO": "SANEAMENTO_GESTAO_URBANA",
    "MUNIC_PLANO_DIRETOR": "SANEAMENTO_GESTAO_URBANA",
    "PNSB_REDE_ESGOTO": "SANEAMENTO_GESTAO_URBANA",
    "PNSB_ETES_ESGOTO": "SANEAMENTO_GESTAO_URBANA",
    "PNSB_RESIDUOS_SOLIDOS": "SANEAMENTO_GESTAO_URBANA",
    "PNSB_DRENAGEM_URBANA": "SANEAMENTO_GESTAO_URBANA",
    "MUNIC_PGIRS_RESIDUOS": "SANEAMENTO_GESTAO_URBANA",
    "PNAD_ANUAL_AGUA_UF": "SANEAMENTO_GESTAO_URBANA",
    "PNAD_ANUAL_ESGOTO_UF": "SANEAMENTO_GESTAO_URBANA",
    "PNAD_ANUAL_LIXO_UF": "SANEAMENTO_GESTAO_URBANA",
    "PNAD_ANUAL_ENERGIA_UF": "SANEAMENTO_GESTAO_URBANA",

    # 2. Antigo HABITACAO_FAVELAS_URBANO -> HABITACAO_FAVELAS

    # 3. Antigo VULNERABILIDADE_DESASTRES_BANCARIZACAO desmembrado
    "BACEN_AGENCIAS_BANCARIAS": "SISTEMA_FINANCEIRO_CREDITO",
    "BACEN_OPERACOES_CREDITO": "SISTEMA_FINANCEIRO_CREDITO",
    "BACEN_DEPOSITOS_POUPANCA": "SISTEMA_FINANCEIRO_CREDITO",
    "BACEN_DEPOSITOS_VISTA": "SISTEMA_FINANCEIRO_CREDITO",
    "BACEN_DEPOSITOS_PRAZO": "SISTEMA_FINANCEIRO_CREDITO",
    "BACEN_OBRIGACOES_RECEBIMENTO": "SISTEMA_FINANCEIRO_CREDITO",
    "ODS_8101_AGENCIAS_ATMS": "SISTEMA_FINANCEIRO_CREDITO",
    "ODS_8102_BANCARIZACAO_ADULTOS": "SISTEMA_FINANCEIRO_CREDITO",
    "ODS_1051_INADIMPLENCIA_CREDITO": "SISTEMA_FINANCEIRO_CREDITO",
    "ODS_932_MICROEMPRESAS_CREDITO": "SISTEMA_FINANCEIRO_CREDITO",
    "CENSO_AGRO_CREDITO_AGENTES": "AGRO_VEGETAL",
    "CEMADEN_POPULACAO_RISCO": "RISCOS_DESASTRES_DEFESA_CIVIL",
    "CEMADEN_DOMICILIOS_RISCO": "RISCOS_DESASTRES_DEFESA_CIVIL",
    "CEMADEN_IDOSOS_RISCO": "RISCOS_DESASTRES_DEFESA_CIVIL",
    "PNSB_AREAS_RISCO_DRENAGEM": "RISCOS_DESASTRES_DEFESA_CIVIL",
    "PNSB_INUNDACOES_ALAGAMENTOS_URBANOS": "RISCOS_DESASTRES_DEFESA_CIVIL",
    "PNSB_FATORES_AGRAVANTES_ENCHENTES": "RISCOS_DESASTRES_DEFESA_CIVIL",
    "PNSB_EXTENSAO_AREAS_INUNDADAS": "RISCOS_DESASTRES_DEFESA_CIVIL",
    "MUNIC_PMRR_INSTRUMENTOS_RISCO": "RISCOS_DESASTRES_DEFESA_CIVIL",
    "MUNIC_MONITORAMENTO_ALERTA_RISCO": "RISCOS_DESASTRES_DEFESA_CIVIL",
    "MUNIC_HABITACAO_AREAS_RISCO": "RISCOS_DESASTRES_DEFESA_CIVIL",
    "MUNIC_DEFESA_CIVIL_RECURSOS_ESTRUTURA": "RISCOS_DESASTRES_DEFESA_CIVIL",
    "ODS_1152_PERDAS_ECONOMICAS_DESASTRES": "RISCOS_DESASTRES_DEFESA_CIVIL",
    "ODS_11B2_ESTRATEGIAS_LOCAIS_DESASTRES": "RISCOS_DESASTRES_DEFESA_CIVIL",
    "ODS_11B1_MARCO_SENDAI_PAIS": "RISCOS_DESASTRES_DEFESA_CIVIL",

    # 4. Desastres naturais e defesa civil (ex-Meio Ambiente)
    "MUNIC_DESASTRES_NATURAIS": "RISCOS_DESASTRES_DEFESA_CIVIL",
    "MUNIC_RISCO_ESCORREGAMENTOS": "RISCOS_DESASTRES_DEFESA_CIVIL",
    "MUNIC_RISCO_INSTRUMENTOS": "RISCOS_DESASTRES_DEFESA_CIVIL",
    "MUNIC_RISCO_MEDIDAS_PREVENTIVAS": "RISCOS_DESASTRES_DEFESA_CIVIL",
    "MUNIC_DEFESA_CIVIL_ESTRUTURA": "RISCOS_DESASTRES_DEFESA_CIVIL",
    "ODS_POPULACAO_AFETADA_DESASTRES": "RISCOS_DESASTRES_DEFESA_CIVIL",
}

for _s in SURVEYS:
    _sid = _s.get("id", "")
    if _sid in CANONICAL_SURVEY_GROUP_REMAP:
        _s["group"] = CANONICAL_SURVEY_GROUP_REMAP[_sid]
    elif _s.get("group") == "HABITACAO_FAVELAS_URBANO":
        _s["group"] = "HABITACAO_FAVELAS"
    if "classification" not in _s:
        _s["classification"] = None
    if "extra_classifications" not in _s:
        _s["extra_classifications"] = None

# Categorias PAM (Lavouras)
PAM_CATEGORIES = [
    (0, "Total das Lavouras"),
    (40124, "Soja (em grão)"),
    (40122, "Milho (em grão)"),
    (40107, "Cebola"),
    (40102, "Arroz (em casca)"),
    (40127, "Trigo (em grão)"),
    (40139, "Café (em grão) Total"),
    (40140, "Café Arábica"),
    (40141, "Café Canephora"),
    (40106, "Cana-de-açúcar"),
    (40112, "Feijão (em grão)"),
    (40119, "Mandioca"),
    (40099, "Algodão herbáceo"),
    (40151, "Laranja"),
    (40260, "Maçã"),
    (40274, "Uva"),
    (40136, "Banana (cacho)"),
    (40113, "Fumo (em folha)"),
    (40105, "Batata-inglesa"),
    (40104, "Batata-doce"),
    (40126, "Tomate"),
    (40100, "Alho"),
    (40138, "Cacau (em amêndoa)"),
    (45982, "Açaí"),
    (40147, "Erva-mate (folha verde)"),
    (83391, "Cenoura"),
    (83396, "Morango"),
    (40120, "Melancia"),
    (40121, "Melão"),
    (40262, "Manga"),
    (40261, "Mamão"),
    (40263, "Maracujá"),
    (40152, "Limão"),
    (40271, "Tangerina"),
    (40129, "Abacate"),
    (40092, "Abacaxi*"),
    (83388, "Abóbora"),
    (83399, "Acerola"),
    (40329, "Alfafa fenada"),
    (83389, "Alface"),
    (40130, "Algodão arbóreo"),
    (40101, "Amendoim (em casca)"),
    (40103, "Aveia (em grão)"),
    (40131, "Azeitona"),
    (40137, "Borracha (látex coagulado)"),
    (40468, "Borracha (látex líquido)"),
    (40330, "Caju"),
    (40331, "Cana para forragem"),
    (83390, "Canola"),
    (40142, "Caqui"),
    (40143, "Castanha de caju"),
    (40108, "Centeio (em grão)"),
    (40109, "Cevada (em grão)"),
    (40144, "Chá-da-índia"),
    (83392, "Chuchu"),
    (40145, "Coco-da-baía*"),
    (83400, "Cupuaçu"),
    (40146, "Dendê (cacho de coco)"),
    (40110, "Ervilha (em grão)"),
    (40111, "Fava (em grão)"),
    (40148, "Figo"),
    (83395, "Gergelim"),
    (40114, "Girassol (em grão)"),
    (40149, "Goiaba"),
    (83401, "Graviola"),
    (40150, "Guaraná (semente)"),
    (83393, "Inhame"),
    (40115, "Juta (fibra)"),
    (40116, "Linho (semente)"),
    (40117, "Malva (fibra)"),
    (40118, "Mamona (baga)"),
    (40264, "Marmelo"),
    (83394, "Milho verde"),
    (40265, "Noz (fruto seco)"),
    (40266, "Palmito"),
    (40267, "Pera"),
    (40268, "Pêssego"),
    (40269, "Pimenta-do-reino"),
    (83397, "Pimentão"),
    (40123, "Rami (fibra)"),
    (83398, "Repolho"),
    (40270, "Sisal ou agave"),
    (40125, "Sorgo (em grão)"),
    (40128, "Triticale (em grão)"),
    (40272, "Tungue (fruto seco)"),
    (40273, "Urucum (semente)"),
]

PAM_MILHO_CATEGORIES = [
    (31693, "Total (Milho 1ª + 2ª safras)"),
    (114253, "Milho (em grão) - 1ª safra"),
    (114254, "Milho (em grão) - 2ª safra"),
]

PAM_FEIJAO_CATEGORIES = [
    (31693, "Total (Feijão 1ª + 2ª + 3ª safras)"),
    (117991, "Feijão (em grão) - 1ª safra"),
    (117992, "Feijão (em grão) - 2ª safra"),
    (117993, "Feijão (em grão) - 3ª safra"),
]

PAM_BATATA_CATEGORIES = [
    (31693, "Total (Batata-inglesa 1ª + 2ª + 3ª safras)"),
    (117989, "Batata-inglesa - 1ª safra"),
    (117990, "Batata-inglesa - 2ª safra"),
    (117994, "Batata-inglesa - 3ª safra"),
]

PAM_AMENDOIM_CATEGORIES = [
    (31693, "Total (Amendoim 1ª + 2ª safras)"),
    (117987, "Amendoim (em casca) - 1ª safra"),
    (117988, "Amendoim (em casca) - 2ª safra"),
]

CENSO_AGRO_TIPOLOGIA_CATEGORIES = [
    (46302, "Total dos Estabelecimentos"),
    (46304, "Agricultura familiar - sim"),
    (46303, "Agricultura familiar - não"),
    (46305, "Agricultura familiar - Pronaf B"),
    (46306, "Agricultura familiar - Pronaf V"),
    (46307, "Agricultura familiar - não pronafiano"),
    (46422, "Pronamp - sim"),
    (46423, "Pronamp - não"),
]

CENSO_AGRO_TERRAS_CATEGORIES = [
    (110087, "Total"),
    (113471, "Lavouras - temporárias"),
    (113470, "Lavouras - permanentes"),
    (40677, "Lavouras - área para cultivo de flores"),
    (113472, "Pastagens - naturais"),
    (113469, "Pastagens - plantadas em boas condições"),
    (40678, "Pastagens - plantadas em más condições"),
    (40679, "Matas ou florestas naturais - APP ou Reserva Legal"),
    (40680, "Matas ou florestas naturais (demais)"),
    (40681, "Matas ou florestas - florestas plantadas"),
    (113476, "Sistemas agroflorestais"),
    (40682, "Lâmina d'água, aquicultura, construções e terras inaproveitáveis"),
]

# Categorias PPM Rebanhos
PPM_REBANHOS_CATEGORIES = [
    (2670, "Bovino (Bovinos)"),
    (32794, "Suíno (Suínos - Total)"),
    (32795, "Suíno (Matrizes de Suínos)"),
    (32796, "Galináceos (Total)"),
    (2677, "Galináceos (Galinhas)"),
    (2676, "Ovinos"),
    (2674, "Caprinos"),
    (2672, "Equinos"),
    (2675, "Bubalinos"),
    (2681, "Codornas"),
]

# Categorias PPM Origem Animal
PPM_PRODUTOS_CATEGORIES = [
    (2682, "Leite de vaca (Mil litros)"),
    (2685, "Ovos de galinha (Mil dúzias)"),
    (2687, "Mel de abelha (Quilogramas)"),
    (2686, "Ovos de codorna (Mil dúzias)"),
    (2684, "Lã (Quilogramas)"),
    (2683, "Casulos do bicho-da-seda (Quilogramas)"),
    (0, "Total (usar apenas com Valor da Produção)"),
]

# Categorias PPM Aquicultura (Tabela 3940)
PPM_AQUICULTURA_CATEGORIES = [
    (0, "Total da Aquicultura"),
    (79366, "Peixes (Total)"),
    (32877, "Tilápia"),
    (32876, "Tambaqui"),
    (32875, "Tambacu, tambatinga"),
    (32870, "Pacu e patinga"),
    (32872, "Pintado, cachara, cachapira e pintachara, surubim"),
    (32874, "Pirarucu"),
    (32861, "Carpa"),
    (32879, "Truta"),
    (32865, "Curimatã, curimbatá"),
    (32866, "Dourado"),
    (32867, "Jatuarana, piabanha e piracanjuba"),
    (32868, "Lambari"),
    (32869, "Matrinxã"),
    (32871, "Piau, piapara, piauçu, piava"),
    (32873, "Pirapitinga"),
    (32878, "Traíra e trairão"),
    (32880, "Tucunaré"),
    (32881, "Outros peixes"),
    (32886, "Alevinos"),
    (32887, "Camarão"),
    (32888, "Larvas e pós-larvas de camarão"),
    (32889, "Ostras, vieiras e mexilhões"),
    (32890, "Sementes de moluscos"),
    (32891, "Outros produtos (rã, jacaré, siri, caranguejo, lagosta, etc.)"),
]

# Categorias PEVS Extração Vegetal (Tabela 289)
PEVS_EXTRACAO_CATEGORIES = [
    (0, "Total"),
    (3402, "1 - Alimentícios"),
    (3403, "1.1 - Açaí (fruto)"),
    (83410, "1.2 - Baru ou Cumaru (amêndoa)"),
    (83411, "1.3 - Buriti (fruto)"),
    (83412, "1.4 - Cajá (fruto)"),
    (3404, "1.5 - Castanha-de-caju"),
    (3405, "1.6 - Castanha-do-pará"),
    (83413, "1.7 - Cupuaçu (fruto)"),
    (3406, "1.8 - Erva-mate"),
    (83414, "1.9 - Juçara (fruto)"),
    (83415, "1.10 - Macaúba (fruto)"),
    (3407, "1.11 - Mangaba (fruto)"),
    (3408, "1.12 - Palmito"),
    (39409, "1.13 - Pequi (fruto)"),
    (3409, "1.14 - Pinhão"),
    (83416, "1.15 - Pupunha (fruto)"),
    (83417, "1.16 - Tucumã ou Tucum (fruto)"),
    (3410, "1.17 - Umbu (fruto)"),
    (11296, "1.18 - Outros alimentícios"),
    (3411, "2 - Aromáticos, medicinais, tóxicos e corantes"),
    (3412, "2.1 - Ipecacuanha ou poaia (raiz)"),
    (3413, "2.2 - Jaborandi (folha)"),
    (3414, "2.3 - Urucum (semente)"),
    (3415, "2.4 - Outros aromáticos"),
    (3416, "3 - Borrachas"),
    (3417, "3.1 - Caucho"),
    (3418, "3.2 - Hevea (látex coagulado)"),
    (3419, "3.3 - Hevea (látex líquido)"),
    (40524, "3.4 - Mangabeira"),
    (3420, "4 - Ceras"),
    (3421, "4.1 - Carnaúba (cera)"),
    (3422, "4.2 - Carnaúba (pó)"),
    (110011, "4.3 - Outras ceras"),
    (3423, "5 - Fibras"),
    (3424, "5.1 - Buriti (fibra)"),
    (3425, "5.2 - Carnaúba (fibra)"),
    (3426, "5.3 - Piaçava"),
    (3427, "5.4 - Outras fibras"),
    (3428, "6 - Gomas não elásticas"),
    (3429, "6.1 - Balata"),
    (3430, "6.2 - Maçaranduba"),
    (3431, "6.3 - Sorva"),
    (3433, "7.1 - Carvão vegetal (extrativo)"),
    (3434, "7.2 - Lenha (extrativa)"),
    (3435, "7.3 - Madeira em tora (extrativa)"),
    (3438, "8 - Oleaginosos"),
    (83418, "8.1 - Andiroba (amêndoa)"),
    (3439, "8.2 - Babaçu (amêndoa)"),
    (3440, "8.3 - Copaíba (óleo)"),
    (3441, "8.4 - Cumaru (amêndoa)"),
    (3442, "8.5 - Licuri (coquilho)"),
    (83419, "8.6 - Murumuru"),
    (3443, "8.7 - Oiticica (semente)"),
    (3444, "8.8 - Pequi (amêndoa)"),
    (3445, "8.9 - Tucum (amêndoa)"),
    (3446, "8.10 - Outros oleaginosos"),
    (3448, "9.1 - Pinheiro brasileiro (nó de pinho)"),
    (3449, "9.2 - Pinheiro brasileiro (árvores abatidas)"),
    (3450, "9.3 - Pinheiro brasileiro (madeira em tora)"),
    (3451, "10 - Tanantes"),
    (3452, "10.1 - Angico (casca)"),
    (3453, "10.2 - Barbatimão (casca)"),
    (3454, "10.3 - Outros tanantes"),
]

# Categorias PEVS Silvicultura (Tabela 291)
PEVS_SILVICULTURA_CATEGORIES = [
    (0, "Total"),
    (3455, "1.1 - Carvão vegetal (Total)"),
    (83420, "1.1.1 - Carvão vegetal de acácia negra"),
    (83421, "1.1.2 - Carvão vegetal de cedro australiano"),
    (33247, "1.1.3 - Carvão vegetal de eucalipto"),
    (83422, "1.1.4 - Carvão vegetal de mogno africano"),
    (33248, "1.1.5 - Carvão vegetal de pinus"),
    (83423, "1.1.6 - Carvão vegetal de teca"),
    (33249, "1.1.7 - Carvão vegetal de outras espécies"),
    (3456, "1.2 - Lenha (Total)"),
    (83424, "1.2.1 - Lenha de acácia negra"),
    (83425, "1.2.2 - Lenha de cedro australiano"),
    (33250, "1.2.3 - Lenha de eucalipto"),
    (83426, "1.2.4 - Lenha de mogno africano"),
    (33251, "1.2.5 - Lenha de pinus"),
    (83427, "1.2.6 - Lenha de teca"),
    (33252, "1.2.7 - Lenha de outras espécies"),
    (3457, "1.3 - Madeira em tora (Total)"),
    (3458, "1.3.1 - Madeira em tora para papel e celulose"),
    (83428, "1.3.1.1 - Madeira em tora de acácia negra para papel e celulose"),
    (83429, "1.3.1.2 - Madeira em tora de cedro australiano para papel e celulose"),
    (33253, "1.3.1.3 - Madeira em tora de eucalipto para papel e celulose"),
    (83430, "1.3.1.4 - Madeira em tora de mogno africano para papel e celulose"),
    (33254, "1.3.1.5 - Madeira em tora de pinus para papel e celulose"),
    (83431, "1.3.1.6 - Madeira em tora de teca para papel e celulose"),
    (33255, "1.3.1.7 - Madeira em tora de outras espécies para papel e celulose"),
    (3459, "1.3.2 - Madeira em tora para outras finalidades"),
    (83432, "1.3.2.1 - Madeira em tora de acácia negra para outras finalidades"),
    (83433, "1.3.2.2 - Madeira em tora de cedro australiano para outras finalidades"),
    (33256, "1.3.2.3 - Madeira em tora de eucalipto para outras finalidades"),
    (83434, "1.3.2.4 - Madeira em tora de mogno africano para outras finalidades"),
    (33257, "1.3.2.5 - Madeira em tora de pinus para outras finalidades"),
    (83435, "1.3.2.6 - Madeira em tora de teca para outras finalidades"),
    (33258, "1.3.2.7 - Madeira em tora de outras espécies para outras finalidades"),
    (3460, "2 - Outros produtos da silvicultura"),
    (3461, "2.1 - Acácia-negra (casca)"),
    (3462, "2.2 - Eucalipto (folha)"),
    (3463, "2.3 - Resina"),
]

# Categorias PEVS Área Existente (Tabela 5930)
PEVS_AREA_CATEGORIES = [
    (0, "Total de Florestas Plantadas"),
    (39326, "Eucalipto"),
    (39327, "Pinus"),
    (83436, "Acácia negra"),
    (83439, "Teca"),
    (83437, "Cedro australiano"),
    (83438, "Mogno africano"),
    (39328, "Outras espécies"),
]

# Categorias PIA-Empresa (Divisões CNAE 2.0 por Estado)
PIA_CNAE_CATEGORIES = [
    (117897, "Total da Indústria Geral"),
    (116880, "B - Indústrias Extrativas (Total)"),
    (116881, "05 - Extração de carvão mineral"),
    (116884, "06 - Extração de petróleo e gás natural"),
    (116887, "07 - Extração de minerais metálicos (minério de ferro, ouro, bauxita)"),
    (116897, "08 - Extração de minerais não-metálicos"),
    (116905, "09 - Atividades de apoio à extração de minerais"),
    (116910, "C - Indústrias de Transformação (Total)"),
    (116911, "10 - Fabricação de produtos alimentícios"),
    (116952, "11 - Fabricação de bebidas"),
    (116960, "12 - Fabricação de produtos do fumo"),
    (116965, "13 - Fabricação de produtos têxteis"),
    (116985, "14 - Confecção de artigos do vestuário e acessórios"),
    (116994, "15 - Artefatos de couro, calçados e artigos de viagem"),
    (117007, "16 - Fabricação de produtos de madeira"),
    (117015, "17 - Fabricação de celulose, papel e papelão"),
    (117029, "18 - Impressão e reprodução de gravações"),
    (117039, "19 - Coque, derivados de petróleo e biocombustíveis"),
    (117048, "20 - Fabricação de produtos químicos"),
    (117082, "21 - Farmoquímicos e farmacêuticos"),
    (117089, "22 - Fabricação de borracha e material plástico"),
    (117099, "23 - Produtos de minerais não-metálicos (cimento, vidro, cerâmica)"),
    (117116, "24 - Metalurgia (aço, ferro, alumínio)"),
    (117136, "25 - Fabricação de produtos de metal"),
    (117159, "26 - Equipamentos de informática, eletrônicos e ópticos"),
    (117179, "27 - Máquinas, aparelhos e materiais elétricos"),
    (117196, "28 - Fabricação de máquinas e equipamentos mecânicos"),
    (117229, "29 - Fabricação de veículos automotores, reboques e carrocerias"),
    (117245, "30 - Outros equipamentos de transporte (aeronaves, embarcações, drones)"),
    (117261, "31 - Fabricação de móveis"),
    (117267, "32 - Produtos diversos"),
    (117283, "33 - Manutenção e instalação de máquinas e equipamentos"),
]

# Categorias Censo Demográfico 2022
CENSO22_SITUACAO_CATEGORIES = [
    (6795, "Total (Urbana + Rural)"),
    (1, "Urbana"),
    (2, "Rural"),
]

CENSO22_SEXO_CATEGORIES = [
    (6794, "Total (Homens + Mulheres)"),
    (4, "Homens"),
    (5, "Mulheres"),
]

CENSO22_ESGOTAMENTO_CATEGORIES = [
    (46292, "Total dos Domicílios"),
    (46290, "Rede geral, rede pluvial ou fossa ligada à rede"),
    (72110, "Rede geral ou pluvial"),
    (72111, "Fossa séptica ou fossa filtro ligada à rede"),
    (72112, "Fossa séptica ou fossa filtro não ligada à rede"),
    (72113, "Fossa rudimentar ou buraco"),
    (92858, "Vala"),
    (72114, "Rio, lago, córrego ou mar"),
    (72115, "Outra forma"),
    (92861, "Não tinham banheiro nem sanitário"),
]

CENSO22_AGUA_CATEGORIES = [
    (72053, "Total dos Domicílios"),
    (31471, "Rede geral de distribuição"),
    (72054, "Poço profundo ou artesiano"),
    (72055, "Poço raso, freático ou cacimba"),
    (72088, "Fonte, nascente ou mina"),
    (72089, "Água da chuva armazenada"),
    (31472, "Carro-pipa"),
    (72090, "Rios, açudes, córregos, lagos e igarapés"),
    (72091, "Outra forma"),
]

CENSO22_LIXO_CATEGORIES = [
    (10972, "Total dos Domicílios"),
    (2520, "Coletado (Total: domicílio ou caçamba)"),
    (72120, "Coletado no domicílio por serviço de limpeza"),
    (72121, "Depositado em caçamba de serviço de limpeza"),
    (72122, "Queimado na propriedade"),
    (72123, "Enterrado na propriedade"),
    (72124, "Jogado em terreno baldio, encosta ou área pública"),
    (1091, "Outro destino"),
]

_STATIC_CATEGORIES_MAP: Dict[str, List[Tuple[int, str]]] = {
    "PAM_CATEGORIES": PAM_CATEGORIES,
    "PAM_MILHO_CATEGORIES": PAM_MILHO_CATEGORIES,
    "PAM_FEIJAO_CATEGORIES": PAM_FEIJAO_CATEGORIES,
    "PAM_BATATA_CATEGORIES": PAM_BATATA_CATEGORIES,
    "PAM_AMENDOIM_CATEGORIES": PAM_AMENDOIM_CATEGORIES,
    "CENSO_AGRO_TIPOLOGIA_CATEGORIES": CENSO_AGRO_TIPOLOGIA_CATEGORIES,
    "CENSO_AGRO_TERRAS_CATEGORIES": CENSO_AGRO_TERRAS_CATEGORIES,
    "PPM_REBANHOS_CATEGORIES": PPM_REBANHOS_CATEGORIES,
    "PPM_PRODUTOS_CATEGORIES": PPM_PRODUTOS_CATEGORIES,
    "PPM_AQUICULTURA_CATEGORIES": PPM_AQUICULTURA_CATEGORIES,
    "PEVS_EXTRACAO_CATEGORIES": PEVS_EXTRACAO_CATEGORIES,
    "PEVS_SILVICULTURA_CATEGORIES": PEVS_SILVICULTURA_CATEGORIES,
    "PEVS_AREA_CATEGORIES": PEVS_AREA_CATEGORIES,
    "PIA_CNAE_CATEGORIES": PIA_CNAE_CATEGORIES,
    "CENSO22_SITUACAO_CATEGORIES": CENSO22_SITUACAO_CATEGORIES,
    "CENSO22_SEXO_CATEGORIES": CENSO22_SEXO_CATEGORIES,
    "CENSO22_ESGOTAMENTO_CATEGORIES": CENSO22_ESGOTAMENTO_CATEGORIES,
    "CENSO22_AGUA_CATEGORIES": CENSO22_AGUA_CATEGORIES,
    "CENSO22_LIXO_CATEGORIES": CENSO22_LIXO_CATEGORIES,
    **PHASE2_STATIC_CATEGORIES,
    **PHASE3_STATIC_CATEGORIES,
    **PHASE4_STATIC_CATEGORIES,
    **PHASE5_STATIC_CATEGORIES,
    **PHASE6_STATIC_CATEGORIES,
    **PHASE7_STATIC_CATEGORIES,
    **PHASE8_STATIC_CATEGORIES,
    **PHASE9_STATIC_CATEGORIES,
    **PHASE10_STATIC_CATEGORIES,
    **PHASE11_STATIC_CATEGORIES,
    **PHASE12_STATIC_CATEGORIES,
    **PHASE13_STATIC_CATEGORIES,
    **PHASE14_STATIC_CATEGORIES,
}

# Caches dinâmicos para catálogos JSON grandes (Prodlist, CNAE 2.0, IPCA c315 e níveis territoriais)
_PIA_PRODLIST_CACHE: List[Tuple[int, str]] = []
_CEMPRE_CNAE_CACHE: List[Tuple[int, str]] = []
_MEI_CNAE_CACHE: List[Tuple[int, str]] = []
_IPCA_C315_CACHE: List[Tuple[int, str]] = []
_EXTRA_CLF_CACHE: Dict[str, Dict[str, Any]] = {}
_SURVEY_LEVELS_CACHE: Dict[str, List[str]] = {}

TERRITORIAL_LEVEL_LABELS: Dict[str, str] = {
    "N6": "Municípios (N6)",
    "N9": "Microrregiões Geográficas (N9)",
    "N8": "Mesorregiões Geográficas (N8)",
    "N7_N6": "RMs + Capitais Isoladas (N7 + N6)",
    "N7_N14": "Regiões Metropolitanas + RIDE (N7 + N14)",
    "N7": "Regiões Metropolitanas (N7 - até 2020)",
    "N14": "RIDE - Grande Teresina (N14)",
    "N3": "Estados / Unidades da Federação (N3)",
    "N2": "Grandes Regiões (N2 - 5 macrorregiões)",
    "N1": "Brasil - Total Nacional (N1)",
}


def _load_json_categories(filename: str) -> List[Tuple[int, str]]:
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                cats = json.load(f)
            return [(int(c["id"]), str(c["nome"])) for c in cats]
        except Exception:
            pass
    return []


def get_pia_prodlist_categories() -> List[Tuple[int, str]]:
    """Carrega dinamicamente a Prodlist da PIA-Produto (3.764 itens)."""
    global _PIA_PRODLIST_CACHE
    if not _PIA_PRODLIST_CACHE:
        _PIA_PRODLIST_CACHE = _load_json_categories("pia_categories.json")
    return _PIA_PRODLIST_CACHE


def get_cempre_cnae_categories() -> List[Tuple[int, str]]:
    """Carrega dinamicamente as 1.067 classes CNAE 2.0 do CEMPRE."""
    global _CEMPRE_CNAE_CACHE
    if not _CEMPRE_CNAE_CACHE:
        _CEMPRE_CNAE_CACHE = _load_json_categories("cempre_cnae_categories.json")
    return _CEMPRE_CNAE_CACHE


def get_mei_cnae_categories() -> List[Tuple[int, str]]:
    """Carrega dinamicamente as 674 classes CNAE 2.0 das Estatísticas MEI (Tabela 9594)."""
    global _MEI_CNAE_CACHE
    if not _MEI_CNAE_CACHE:
        _MEI_CNAE_CACHE = _load_json_categories("mei_cnae_categories.json")
    return _MEI_CNAE_CACHE


def get_ipca_c315_categories() -> List[Tuple[int, str]]:
    """Carrega dinamicamente os 354 grupos, subgrupos e itens da POF comuns ao IPCA, INPC e IPCA-15."""
    global _IPCA_C315_CACHE
    if not _IPCA_C315_CACHE:
        _IPCA_C315_CACHE = _load_json_categories("ipca_c315_categories.json")
    return _IPCA_C315_CACHE


def get_survey_categories(survey: Dict[str, Any]) -> List[Tuple[int, str]]:
    """Retorna a lista de categorias (id, nome) para a pesquisa informada."""
    src = survey.get("category_source")
    if src == "PIA_PRODLIST":
        return get_pia_prodlist_categories()
    if src == "CEMPRE_CNAE":
        return get_cempre_cnae_categories()
    if src == "MEI_CNAE":
        return get_mei_cnae_categories()
    if src == "IPCA_C315":
        return get_ipca_c315_categories()
    if src and src in _STATIC_CATEGORIES_MAP:
        return _STATIC_CATEGORIES_MAP[src]
    return [(0, "Total")]


def _load_survey_levels_db() -> Dict[str, List[str]]:
    global _SURVEY_LEVELS_CACHE
    if not _SURVEY_LEVELS_CACHE:
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "survey_supported_levels.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    _SURVEY_LEVELS_CACHE = json.load(f)
            except Exception:
                _SURVEY_LEVELS_CACHE = {}
    return _SURVEY_LEVELS_CACHE


def get_survey_supported_levels(survey: Dict[str, Any]) -> List[str]:
    """Retorna os níveis territoriais suportados pela pesquisa em ordem recomendada de uso."""
    explicit = survey.get("supported_levels")
    if explicit:
        return list(explicit)
    db = _load_survey_levels_db()
    levels = list(db.get(survey.get("id", "")) or [])
    default_lv = survey.get("level", "N6")
    if not levels:
        levels = [default_lv]
    if default_lv not in levels:
        levels.insert(0, default_lv)
    return levels


def _load_extra_classifications_db() -> Dict[str, Dict[str, Any]]:
    """Carrega cache estático com metadados de classificações secundárias das tabelas SIDRA."""
    global _EXTRA_CLF_CACHE
    if not _EXTRA_CLF_CACHE:
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extra_classifications.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    _EXTRA_CLF_CACHE = json.load(f)
            except Exception:
                _EXTRA_CLF_CACHE = {}
    return _EXTRA_CLF_CACHE


def get_survey_extra_classifications(survey: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Retorna definições das classificações secundárias selecionáveis da pesquisa
    (id, name, default, categories), omitindo travas técnicas internas (c12716).
    """
    extra_map = survey.get("extra_classifications") or {}
    if not extra_map:
        return []

    db = _load_extra_classifications_db()
    tbl = survey.get("table")
    try:
        table_id = int(tbl)
    except (TypeError, ValueError):
        return []
    out: List[Dict[str, Any]] = []
    for cid, default_val in extra_map.items():
        cid_int = int(cid)
        if cid_int == 12716:
            continue
        entry = db.get(f"{table_id}_{cid_int}")
        if not entry or len(entry.get("categories") or []) <= 1:
            continue
        cats = [
            (int(c["id"]), str(c["name"])) if isinstance(c, dict)
            else (int(c[0]), str(c[1]))
            for c in entry["categories"]
        ]
        out.append({
            "id": cid_int,
            "name": str(entry.get("name") or f"Classificação {cid_int}"),
            "default": int(default_val),
            "categories": cats,
        })
    return out


def _period_base_year(code: int) -> int:
    """Extrai o ano base (4 dígitos) tanto para códigos anuais (YYYY) quanto trimestrais (YYYYQQ)."""
    return code // 100 if code > 9999 else code


def _period_sort_key(code: int) -> Tuple[int, int]:
    """Ordena anos fechados (YYYY -> 99) imediatamente acima de seus trimestres (4..1)."""
    if code > 9999:
        return (code // 100, code % 100)
    return (code, 99)


def get_survey_year_label(
    survey: Dict[str, Any],
    year: int,
    variable_id: Optional[int] = None,
) -> str:
    """Retorna rótulo legível para o período na interface (anual consolidado, trimestre ou mês)."""
    if survey.get("periodicity") == "quarterly" and year <= 9999:
        agg_mode = "sum"
        if variable_id is not None:
            for v in survey.get("variables", []):
                if v["id"] == variable_id:
                    agg_mode = (v.get("agg_mode") or "sum").lower()
                    break
        elif survey.get("default_var") is not None:
            for v in survey.get("variables", []):
                if v["id"] == survey.get("default_var"):
                    agg_mode = (v.get("agg_mode") or "sum").lower()
                    break
        if agg_mode == "sum":
            return f"{year} - Total Anual (Soma 1T a 4T)"
        if agg_mode == "mean":
            return f"{year} - Média Anual (1T a 4T)"
        return f"{year} - Fechamento Anual (4T / Série 1T-4T)"

    labels = survey.get("period_labels") or {}
    return str(labels.get(year, year))


def get_survey_by_id(survey_id: str) -> Optional[Dict[str, Any]]:
    """Retorna o dicionário de definição da pesquisa."""
    for s in SURVEYS:
        if s["id"] == survey_id:
            return s
    return None


def get_survey_valid_years(
    survey: Dict[str, Any],
    candidate_years: Optional[List[int]] = None,
    variable_id: Optional[int] = None,
) -> List[int]:
    """Filtra e retorna os anos ou códigos de períodos válidos para a pesquisa (e variável, se restrita)."""
    min_y = survey.get("min_year", 1970)
    max_y = survey.get("max_year", 2026)

    if variable_id is not None:
        for v in survey.get("variables", []):
            if v["id"] == variable_id:
                if v.get("min_year") is not None:
                    min_y = max(min_y, v["min_year"])
                if v.get("max_year") is not None:
                    max_y = min(max_y, v["max_year"])
                break

    if survey.get("valid_years"):
        allowed = [y for y in survey["valid_years"] if min_y <= _period_base_year(y) <= max_y]
    else:
        allowed = list(range(max_y, min_y - 1, -1))

    if candidate_years is None:
        return sorted(allowed, key=_period_sort_key, reverse=True)

    allowed_set = set(allowed)
    return [y for y in candidate_years if y in allowed_set]


def resolve_table_queries(
    survey: Dict[str, Any],
    years: List[int],
    variable_id: int,
    category_id: Optional[int] = None,
) -> Tuple[List[Dict[str, Any]], List[int]]:
    """
    Divide a lista de anos por tabela SIDRA correspondente (para séries contínuas
    divididas entre tabelas antiga e nova, como CEMPRE, PIA, PIB, PAC e PAS) e
    aplica mapeamento de períodos subanuais, variáveis e categorias por segmento.
    Retorna (planos_de_consulta, anos_ignorados).
    """
    valid_set = set(get_survey_valid_years(survey, years, variable_id=variable_id))
    skipped = [y for y in sorted(years) if y not in valid_set]
    selected_valid = [y for y in sorted(years) if y in valid_set]

    if not selected_valid:
        return [], skipped

    period_map = survey.get("period_map") or {}

    def _map_periods(yrs: List[int]) -> List[Any]:
        out: List[Any] = []
        seen = set()
        for y in yrs:
            mapped = period_map.get(y, y)
            items = mapped if isinstance(mapped, (list, tuple)) else [mapped]
            for it in items:
                k = str(it)
                if k not in seen:
                    seen.add(k)
                    out.append(it)
        return sorted(out, key=lambda x: str(x))

    series = survey.get("table_series")
    provider = survey.get("provider")
    if not series:
        plan: Dict[str, Any] = {
            "table": survey.get("table", "FINBRA"),
            "years": _map_periods(selected_valid),
            "query_var": variable_id,
            "requested_var": variable_id,
        }
        if provider:
            plan["provider"] = provider
        return [plan], skipped

    plans: List[Dict[str, Any]] = []
    covered_years = set()
    for seg in series:
        seg_min = seg.get("min_year", 1900)
        seg_max = seg.get("max_year", 2100)
        seg_min_p = seg.get("min_period")
        seg_max_p = seg.get("max_period")
        seg_years = []
        for y in selected_valid:
            if not (seg_min <= _period_base_year(y) <= seg_max):
                continue
            if seg_min_p is not None or seg_max_p is not None:
                mapped_items = _map_periods([y])
                p_vals = [int(str(it)) for it in mapped_items if str(it).isdigit()]
                if not p_vals:
                    continue
                if seg_min_p is not None and any(pv < int(seg_min_p) for pv in p_vals):
                    continue
                if seg_max_p is not None and any(pv > int(seg_max_p) for pv in p_vals):
                    continue
            seg_years.append(y)
        if not seg_years:
            continue

        overrides = seg.get("var_overrides", {})
        if variable_id in overrides:
            mapped_var = overrides[variable_id]
            if mapped_var is None:
                skipped.extend(seg_years)
                continue
        else:
            mapped_var = variable_id

        cat_overrides = seg.get("cat_overrides") or {}
        if category_id is not None and int(category_id) in cat_overrides:
            if cat_overrides[int(category_id)] is None:
                skipped.extend(seg_years)
                continue

        covered_years.update(seg_years)
        plans.append({
            "table": seg["table"],
            "years": _map_periods(seg_years),
            "query_var": mapped_var,
            "requested_var": variable_id,
            "cat_overrides": cat_overrides or None,
            "uf_classification": seg.get("uf_classification"),
        })

    for y in selected_valid:
        if y not in covered_years and y not in skipped:
            skipped.append(y)

    return plans, sorted(set(skipped))


# Lista de Estados (UF)
BRAZIL_UFS = [
    ("BR", "Brasil (Todos os Municípios / Estados)", None),
    ("AC", "Acre", 12),
    ("AL", "Alagoas", 27),
    ("AM", "Amazonas", 13),
    ("AP", "Amapá", 16),
    ("BA", "Bahia", 29),
    ("CE", "Ceará", 23),
    ("DF", "Distrito Federal", 53),
    ("ES", "Espírito Santo", 32),
    ("GO", "Goiás", 52),
    ("MA", "Maranhão", 21),
    ("MG", "Minas Gerais", 31),
    ("MS", "Mato Grosso do Sul", 50),
    ("MT", "Mato Grosso", 51),
    ("PA", "Pará", 15),
    ("PB", "Paraíba", 25),
    ("PE", "Pernambuco", 26),
    ("PI", "Piauí", 22),
    ("PR", "Paraná", 41),
    ("RJ", "Rio de Janeiro", 33),
    ("RN", "Rio Grande do Norte", 24),
    ("RO", "Rondônia", 11),
    ("RR", "Roraima", 14),
    ("RS", "Rio Grande do Sul", 43),
    ("SC", "Santa Catarina", 42),
    ("SE", "Sergipe", 28),
    ("SP", "São Paulo", 35),
    ("TO", "Tocantins", 17),
]


def slugify_variable_name(name: str) -> str:
    """Converte o nome da variável em um subnome padronizado snake_case sem acentos."""
    nfkd = unicodedata.normalize("NFKD", name)
    clean = "".join([c for c in nfkd if not unicodedata.combining(c)])
    name_lower = clean.lower()

    mappings = [
        ("quantidade produzida na extracao", "quantidade_produzida_extracao"),
        ("valor da producao na extracao", "valor_producao_extracao"),
        ("quantidade produzida na silvicultura", "quantidade_produzida_silvicultura"),
        ("valor da producao na silvicultura", "valor_producao_silvicultura"),
        ("quantidade produzida", "quantidade_produzida"),
        ("producao da aquicultura", "producao_aquicultura"),
        ("rendimento medio", "rendimento_medio"),
        ("valor da producao", "valor_producao"),
        ("area colhida", "area_colhida"),
        ("area plantada", "area_plantada"),
        ("area total existente", "area_silvicultura"),
        ("efetivo do rebanho", "efetivo_rebanho"),
        ("vacas ordenhadas", "vacas_ordenhadas"),
        ("ovinos tosquiados", "ovinos_tosquiados"),
        ("produto interno bruto", "pib"),
        ("vab agropecuaria", "vab_agropecuaria"),
        ("vab industria", "vab_industria"),
        ("vab servicos", "vab_servicos"),
        ("vab administracao", "vab_administracao_publica"),
        ("valor adicionado bruto total", "vab_total"),
        ("impostos liquidos", "impostos_liquidos"),
        ("transformacao industrial", "vti"),
        ("bruto da producao industrial", "vbpi"),
        ("receita liquida", "receita_liquida_vendas"),
        ("quantidade vendida", "quantidade_vendida"),
        ("pessoal ocupado", "pessoal_ocupado"),
        ("salarios", "salarios_remuneracoes"),
        ("unidades locais", "unidades_locais"),
        ("numero de empresas", "numero_empresas"),
        ("populacao residente estimada", "populacao_estimada"),
        ("densidade demografica", "densidade_demografica"),
        ("crescimento geometrico", "taxa_crescimento_geometrico"),
        ("alfabetizacao", "taxa_alfabetizacao"),
    ]
    for key, val in mappings:
        if key in name_lower:
            return val

    slug = re.sub(r"[^a-zA-Z0-9]+", "_", clean.lower()).strip("_")
    return slug or "indicador"


def get_variable_info(survey_id: str, variable_id: int) -> Optional[Dict[str, Any]]:
    """Retorna os metadados da variável cadastrada na pesquisa."""
    for s in SURVEYS:
        if s["id"] == survey_id or str(s.get("table")) == str(survey_id):
            for v in s.get("variables", []):
                if v["id"] == variable_id:
                    return v
    return None


def get_variable_slug(survey_id: str, variable_id: int) -> str:
    """Retorna o subnome/slug do tipo de mapa para a variável especificada."""
    v = get_variable_info(survey_id, variable_id)
    if v:
        return v.get("slug") or slugify_variable_name(v["name"])
    return "indicador"
