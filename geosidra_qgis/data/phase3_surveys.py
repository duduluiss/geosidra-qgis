# -*- coding: utf-8 -*-
"""
Definições das 41 pesquisas oficiais IBGE/SIDRA incorporadas na Fase 3 (v0.4.0):
  - Conjuntura Econômica Mensal e Preços da Construção (PIM-PF, PMC, PMS, SINAPI)
  - Pesquisa de Estoques Semestral, Couro Trimestral e Censo Agropecuário 2017
  - PNAD Contínua (Informalidade e Subutilização), Demografia das Empresas e Hospedagem
  - Censo 2022 (Internet, Entorno Urbanístico, Fecundidade, Autismo, Sub-registro) e Projeções
  - PNSB (Rede Coletora, ETEs, Resíduos Sólidos, Drenagem) e MUNIC (Ambiental, Social e Segurança)
  - Registro Civil (Divórcios)
"""

from typing import Any, Callable, Dict, List


def build_phase3_surveys(
    build_monthly_periods: Callable[..., Any],
    build_quarterly_periods: Callable[..., Any],
    build_semiannual_periods: Callable[..., Any],
) -> List[Dict[str, Any]]:
    """Constrói a lista das pesquisas da Fase 3 reutilizando os construtores de períodos."""
    sinapi_sem_valid, sinapi_sem_map, sinapi_sem_labels = build_monthly_periods(2017, 1, 2026, 9)
    sinapi_com_valid, sinapi_com_map, sinapi_com_labels = build_monthly_periods(1986, 3, 2026, 9)
    pimpf_valid, pimpf_map, pimpf_labels = build_monthly_periods(2002, 1, 2026, 9)
    pmc_tot_valid, pmc_tot_map, pmc_tot_labels = build_monthly_periods(2000, 1, 2026, 8)
    pmc_amp_valid, pmc_amp_map, pmc_amp_labels = build_monthly_periods(2003, 1, 2026, 8)
    pms_valid, pms_map, pms_labels = build_monthly_periods(2011, 1, 2026, 9)
    ipca_valid, ipca_map, ipca_labels = build_monthly_periods(2012, 1, 2026, 9)
    ipca15_valid, ipca15_map, ipca15_labels = build_monthly_periods(2012, 2, 2026, 10)

    estoques_valid, estoques_map, estoques_labels = build_semiannual_periods(2007, 2, 2025, 2)
    couro_valid, couro_map, couro_labels = build_quarterly_periods(
        list(range(1999, 2027)), latest_year=2026, latest_quarter=2
    )
    pnad_valid, pnad_map, pnad_labels = build_quarterly_periods(
        list(range(2012, 2027)), latest_year=2026, latest_quarter=2
    )

    pmc_vars = [
        {"id": 11711, "name": "PMC - Variação Acumulada em 12 Meses (%)", "slug": "pmc_var_12m", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
        {"id": 11709, "name": "PMC - Variação Mensal Interanual (M/M-12, %)", "slug": "pmc_var_mm12", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
        {"id": 11708, "name": "PMC - Variação Mês/Mês Anterior c/ Ajuste Sazonal (%)", "slug": "pmc_var_mom_sa", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
        {"id": 11710, "name": "PMC - Variação Acumulada no Ano (%)", "slug": "pmc_var_ano", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
        {"id": 7169, "name": "PMC - Número-Índice (Base 2022 = 100)", "slug": "pmc_indice", "unit": "Número-índice", "multiplier": 1.0, "agg_mode": "mean"},
        {"id": 7170, "name": "PMC - Número-Índice c/ Ajuste Sazonal (2022 = 100)", "slug": "pmc_indice_sa", "unit": "Número-índice", "multiplier": 1.0, "agg_mode": "mean"},
    ]

    pms_vars = [
        {"id": 11626, "name": "PMS - Variação Acumulada em 12 Meses (%)", "slug": "pms_var_12m", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
        {"id": 11624, "name": "PMS - Variação Mensal Interanual (M/M-12, %)", "slug": "pms_var_mm12", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
        {"id": 11623, "name": "PMS - Variação Mês/Mês Anterior c/ Ajuste Sazonal (%)", "slug": "pms_var_mom_sa", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
        {"id": 11625, "name": "PMS - Variação Acumulada no Ano (%)", "slug": "pms_var_ano", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
        {"id": 7167, "name": "PMS - Número-Índice (Base 2022 = 100)", "slug": "pms_indice", "unit": "Número-índice", "multiplier": 1.0, "agg_mode": "mean"},
        {"id": 7168, "name": "PMS - Número-Índice c/ Ajuste Sazonal (2022 = 100)", "slug": "pms_indice_sa", "unit": "Número-índice", "multiplier": 1.0, "agg_mode": "mean"},
    ]

    return [
        # =====================================================================
        # CONJUNTURA ECONÔMICA MENSAL E INFLAÇÃO REGIONAL (IPCA / INPC / SINAPI)
        # =====================================================================
        {
            "id": "IPCA_REGIONAL",
            "group": "CONJUNTURA_MENSAL",
            "name": "IPCA: Índice Nacional de Preços ao Consumidor Amplo (RMs e Capitais)",
            "table": 7060,
            "table_series": [
                {"min_year": 2012, "max_year": 2019, "table": 1419},
                {"min_year": 2020, "max_year": 2026, "table": 7060},
            ],
            "classification": 315,
            "category_source": "IPCA_C315",
            "min_year": 2012,
            "max_year": 2026,
            "valid_years": ipca_valid,
            "period_map": ipca_map,
            "period_labels": ipca_labels,
            "default_years": [202609],
            "periodicity": "monthly",
            "level": "N7_N6",
            "supported_levels": ["N7_N6", "N7", "N6"],
            "partial_n6": True,
            "default_cat": 7169,
            "default_var": 2265,
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "IPCA Regional — 10 RMs (N7) + 6 Capitais Isoladas (N6)",
            "notice_text": (
                "O IPCA regional do IBGE abrange 16 áreas oficiais de coleta: 10 Regiões Metropolitanas "
                "(Belém, Fortaleza, Recife, Salvador, Belo Horizonte, Grande Vitória, Rio de Janeiro, São Paulo, "
                "Curitiba e Porto Alegre — N7) e 6 capitais sem RM no índice (Rio Branco, São Luís, Aracaju, "
                "Campo Grande, Goiânia e Brasília — N6). O modo N7 + N6 integra as 16 áreas no mesmo mapa. "
                "Série contínua 2012–2026 une Tabelas 1419 e 7060 nos 354 grupos/itens em comum."
            ),
            "variables": [
                {"id": 2265, "name": "IPCA - Variação Acumulada em 12 Meses (%)", "slug": "ipca_var_12m", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
                {"id": 63, "name": "IPCA - Variação Mensal (%)", "slug": "ipca_var_mensal", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
                {"id": 69, "name": "IPCA - Variação Acumulada no Ano (%)", "slug": "ipca_var_ano", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
                {"id": 66, "name": "IPCA - Peso Mensal na Cesta (%)", "slug": "ipca_peso_mensal", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            ],
        },
        {
            "id": "INPC_REGIONAL",
            "group": "CONJUNTURA_MENSAL",
            "name": "INPC: Índice Nacional de Preços ao Consumidor (RMs e Capitais)",
            "table": 7063,
            "table_series": [
                {"min_year": 2012, "max_year": 2019, "table": 1100},
                {"min_year": 2020, "max_year": 2026, "table": 7063},
            ],
            "classification": 315,
            "category_source": "IPCA_C315",
            "min_year": 2012,
            "max_year": 2026,
            "valid_years": ipca_valid,
            "period_map": ipca_map,
            "period_labels": ipca_labels,
            "default_years": [202609],
            "periodicity": "monthly",
            "level": "N7_N6",
            "supported_levels": ["N7_N6", "N7", "N6"],
            "partial_n6": True,
            "default_cat": 7169,
            "default_var": 2292,
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "INPC Regional — 10 RMs (N7) + 6 Capitais Isoladas (N6)",
            "notice_text": (
                "Acompanha a variação de preços para famílias com rendimento de 1 a 5 salários mínimos nas "
                "mesmas 16 áreas regionais (10 RMs N7 + 6 capitais N6). O modo padrão N7 + N6 exibe todas as 16 "
                "áreas no mapa; série contínua 2012–2026 une Tabelas 1100 e 7063."
            ),
            "variables": [
                {"id": 2292, "name": "INPC - Variação Acumulada em 12 Meses (%)", "slug": "inpc_var_12m", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
                {"id": 44, "name": "INPC - Variação Mensal (%)", "slug": "inpc_var_mensal", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
                {"id": 68, "name": "INPC - Variação Acumulada no Ano (%)", "slug": "inpc_var_ano", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
                {"id": 45, "name": "INPC - Peso Mensal na Cesta (%)", "slug": "inpc_peso_mensal", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            ],
        },
        {
            "id": "IPCA15_REGIONAL",
            "group": "CONJUNTURA_MENSAL",
            "name": "IPCA-15: Prévia da Inflação Oficial (RMs, Brasília e Goiânia)",
            "table": 7062,
            "table_series": [
                {"min_year": 2012, "max_year": 2020, "min_period": 201202, "max_period": 202001, "table": 1705},
                {"min_year": 2020, "max_year": 2026, "min_period": 202002, "max_period": 202610, "table": 7062},
            ],
            "classification": 315,
            "category_source": "IPCA_C315",
            "min_year": 2012,
            "max_year": 2026,
            "valid_years": ipca15_valid,
            "period_map": ipca15_map,
            "period_labels": ipca15_labels,
            "default_years": [202610],
            "periodicity": "monthly",
            "level": "N7_N6",
            "supported_levels": ["N7_N6", "N7", "N6"],
            "partial_n6": True,
            "default_cat": 7169,
            "default_var": 1120,
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "IPCA-15 Regional — 9 RMs (N7) + Brasília e Goiânia (N6)",
            "notice_text": (
                "O IPCA-15 cobre 11 regiões oficiais de pesquisa: 9 Regiões Metropolitanas (Belém, Fortaleza, "
                "Recife, Salvador, Belo Horizonte, Rio de Janeiro, São Paulo, Curitiba e Porto Alegre — N7) e "
                "2 municípios isolados (Goiânia e Brasília — N6). Série contínua 201202–202610 integra Tabelas 1705 e 7062."
            ),
            "variables": [
                {"id": 1120, "name": "IPCA-15 - Variação Acumulada em 12 Meses (%)", "slug": "ipca15_var_12m", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
                {"id": 355, "name": "IPCA-15 - Variação Mensal (%)", "slug": "ipca15_var_mensal", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
                {"id": 356, "name": "IPCA-15 - Variação Acumulada no Ano (%)", "slug": "ipca15_var_ano", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
                {"id": 357, "name": "IPCA-15 - Peso Mensal na Cesta (%)", "slug": "ipca15_peso_mensal", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            ],
        },
        {
            "id": "SINAPI_SEM_DESONERACAO",
            "group": "CONJUNTURA_MENSAL",
            "name": "SINAPI: Custo Médio m² da Construção Civil (Sem Desoneração, UF)",
            "table": 6586,
            "classification": None,
            "category_source": None,
            "min_year": 2017,
            "max_year": 2026,
            "valid_years": sinapi_sem_valid,
            "period_map": sinapi_sem_map,
            "period_labels": sinapi_sem_labels,
            "default_years": [202609],
            "periodicity": "monthly",
            "level": "N3",
            "default_cat": 0,
            "default_var": 9327,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "Série Mensal Estadual (27 UFs) — SINAPI Sem Desoneração",
            "notice_text": (
                "Custo médio da construção civil em R$/m² e variações (%) sem desoneração da folha de "
                "pagamento, apurados pelo IBGE/Caixa apenas em nível estadual (N3, 27/27 UFs) desde Jan/2017. "
                "Selecionar um ano fechado consulta Dezembro (YYYY12)."
            ),
            "variables": [
                {"id": 9327, "name": "Custo Médio m² - Moeda Corrente (Sem Desoneração)", "slug": "sinapi_custo_m2", "unit": "Reais", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 9328, "name": "Custo Médio m² - Componente Material", "slug": "sinapi_material", "unit": "Reais", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 9329, "name": "Custo Médio m² - Componente Mão de Obra", "slug": "sinapi_mao_obra", "unit": "Reais", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 9330, "name": "Custo Médio m² - Número-Índice", "slug": "sinapi_indice", "unit": "Número-índice", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 9333, "name": "Custo Médio m² - Variação no Mês (%)", "slug": "sinapi_var_mes", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
                {"id": 9334, "name": "Custo Médio m² - Variação no Ano (%)", "slug": "sinapi_var_ano", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
                {"id": 9335, "name": "Custo Médio m² - Variação em 12 Meses (%)", "slug": "sinapi_var_12m", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
            ],
        },
        {
            "id": "SINAPI_COM_DESONERACAO",
            "group": "CONJUNTURA_MENSAL",
            "name": "SINAPI: Custo Médio m² da Construção Civil (Com Desoneração, 1986+, UF)",
            "table": 2296,
            "classification": None,
            "category_source": None,
            "min_year": 1986,
            "max_year": 2026,
            "valid_years": sinapi_com_valid,
            "period_map": sinapi_com_map,
            "period_labels": sinapi_com_labels,
            "default_years": [202609],
            "periodicity": "monthly",
            "level": "N3",
            "default_cat": 0,
            "default_var": 48,
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Série Longa SINAPI (1986–2026) — Atenção às Mudanças de Moeda",
            "notice_text": (
                "Custo médio m² estadual (N3, 27/27 UFs) com série mensal desde Março/1986. Para comparações "
                "anteriores a Jul/1994 os valores nominais refletem moedas anteriores ao Real; prefira variações "
                "percentuais ou períodos pós-1994 para análises monetárias."
            ),
            "variables": [
                {"id": 48, "name": "Custo Médio m² - Moeda Corrente", "slug": "sinapi_deson_custo_m2", "unit": "Reais", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 2119, "name": "Custo Médio m² - Componente Material", "slug": "sinapi_deson_material", "unit": "Reais", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 2120, "name": "Custo Médio m² - Componente Mão de Obra", "slug": "sinapi_deson_mao_obra", "unit": "Reais", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 49, "name": "Custo Médio m² - Número-Índice", "slug": "sinapi_deson_indice", "unit": "Número-índice", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 1196, "name": "Custo Médio m² - Variação no Mês (%)", "slug": "sinapi_deson_var_mes", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
                {"id": 1197, "name": "Custo Médio m² - Variação no Ano (%)", "slug": "sinapi_deson_var_ano", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
                {"id": 1198, "name": "Custo Médio m² - Variação em 12 Meses (%)", "slug": "sinapi_deson_var_12m", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
            ],
        },
        {
            "id": "PIM_PF_IND_UF",
            "group": "CONJUNTURA_MENSAL",
            "name": "PIM-PF: Produção Física Industrial por Seções e Atividades (UF)",
            "table": 8888,
            "classification": 544,
            "category_source": "P3_8888_544",
            "min_year": 2002,
            "max_year": 2026,
            "valid_years": pimpf_valid,
            "period_map": pimpf_map,
            "period_labels": pimpf_labels,
            "default_years": [202609],
            "periodicity": "monthly",
            "level": "N3",
            "default_cat": 129314,
            "default_var": 11604,
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Cobertura Regional Parcial — PIM-PF Regional (17 UFs)",
            "notice_text": (
                "O IBGE apura a Pesquisa Industrial Mensal Regional (PIM-PF) apenas para 17 UFs selecionadas com "
                "parque industrial representativo (AM, PA, MA, CE, RN, PE, BA, MG, ES, RJ, SP, PR, SC, RS, MS, MT, GO). "
                "As demais UFs aparecem no mapa sem dado publicado no SIDRA."
            ),
            "variables": [
                {"id": 11604, "name": "PIM-PF - Variação Acumulada em 12 Meses (%)", "slug": "pimpf_var_12m", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
                {"id": 11602, "name": "PIM-PF - Variação Mensal Interanual (M/M-12, %)", "slug": "pimpf_var_mm12", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
                {"id": 11601, "name": "PIM-PF - Variação Mês/Mês Anterior c/ Ajuste Sazonal (%)", "slug": "pimpf_var_mom_sa", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
                {"id": 11603, "name": "PIM-PF - Variação Acumulada no Ano (%)", "slug": "pimpf_var_ano", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
                {"id": 12606, "name": "PIM-PF - Número-Índice (Base 2022 = 100)", "slug": "pimpf_indice", "unit": "Número-índice", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 12607, "name": "PIM-PF - Número-Índice c/ Ajuste Sazonal (2022 = 100)", "slug": "pimpf_indice_sa", "unit": "Número-índice", "multiplier": 1.0, "agg_mode": "mean"},
            ],
        },
        {
            "id": "PMC_VAREJO_TOTAL_UF",
            "group": "CONJUNTURA_MENSAL",
            "name": "PMC: Comércio Varejista Total — Volume e Receita Nominal (UF)",
            "table": 8880,
            "classification": 11046,
            "category_source": "P3_8880_11046",
            "min_year": 2000,
            "max_year": 2026,
            "valid_years": pmc_tot_valid,
            "period_map": pmc_tot_map,
            "period_labels": pmc_tot_labels,
            "default_years": [202608],
            "periodicity": "monthly",
            "level": "N3",
            "default_cat": 56734,
            "default_var": 11711,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "Pesquisa Mensal de Comércio Total — Cobertura nas 27 UFs (N3)",
            "notice_text": (
                "Cobertura completa das 27 Unidades da Federação (N3) para o comércio varejista total, "
                "com índices base 2022=100 e variações percentuais (inclusive negativas). Última competência "
                "publicada no catálogo: Ago/2026."
            ),
            "variables": pmc_vars,
        },
        {
            "id": "PMC_VAREJO_AMPLIADO_UF",
            "group": "CONJUNTURA_MENSAL",
            "name": "PMC: Comércio Varejista Ampliado (Inclui Veículos e Mat. Construção, UF)",
            "table": 8881,
            "classification": 11046,
            "category_source": "P3_8881_11046",
            "min_year": 2003,
            "max_year": 2026,
            "valid_years": pmc_amp_valid,
            "period_map": pmc_amp_map,
            "period_labels": pmc_amp_labels,
            "default_years": [202608],
            "periodicity": "monthly",
            "level": "N3",
            "default_cat": 56736,
            "default_var": 11711,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "PMC Ampliado (2003–2026) — Cobertura nas 27 UFs (N3)",
            "notice_text": (
                "Abrange o comércio varejista mais veículos/motos e material de construção em nível estadual "
                "(27/27 UFs, N3) desde Jan/2003."
            ),
            "variables": pmc_vars,
        },
        {
            "id": "PMC_ATIVIDADES_UF",
            "group": "CONJUNTURA_MENSAL",
            "name": "PMC: Comércio Varejista por Atividades (Supermercados, Combustíveis, UF)",
            "table": 8882,
            "classification": 85,
            "category_source": "P3_8882_85",
            "min_year": 2000,
            "max_year": 2026,
            "valid_years": pmc_tot_valid,
            "period_map": pmc_tot_map,
            "period_labels": pmc_tot_labels,
            "default_years": [202608],
            "periodicity": "monthly",
            "level": "N3",
            "default_cat": 90672,
            "default_var": 11711,
            "extra_classifications": {"11046": 56734},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Abertura por Atividade da PMC — Amostra de 12 UFs",
            "notice_text": (
                "Na Pesquisa Mensal de Comércio, a abertura detalhada por atividade (supermercados, combustíveis, "
                "farmácias, vestuário, móveis etc.) é divulgada apenas para 12 UFs selecionadas da amostra. "
                "Para mapear as 27 UFs, utilize PMC Total (8880) ou PMC Ampliado (8881)."
            ),
            "variables": pmc_vars,
        },
        {
            "id": "PMS_SERVICOS_UF",
            "group": "CONJUNTURA_MENSAL",
            "name": "PMS: Pesquisa Mensal de Serviços Total — Volume e Receita (UF)",
            "table": 5906,
            "classification": 11046,
            "category_source": "P3_5906_11046",
            "min_year": 2011,
            "max_year": 2026,
            "valid_years": pms_valid,
            "period_map": pms_map,
            "period_labels": pms_labels,
            "default_years": [202609],
            "periodicity": "monthly",
            "level": "N3",
            "default_cat": 56726,
            "default_var": 11626,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "Pesquisa Mensal de Serviços Total — Cobertura nas 27 UFs (N3)",
            "notice_text": (
                "Série estadual completa (27/27 UFs, N3) de Jan/2011 a Set/2026 para volume e receita nominal "
                "dos serviços não financeiros, com suporte a variações negativas."
            ),
            "variables": pms_vars,
        },
        {
            "id": "PMS_TURISMO_UF",
            "group": "CONJUNTURA_MENSAL",
            "name": "PMS: Índice Mensal de Atividades Turísticas (UF)",
            "table": 8694,
            "classification": 11046,
            "category_source": "P3_8694_11046",
            "min_year": 2011,
            "max_year": 2026,
            "valid_years": pms_valid,
            "period_map": pms_map,
            "period_labels": pms_labels,
            "default_years": [202609],
            "periodicity": "monthly",
            "level": "N3",
            "default_cat": 56728,
            "default_var": 11626,
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Atividades Turísticas (PMS) — Amostra de 17 UFs",
            "notice_text": (
                "O índice específico de atividades turísticas da PMS é calculado pelo IBGE para 17 UFs "
                "selecionadas. Estados fora do recorte permanecem sem registro no mapa."
            ),
            "variables": pms_vars,
        },

        # =====================================================================
        # AGROPECUÁRIA: ESTOQUES SEMESTRAIS E CENSO AGROPECUÁRIO 2017
        # =====================================================================
        {
            "id": "ESTOQUES_ARMAZENADOS",
            "group": "AGRO_VEGETAL",
            "name": "Pesquisa de Estoques: Quantidade Estocada em Armazéns (Semestral)",
            "table": 254,
            "classification": 162,
            "category_source": "P3_254_162",
            "min_year": 2007,
            "max_year": 2025,
            "valid_years": estoques_valid,
            "period_map": estoques_map,
            "period_labels": estoques_labels,
            "default_years": [2025],
            "periodicity": "semiannual",
            "level": "N6",
            "default_cat": 118423,
            "default_var": 150,
            "extra_classifications": {"161": 0, "163": 0},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Pesquisa Semestral com Sigilo Estatístico e Cobertura Esparsa",
            "notice_text": (
                "A Pesquisa de Estoques é semestral (2º Sem/2007 a 2º Sem/2025). Em nível municipal (N6), só há "
                "dados para os cerca de 2.410 municípios com armazéns cadastrados, e municípios com poucos "
                "informantes recebem sigilo ('X' / '..') pelo IBGE."
            ),
            "variables": [
                {"id": 150, "name": "Quantidade Estocada", "slug": "estoques_quantidade", "unit": "Toneladas", "multiplier": 1.0, "agg_mode": "last"},
                {"id": 151, "name": "Número de Informantes", "slug": "estoques_informantes", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
            ],
        },
        {
            "id": "ESTOQUES_CAPACIDADE_SILOS",
            "group": "AGRO_VEGETAL",
            "name": "Pesquisa de Estoques: Capacidade Útil de Armazéns Graneleiros e Silos (Semestral)",
            "table": 259,
            "classification": 12687,
            "category_source": "P3_259_12687",
            "min_year": 2007,
            "max_year": 2025,
            "valid_years": estoques_valid,
            "period_map": estoques_map,
            "period_labels": estoques_labels,
            "default_years": [2025],
            "periodicity": "semiannual",
            "level": "N6",
            "default_cat": 114626,
            "default_var": 153,
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Pesquisa Semestral — Silos e Armazéns Graneleiros (Toneladas)",
            "notice_text": (
                "Periodicidade semestral (2º Sem/2007 a 2º Sem/2025) cobrindo municípios com unidades "
                "armazenadoras a granel cadastradas e sujeito a sigilo estatístico ('X' / '..')."
            ),
            "variables": [
                {"id": 153, "name": "Capacidade Útil (Graneleiros e Silos)", "slug": "capacidade_util_silos", "unit": "Toneladas", "multiplier": 1.0, "agg_mode": "last"},
                {"id": 151, "name": "Número de Informantes", "slug": "silos_informantes", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
            ],
        },
        {
            "id": "CAGRO_SILOS_ARMAZENS",
            "group": "AGRO_VEGETAL",
            "name": "Censo Agro 2017: Silos e Armazéns nos Estabelecimentos Agropecuários",
            "table": 6866,
            "classification": 166,
            "category_source": "P3_6866_166",
            "min_year": 2017,
            "max_year": 2017,
            "valid_years": [2017],
            "level": "N6",
            "default_cat": 114630,
            "default_var": 9561,
            "extra_classifications": {"829": 46302, "12564": 41145, "12771": 45951},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Censo Agropecuário 2017 — Recorte Censitário Único",
            "notice_text": (
                "Dados estruturais do Censo Agropecuário disponíveis apenas para 2017. Permite filtrar tipo "
                "de unidade armazenadora, tipologia familiar/não familiar, sexo e idade do produtor."
            ),
            "variables": [
                {"id": 9561, "name": "Capacidade das Unidades Armazenadoras", "slug": "cagro_capacidade_armazens", "unit": "Toneladas", "multiplier": 1.0, "agg_mode": "last"},
                {"id": 9560, "name": "Número de Unidades Armazenadoras", "slug": "cagro_unidades_armazenadoras", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
                {"id": 10113, "name": "Estabelecimentos com Unidades Armazenadoras", "slug": "cagro_estab_armazenadores", "unit": "Estabelecimentos", "multiplier": 1.0, "agg_mode": "last"},
            ],
        },
        {
            "id": "CAGRO_PRATICAS_AGRICOLAS",
            "group": "AGRO_VEGETAL",
            "name": "Censo Agro 2017: Práticas Agrícolas e Conservação do Solo",
            "table": 6846,
            "classification": 12568,
            "category_source": "P3_6846_12568",
            "min_year": 2017,
            "max_year": 2017,
            "valid_years": [2017],
            "level": "N6",
            "default_cat": 112654,
            "default_var": 183,
            "extra_classifications": {"829": 46302, "12598": 41141, "12567": 41151, "220": 110085},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Censo Agropecuário 2017 — Práticas Agrícolas",
            "notice_text": (
                "Ano único (2017). Escolha na categoria práticas como Plantio em nível, Rotação de culturas, "
                "Pousio, Proteção de encostas, além de filtros por associação à cooperativa e orientação técnica."
            ),
            "variables": [
                {"id": 183, "name": "Número de Estabelecimentos Agropecuários", "slug": "cagro_praticas_agricolas", "unit": "Estabelecimentos", "multiplier": 1.0, "agg_mode": "last"},
            ],
        },
        {
            "id": "CAGRO_CALCARIO_CORRETIVOS",
            "group": "AGRO_VEGETAL",
            "name": "Censo Agro 2017: Uso de Calcário e Corretivos do Solo",
            "table": 6850,
            "classification": 12549,
            "category_source": "P3_6850_12549",
            "min_year": 2017,
            "max_year": 2017,
            "valid_years": [2017],
            "level": "N6",
            "default_cat": 46554,
            "default_var": 183,
            "extra_classifications": {"829": 46302, "12567": 41151, "220": 110085},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Censo Agropecuário 2017 — Corretivos de Solo",
            "notice_text": (
                "Ano único (2017). Padrão selecionado: estabelecimentos que aplicaram calcário ou corretivos "
                "do pH do solo, com subfiltros de tipologia, orientação técnica e grupos de área."
            ),
            "variables": [
                {"id": 183, "name": "Número de Estabelecimentos Agropecuários", "slug": "cagro_uso_calcario", "unit": "Estabelecimentos", "multiplier": 1.0, "agg_mode": "last"},
            ],
        },
        {
            "id": "CAGRO_ORGANICOS",
            "group": "AGRO_VEGETAL",
            "name": "Censo Agro 2017: Agricultura e Pecuária Orgânica",
            "table": 6853,
            "classification": 838,
            "category_source": "P3_6853_838",
            "min_year": 2017,
            "max_year": 2017,
            "valid_years": [2017],
            "level": "N6",
            "default_cat": 47123,
            "default_var": 183,
            "extra_classifications": {"829": 46302, "12564": 41145, "12771": 45951, "218": 46502},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Censo Agropecuário 2017 — Produção Orgânica",
            "notice_text": (
                "Ano único (2017). Permite distinguir estabelecimentos com produção vegetal orgânica, animal "
                "orgânica ou ambas, por perfil do produtor."
            ),
            "variables": [
                {"id": 183, "name": "Número de Estabelecimentos Agropecuários", "slug": "cagro_organicos", "unit": "Estabelecimentos", "multiplier": 1.0, "agg_mode": "last"},
            ],
        },

        # =====================================================================
        # PECUÁRIA: PESQUISA TRIMESTRAL DO COURO E EFETIVO CENSO AGRO
        # =====================================================================
        {
            "id": "COURO_CRU_TRIMESTRAL_UF",
            "group": "PECUARIA_AQUI",
            "name": "Couro Trimestral: Couro Cru Adquirido por Procedência (UF)",
            "table": 1088,
            "classification": 11531,
            "category_source": "P3_1088_11531",
            "min_year": 1999,
            "max_year": 2026,
            "valid_years": couro_valid,
            "period_map": couro_map,
            "period_labels": couro_labels,
            "default_years": [202602],
            "periodicity": "quarterly",
            "level": "N3",
            "default_cat": 119293,
            "default_var": 622,
            "extra_classifications": {"12716": 115236},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Pesquisa Trimestral do Couro — Nível UF (N3) e Sigilo Estatístico",
            "notice_text": (
                "Série trimestral (1T/1999 a 2T/2026) disponível apenas por UF/Brasil (N3). Unidades federativas "
                "com poucos curtumes informantes exibem sigilo ('X' / '..') no SIDRA."
            ),
            "variables": [
                {"id": 622, "name": "Quantidade de Couro Cru Bovino Adquirido", "slug": "couro_cru_adquirido", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "sum"},
                {"id": 151, "name": "Número de Curtumes Informantes", "slug": "couro_cru_informantes", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
            ],
        },
        {
            "id": "COURO_CURTIDO_TRIMESTRAL_UF",
            "group": "PECUARIA_AQUI",
            "name": "Couro Trimestral: Couro Curtido por Método (Cromo/Tanino, UF)",
            "table": 1090,
            "classification": 11532,
            "category_source": "P3_1090_11532",
            "min_year": 1999,
            "max_year": 2026,
            "valid_years": couro_valid,
            "period_map": couro_map,
            "period_labels": couro_labels,
            "default_years": [202602],
            "periodicity": "quarterly",
            "level": "N3",
            "default_cat": 119294,
            "default_var": 624,
            "extra_classifications": {"12716": 115236},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Pesquisa Trimestral do Couro — Método de Curtimento (N3)",
            "notice_text": (
                "Série trimestral estadual (N3) diferenciando curtimento ao cromo, ao tanino e outros métodos, "
                "sujeita a sigilo estatístico ('X') em estados com baixa concentração de curtumes."
            ),
            "variables": [
                {"id": 624, "name": "Quantidade de Couro Curtido Bovino", "slug": "couro_curtido_qtd", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "sum"},
                {"id": 151, "name": "Número de Curtumes Informantes", "slug": "couro_curtido_informantes", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
            ],
        },
        {
            "id": "CAGRO_PECUARIA_EFETIVO",
            "group": "PECUARIA_AQUI",
            "name": "Censo Agro 2017: Efetivo da Pecuária nos Estabelecimentos",
            "table": 6907,
            "classification": 12443,
            "category_source": "P3_6907_12443",
            "min_year": 2017,
            "max_year": 2017,
            "valid_years": [2017],
            "level": "N6",
            "default_cat": 110056,
            "default_var": 2209,
            "extra_classifications": {"829": 46302, "218": 46502},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Censo Agropecuário 2017 — Rebanhos com Filtro de Tipologia",
            "notice_text": (
                "Recorte único de 2017 complementar à PPM anual: permite cruzar efetivo bovino, suíno, equino e "
                "outros rebanhos por agricultura familiar/Pronaf/Pronamp e condição das terras."
            ),
            "variables": [
                {"id": 2209, "name": "Número de Cabeças", "slug": "cagro_pecuaria_cabecas", "unit": "Cabeças", "multiplier": 1.0, "agg_mode": "last"},
                {"id": 10010, "name": "Estabelecimentos com Efetivo da Pecuária", "slug": "cagro_pecuaria_estab", "unit": "Estabelecimentos", "multiplier": 1.0, "agg_mode": "last"},
            ],
        },

        # =====================================================================
        # ECONOMIA, DEMOGRAFIA DAS EMPRESAS E SERVIÇOS DE HOSPEDAGEM
        # =====================================================================
        {
            "id": "DEMOGRAFIA_EMPRESAS_UF",
            "group": "ECONOMIA_EMPRESAS",
            "name": "Demografia das Empresas: Nascimentos e Sobrevivência (1 a 5 Anos, UF)",
            "table": 9950,
            "classification": 12762,
            "category_source": "P3_9950_12762",
            "min_year": 2017,
            "max_year": 2021,
            "valid_years": list(range(2021, 2016, -1)),
            "default_years": [2021],
            "level": "N3",
            "default_cat": 117897,
            "default_var": 13281,
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Nível Estadual (N3) — Série Publicada de 2017 a 2021",
            "notice_text": (
                "Estatísticas de nascimentos de unidades locais empregadoras e taxas de sobrevivência de 1 a 5 anos "
                "por seção CNAE 2.0, divulgadas pelo IBGE em nível estadual/Brasil (N3) até 2021."
            ),
            "variables": [
                {"id": 13281, "name": "Nascimentos de Unidades Locais Empregadoras", "slug": "empresas_nascimentos", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "sum"},
                {"id": 13235, "name": "Taxa de 1 Ano de Sobrevivência (%)", "slug": "sobrevivencia_1ano", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 13236, "name": "Taxa de 2 Anos de Sobrevivência (%)", "slug": "sobrevivencia_2anos", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 13237, "name": "Taxa de 3 Anos de Sobrevivência (%)", "slug": "sobrevivencia_3anos", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 13238, "name": "Taxa de 4 Anos de Sobrevivência (%)", "slug": "sobrevivencia_4anos", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 13239, "name": "Taxa de 5 Anos de Sobrevivência (%)", "slug": "sobrevivencia_5anos", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            ],
        },
        {
            "id": "SERVICOS_HOSPEDAGEM",
            "group": "ECONOMIA_EMPRESAS",
            "name": "Serviços de Hospedagem: Hotéis, Pousadas, UHs e Leitos (2016)",
            "table": 6589,
            "classification": 493,
            "category_source": "P3_6589_493",
            "min_year": 2016,
            "max_year": 2016,
            "valid_years": [2016],
            "level": "N6",
            "default_cat": 40474,
            "default_var": 9296,
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Pesquisa de Serviços de Hospedagem 2016 — Amostra Municipal Selecionada",
            "notice_text": (
                "Levantamento único de 2016 voltado a capitais, regiões metropolitanas e municípios de vocação "
                "turística selecionados (~3.412 municípios no Brasil). Municípios fora do recorte permanecem "
                "sem dado publicado."
            ),
            "variables": [
                {"id": 9296, "name": "Número de Leitos", "slug": "hospedagem_leitos", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
                {"id": 1322, "name": "Número de Unidades Habitacionais", "slug": "hospedagem_uhs", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
                {"id": 1321, "name": "Número de Estabelecimentos de Hospedagem", "slug": "hospedagem_estab", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
            ],
        },

        # =====================================================================
        # TRABALHO E RENDIMENTO: PNAD CONTÍNUA COMPLEMENTAR (UF / N3)
        # =====================================================================
        {
            "id": "PNAD_OCUPACAO_CARTEIRA_UF",
            "group": "TRABALHO_RENDA",
            "name": "PNAD Contínua: Posição na Ocupação e Carteira Assinada (UF)",
            "table": 4097,
            "classification": 11913,
            "category_source": "P3_4097_11913",
            "min_year": 2012,
            "max_year": 2026,
            "valid_years": pnad_valid,
            "period_map": pnad_map,
            "period_labels": pnad_labels,
            "default_years": [202602],
            "periodicity": "quarterly",
            "level": "N3",
            "default_cat": 96165,
            "default_var": 4090,
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "PNAD Contínua Trimestral (UF / N3) — Valores em Mil Pessoas",
            "notice_text": (
                "Série trimestral estadual (N3, 1T/2012 a 2T/2026) detalhando empregados com e sem carteira "
                "assinada, trabalhadores domésticos, setor público, empregadores e conta própria. Valores "
                "absolutos informados em mil pessoas."
            ),
            "variables": [
                {"id": 4090, "name": "Pessoas Ocupadas (14 anos ou mais)", "slug": "pnad_ocupados_categoria", "unit": "Mil pessoas", "multiplier": 1.0, "agg_mode": "last"},
                {"id": 4108, "name": "Distribuição Percentual da Ocupação (%)", "slug": "pnad_ocupados_pct", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            ],
        },
        {
            "id": "PNAD_SUBUTILIZACAO_UF",
            "group": "TRABALHO_RENDA",
            "name": "PNAD Contínua: Subutilização da Força de Trabalho e Força Potencial (UF)",
            "table": 4100,
            "classification": 604,
            "category_source": "P3_4100_604",
            "min_year": 2012,
            "max_year": 2026,
            "valid_years": pnad_valid,
            "period_map": pnad_map,
            "period_labels": pnad_labels,
            "default_years": [202602],
            "periodicity": "quarterly",
            "level": "N3",
            "partial_n6": True,
            "default_cat": 40287,
            "default_var": 1641,
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "PNAD Contínua Trimestral — Subutilização Ampliada (N3)",
            "notice_text": (
                "Cobertura completa das 27 UFs (N3) de 1T/2012 a 2T/2026 para desocupados, subocupados por "
                "insuficiência de horas e força de trabalho potencial (valores em mil pessoas)."
            ),
            "variables": [
                {"id": 1641, "name": "Pessoas de 14 Anos ou Mais por Medida de Subutilização", "slug": "pnad_subutilizacao_qtd", "unit": "Mil pessoas", "multiplier": 1.0, "agg_mode": "last"},
                {"id": 4104, "name": "Distribuição Percentual (%)", "slug": "pnad_subutilizacao_pct", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            ],
        },

        # =====================================================================
        # DEMOGRAFIA: CENSO 2022 COMPLEMENTAR E PROJEÇÕES DA POPULAÇÃO
        # =====================================================================
        {
            "id": "CENSO22_INTERNET_DOM",
            "group": "DEMOGRAFIA_EDUCACAO",
            "name": "Censo 2022: Conexão Domiciliar à Internet (10+ Anos)",
            "table": 10201,
            "classification": 2072,
            "category_source": "P3_10201_2072",
            "min_year": 2022,
            "max_year": 2022,
            "valid_years": [2022],
            "level": "N6",
            "default_cat": 77585,
            "default_var": 1013436,
            "extra_classifications": {"133": 95278},
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "Censo Demográfico 2022 — Acesso à Internet nos Domicílios",
            "notice_text": (
                "Ano único (2022). Por padrão seleciona moradores de 10+ anos com conexão domiciliar à "
                "internet (Sim) e o percentual correspondente sobre o total municipal."
            ),
            "variables": [
                {"id": 1013436, "name": "Percentual de Moradores 10+ com/sem Internet (%)", "slug": "censo22_internet_pct", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 13436, "name": "Moradores 10+ Anos em Domicílios Permanentes", "slug": "censo22_internet_pessoas", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            ],
        },
        {
            "id": "CENSO22_FECUNDIDADE",
            "group": "DEMOGRAFIA_EDUCACAO",
            "name": "Censo 2010/2022: Fecundidade (Mulheres 12+ e Filhos Nascidos Vivos)",
            "table": 10078,
            "classification": 12232,
            "category_source": "P3_10078_12232",
            "min_year": 2010,
            "max_year": 2022,
            "valid_years": [2022, 2010],
            "level": "N6",
            "default_cat": 58896,
            "default_var": 13316,
            "extra_classifications": {"1568": 120704, "12293": 58898},
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "Série Comparativa Censitária (2010 e 2022)",
            "notice_text": (
                "Disponível exclusivamente para os Censos de 2010 e 2022, com cruzamentos opcionais de faixa "
                "etária da mulher, nível de instrução e cor ou raça."
            ),
            "variables": [
                {"id": 13316, "name": "Filhos Tidos Nascidos Vivos pelas Mulheres de 12+ Anos", "slug": "censo_filhos_nascidos_vivos", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
                {"id": 13317, "name": "Filhos Nascidos Vivos nos Últimos 12 Meses", "slug": "censo_filhos_12_meses", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
                {"id": 13315, "name": "Mulheres de 12 Anos ou Mais de Idade", "slug": "censo_mulheres_12_mais", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
                {"id": 13318, "name": "Filhos Tidos que Estavam Vivos na Data de Referência", "slug": "censo_filhos_sobreviventes", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            ],
        },
        {
            "id": "CENSO22_AUTISMO",
            "group": "DEMOGRAFIA_EDUCACAO",
            "name": "Censo 2022: Pessoas e Domicílios com Diagnóstico de Autismo (TEA)",
            "table": 10154,
            "classification": 458,
            "category_source": "P3_10154_458",
            "min_year": 2022,
            "max_year": 2022,
            "valid_years": [2022],
            "level": "N6",
            "default_cat": 72117,
            "default_var": 13411,
            "extra_classifications": {"1821": 72129},
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "Censo Demográfico 2022 — Levantamento Inédito sobre Autismo (TEA)",
            "notice_text": (
                "Ano único (2022). Traz o total e o percentual de moradores diagnosticados com autismo e de "
                "domicílios com pelo menos um morador diagnosticado."
            ),
            "variables": [
                {"id": 13411, "name": "Percentual de Moradores Diagnosticados com Autismo (%)", "slug": "censo22_autismo_pct_moradores", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 13312, "name": "Moradores Diagnosticados com Autismo", "slug": "censo22_autismo_moradores", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
                {"id": 13412, "name": "Percentual de Domicílios c/ Morador com Autismo (%)", "slug": "censo22_autismo_pct_domic", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 13313, "name": "Domicílios com Pelo Menos 1 Morador com Autismo", "slug": "censo22_autismo_domicilios", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
            ],
        },
        {
            "id": "CENSO22_SUBREGISTRO_NASC",
            "group": "DEMOGRAFIA_EDUCACAO",
            "name": "Censo 2022: Registro de Nascimento e Sub-registro (0 a 5 Anos)",
            "table": 9953,
            "classification": 297,
            "category_source": "P3_9953_297",
            "min_year": 2022,
            "max_year": 2022,
            "valid_years": [2022],
            "level": "N6",
            "default_cat": 2766,
            "default_var": 9459,
            "extra_classifications": {"287": 100362, "2661": 32776, "1": 6795},
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "Censo 2022 — Sub-registro Civil de Nascimento (0 a 5 Anos)",
            "notice_text": (
                "Ano único (2022). Por padrão seleciona crianças sem registro de nascimento; permite "
                "comparar crianças indígenas, áreas urbanas/rurais e terras indígenas."
            ),
            "variables": [
                {"id": 9459, "name": "Pessoas de Até 5 Anos de Idade", "slug": "censo22_reg_nasc_criancas", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
                {"id": 9463, "name": "Pessoas Indígenas de Até 5 Anos de Idade", "slug": "censo22_reg_nasc_indigenas", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            ],
        },
        {
            "id": "PROJECAO_VIDA_MORT_UF",
            "group": "DEMOGRAFIA_EDUCACAO",
            "name": "Projeção da População (2000–2060): Esperança de Vida e Mortalidade Infantil (UF)",
            "table": 7362,
            "classification": 1933,
            "category_source": "P3_7362_1933",
            "min_year": 2018,
            "max_year": 2018,
            "valid_years": [2018],
            "level": "N3",
            "default_cat": 49042,
            "default_var": 2503,
            "extra_classifications": {"2": 6794},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Atenção à Seleção do Ano Projetado (2000–2060) — Nível UF (N3)",
            "notice_text": (
                "Na estrutura oficial desta tabela do SIDRA, o período base fica fixo em 2018 (edição da "
                "projeção) e o ANO PROJETADO (2000 a 2060) é escolhido no seletor de categorias acima "
                "(padrão 2026). Disponível apenas por UF (N3)."
            ),
            "variables": [
                {"id": 2503, "name": "Esperança de Vida ao Nascer", "slug": "proj_esperanca_vida", "unit": "Anos", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 1940, "name": "Taxa de Mortalidade Infantil (por mil nascidos vivos)", "slug": "proj_mortalidade_infantil", "unit": "‰", "multiplier": 1.0, "agg_mode": "mean"},
            ],
        },
        {
            "id": "PROJECAO_DINAMICA_DEMOG_UF",
            "group": "DEMOGRAFIA_EDUCACAO",
            "name": "Projeção da População (2000–2060): Saldo Migratório, Fecundidade e Envelhecimento (UF)",
            "table": 7360,
            "classification": 1933,
            "category_source": "P3_7362_1933",
            "min_year": 2018,
            "max_year": 2018,
            "valid_years": [2018],
            "level": "N3",
            "default_cat": 49042,
            "default_var": 10602,
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Projeção Demográfica (2000–2060) — Ano Selecionado na Categoria (N3)",
            "notice_text": (
                "O período no SIDRA permanece fixo em 2018 e o ano projetado (2000 a 2060) é selecionado "
                "como categoria (padrão 2026). Suporta valores negativos em saldo migratório e taxa de crescimento."
            ),
            "variables": [
                {"id": 10602, "name": "Saldo Migratório Total", "slug": "proj_saldo_migratorio", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
                {"id": 10605, "name": "Taxa de Crescimento Geométrico (%)", "slug": "proj_taxa_crescimento", "unit": "%", "multiplier": 1.0, "agg_mode": "mean", "allow_negative": True},
                {"id": 2493, "name": "Taxa de Fecundidade Total", "slug": "proj_fecundidade", "unit": "Filhos", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 10612, "name": "Índice de Envelhecimento (%)", "slug": "proj_indice_envelhecimento", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 10613, "name": "Idade Mediana da População", "slug": "proj_idade_mediana", "unit": "Anos", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 10600, "name": "Nascimentos Anuais Projetados", "slug": "proj_nascimentos", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "sum"},
                {"id": 10601, "name": "Óbitos Anuais Projetados", "slug": "proj_obitos", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "sum"},
            ],
        },

        # =====================================================================
        # URBANO, SANEAMENTO (PNSB) E GESTÃO MUNICIPAL (MUNIC)
        # =====================================================================
        {
            "id": "CENSO22_ENTORNO_URBANISTICO",
            "group": "URBANO_SANEAMENTO_GESTAO",
            "name": "Censo 2022: Entorno Urbanístico dos Domicílios (Pavimentação, Iluminação, Arborização)",
            "table": 10050,
            "classification": 14,
            "category_source": "P3_10050_14",
            "min_year": 2022,
            "max_year": 2022,
            "valid_years": [2022],
            "level": "N6",
            "default_cat": 72246,
            "default_var": 1009611,
            "extra_classifications": {"2075": 77703},
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "Censo 2022 — Características Urbanísticas do Entorno",
            "notice_text": (
                "Pesquisa Urbanística do Entorno dos Domicílios (ano único 2022). Padrão selecionado: via "
                "pavimentada (%). Você pode filtrar pavimentação, iluminação pública, calçada, bueiro, "
                "ciclovia, rampa de acessibilidade e arborização."
            ),
            "variables": [
                {"id": 1009611, "name": "Percentual de Domicílios com a Característica (%)", "slug": "censo22_entorno_pct", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 9611, "name": "Domicílios em Setores Selecionados", "slug": "censo22_entorno_domic", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
            ],
        },
        {
            "id": "PNSB_REDE_ESGOTO",
            "group": "URBANO_SANEAMENTO_GESTAO",
            "name": "PNSB 2017: Extensão da Rede Coletora de Esgoto (km)",
            "table": 7483,
            "classification": 12005,
            "category_source": "P3_7483_12005",
            "min_year": 2017,
            "max_year": 2017,
            "valid_years": [2017],
            "level": "N6",
            "default_cat": 2074,
            "default_var": 10757,
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "PNSB 2017 — Rede Coletora de Esgoto Sem Categoria Total",
            "notice_text": (
                "Ano de referência 2017. A tabela detalha apenas tipos individuais de rede (Separadora convencional, "
                "Unitária convencional e Condominial), não possuindo categoria Total agregada; municípios sem "
                "rede operante aparecem sem registro."
            ),
            "variables": [
                {"id": 10757, "name": "Extensão da Rede Coletora de Esgoto", "slug": "pnsb_extensao_rede_esgoto", "unit": "Quilômetros", "multiplier": 1.0, "agg_mode": "last"},
                {"id": 10656, "name": "Município com Rede Coletora (Sim = 1)", "slug": "pnsb_mun_rede_esgoto", "unit": "Municípios", "multiplier": 1.0, "agg_mode": "last", "is_binary": True},
            ],
        },
        {
            "id": "PNSB_ETES_ESGOTO",
            "group": "URBANO_SANEAMENTO_GESTAO",
            "name": "PNSB 2017: Estações de Tratamento de Esgoto (ETEs)",
            "table": 7478,
            "classification": 946,
            "category_source": "P3_7478_946",
            "min_year": 2017,
            "max_year": 2017,
            "valid_years": [2017],
            "level": "N6",
            "default_cat": 48514,
            "default_var": 10674,
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "PNSB 2017 — Estações de Tratamento de Esgoto (ETEs)",
            "notice_text": (
                "Ano único (2017). Mostra o número de ETEs segundo condição de operação (padrão: Em operação). "
                "Apenas municípios com unidades cadastradas possuem valor numérico."
            ),
            "variables": [
                {"id": 10674, "name": "Número de Estações de Tratamento (ETEs)", "slug": "pnsb_numero_etes", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
                {"id": 10673, "name": "Município com ETE (Sim = 1)", "slug": "pnsb_mun_com_ete", "unit": "Municípios", "multiplier": 1.0, "agg_mode": "last", "is_binary": True},
            ],
        },
        {
            "id": "PNSB_RESIDUOS_SOLIDOS",
            "group": "URBANO_SANEAMENTO_GESTAO",
            "name": "PNSB (2000/2008): Manejo de Resíduos Sólidos e Coleta Seletiva (Binário)",
            "table": 1241,
            "classification": 11461,
            "category_source": "P3_1241_11461",
            "min_year": 2000,
            "max_year": 2008,
            "valid_years": [2008, 2000],
            "level": "N6",
            "default_cat": 91763,
            "default_var": 2594,
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Dado Histórico (Último Levantamento PNSB de Resíduos: 2008)",
            "notice_text": (
                "A pesquisa mais recente de manejo de resíduos sólidos da PNSB no SIDRA refere-se a 2008 "
                "(pois a edição de 2017 abrangeu apenas água e esgoto). Para informações municipais mais "
                "atuais sobre gestão de resíduos, consulte também MUNIC PGIRS (2020)."
            ),
            "variables": [
                {"id": 2594, "name": "Município Enquadrado / Coleta Seletiva (Indicador Sim = 1)", "slug": "pnsb_residuos_binario", "unit": "Municípios", "multiplier": 1.0, "agg_mode": "last", "is_binary": True},
            ],
        },
        {
            "id": "PNSB_DRENAGEM_URBANA",
            "group": "URBANO_SANEAMENTO_GESTAO",
            "name": "PNSB (2000/2008): Serviço de Drenagem Urbana Subterrânea (Binário)",
            "table": 2230,
            "classification": 12005,
            "category_source": "P3_2230_12005",
            "min_year": 2000,
            "max_year": 2008,
            "valid_years": [2008, 2000],
            "level": "N6",
            "default_cat": 101287,
            "default_var": 1164,
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Dado Histórico (Último Levantamento PNSB de Drenagem: 2008)",
            "notice_text": (
                "A edição de 2017 da PNSB não investigou drenagem urbana; portanto o dado oficial mais recente "
                "desta tabela é de 2008 (série 2000 e 2008, indicador binário Sim = 1)."
            ),
            "variables": [
                {"id": 1164, "name": "Município com Drenagem Urbana Subterrânea (Indicador Sim = 1)", "slug": "pnsb_drenagem_binario", "unit": "Municípios", "multiplier": 1.0, "agg_mode": "last", "is_binary": True},
            ],
        },
        {
            "id": "MUNIC_MEIO_AMBIENTE",
            "group": "URBANO_SANEAMENTO_GESTAO",
            "name": "MUNIC 2020: Recursos Financeiros Próprios para Meio Ambiente (Binário)",
            "table": 8486,
            "classification": 1166,
            "category_source": "P3_8486_1166",
            "min_year": 2020,
            "max_year": 2020,
            "valid_years": [2020],
            "level": "N6",
            "default_cat": 50645,
            "default_var": 603,
            "extra_classifications": {"12446": 47692},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Indicador Binário Municipal (MUNIC 2020)",
            "notice_text": (
                "Ano único (2020). Valores codificados automaticamente como Sim = 1 e Não / Sem registro = 0."
            ),
            "variables": [
                {"id": 603, "name": "Município Enquadrado (Indicador Sim = 1)", "slug": "munic_recursos_meio_ambiente", "unit": "Municípios", "multiplier": 1.0, "agg_mode": "last", "is_binary": True},
            ],
        },
        {
            "id": "MUNIC_PGIRS_RESIDUOS",
            "group": "URBANO_SANEAMENTO_GESTAO",
            "name": "MUNIC 2020: Plano de Gestão Integrada de Resíduos Sólidos — PGIRS (Binário)",
            "table": 8488,
            "classification": 1173,
            "category_source": "P3_8488_1173",
            "min_year": 2020,
            "max_year": 2020,
            "valid_years": [2020],
            "level": "N6",
            "default_cat": 50684,
            "default_var": 603,
            "extra_classifications": {"12446": 47692, "1174": 50688},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Indicador Binário Municipal — MUNIC PGIRS 2020",
            "notice_text": (
                "Ano único (2020). Mostra presença municipal de Plano de Gestão Integrada de Resíduos Sólidos "
                "(Sim = 1 / Não = 0) com subfiltro de programas ambientais em parceria federal."
            ),
            "variables": [
                {"id": 603, "name": "Município com PGIRS / Categoria (Indicador Sim = 1)", "slug": "munic_pgirs", "unit": "Municípios", "multiplier": 1.0, "agg_mode": "last", "is_binary": True},
            ],
        },
        {
            "id": "MUNIC_SECA_ESTIAGEM",
            "group": "URBANO_SANEAMENTO_GESTAO",
            "name": "MUNIC 2020: Ocorrência de Seca/Estiagem e Planos de Contingência (Binário)",
            "table": 8530,
            "classification": 1346,
            "category_source": "P3_8530_1346",
            "min_year": 2020,
            "max_year": 2020,
            "valid_years": [2020],
            "level": "N6",
            "default_cat": 57248,
            "default_var": 603,
            "extra_classifications": {"12446": 47692, "1347": 57252},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Indicador Binário Municipal — Ocorrência de Seca (MUNIC 2020)",
            "notice_text": (
                "Ano único (2020). Identifica municípios atingidos por seca nos 4 anos anteriores (Sim = 1), "
                "com filtro secundário de Plano de Contingência para a seca."
            ),
            "variables": [
                {"id": 603, "name": "Município Enquadrado (Indicador Sim = 1)", "slug": "munic_seca", "unit": "Municípios", "multiplier": 1.0, "agg_mode": "last", "is_binary": True},
            ],
        },
        {
            "id": "MUNIC_SEGURANCA_ALIMENTAR",
            "group": "URBANO_SANEAMENTO_GESTAO",
            "name": "MUNIC 2023: Lei Municipal de Segurança Alimentar e Nutricional (Binário)",
            "table": 10010,
            "classification": 1949,
            "category_source": "P3_10010_1949",
            "min_year": 2023,
            "max_year": 2023,
            "valid_years": [2023],
            "level": "N6",
            "default_cat": 72978,
            "default_var": 603,
            "extra_classifications": {"12446": 47692},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Indicador Binário Municipal — MUNIC 2023",
            "notice_text": (
                "Ano único (2023). Identifica presença de lei municipal de segurança alimentar e nutricional "
                "(Sim = 1 / Não = 0)."
            ),
            "variables": [
                {"id": 603, "name": "Município Enquadrado (Indicador Sim = 1)", "slug": "munic_seguranca_alimentar", "unit": "Municípios", "multiplier": 1.0, "agg_mode": "last", "is_binary": True},
            ],
        },
        {
            "id": "MUNIC_MULHERES_ABRIGO",
            "group": "URBANO_SANEAMENTO_GESTAO",
            "name": "MUNIC 2023: Casas-Abrigo / Acolhimento para Mulheres em Violência (Binário)",
            "table": 10021,
            "classification": 1999,
            "category_source": "P3_10021_1999",
            "min_year": 2023,
            "max_year": 2023,
            "valid_years": [2023],
            "level": "N6",
            "default_cat": 73131,
            "default_var": 603,
            "extra_classifications": {"12446": 47692},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Indicador Binário Municipal — MUNIC 2023",
            "notice_text": (
                "Ano único (2023). Identifica municípios que possuem casa-abrigo ou serviço de acolhimento para "
                "mulheres em situação de violência (Sim = 1)."
            ),
            "variables": [
                {"id": 603, "name": "Município com Casa-Abrigo (Indicador Sim = 1)", "slug": "munic_casas_abrigo", "unit": "Municípios", "multiplier": 1.0, "agg_mode": "last", "is_binary": True},
            ],
        },
        {
            "id": "MUNIC_SEGURANCA_PUBLICA",
            "group": "URBANO_SANEAMENTO_GESTAO",
            "name": "MUNIC 2023: Guarda Municipal, Bombeiros, IML e Comarca (Binário)",
            "table": 10027,
            "classification": 2010,
            "category_source": "P3_10027_2010",
            "min_year": 2023,
            "max_year": 2023,
            "valid_years": [2023],
            "level": "N6",
            "default_cat": 73552,
            "default_var": 603,
            "extra_classifications": {"12446": 47692},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Indicador Binário Municipal — Infraestrutura de Segurança Pública (2023)",
            "notice_text": (
                "Ano único (2023). Selecione na categoria: Guarda Municipal, Unidade do Corpo de Bombeiros, "
                "Instituto Médico Legal (IML) ou Sede de Comarca (Sim = 1)."
            ),
            "variables": [
                {"id": 603, "name": "Município com Equipamento / Sede (Indicador Sim = 1)", "slug": "munic_seguranca_publica", "unit": "Municípios", "multiplier": 1.0, "agg_mode": "last", "is_binary": True},
            ],
        },
        {
            "id": "MUNIC_PRIMEIRA_INFANCIA",
            "group": "URBANO_SANEAMENTO_GESTAO",
            "name": "MUNIC 2023: Plano Municipal para a Primeira Infância (Binário)",
            "table": 10044,
            "classification": 2061,
            "category_source": "P3_10044_2061",
            "min_year": 2023,
            "max_year": 2023,
            "valid_years": [2023],
            "level": "N6",
            "default_cat": 74122,
            "default_var": 603,
            "extra_classifications": {"12446": 47692},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Indicador Binário Municipal — MUNIC 2023",
            "notice_text": (
                "Ano único (2023). Identifica municípios com Plano Municipal para a Primeira Infância "
                "(Sim = 1 / Não = 0)."
            ),
            "variables": [
                {"id": 603, "name": "Município com Plano para 1ª Infância (Indicador Sim = 1)", "slug": "munic_primeira_infancia", "unit": "Municípios", "multiplier": 1.0, "agg_mode": "last", "is_binary": True},
            ],
        },
        {
            "id": "MUNIC_CRECHES",
            "group": "URBANO_SANEAMENTO_GESTAO",
            "name": "MUNIC 2021: Municípios com Creches Públicas Municipais (Binário)",
            "table": 9701,
            "classification": 1526,
            "category_source": "P3_9701_1526",
            "min_year": 2021,
            "max_year": 2021,
            "valid_years": [2021],
            "level": "N6",
            "default_cat": 58852,
            "default_var": 12833,
            "extra_classifications": {"12446": 47692},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Indicador Binário Municipal — MUNIC Educação / Creches (2021)",
            "notice_text": (
                "Ano único (2021). Permite identificar presença de creches municipais (ou em período integral) "
                "e filtrar por faixas de quantidade de creches (Indicador Sim = 1)."
            ),
            "variables": [
                {"id": 12833, "name": "Município com Creche Municipal (Indicador Sim = 1)", "slug": "munic_creches", "unit": "Municípios", "multiplier": 1.0, "agg_mode": "last", "is_binary": True},
                {"id": 13073, "name": "Município com Creche em Período Integral (Indicador Sim = 1)", "slug": "munic_creches_integrais", "unit": "Municípios", "multiplier": 1.0, "agg_mode": "last", "is_binary": True},
            ],
        },

        # =====================================================================
        # REGISTRO CIVIL COMPLEMENTAR: DIVÓRCIOS
        # =====================================================================
        {
            "id": "RC_DIVORCIOS",
            "group": "REGISTRO_CIVIL",
            "name": "Estatísticas do Registro Civil: Divórcios Concedidos (1ª Instância / Escritura)",
            "table": 1695,
            "classification": 345,
            "category_source": "P3_1695_345",
            "min_year": 2009,
            "max_year": 2024,
            "valid_years": list(range(2024, 2008, -1)),
            "default_years": [2024],
            "level": "N6",
            "default_cat": 0,
            "default_var": 393,
            "extra_classifications": {"274": 0, "275": 0, "269": 0},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Atenção Territorial — Registro pelo Município da Vara Judicial / Cartório",
            "notice_text": (
                "Série 2009–2024 em nível municipal (N6). Os divórcios são computados pelo município da vara de "
                "família ou tabelionato onde tramitou o processo (sede de comarca), e não necessariamente pelo "
                "domicílio dos cônjuges."
            ),
            "variables": [
                {"id": 393, "name": "Número de Divórcios Concedidos", "slug": "rc_divorcios", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "sum"},
            ],
        },
    ]
