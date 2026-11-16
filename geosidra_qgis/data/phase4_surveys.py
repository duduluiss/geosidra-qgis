# -*- coding: utf-8 -*-
"""
Pesquisas da Fase 4 de expansão temática do catálogo GeoSIDRA:
- Economia / Empresas: PAIC Construção (2007-2024) e POF (2017-2018)
- Trabalho e Renda: PNAD Contínua Anual (Gini, Rendimento per capita, Segurança Alimentar EBIA) e Censo 2022 (Gini, Deslocamento)
- Demografia e Educação: PNAD Anual (Internet, Celular, Analfabetismo, Escolarização) e Censo 2022 (Migração, Nupcialidade, Etnias/Línguas Indígenas)
- Urbano, Saneamento e Gestão: PNAD Anual Habitação (Água, Esgoto, Lixo, Energia) e MUNIC (SUAS/CRAS, Benefícios, CMAS, Conselhos Tutelares, Transporte, Cultura, Esporte)
- Saúde Pública (PNS - Pesquisa Nacional de Saúde): Cobertura, Doenças Crônicas, Hábitos e SUS
"""

from typing import Any, Dict, List


_PNAD_ANUAL_TIC_YEARS = [2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024, 2025]
_PNAD_ANUAL_EDUC_HAB_YEARS = [2016, 2017, 2018, 2019, 2022, 2023, 2024, 2025]
_PNAD_ANUAL_GINI_YEARS = list(range(2012, 2026))


def _pnad_domicilio_vars(
    pct_dom_id: int,
    mil_dom_id: int,
    pct_mor_id: int,
    mil_mor_id: int,
    slug_prefix: str,
    label_suffix: str,
) -> List[Dict[str, Any]]:
    """Constrói conjunto padrão de variáveis de domicílios e moradores da PNAD Anual."""
    return [
        {
            "id": pct_dom_id,
            "name": f"Distribuição Percentual dos Domicílios — {label_suffix} (%)",
            "slug": f"{slug_prefix}_pct_dom",
            "unit": "%",
            "multiplier": 1.0,
            "agg_mode": "mean",
        },
        {
            "id": mil_dom_id,
            "name": f"Total de Domicílios — {label_suffix}",
            "slug": f"{slug_prefix}_domicilios",
            "unit": "Mil unidades",
            "multiplier": 1.0,
            "agg_mode": "last",
        },
        {
            "id": pct_mor_id,
            "name": f"Distribuição Percentual dos Moradores — {label_suffix} (%)",
            "slug": f"{slug_prefix}_pct_moradores",
            "unit": "%",
            "multiplier": 1.0,
            "agg_mode": "mean",
        },
        {
            "id": mil_mor_id,
            "name": f"Moradores em Domicílios — {label_suffix}",
            "slug": f"{slug_prefix}_moradores",
            "unit": "Mil pessoas",
            "multiplier": 1.0,
            "agg_mode": "last",
        },
    ]


def _munic_survey(
    survey_id: str,
    name: str,
    table: int,
    year: int,
    classification: int,
    category_source: str,
    default_cat: int,
    var_id: int,
    var_name: str,
    var_slug: str,
    extra_classifications: Dict[str, int],
    notice_text: str,
    supported_levels: List[str] | None = None,
) -> Dict[str, Any]:
    """Constrói entrada curada para tabelas binárias da MUNIC."""
    entry: Dict[str, Any] = {
        "id": survey_id,
        "group": "URBANO_SANEAMENTO_GESTAO",
        "name": name,
        "table": table,
        "classification": classification,
        "category_source": category_source,
        "min_year": year,
        "max_year": year,
        "valid_years": [year],
        "level": "N6",
        "default_cat": default_cat,
        "default_var": var_id,
        "extra_classifications": extra_classifications,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": f"Indicador Binário Municipal — MUNIC {year}",
        "notice_text": notice_text,
        "variables": [
            {
                "id": var_id,
                "name": var_name,
                "slug": var_slug,
                "unit": "Municípios",
                "multiplier": 1.0,
                "agg_mode": "last",
                "is_binary": True,
            }
        ],
    }
    if supported_levels is not None:
        entry["supported_levels"] = supported_levels
    return entry


def _pns_survey(
    survey_id: str,
    name: str,
    table: int,
    years: List[int],
    pct_var_id: int,
    mil_var_id: int,
    pct_label: str,
    mil_label: str,
    slug_prefix: str,
    notice_text: str,
    classification: int = 2,
    category_source: str = "P4_PNS_SEXO",
    default_cat: int = 6794,
) -> Dict[str, Any]:
    """Constrói entrada curada para tabelas da Pesquisa Nacional de Saúde (PNS)."""
    period_label = " / ".join(str(y) for y in years)
    return {
        "id": survey_id,
        "group": "SAUDE_PNS",
        "name": name,
        "table": table,
        "classification": classification,
        "category_source": category_source,
        "min_year": min(years),
        "max_year": max(years),
        "valid_years": list(years),
        "default_years": [max(years)],
        "level": "N3",
        "partial_n6": True,
        "default_cat": default_cat,
        "default_var": pct_var_id,
        "extra_classifications": {"1": 6795},
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": f"PNS ({period_label}) — Estados, Regiões e 27 Capitais",
        "notice_text": notice_text,
        "variables": [
            {
                "id": pct_var_id,
                "name": pct_label,
                "slug": f"{slug_prefix}_pct",
                "unit": "%",
                "multiplier": 1.0,
                "agg_mode": "mean",
            },
            {
                "id": mil_var_id,
                "name": mil_label,
                "slug": f"{slug_prefix}_pessoas",
                "unit": "Mil pessoas",
                "multiplier": 1.0,
                "agg_mode": "last",
            },
        ],
    }


def build_phase4_surveys() -> List[Dict[str, Any]]:
    """Retorna as 40 pesquisas curadas da Fase 4 do catálogo GeoSIDRA."""
    return [
        # =====================================================================
        # ECONOMIA, INDÚSTRIA, COMÉRCIO, SERVIÇOS E MEIS (+3)
        # =====================================================================
        {
            "id": "PAIC_CONSTRUCAO_UF",
            "group": "ECONOMIA_EMPRESAS",
            "name": "PAIC: Indústria da Construção Civil por UF (2007 a 2024)",
            "table": 10442,
            "table_series": [
                {"table": 1761, "min_year": 2007, "max_year": 2023},
                {
                    "table": 10442,
                    "min_year": 2024,
                    "max_year": 2024,
                    "var_overrides": {1243: 13807, 1244: 13808},
                },
            ],
            "classification": None,
            "min_year": 2007,
            "max_year": 2024,
            "valid_years": list(range(2007, 2025)),
            "default_years": [2024, 2023],
            "level": "N3",
            "default_var": 1241,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "PAIC — Construção Civil (Série Unificada 2007 a 2024)",
            "notice_text": (
                "Pesquisa Anual da Indústria da Construção (empresas com 5+ pessoas ocupadas). "
                "Combina automaticamente a série 2007-2023 (Tabela 1761) e a série nova 2024 (Tabela 10442) "
                "no nível Estadual (N3) e Grandes Regiões (N2)."
            ),
            "variables": [
                {"id": 1241, "name": "Valor das Incorporações, Obras e Serviços", "slug": "paic_valor_obras", "unit": "Mil Reais", "multiplier": 1.0, "agg_mode": "sum"},
                {"id": 631, "name": "Pessoal Ocupado em 31/12", "slug": "paic_pessoal_ocupado", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
                {"id": 673, "name": "Salários, Retiradas e Remunerações", "slug": "paic_salarios", "unit": "Mil Reais", "multiplier": 1.0, "agg_mode": "sum"},
                {"id": 1245, "name": "Custos das Obras e Serviços da Construção", "slug": "paic_custos_obras", "unit": "Mil Reais", "multiplier": 1.0, "agg_mode": "sum"},
                {"id": 1243, "name": "Empresas da Construção (UF Sede)", "slug": "paic_empresas_sede", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
                {"id": 1244, "name": "Empresas Atuantes na UF", "slug": "paic_empresas_atuantes", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "last"},
            ],
        },
        {
            "id": "POF_DESPESAS_FAMILIARES_UF",
            "group": "ECONOMIA_EMPRESAS",
            "name": "POF 2017-2018: Despesa Média Mensal Familiar por Tipo e Faixa de Renda (UF)",
            "table": 6715,
            "classification": 12190,
            "category_source": "P4_6715_12190",
            "min_year": 2018,
            "max_year": 2018,
            "valid_years": [2018],
            "level": "N3",
            "default_cat": 103536,
            "default_var": 1201,
            "extra_classifications": {"339": 7999},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "POF 2017-2018 — Orçamentos Familiares por UF (N3)",
            "notice_text": (
                "Edição 2017-2018 (referência 2018 no SIDRA) disponível para Estados (N3) e Grandes Regiões (N2). "
                "Traz 93 itens detalhados de despesa familiar (alimentação, habitação, saúde, educação, transporte) "
                "com subfiltro opcional por faixa de rendimento mensal familiar."
            ),
            "variables": [
                {"id": 1201, "name": "Despesa Média Mensal Familiar (Monetária e Não Monetária)", "slug": "pof_despesa_media", "unit": "Reais", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 1204, "name": "Participação do Item na Despesa Total (%)", "slug": "pof_despesa_pct", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            ],
        },
        {
            "id": "POF_RENDIMENTO_FAMILIAR_UF",
            "group": "ECONOMIA_EMPRESAS",
            "name": "POF 2017-2018: Rendimento Médio Mensal Familiar por Origem e Faixa (UF)",
            "table": 6974,
            "classification": 4908,
            "category_source": "P4_6974_4908",
            "min_year": 2018,
            "max_year": 2018,
            "valid_years": [2018],
            "level": "N3",
            "default_cat": 8049,
            "default_var": 388,
            "extra_classifications": {"339": 7999},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "POF 2017-2018 — Composição do Rendimento Familiar por UF (N3)",
            "notice_text": (
                "Edição 2017-2018 (referência 2018 no SIDRA) no nível Estadual (N3) e Regiões (N2). "
                "Detalha 17 origens de rendimento familiar (trabalho, INSS, programas sociais federais, pensões etc.)."
            ),
            "variables": [
                {"id": 388, "name": "Rendimento Total e Variação Patrimonial Médio Mensal", "slug": "pof_rendimento_medio", "unit": "Reais", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 443, "name": "Participação da Origem no Rendimento Total (%)", "slug": "pof_rendimento_pct", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            ],
        },

        # =====================================================================
        # TRABALHO, RENDIMENTO E DESLOCAMENTO (+6)
        # =====================================================================
        {
            "id": "PNAD_ANUAL_GINI_DOM_PC_UF",
            "group": "TRABALHO_RENDA",
            "name": "PNAD Contínua Anual: Índice de Gini do Rendimento Domiciliar per Capita (UF)",
            "table": 7435,
            "classification": None,
            "min_year": 2012,
            "max_year": 2025,
            "valid_years": _PNAD_ANUAL_GINI_YEARS,
            "default_years": [2025],
            "level": "N3",
            "default_var": 10681,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "PNAD Contínua Anual — Desigualdade (Índice de Gini por UF)",
            "notice_text": (
                "Série anual completa de 2012 a 2025 no nível Estadual (N3) e Grandes Regiões (N2). "
                "Valores próximos de 1 indicam maior desigualdade na distribuição do rendimento domiciliar per capita."
            ),
            "variables": [
                {"id": 10681, "name": "Índice de Gini (Rendimento Domiciliar per Capita)", "slug": "pnad_gini_dom_pc", "unit": "Índice", "multiplier": 1.0, "agg_mode": "mean"},
            ],
        },
        {
            "id": "PNAD_ANUAL_GINI_TRAB_UF",
            "group": "TRABALHO_RENDA",
            "name": "PNAD Contínua Anual: Índice de Gini do Rendimento do Trabalho (UF)",
            "table": 7453,
            "classification": None,
            "min_year": 2012,
            "max_year": 2025,
            "valid_years": _PNAD_ANUAL_GINI_YEARS,
            "default_years": [2025],
            "level": "N3",
            "default_var": 10806,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "PNAD Contínua Anual — Gini do Rendimento do Trabalho (2012 a 2025)",
            "notice_text": (
                "Desigualdade salarial entre pessoas ocupadas de 14+ anos com rendimento de trabalho "
                "de 2012 a 2025, disponível para Estados (N3) e Grandes Regiões (N2)."
            ),
            "variables": [
                {"id": 10806, "name": "Índice de Gini (Rendimento do Trabalho)", "slug": "pnad_gini_trabalho", "unit": "Índice", "multiplier": 1.0, "agg_mode": "mean"},
            ],
        },
        {
            "id": "PNAD_ANUAL_RENDIMENTO_DOM_PC_UF",
            "group": "TRABALHO_RENDA",
            "name": "PNAD Contínua Anual: Rendimento Médio Real Domiciliar per Capita (UF/RM)",
            "table": 7395,
            "classification": None,
            "min_year": 2016,
            "max_year": 2025,
            "valid_years": _PNAD_ANUAL_TIC_YEARS,
            "default_years": [2025],
            "level": "N3",
            "default_var": 4196,
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "PNAD Anual — Rendimento Real Domiciliar per Capita (Sem 2020)",
            "notice_text": (
                "Rendimento médio mensal real deflacionado para Estados (N3), RMs/RIDEs (N7/N14) e Regiões (N2). "
                "O suplemento anual não foi divulgado em 2020."
            ),
            "variables": [
                {"id": 4196, "name": "Rendimento Médio Real Domiciliar per Capita", "slug": "pnad_rendimento_dom_pc", "unit": "Reais", "multiplier": 1.0, "agg_mode": "mean"},
            ],
        },
        {
            "id": "CENSO22_GINI_UF",
            "group": "TRABALHO_RENDA",
            "name": "Censo 2022: Índice de Gini do Rendimento Domiciliar per Capita (UF)",
            "table": 10301,
            "classification": None,
            "min_year": 2022,
            "max_year": 2022,
            "valid_years": [2022],
            "level": "N3",
            "default_var": 13418,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "Censo Demográfico 2022 — Índice de Gini Estadual",
            "notice_text": (
                "Ano único (2022), publicado pelo IBGE no nível Estadual (N3) e Grandes Regiões (N2)."
            ),
            "variables": [
                {"id": 13418, "name": "Índice de Gini Domiciliar per Capita (Censo 2022)", "slug": "censo22_gini_dom_pc", "unit": "Índice", "multiplier": 1.0, "agg_mode": "mean"},
            ],
        },
        {
            "id": "CENSO22_MEIO_TRANSPORTE",
            "group": "TRABALHO_RENDA",
            "name": "Censo 2022: Meio de Transporte no Deslocamento Casa-Trabalho (Municípios)",
            "table": 10332,
            "classification": 2088,
            "category_source": "P4_10332_2088",
            "min_year": 2022,
            "max_year": 2022,
            "valid_years": [2022],
            "level": "N6",
            "default_cat": 79488,
            "default_var": 1013377,
            "extra_classifications": {"1568": 120704, "86": 95251},
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "Censo 2022 — Mobilidade Casa-Trabalho",
            "notice_text": (
                "Ano único (2022) para todos os Municípios (N6), Estados (N3) e Regiões (N2). "
                "Permite mapear ocupados por modal (A pé, Bicicleta, Ônibus, Automóvel, Trem/Metrô, Motocicleta etc.) "
                "com filtros de instrução e cor ou raça."
            ),
            "variables": [
                {"id": 1013377, "name": "Percentual de Ocupados por Meio de Transporte (%)", "slug": "censo22_transporte_pct", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 13377, "name": "Pessoas Ocupadas que Trabalham Fora do Domicílio", "slug": "censo22_transporte_pessoas", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            ],
        },
        {
            "id": "PNAD_ANUAL_SEGURANCA_ALIMENTAR_UF",
            "group": "TRABALHO_RENDA",
            "name": "PNAD Contínua Anual: Segurança e Insegurança Alimentar — EBIA (UF)",
            "table": 9552,
            "classification": 12404,
            "category_source": "P4_9552_12404",
            "min_year": 2023,
            "max_year": 2024,
            "valid_years": [2023, 2024],
            "default_years": [2024, 2023],
            "level": "N3",
            "default_cat": 109099,
            "default_var": 9784,
            "extra_classifications": {"1": 6795},
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "PNAD Contínua Anual — Escala Brasileira de Insegurança Alimentar (EBIA)",
            "notice_text": (
                "Disponível para 2023 e 2024 no nível Estadual (N3) e Grandes Regiões (N2). "
                "Padrão selecionado: domicílios com insegurança alimentar (inclui níveis leve, moderado e grave no filtro)."
            ),
            "variables": _pnad_domicilio_vars(
                9784, 162, 10117, 10114, "pnad_ebia", "Segurança Alimentar"
            ),
        },

        # =====================================================================
        # DEMOGRAFIA, EDUCAÇÃO, POVOS E INCLUSÃO SOCIAL (+7)
        # =====================================================================
        {
            "id": "PNAD_ANUAL_INTERNET_UF",
            "group": "DEMOGRAFIA_EDUCACAO",
            "name": "PNAD Contínua Anual: Uso da Internet na População de 10+ Anos (UF/RM)",
            "table": 7334,
            "classification": 58,
            "category_source": "P4_7334_58",
            "min_year": 2016,
            "max_year": 2025,
            "valid_years": _PNAD_ANUAL_TIC_YEARS,
            "default_years": [2025],
            "level": "N3",
            "default_cat": 95253,
            "default_var": 10659,
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "PNAD Anual TIC — Uso da Internet (2016-2019 e 2021-2025)",
            "notice_text": (
                "Suplemento TIC disponível para Estados (N3), RMs/RIDEs (N7/N14) e Regiões (N2), por grupo de idade. "
                "O suplemento não foi realizado em 2020."
            ),
            "variables": [
                {"id": 10659, "name": "Percentual de Pessoas 10+ que Utilizaram a Internet (%)", "slug": "pnad_internet_pct", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            ],
        },
        {
            "id": "PNAD_ANUAL_CELULAR_UF",
            "group": "DEMOGRAFIA_EDUCACAO",
            "name": "PNAD Contínua Anual: Posse de Telefone Celular Pessoal — 10+ Anos (UF/RM)",
            "table": 7376,
            "classification": 58,
            "category_source": "P4_7334_58",
            "min_year": 2016,
            "max_year": 2025,
            "valid_years": _PNAD_ANUAL_TIC_YEARS,
            "default_years": [2025],
            "level": "N3",
            "default_cat": 95253,
            "default_var": 10663,
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "PNAD Anual TIC — Telefone Móvel Celular Pessoal (Sem 2020)",
            "notice_text": (
                "Disponível para 2016-2019 e 2021-2025 em Estados (N3), RMs/RIDEs (N7/N14) e Regiões (N2)."
            ),
            "variables": [
                {"id": 10663, "name": "Percentual de Pessoas 10+ com Celular para Uso Pessoal (%)", "slug": "pnad_celular_pct", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            ],
        },
        {
            "id": "PNAD_ANUAL_ANALFABETISMO_UF",
            "group": "DEMOGRAFIA_EDUCACAO",
            "name": "PNAD Contínua Anual: Taxa de Analfabetismo 15+ Anos por UF/RM",
            "table": 7113,
            "classification": 58,
            "category_source": "P4_7113_58",
            "min_year": 2016,
            "max_year": 2025,
            "valid_years": _PNAD_ANUAL_EDUC_HAB_YEARS,
            "default_years": [2025],
            "level": "N3",
            "default_cat": 2795,
            "default_var": 10267,
            "extra_classifications": {"2": 6794},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "PNAD Anual Educação — Taxa de Analfabetismo (Sem 2020 e 2021)",
            "notice_text": (
                "Módulo anual de Educação com série em 2016-2019 e 2022-2025 (não coletado em 2020-2021) "
                "para Estados (N3), RMs/RIDEs (N7/N14) e Regiões (N2), com recorte de faixa etária e sexo."
            ),
            "variables": [
                {"id": 10267, "name": "Taxa de Analfabetismo (15 Anos ou Mais)", "slug": "pnad_analfabetismo_pct", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            ],
        },
        {
            "id": "PNAD_ANUAL_ESCOLARIZACAO_UF",
            "group": "DEMOGRAFIA_EDUCACAO",
            "name": "PNAD Contínua Anual: Taxa de Escolarização por Faixa Etária (UF/RM/Capitais)",
            "table": 7138,
            "classification": 58,
            "category_source": "P4_7138_58",
            "min_year": 2016,
            "max_year": 2025,
            "valid_years": _PNAD_ANUAL_EDUC_HAB_YEARS,
            "default_years": [2025],
            "level": "N3",
            "partial_n6": True,
            "default_cat": 95253,
            "default_var": 10276,
            "extra_classifications": {"2": 6794},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "PNAD Anual Educação — Taxa de Escolarização (N6 = Apenas 27 Capitais)",
            "notice_text": (
                "Disponível para 2016-2019 e 2022-2025 em Estados (N3), RMs/RIDEs (N7/N14) e Regiões (N2). "
                "No nível Municipal (N6), o IBGE publica dados exclusivamente para os 27 municípios das Capitais."
            ),
            "variables": [
                {"id": 10276, "name": "Taxa de Escolarização (%)", "slug": "pnad_escolarizacao_pct", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            ],
        },
        {
            "id": "CENSO22_MIGRACAO_MUN",
            "group": "DEMOGRAFIA_EDUCACAO",
            "name": "Censo 2022: Migração Recente (Pessoas 5+ que Não Residiam no Município Há 5 Anos)",
            "table": 10160,
            "classification": 58,
            "category_source": "P4_10160_58",
            "min_year": 2022,
            "max_year": 2022,
            "valid_years": [2022],
            "level": "N6",
            "default_cat": 95253,
            "default_var": 13435,
            "extra_classifications": {"2": 6794},
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "Censo Demográfico 2022 — Imigração Intermunicipal Quinquenal",
            "notice_text": (
                "Ano único (2022) para todos os Municípios (N6), UFs (N3) e Regiões (N2). "
                "Quantifica moradores com 5+ anos residentes em outro município em 31/07/2017."
            ),
            "variables": [
                {"id": 13435, "name": "Imigrantes 5+ Anos (Últimos 5 Anos)", "slug": "censo22_imigrantes_5anos", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "sum"},
                {"id": 1013435, "name": "Percentual do Total Geral (%)", "slug": "censo22_imigrantes_pct", "unit": "%", "multiplier": 1.0, "agg_mode": "mean"},
            ],
        },
        {
            "id": "CENSO22_ESTADO_CONJUGAL",
            "group": "DEMOGRAFIA_EDUCACAO",
            "name": "Censo 2022: Estado Conjugal (Pessoas 10+ em União ou Não União)",
            "table": 10185,
            "classification": 464,
            "category_source": "P4_10185_464",
            "min_year": 2022,
            "max_year": 2022,
            "valid_years": [2022],
            "level": "N6",
            "default_cat": 12108,
            "default_var": 140,
            "extra_classifications": {"2": 6794, "58": 95253, "86": 95251},
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "Censo Demográfico 2022 — Nupcialidade e Estado Conjugal",
            "notice_text": (
                "Ano único (2022) para Municípios (N6), UFs (N3) e Regiões (N2). "
                "Permite cruzar união conjugal com sexo, faixa etária e cor ou raça."
            ),
            "variables": [
                {"id": 140, "name": "Pessoas de 10 Anos ou Mais de Idade", "slug": "censo22_estado_conjugal_pessoas", "unit": "Pessoas", "multiplier": 1.0, "agg_mode": "last"},
            ],
        },
        {
            "id": "CENSO22_ETNIAS_LINGUAS_IND",
            "group": "DEMOGRAFIA_EDUCACAO",
            "name": "Censo 2022: Diversidade Indígena — Número de Etnias e Línguas Faladas",
            "table": 10412,
            "classification": None,
            "min_year": 2022,
            "max_year": 2022,
            "valid_years": [2022],
            "level": "N6",
            "default_var": 13596,
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Censo 2022 — Etnias e Línguas Indígenas nos Domicílios",
            "notice_text": (
                "Ano único (2022). Contagem distinta de etnias e línguas declaradas em cada município (ou UF); "
                "apenas localidades com população indígena recenseada possuem registro."
            ),
            "variables": [
                {"id": 13596, "name": "Número de Etnias, Povos ou Grupos Indígenas", "slug": "censo22_num_etnias_ind", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "mean"},
                {"id": 13597, "name": "Número de Línguas Indígenas Faladas", "slug": "censo22_num_linguas_ind", "unit": "Unidades", "multiplier": 1.0, "agg_mode": "mean"},
            ],
        },

        # =====================================================================
        # URBANO, FAVELAS, SANEAMENTO E GESTÃO MUNICIPAL (+12)
        # =====================================================================
        {
            "id": "PNAD_ANUAL_AGUA_UF",
            "group": "URBANO_SANEAMENTO_GESTAO",
            "name": "PNAD Contínua Anual: Abastecimento de Água nos Domicílios (UF)",
            "table": 6731,
            "classification": 825,
            "category_source": "P4_6731_825",
            "min_year": 2016,
            "max_year": 2025,
            "valid_years": _PNAD_ANUAL_EDUC_HAB_YEARS,
            "default_years": [2025],
            "level": "N3",
            "default_cat": 46285,
            "default_var": 9784,
            "extra_classifications": {"1": 6795},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "PNAD Anual Habitação — Água (Sem 2020-2021)",
            "notice_text": (
                "Disponível para 2016-2019 e 2022-2025 no nível Estadual (N3) e Regiões (N2). "
                "Padrão selecionado: rede geral de distribuição."
            ),
            "variables": _pnad_domicilio_vars(
                9784, 162, 10117, 10114, "pnad_agua", "Fonte de Água"
            ),
        },
        {
            "id": "PNAD_ANUAL_ESGOTO_UF",
            "group": "URBANO_SANEAMENTO_GESTAO",
            "name": "PNAD Contínua Anual: Esgotamento Sanitário (2019 e 2022-2025, UF/RM/Capitais)",
            "table": 7192,
            "classification": 11558,
            "category_source": "P4_7192_11558",
            "min_year": 2019,
            "max_year": 2025,
            "valid_years": [2019, 2022, 2023, 2024, 2025],
            "default_years": [2025],
            "level": "N3",
            "partial_n6": True,
            "default_cat": 47930,
            "default_var": 9988,
            "extra_classifications": {"1": 6795},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "PNAD Anual Habitação — Esgotamento Sanitário (N6 = Apenas 27 Capitais)",
            "notice_text": (
                "Série harmonizada a partir de 2019 (2019 e 2022-2025) para UFs (N3), RMs/RIDEs (N7/N14) e "
                "Regiões (N2). Em N6 retorna exclusivamente os 27 municípios das Capitais."
            ),
            "variables": _pnad_domicilio_vars(
                9988, 9986, 10133, 10131, "pnad_esgoto", "Esgotamento Sanitário"
            ),
        },
        {
            "id": "PNAD_ANUAL_LIXO_UF",
            "group": "URBANO_SANEAMENTO_GESTAO",
            "name": "PNAD Contínua Anual: Coleta e Destino do Lixo (UF/RM/Capitais)",
            "table": 6736,
            "classification": 67,
            "category_source": "P4_6736_67",
            "min_year": 2016,
            "max_year": 2025,
            "valid_years": _PNAD_ANUAL_EDUC_HAB_YEARS,
            "default_years": [2025],
            "level": "N3",
            "partial_n6": True,
            "default_cat": 4661,
            "default_var": 9784,
            "extra_classifications": {"1": 6795},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "PNAD Anual Habitação — Destino do Lixo (N6 = Apenas 27 Capitais)",
            "notice_text": (
                "Série 2016-2019 e 2022-2025 em Estados (N3), RMs/RIDEs (N7/N14) e Regiões (N2). "
                "Em N6 retorna exclusivamente os 27 municípios das Capitais."
            ),
            "variables": _pnad_domicilio_vars(
                9784, 162, 10117, 10114, "pnad_lixo", "Destino do Lixo"
            ),
        },
        {
            "id": "PNAD_ANUAL_ENERGIA_UF",
            "group": "URBANO_SANEAMENTO_GESTAO",
            "name": "PNAD Contínua Anual: Acesso à Energia Elétrica nos Domicílios (UF/RM/Capitais)",
            "table": 6737,
            "classification": 827,
            "category_source": "P4_6737_827",
            "min_year": 2016,
            "max_year": 2025,
            "valid_years": _PNAD_ANUAL_EDUC_HAB_YEARS,
            "default_years": [2025],
            "level": "N3",
            "partial_n6": True,
            "default_cat": 46296,
            "default_var": 5074,
            "extra_classifications": {"1": 6795},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "PNAD Anual Habitação — Energia Elétrica (N6 = Apenas 27 Capitais)",
            "notice_text": (
                "Série 2016-2019 e 2022-2025 em Estados (N3), RMs/RIDEs (N7/N14) e Regiões (N2). "
                "Em N6 retorna exclusivamente os 27 municípios das Capitais."
            ),
            "variables": _pnad_domicilio_vars(
                5074, 5157, 10137, 10135, "pnad_energia", "Energia Elétrica"
            ),
        },
        _munic_survey(
            survey_id="MUNIC_REDE_SUAS_CRAS",
            name="MUNIC 2023: Rede Socioassistencial — CRAS, CREAS, Centro POP e Serviços SUAS (Binário)",
            table=9998,
            year=2023,
            classification=1914,
            category_source="P4_9998_1914",
            default_cat=72668,
            var_id=13139,
            var_name="Município com Unidade / Serviço SUAS (Indicador Sim = 1)",
            var_slug="munic_rede_suas_cras",
            extra_classifications={"1906": 72643, "1915": 72801, "12446": 47692},
            notice_text=(
                "Ano único (2023). Padrão selecionado: CRAS (Centro de Referência da Assistência Social). "
                "Inclui filtros secundários para serviços executados (PAIF, SCFV, PAEFI), grupos vulneráveis "
                "atendidos e porte populacional."
            ),
        ),
        _munic_survey(
            survey_id="MUNIC_BENEFICIOS_EVENTUAIS",
            name="MUNIC 2023: Concessão de Benefícios Eventuais de Assistência Social (Binário)",
            table=9997,
            year=2023,
            classification=1903,
            category_source="P4_9997_1903",
            default_cat=72637,
            var_id=603,
            var_name="Município com Concessão de Benefícios Eventuais (Sim = 1)",
            var_slug="munic_beneficios_eventuais",
            extra_classifications={"1902": 72633, "12446": 47692},
            notice_text=(
                "Ano único (2023). Mapeia municípios com concessão de benefícios eventuais "
                "(morte, natalidade, calamidade pública e vulnerabilidade temporária)."
            ),
        ),
        _munic_survey(
            survey_id="MUNIC_CONSELHO_ASSISTENCIA",
            name="MUNIC 2023: Conselho Municipal de Assistência Social — CMAS (Binário)",
            table=10388,
            year=2023,
            classification=1510,
            category_source="P4_10388_1510",
            default_cat=58783,
            var_id=13580,
            var_name="Município com Conselho Municipal de Assistência Social (Sim = 1)",
            var_slug="munic_cmas",
            extra_classifications={"1164": 50632, "12446": 47692},
            notice_text=(
                "Ano único (2023). Padrão selecionado: Conselhos ativos. Inclui subfiltro de paridade de representação."
            ),
        ),
        _munic_survey(
            survey_id="MUNIC_CONSELHO_TUTELAR",
            name="MUNIC 2023: Conselhos Tutelares por Município e Quantidade (Binário)",
            table=10037,
            year=2023,
            classification=2041,
            category_source="P4_10037_2041",
            default_cat=73885,
            var_id=13255,
            var_name="Município com Conselho Tutelar na Faixa Selecionada (Sim = 1)",
            var_slug="munic_conselho_tutelar",
            extra_classifications={"12446": 47692},
            notice_text=(
                "Ano único (2023). Permite visualizar todos os municípios com Conselho Tutelar ou filtrar por "
                "quantidade instalada (1, 2, 3, 4, 5 ou acima de 5)."
            ),
        ),
        _munic_survey(
            survey_id="MUNIC_TRANSPORTE_ONIBUS",
            name="MUNIC 2020: Transporte Coletivo por Ônibus Intramunicipal e Concessão (Binário)",
            table=8444,
            year=2020,
            classification=1087,
            category_source="P4_8444_1087",
            default_cat=50248,
            var_id=603,
            var_name="Município com Transporte Coletivo por Ônibus (Sim = 1)",
            var_slug="munic_transporte_onibus",
            extra_classifications={"12446": 47692},
            notice_text=(
                "Ano único (2020). Identifica municípios com serviço de ônibus intramunicipal e tipo de "
                "regulamentação (concessão, permissão, prestação direta pela prefeitura ou não regulamentado)."
            ),
        ),
        _munic_survey(
            survey_id="MUNIC_CULTURA_PLANO",
            name="MUNIC 2021: Plano Municipal de Cultura e Fase de Elaboração (Binário)",
            table=9703,
            year=2021,
            classification=1529,
            category_source="P4_9703_1529",
            default_cat=58874,
            var_id=603,
            var_name="Município com Plano Municipal de Cultura (Sim = 1)",
            var_slug="munic_plano_cultura",
            extra_classifications={"12446": 47692},
            notice_text=(
                "Ano único (2021). Padrão selecionado: municípios com Plano de Cultura instituído por instrumento legal."
            ),
        ),
        _munic_survey(
            survey_id="MUNIC_FUNDOS_CULTURA_SAUDE",
            name="MUNIC 2021: Fundos Municipais de Cultura e de Saúde (Binário)",
            table=9706,
            year=2021,
            classification=1536,
            category_source="P4_9706_1536",
            default_cat=58909,
            var_id=603,
            var_name="Município com Fundo Municipal na Área Selecionada (Sim = 1)",
            var_slug="munic_fundos_cultura_saude",
            extra_classifications={"12446": 47692},
            notice_text=(
                "Ano único (2021). Selecione na categoria a existência de Fundo Municipal de Cultura ou de Saúde."
            ),
        ),
        _munic_survey(
            survey_id="MUNIC_ESPORTE_INSTALACOES",
            name="MUNIC 2021: Instalações Esportivas Municipais (Binário)",
            table=9710,
            year=2021,
            classification=1572,
            category_source="P4_9710_1572",
            default_cat=59322,
            var_id=603,
            var_name="Município com Instalações Esportivas Municipais (Sim = 1)",
            var_slug="munic_esporte_instalacoes",
            extra_classifications={"12446": 47692},
            supported_levels=["N6", "N2"],
            notice_text=(
                "Ano único (2021). No SIDRA, esta tabela possui abrangência municipal (N6) e regional (N2), sem N3."
            ),
        ),

        # =====================================================================
        # SAÚDE PÚBLICA, DOENÇAS CRÔNICAS E HÁBITOS — PNS (+12)
        # =====================================================================
        _pns_survey(
            survey_id="PNS_PLANO_SAUDE",
            name="PNS (2013/2019): Cobertura de Plano de Saúde Médico ou Odontológico",
            table=4938,
            years=[2013, 2019],
            pct_var_id=5264,
            mil_var_id=5260,
            pct_label="Percentual da População com Plano de Saúde (%)",
            mil_label="Pessoas com Plano de Saúde",
            slug_prefix="pns_plano_saude",
            notice_text=(
                "Edições 2013 e 2019 da Pesquisa Nacional de Saúde. Disponível para UFs (N3), Grandes Regiões (N2) "
                "e 27 Capitais em N6."
            ),
        ),
        _pns_survey(
            survey_id="PNS_AUTOAVALIACAO_SAUDE",
            name="PNS (2013/2019): Autoavaliação de Saúde Boa ou Muito Boa (18+ Anos)",
            table=4751,
            years=[2013, 2019],
            pct_var_id=4738,
            mil_var_id=4735,
            pct_label="Percentual 18+ com Autoavaliação de Saúde Boa/Muito Boa (%)",
            mil_label="Pessoas 18+ com Saúde Boa ou Muito Boa",
            slug_prefix="pns_autoavaliacao_boa",
            notice_text=(
                "Edições 2013 e 2019 (população adulta 18+) para Estados (N3), Regiões (N2) e 27 Capitais (N6)."
            ),
        ),
        _pns_survey(
            survey_id="PNS_HIPERTENSAO",
            name="PNS (2013/2019): Prevalência de Hipertensão Arterial Diagnosticada (18+ Anos)",
            table=4418,
            years=[2013, 2019],
            pct_var_id=4399,
            mil_var_id=4396,
            pct_label="Percentual 18+ com Diagnóstico de Hipertensão Arterial (%)",
            mil_label="Pessoas 18+ com Hipertensão Arterial",
            slug_prefix="pns_hipertensao",
            notice_text=(
                "Edições 2013 e 2019 (população adulta 18+) para Estados (N3), Regiões (N2) e 27 Capitais (N6)."
            ),
        ),
        _pns_survey(
            survey_id="PNS_DIABETES",
            name="PNS (2013/2019): Prevalência de Diabetes Diagnosticada (18+ Anos)",
            table=4487,
            years=[2013, 2019],
            pct_var_id=4465,
            mil_var_id=4462,
            pct_label="Percentual 18+ com Diagnóstico de Diabetes (%)",
            mil_label="Pessoas 18+ com Diabetes",
            slug_prefix="pns_diabetes",
            notice_text=(
                "Edições 2013 e 2019 (população adulta 18+) para Estados (N3), Regiões (N2) e 27 Capitais (N6)."
            ),
        ),
        _pns_survey(
            survey_id="PNS_COLESTEROL_ALTO",
            name="PNS (2013/2019): Prevalência de Colesterol Alto Diagnosticado (18+ Anos)",
            table=4547,
            years=[2013, 2019],
            pct_var_id=4549,
            mil_var_id=4546,
            pct_label="Percentual 18+ com Diagnóstico de Colesterol Alto (%)",
            mil_label="Pessoas 18+ com Colesterol Alto",
            slug_prefix="pns_colesterol_alto",
            notice_text=(
                "Edições 2013 e 2019 (população adulta 18+) para Estados (N3), Regiões (N2) e 27 Capitais (N6)."
            ),
        ),
        _pns_survey(
            survey_id="PNS_DEPRESSAO",
            name="PNS (2013/2019): Diagnóstico de Depressão por Profissional de Saúde Mental (18+ Anos)",
            table=4694,
            years=[2013, 2019],
            pct_var_id=4642,
            mil_var_id=4639,
            pct_label="Percentual 18+ com Diagnóstico de Depressão (%)",
            mil_label="Pessoas 18+ com Diagnóstico de Depressão",
            slug_prefix="pns_depressao",
            notice_text=(
                "Edições 2013 e 2019 (população adulta 18+) para Estados (N3), Regiões (N2) e 27 Capitais (N6)."
            ),
        ),
        _pns_survey(
            survey_id="PNS_ASMA",
            name="PNS (2013/2019): Prevalência de Asma Diagnosticada (18+ Anos)",
            table=4576,
            years=[2013, 2019],
            pct_var_id=4585,
            mil_var_id=4582,
            pct_label="Percentual 18+ com Diagnóstico de Asma (%)",
            mil_label="Pessoas 18+ com Asma",
            slug_prefix="pns_asma",
            notice_text=(
                "Edições 2013 e 2019 (população adulta 18+) para Estados (N3), Regiões (N2) e 27 Capitais (N6)."
            ),
        ),
        _pns_survey(
            survey_id="PNS_ATIVIDADE_FISICA_LAZER",
            name="PNS (2013/2019): Prática de Atividade Física Recomendada no Lazer (18+ Anos)",
            table=4250,
            years=[2013, 2019],
            pct_var_id=4229,
            mil_var_id=4226,
            pct_label="Percentual 18+ Ativo no Lazer (%)",
            mil_label="Pessoas 18+ Ativas no Lazer",
            slug_prefix="pns_atividade_fisica_lazer",
            notice_text=(
                "Edições 2013 e 2019 (150+ minutos semanais de atividade leve/moderada ou 75+ vigorosa no lazer) "
                "para Estados (N3), Regiões (N2) e 27 Capitais (N6)."
            ),
        ),
        _pns_survey(
            survey_id="PNS_TABAGISMO",
            name="PNS 2019: Fumantes Atuais de Tabaco (15+ Anos)",
            table=7796,
            years=[2019],
            pct_var_id=11103,
            mil_var_id=11099,
            pct_label="Percentual 15+ Fumante Atual de Tabaco (%)",
            mil_label="Fumantes Atuais de Tabaco (15+ Anos)",
            slug_prefix="pns_tabagismo",
            notice_text=(
                "Edição PNS 2019 (recorte harmonizado de 15 anos ou mais) para UFs (N3), Regiões (N2) e 27 Capitais (N6)."
            ),
        ),
        _pns_survey(
            survey_id="PNS_CONSUMO_ALCOOL",
            name="PNS 2019: Consumo Abusivo de Álcool nos Últimos 30 Dias (18+ Anos)",
            table=7726,
            years=[2019],
            pct_var_id=4301,
            mil_var_id=4298,
            pct_label="Percentual 18+ com Consumo Abusivo de Álcool (%)",
            mil_label="Pessoas 18+ com Consumo Abusivo de Álcool",
            slug_prefix="pns_consumo_alcool",
            notice_text=(
                "Edição PNS 2019 (5 ou mais doses em única ocasião nos últimos 30 dias) para UFs (N3), Regiões (N2) e 27 Capitais (N6)."
            ),
        ),
        _pns_survey(
            survey_id="PNS_ACESSO_ATENDIMENTO",
            name="PNS 2019: Sucesso na Procura por Atendimento de Saúde (Últimas 2 Semanas)",
            table=7591,
            years=[2019],
            pct_var_id=5402,
            mil_var_id=5398,
            pct_label="Percentual que Conseguiu Atendimento (% dos que Procuraram)",
            mil_label="Pessoas que Procuraram e Conseguiram Atendimento",
            slug_prefix="pns_acesso_atendimento",
            notice_text=(
                "Edição PNS 2019 para Estados (N3), Grandes Regiões (N2) e 27 Capitais (N6)."
            ),
        ),
        _pns_survey(
            survey_id="PNS_INTERNACOES_SUS",
            name="PNS (2013/2019): Internações Hospitalares (24h+) Realizadas pelo SUS",
            table=5249,
            years=[2013, 2019],
            pct_var_id=5474,
            mil_var_id=5470,
            pct_label="Percentual das Internações 24h+ Realizadas pelo SUS (%)",
            mil_label="Pessoas com Última Internação (24h+) pelo SUS",
            slug_prefix="pns_internacoes_sus",
            notice_text=(
                "Edições 2013 e 2019 para Estados (N3), Grandes Regiões (N2) e 27 Capitais (N6), "
                "com recorte por nível de instrução e situação urbana/rural."
            ),
            classification=1568,
            category_source="P4_5249_1568",
            default_cat=120704,
        ),
    ]
