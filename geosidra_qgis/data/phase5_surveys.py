# -*- coding: utf-8 -*-
"""
Pesquisas da Fase 5 (Meio Ambiente, Clima, Biodiversidade e ODS) do GeoSIDRA:
- Biodiversidade Brasileira (EO - Avaliação dos dados sobre a Biodiversidade)
- Contribuição dos Polinizadores (EL - Valor da Produção Agrícola e Extrativista)
- Gestão Municipal de Riscos e Desastres / Defesa Civil (PM - MUNIC 2020)
- Indicadores de Desenvolvimento Sustentável (IU - Mata Atlântica, Unidades de Conservação e Queimadas)
- Objetivos de Desenvolvimento Sustentável (C2 - ODS: Desastres, Qualidade do Ar, Água/Esgoto Seguro e Linhas de Pobreza)
"""

from typing import Any, Dict, List


def _munic_disaster_survey(
    survey_id: str,
    name: str,
    table: int,
    classification: int,
    category_source: str,
    default_cat: int,
    var_id: int,
    var_name: str,
    var_slug: str,
    extra_classifications: Dict[str, int],
    notice_text: str,
) -> Dict[str, Any]:
    """Constrói entrada curada para tabelas de gestão de riscos e desastres da MUNIC."""
    return {
        "id": survey_id,
        "group": "RISCOS_DESASTRES_DEFESA_CIVIL",
        "name": name,
        "table": table,
        "classification": classification,
        "category_source": category_source,
        "min_year": 2020,
        "max_year": 2020,
        "valid_years": [2020],
        "level": "N6",
        "default_cat": default_cat,
        "default_var": var_id,
        "extra_classifications": extra_classifications,
        "notice_severity": "warning",
        "popup_notice": True,
        "notice_title": "Indicador Municipal de Gestão de Riscos e Desastres — MUNIC 2020",
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


def build_phase5_surveys() -> List[Dict[str, Any]]:
    """Retorna as 18 pesquisas curadas da Fase 5 (Meio Ambiente, Clima, Biodiversidade e ODS)."""
    return [
        # =====================================================================
        # BIODIVERSIDADE E POLINIZADORES (EO / EL)
        # =====================================================================
        {
            "id": "BIO_CONHECIMENTO_UF_MUN",
            "group": "MEIO_AMBIENTE_CLIMA_ODS",
            "name": "Biodiversidade: Índice de Conhecimento da Biodiversidade Brasileira (2022/2025)",
            "table": 10510,
            "classification": None,
            "min_year": 2022,
            "max_year": 2025,
            "valid_years": [2022, 2025],
            "default_years": [2025],
            "level": "N6",
            "default_var": 2323,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "Avaliação dos Dados sobre a Biodiversidade Brasileira (2022 e 2025)",
            "notice_text": (
                "Índice oficial calculado pelo IBGE para todos os Municípios (N6) e UFs (N3) com base "
                "nos registros de ocorrência de espécies (fauna e flora) e sua distribuição espacial."
            ),
            "variables": [
                {
                    "id": 2323,
                    "name": "Índice de Conhecimento da Biodiversidade (%)",
                    "slug": "bio_indice_conhecimento",
                    "unit": "Proporção (%)",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
            ],
        },
        {
            "id": "BIO_REGISTROS_OCORRENCIA",
            "group": "MEIO_AMBIENTE_CLIMA_ODS",
            "name": "Biodiversidade: Registros de Espécies por Grupo Taxonômico (2022/2025)",
            "table": 10511,
            "classification": 12919,
            "category_source": "P5_10511_12919",
            "min_year": 2022,
            "max_year": 2025,
            "valid_years": [2022, 2025],
            "default_years": [2025],
            "level": "N6",
            "default_cat": 119371,
            "default_var": 14020,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "Biodiversidade — Registros por Grupo Taxonômico",
            "notice_text": (
                "Quantitativo de registros de ocorrência (total e Nível 1 de qualidade da informação) "
                "por município ou estado, categorizados por Aves, Mamíferos, Répteis, Anfíbios, Peixes, Plantas, Fungos etc."
            ),
            "variables": [
                {
                    "id": 14020,
                    "name": "Número de Registros de Ocorrência",
                    "slug": "bio_num_registros_total",
                    "unit": "Unidades",
                    "multiplier": 1.0,
                    "agg_mode": "sum",
                },
                {
                    "id": 14019,
                    "name": "Registros com Nível 1 de Qualidade",
                    "slug": "bio_registros_nivel1_qualidade",
                    "unit": "Unidades",
                    "multiplier": 1.0,
                    "agg_mode": "sum",
                },
            ],
        },
        {
            "id": "BIO_COBERTURA_AMOSTRAL",
            "group": "MEIO_AMBIENTE_CLIMA_ODS",
            "name": "Biodiversidade: Cobertura Temporal e Completude Amostral (2022/2025)",
            "table": 10512,
            "classification": 12919,
            "category_source": "P5_10511_12919",
            "min_year": 2022,
            "max_year": 2025,
            "valid_years": [2022, 2025],
            "default_years": [2025],
            "level": "N6",
            "default_cat": 119371,
            "default_var": 14015,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "Biodiversidade — Completude e Cobertura Amostral",
            "notice_text": (
                "Métricas de consistência dos dados de biodiversidade: completude amostral, cobertura anual e cobertura sazonal "
                "para Municípios (N6) e Estados (N3)."
            ),
            "variables": [
                {
                    "id": 14015,
                    "name": "Completude Amostral (%)",
                    "slug": "bio_completude_amostral",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
                {
                    "id": 14016,
                    "name": "Cobertura Anual (%)",
                    "slug": "bio_cobertura_anual",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
                {
                    "id": 14017,
                    "name": "Cobertura Sazonal (%)",
                    "slug": "bio_cobertura_sazonal",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
            ],
        },
        {
            "id": "POLINIZADORES_VALOR_PRODUCAO",
            "group": "MEIO_AMBIENTE_CLIMA_ODS",
            "name": "Polinizadores: Contribuição Econômica na Produção Agrícola e Extrativista (1996 a 2023)",
            "table": 10255,
            "classification": 2101,
            "category_source": "P5_10255_2101",
            "min_year": 1996,
            "max_year": 2023,
            "valid_years": list(range(1996, 2024)),
            "default_years": [2023],
            "level": "N6",
            "default_cat": 79453,
            "default_var": 13521,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "Contribuição dos Polinizadores — Série Histórica 1996 a 2023",
            "notice_text": (
                "Estima a dependência econômica e a parcela do valor da produção municipal (N6) e estadual (N3) "
                "atribuível à polinização por animais (insetos e outros), segundo o modo de produção (Lavouras Permanentes, Temporárias e Extração)."
            ),
            "variables": [
                {
                    "id": 13521,
                    "name": "Contribuição Média dos Polinizadores no Valor da Produção (%)",
                    "slug": "polinizadores_contrib_media_pct",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
                {
                    "id": 13425,
                    "name": "Contribuição Mínima Estimada (%)",
                    "slug": "polinizadores_contrib_min_pct",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
                {
                    "id": 13426,
                    "name": "Contribuição Máxima Estimada (%)",
                    "slug": "polinizadores_contrib_max_pct",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
            ],
        },

        # =====================================================================
        # GESTÃO MUNICIPAL DE RISCOS, DESASTRES E DEFESA CIVIL (PM / C2)
        # =====================================================================
        {
            "id": "MUNIC_DESASTRES_NATURAIS",
            "group": "RISCOS_DESASTRES_DEFESA_CIVIL",
            "name": "MUNIC 2020: Municípios Atingidos por Desastres Naturais (Inundações, Enxurradas e Encostas)",
            "table": 8536,
            "classification": 1210,
            "category_source": "P5_8536_1210",
            "min_year": 2020,
            "max_year": 2020,
            "valid_years": [2020],
            "level": "N6",
            "default_cat": 50871,
            "default_var": 12443,
            "extra_classifications": {"12446": 47692, "1211": 50872, "1212": 50880, "1213": 50888},
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "MUNIC 2020 — Ocorrência de Desastres Naturais",
            "notice_text": (
                "Mapeia municípios atingidos nos últimos 4 anos por inundações graduais/enchentes, enxurradas bruscas ou "
                "deslizamentos de encostas, com subfiltros de edificações atingidas, desalojados/desabrigados e óbitos. "
                "Selecione na Categoria o ano do desastre de maior impacto (2017 a 2020)."
            ),
            "variables": [
                {
                    "id": 12443,
                    "name": "Municípios Atingidos por Enchentes ou Inundações Graduais (Sim = 1)",
                    "slug": "munic_desastres_inundacao_gradual",
                    "unit": "Municípios",
                    "multiplier": 1.0,
                    "agg_mode": "last",
                    "is_binary": True,
                },
                {
                    "id": 12444,
                    "name": "Municípios Atingidos por Enxurradas ou Inundações Bruscas (Sim = 1)",
                    "slug": "munic_desastres_enxurrada_brusca",
                    "unit": "Municípios",
                    "multiplier": 1.0,
                    "agg_mode": "last",
                    "is_binary": True,
                },
                {
                    "id": 12445,
                    "name": "Municípios Atingidos por Deslizamentos de Encostas (Sim = 1)",
                    "slug": "munic_desastres_deslizamento_encostas",
                    "unit": "Municípios",
                    "multiplier": 1.0,
                    "agg_mode": "last",
                    "is_binary": True,
                },
            ],
        },
        _munic_disaster_survey(
            survey_id="MUNIC_RISCO_ESCORREGAMENTOS",
            name="MUNIC 2020: Deslizamento de Encostas — Áreas de Risco e Intervenções (Binário)",
            table=8539,
            classification=1234,
            category_source="P5_8539_1234",
            default_cat=57265,
            var_id=12445,
            var_name="Município com Intervenção / Medida em Encostas (Sim = 1)",
            var_slug="munic_encostas_intervencao",
            extra_classifications={"12446": 47692, "1233": 57263},
            notice_text=(
                "Ano único (2020). Identifica municípios com obras e intervenções para contenção de encostas "
                "(estabilização de taludes, retaludamento, macrodrenagem, realocação de população de risco)."
            ),
        ),
        _munic_disaster_survey(
            survey_id="MUNIC_RISCO_INSTRUMENTOS",
            name="MUNIC 2020: Instrumentos de Planejamento de Gestão de Riscos e Desastres (Binário)",
            table=8540,
            classification=1235,
            category_source="P5_8540_1235",
            default_cat=51165,
            var_id=603,
            var_name="Município com Instrumento de Gestão de Riscos (Sim = 1)",
            var_slug="munic_risco_instrumentos",
            extra_classifications={"12446": 47692},
            notice_text=(
                "Ano único (2020). Mostra a presença de instrumentos urbanísticos e legais voltados a riscos: "
                "Plano Diretor preventivo, Lei de Uso do Solo com restrição de risco, Plano Municipal de Redução de Riscos (PMRR) e Carta Geotécnica."
            ),
        ),
        _munic_disaster_survey(
            survey_id="MUNIC_RISCO_MEDIDAS_PREVENTIVAS",
            name="MUNIC 2020: Medidas Preventivas e Sistemas de Alerta para Inundações e Encostas (Binário)",
            table=8541,
            classification=1236,
            category_source="P5_8541_1236",
            default_cat=51177,
            var_id=603,
            var_name="Município com Medida Preventiva / Alerta de Inundações (Sim = 1)",
            var_slug="munic_risco_medidas_prevencao",
            extra_classifications={"12446": 47692, "1237": 51186, "1238": 51190},
            notice_text=(
                "Ano único (2020). Identifica a adoção de medidas estruturais e não estruturais: mapeamento de áreas de risco, "
                "plano de contingência, sistema de alerta antecipado, projetos de engenharia e limpeza periódica de bueiros."
            ),
        ),
        _munic_disaster_survey(
            survey_id="MUNIC_DEFESA_CIVIL_ESTRUTURA",
            name="MUNIC 2020: Estrutura Municipal de Defesa Civil — COMPDEC e Bombeiros (Binário)",
            table=8542,
            classification=1239,
            category_source="P5_8542_1239",
            default_cat=51203,
            var_id=603,
            var_name="Município com Órgão / Recurso de Proteção e Defesa Civil (Sim = 1)",
            var_slug="munic_defesa_civil_estrutura",
            extra_classifications={"12446": 47692, "1244": 51238},
            notice_text=(
                "Ano único (2020). Mapeia a presença de Coordenação Municipal de Proteção e Defesa Civil (COMPDEC), "
                "Corpo de Bombeiros, recursos próprios na LOA, uso do S2ID e atividades educativas de percepção de risco."
            ),
        ),
        {
            "id": "ODS_POPULACAO_AFETADA_DESASTRES",
            "group": "RISCOS_DESASTRES_DEFESA_CIVIL",
            "name": "ODS 11.5.1: População Afetada por Desastres Naturais por UF (2015 a 2024)",
            "table": 6689,
            "classification": None,
            "min_year": 2015,
            "max_year": 2024,
            "valid_years": list(range(2015, 2025)),
            "default_years": [2024],
            "level": "N3",
            "default_var": 9619,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "ODS 11.5.1 / 1.5.1 / 13.1.1 — Impacto Humano de Desastres",
            "notice_text": (
                "Indicador oficial da Agenda 2030 medido pelo IBGE: número de mortes, pessoas desaparecidas "
                "e pessoas diretamente afetadas por desastres para cada 100 mil habitantes, em nível Estadual (N3) e Regional (N2)."
            ),
            "variables": [
                {
                    "id": 9619,
                    "name": "População Afetada por Desastres (por 100 mil hab.)",
                    "slug": "ods_pop_afetada_desastres",
                    "unit": "Pessoas",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
            ],
        },

        # =====================================================================
        # MEIO AMBIENTE, BIOMAS E QUALIDADE AMBIENTAL (IU / C2)
        # =====================================================================
        {
            "id": "IDS_MATA_ATLANTICA_DESMATAMENTO",
            "group": "MEIO_AMBIENTE_CLIMA_ODS",
            "name": "IDS Meio Ambiente: Remanescentes e Desmatamento da Mata Atlântica (UF)",
            "table": 5613,
            "classification": None,
            "min_year": 2012,
            "max_year": 2014,
            "valid_years": [2012, 2014],
            "default_years": [2014],
            "level": "N3",
            "default_var": 3846,
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Indicadores de Desenvolvimento Sustentável — Mata Atlântica",
            "notice_text": (
                "Inventário da vegetação nativa remanescente e desflorestamento no domínio da Mata Atlântica "
                "para as 17 Unidades da Federação abrangidas pelo bioma."
            ),
            "variables": [
                {
                    "id": 3846,
                    "name": "Área Remanescente de Mata Atlântica (km²)",
                    "slug": "ids_mata_atlantica_remanescente_km2",
                    "unit": "Quilômetros quadrados",
                    "multiplier": 1.0,
                    "agg_mode": "sum",
                },
                {
                    "id": 3850,
                    "name": "Percentual de Área Remanescente da Mata Atlântica (%)",
                    "slug": "ids_mata_atlantica_remanescente_pct",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
                {
                    "id": 3851,
                    "name": "Área Desmatada no Período (km²)",
                    "slug": "ids_mata_atlantica_desmatada_km2",
                    "unit": "Quilômetros quadrados",
                    "multiplier": 1.0,
                    "agg_mode": "sum",
                },
                {
                    "id": 3852,
                    "name": "Taxa de Desmatamento (%)",
                    "slug": "ids_mata_atlantica_desmatada_pct",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
                {
                    "id": 3845,
                    "name": "Área Original do Bioma na UF (km²)",
                    "slug": "ids_mata_atlantica_origem_km2",
                    "unit": "Quilômetros quadrados",
                    "multiplier": 1.0,
                    "agg_mode": "sum",
                },
            ],
        },
        {
            "id": "IDS_UNIDADES_CONSERVACAO_UF",
            "group": "MEIO_AMBIENTE_CLIMA_ODS",
            "name": "IDS Meio Ambiente: Unidades de Conservação e Áreas Protegidas por UF (2013 a 2016)",
            "table": 5625,
            "classification": 713,
            "category_source": "P5_5625_713",
            "min_year": 2013,
            "max_year": 2016,
            "valid_years": [2013, 2014, 2015, 2016],
            "default_years": [2016],
            "level": "N3",
            "default_cat": 33558,
            "default_var": 6317,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "Unidades de Conservação — Proteção Integral e Uso Sustentável",
            "notice_text": (
                "Percentual territorial e área total sob regime de Unidades de Conservação estaduais e federais por UF, "
                "com distinção entre Proteção Integral e Uso Sustentável."
            ),
            "variables": [
                {
                    "id": 6317,
                    "name": "Proporção da Área da UF sob Unidades de Conservação (%)",
                    "slug": "ids_ucs_proporcao_uf_pct",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
                {
                    "id": 6314,
                    "name": "Área das Unidades de Conservação (km²)",
                    "slug": "ids_ucs_area_total_km2",
                    "unit": "Quilômetros quadrados",
                    "multiplier": 1.0,
                    "agg_mode": "sum",
                },
                {
                    "id": 6313,
                    "name": "Número de Unidades de Conservação",
                    "slug": "ids_ucs_quantidade",
                    "unit": "Unidades",
                    "multiplier": 1.0,
                    "agg_mode": "sum",
                },
            ],
        },
        {
            "id": "IDS_FOCOS_CALOR_AMAZONIA",
            "group": "MEIO_AMBIENTE_CLIMA_ODS",
            "name": "IDS Meio Ambiente: Queimadas e Focos de Calor na Amazônia Legal (1999 a 2016)",
            "table": 5804,
            "classification": None,
            "min_year": 1999,
            "max_year": 2016,
            "valid_years": list(range(1999, 2017)),
            "default_years": [2016],
            "level": "N3",
            "default_var": 6537,
            "notice_severity": "warning",
            "popup_notice": True,
            "notice_title": "Queimadas e Focos de Calor — Amazônia Legal",
            "notice_text": (
                "Monitoramento de focos de calor por satélite nas 9 UFs da Amazônia Legal (N3) e na Região Norte/Centro-Oeste (N2), "
                "incluindo a participação percentual no total de focos do Brasil."
            ),
            "variables": [
                {
                    "id": 6537,
                    "name": "Número de Focos de Calor na Amazônia Legal",
                    "slug": "ids_focos_calor_amazonia",
                    "unit": "Unidades",
                    "multiplier": 1.0,
                    "agg_mode": "sum",
                },
                {
                    "id": 6538,
                    "name": "Participação no Total de Focos de Calor do Brasil (%)",
                    "slug": "ids_focos_calor_participacao_br",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
            ],
        },
        {
            "id": "ODS_QUALIDADE_AR_CIDADES",
            "group": "MEIO_AMBIENTE_CLIMA_ODS",
            "name": "ODS 11.6.2: Qualidade do Ar nas Cidades — Partículas MP 2,5 e MP 10 (Municípios)",
            "table": 10544,
            "classification": None,
            "min_year": 2010,
            "max_year": 2024,
            "valid_years": list(range(2010, 2025)),
            "default_years": [2024],
            "level": "N6",
            "partial_n6": True,
            "default_var": 14035,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "ODS 11.6.2 — Qualidade do Ar Urbano (Partículas Inaláveis)",
            "notice_text": (
                "Média anual de concentração de partículas finas em suspensão (MP 2,5 e MP 10) nas cidades com rede oficial de monitoramento, "
                "expressas em microgramas por metro cúbico (µg/m³). Atenção: no nível municipal (N6), possui dados apenas para os municípios monitorados."
            ),
            "variables": [
                {
                    "id": 14035,
                    "name": "Média Anual de Partículas Finas MP 2,5 (µg/m³)",
                    "slug": "ods_qualidade_ar_mp25_media",
                    "unit": "Microgramas por metro cúbico",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
                {
                    "id": 14037,
                    "name": "Média Anual de Partículas Inaláveis MP 10 (µg/m³)",
                    "slug": "ods_qualidade_ar_mp10_media",
                    "unit": "Microgramas por metro cúbico",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
                {
                    "id": 14036,
                    "name": "Concentração MP 2,5 por 100 mil habitantes",
                    "slug": "ods_qualidade_ar_mp25_por_100k",
                    "unit": "Microgramas por metro cúbico",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
            ],
        },
        {
            "id": "ODS_MORTALIDADE_POLUICAO_AR",
            "group": "MEIO_AMBIENTE_CLIMA_ODS",
            "name": "ODS 3.9.1: Mortalidade Atribuída à Poluição Atmosférica (UF, 2022/2023)",
            "table": 10755,
            "classification": 2,
            "category_source": "P5_10755_2",
            "min_year": 2022,
            "max_year": 2023,
            "valid_years": [2022, 2023],
            "default_years": [2023],
            "level": "N3",
            "default_cat": 6794,
            "default_var": 14195,
            "extra_classifications": {"1481": 82768},
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "ODS 3.9.1 — Mortalidade por Poluição do Ar Ambiental e Domiciliar",
            "notice_text": (
                "Taxa de mortalidade padronizada para cada 100 mil habitantes atribuída à exposição ao material particulado fino (MP 2,5), "
                "segundo tipo de agravo respiratório e cardiovascular (Câncer de Pulmão, DPOC, AVC, Doenças Cardíacas)."
            ),
            "variables": [
                {
                    "id": 14195,
                    "name": "Taxa de Mortalidade Atribuída à Poluição do Ar (por 100 mil hab.)",
                    "slug": "ods_mortalidade_poluicao_ar_taxa",
                    "unit": "Óbitos por 100.000 habitantes",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
                {
                    "id": 10601,
                    "name": "Total de Óbitos Atribuídos",
                    "slug": "ods_mortalidade_poluicao_ar_obitos",
                    "unit": "Óbitos",
                    "multiplier": 1.0,
                    "agg_mode": "sum",
                },
                {
                    "id": 14192,
                    "name": "Fração Atribuível da População (FAP) Exposta ao MP 2,5 (%)",
                    "slug": "ods_mortalidade_poluicao_ar_fap",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
            ],
        },

        # =====================================================================
        # SANEAMENTO, ÁGUA SEGURA E POBREZA MULTIDIMENSIONAL ODS (C2)
        # =====================================================================
        {
            "id": "ODS_AGUA_POTAVEL_SEGURA",
            "group": "MEIO_AMBIENTE_CLIMA_ODS",
            "name": "ODS 6.1.1: Acesso a Serviços de Água Potável Gerenciados de Forma Segura (UF)",
            "table": 9787,
            "classification": None,
            "min_year": 2016,
            "max_year": 2023,
            "valid_years": [2016, 2017, 2018, 2019, 2022, 2023],
            "default_years": [2023],
            "level": "N3",
            "default_var": 9484,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "ODS 6.1.1 — Água Potável Gerenciada de Forma Segura",
            "notice_text": (
                "Proporção da população que utiliza serviços de água potável provenientes de fonte melhorada, "
                "disponível quando necessário e livre de contaminação fecal/química, por UF (N3) e Regiões (N2)."
            ),
            "variables": [
                {
                    "id": 9484,
                    "name": "População com Água Potável Gerenciada de Forma Segura (%)",
                    "slug": "ods_agua_potavel_segura_pct",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
            ],
        },
        {
            "id": "ODS_ESGOTO_TRATADO_SEGURO",
            "group": "MEIO_AMBIENTE_CLIMA_ODS",
            "name": "ODS 6.3.1: Proporção de Águas Residuais Domésticas Tratadas de Forma Segura (UF)",
            "table": 8916,
            "classification": None,
            "min_year": 2009,
            "max_year": 2019,
            "valid_years": [2009, 2011, 2012, 2013, 2014, 2015, 2019],
            "default_years": [2019],
            "level": "N3",
            "default_var": 12735,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "ODS 6.3.1 — Esgotamento Doméstico Tratado com Segurança",
            "notice_text": (
                "Proporção de efluentes sanitários domésticos gerados que passam por tratamento adequado "
                "antes do descarte em corpos hídricos, para as 27 UFs (N3) e Grandes Regiões (N2)."
            ),
            "variables": [
                {
                    "id": 12735,
                    "name": "Águas Residuais Domésticas Tratadas de Forma Segura (%)",
                    "slug": "ods_esgoto_tratado_seguro_pct",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
            ],
        },
        {
            "id": "ODS_POBREZA_VULNERABILIDADE_UF",
            "group": "MEIO_AMBIENTE_CLIMA_ODS",
            "name": "ODS 1.2.1: População Abaixo da Linha de Pobreza Nacional (2012 a 2024, UF)",
            "table": 5877,
            "classification": None,
            "min_year": 2012,
            "max_year": 2024,
            "valid_years": list(range(2012, 2025)),
            "default_years": [2024],
            "level": "N3",
            "default_var": 9948,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "ODS 1.2.1 — Linha de Pobreza Nacional",
            "notice_text": (
                "Série histórica 2012 a 2024 de erradicação da pobreza para Estados (N3) e Regiões (N2), "
                "medindo a parcela da população vivendo abaixo da linha de pobreza nacional."
            ),
            "variables": [
                {
                    "id": 9948,
                    "name": "Proporção da População Abaixo da Linha de Pobreza Nacional (%)",
                    "slug": "ods_pobreza_nacional_pct",
                    "unit": "Proporção (%)",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
            ],
        },
    ]
