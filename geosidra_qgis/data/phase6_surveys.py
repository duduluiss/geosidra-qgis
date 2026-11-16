# -*- coding: utf-8 -*-
"""
Pesquisas da Fase 6 (Infância, Juventude, Educação e Saúde do Escolar — PeNSE) do GeoSIDRA:
- Primeira Infância, Creches e Frequência Escolar (Censo 2022 & MUNIC 2023)
- Infraestrutura Escolar e Acesso à Internet (PeNSE, ODS 4 & PNAD)
- Clima Escolar, Bullying e Violência (PeNSE)
- Saúde Mental, Hábitos e Fatores de Risco na Adolescência (PeNSE)
"""

from typing import Any, Dict, List


def _munic_infancia_survey(
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
    """Constrói entrada curada para tabelas municipais de infância e adolescência da MUNIC 2023."""
    return {
        "id": survey_id,
        "group": "INFANCIA_JUVENTUDE_ESCOLAS",
        "name": name,
        "table": table,
        "classification": classification,
        "category_source": category_source,
        "min_year": 2023,
        "max_year": 2023,
        "valid_years": [2023],
        "level": "N6",
        "default_cat": default_cat,
        "default_var": var_id,
        "extra_classifications": extra_classifications,
        "notice_severity": "info",
        "popup_notice": True,
        "notice_title": "Indicador Municipal da Primeira Infância e Juventude — MUNIC 2023",
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


def _pense_habits_survey(
    survey_id: str,
    name: str,
    table: int,
    var_id: int,
    var_name: str,
    var_slug: str,
    notice_text: str,
) -> Dict[str, Any]:
    """Constrói entrada curada para tabelas de comportamento e saúde do escolar da PeNSE."""
    return {
        "id": survey_id,
        "group": "INFANCIA_JUVENTUDE_ESCOLAS",
        "name": name,
        "table": table,
        "classification": 2,
        "category_source": "P6_PENSE_SEXO",
        "min_year": 2015,
        "max_year": 2015,
        "valid_years": [2015],
        "level": "N3",
        "partial_n6": True,
        "default_cat": 6794,
        "default_var": var_id,
        "extra_classifications": {"556": 31050},
        "notice_severity": "info",
        "popup_notice": True,
        "notice_title": "Pesquisa Nacional de Saúde do Escolar — PeNSE (9º ano)",
        "notice_text": notice_text,
        "variables": [
            {
                "id": var_id,
                "name": var_name,
                "slug": var_slug,
                "unit": "%",
                "multiplier": 1.0,
                "agg_mode": "mean",
            }
        ],
    }


def build_phase6_surveys() -> List[Dict[str, Any]]:
    """Retorna as 23 pesquisas curadas da Fase 6 (Infância, Juventude, Educação e Saúde do Escolar)."""
    return [
        # =====================================================================
        # 1. PRIMEIRA INFÂNCIA, CRECHES E EDUCAÇÃO INFANTIL (CENSO 2022 & MUNIC)
        # =====================================================================
        {
            "id": "CENSO22_CRECHE_PREESCOLA",
            "group": "INFANCIA_JUVENTUDE_ESCOLAS",
            "name": "Censo 2022: Crianças de até 5 Anos em Creche e Pré-escola (Municípios)",
            "table": 10057,
            "classification": 11798,
            "category_source": "P6_10057_11798",
            "min_year": 2022,
            "max_year": 2022,
            "valid_years": [2022],
            "level": "N6",
            "default_cat": 95301,  # Creche
            "default_var": 13282,
            "extra_classifications": {"58": 99749, "2": 6794, "86": 95251},
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "Censo 2022 — Educação Infantil e Creche",
            "notice_text": (
                "Quantitativo e percentual de crianças de até 5 anos que frequentavam creche (0 a 3 anos) "
                "e pré-escola (4 a 5 anos), com desagregação por cor/raça, sexo e todos os municípios do país."
            ),
            "variables": [
                {
                    "id": 13282,
                    "name": "Crianças de até 5 Anos em Creche ou Pré-escola",
                    "slug": "censo22_criancas_creche_preescola",
                    "unit": "Pessoas",
                    "multiplier": 1.0,
                    "agg_mode": "sum",
                },
                {
                    "id": 1013282,
                    "name": "Percentual do Total de Crianças da Faixa (%)",
                    "slug": "censo22_criancas_creche_preescola_pct",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
            ],
        },
        {
            "id": "CENSO22_TAXA_FREQ_ESCOLAR",
            "group": "INFANCIA_JUVENTUDE_ESCOLAS",
            "name": "Censo 2022: Taxa Bruta de Frequência Escolar por Faixa Etária (Municípios)",
            "table": 10056,
            "classification": 58,
            "category_source": "P6_10056_58",
            "min_year": 2022,
            "max_year": 2022,
            "valid_years": [2022],
            "level": "N6",
            "default_cat": 47813,  # 4 a 5 anos
            "default_var": 3795,
            "extra_classifications": {"2": 6794, "86": 95251},
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "Censo 2022 — Taxa de Frequência Escolar",
            "notice_text": (
                "Taxa de frequência escolar da população de 0 a 3 anos, 4 a 5 anos (pré-escola), "
                "6 a 14 anos (fundamental) e 15 a 17 anos (médio) para todos os municípios (N6) e estados (N3)."
            ),
            "variables": [
                {
                    "id": 3795,
                    "name": "Taxa Bruta de Frequência Escolar (%)",
                    "slug": "censo22_taxa_freq_escolar_pct",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
            ],
        },
        {
            "id": "CENSO22_EDUC_INDIGENA_INFANTIL",
            "group": "INFANCIA_JUVENTUDE_ESCOLAS",
            "name": "Censo 2022: Crianças Indígenas de até 5 Anos em Creche e Escola (Municípios)",
            "table": 10067,
            "classification": 11798,
            "category_source": "P6_10057_11798",
            "min_year": 2022,
            "max_year": 2022,
            "valid_years": [2022],
            "level": "N6",
            "default_cat": 95301,  # Creche
            "default_var": 13288,
            "extra_classifications": {"58": 99749, "2": 6794},
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "Censo 2022 — Educação Infantil Indígena",
            "notice_text": (
                "Total e proporção de crianças indígenas de até 5 anos que frequentavam creche ou escola, "
                "por sexo e idade, para os municípios brasileiros."
            ),
            "variables": [
                {
                    "id": 13288,
                    "name": "Crianças Indígenas em Creche ou Escola",
                    "slug": "censo22_indigenas_creche_escola",
                    "unit": "Pessoas",
                    "multiplier": 1.0,
                    "agg_mode": "sum",
                },
                {
                    "id": 1013288,
                    "name": "Percentual do Total de Crianças Indígenas (%)",
                    "slug": "censo22_indigenas_creche_escola_pct",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
            ],
        },
        _munic_infancia_survey(
            survey_id="MUNIC_AUXILIO_CRECHE",
            name="MUNIC 2023: Municípios com Auxílio Creche para a Educação Infantil (Binário)",
            table=10048,
            classification=2071,
            category_source="P6_10048_2071",
            default_cat=77571,
            var_id=13279,
            var_name="Município com Auxílio Creche (Sim = 1)",
            var_slug="munic_auxilio_creche",
            extra_classifications={"12446": 47692},
            notice_text=(
                "Ano único (2023). Mapeia a oferta municipal de auxílio creche a famílias com crianças na educação infantil, "
                "nas modalidades de transferência em dinheiro, bolsa de estudo ou compra de vagas em creches privadas."
            ),
        ),
        _munic_infancia_survey(
            survey_id="MUNIC_COMITE_PRIMEIRA_INFANCIA",
            name="MUNIC 2023: Comitê Intersetorial de Políticas da Primeira Infância (Binário)",
            table=10046,
            classification=2068,
            category_source="P6_10046_2068",
            default_cat=77464,
            var_id=13277,
            var_name="Município com Comitê da Primeira Infância (Sim = 1)",
            var_slug="munic_comite_primeira_infancia",
            extra_classifications={"12446": 47692, "2066": 77439, "2067": 77459, "2070": 77567},
            notice_text=(
                "Ano único (2023). Identifica a presença de Comitê Intersetorial voltado a crianças de 0 a 6 anos, "
                "reunindo representantes das pastas de Assistência Social, Educação, Saúde, CMDCA e Conselho Tutelar."
            ),
        ),
        _munic_infancia_survey(
            survey_id="MUNIC_DIREITOS_CRIANCA_ADOLESCENTE",
            name="MUNIC 2023: Ações de Promoção e Defesa de Crianças e Adolescentes (Binário)",
            table=10036,
            classification=2040,
            category_source="P6_10036_2040",
            default_cat=73871,  # Enfrentamento ao bullying
            var_id=13254,
            var_name="Município com Ação de Defesa da Criança/Adolescente (Sim = 1)",
            var_slug="munic_defesa_direitos_crianca",
            extra_classifications={"12446": 47692, "2039": 73832},
            notice_text=(
                "Ano único (2023). Verifica a existência de programas municipais específicos contra o bullying escolar, "
                "erradicação do trabalho infantil, violência física/sexual e acolhimento familiar ou institucional."
            ),
        ),
        _munic_infancia_survey(
            survey_id="MUNIC_MEDIDAS_SOCIOEDUCATIVAS",
            name="MUNIC 2023: Execução de Medidas Socioeducativas em Meio Aberto (Binário)",
            table=10038,
            classification=2045,
            category_source="P6_10038_2045",
            default_cat=73922,  # Pela Prefeitura - Assistência Social
            var_id=603,
            var_name="Município com Execução de Medida Socioeducativa (Sim = 1)",
            var_slug="munic_medidas_socioeducativas",
            extra_classifications={"12446": 47692, "2046": 73934, "2047": 73958, "2048": 73963},
            notice_text=(
                "Ano único (2023). Mapeia a oferta e execução de Liberdade Assistida (LA) e Prestação de Serviços "
                "à Comunidade (PSC) para adolescentes em conflito com a lei no território municipal."
            ),
        ),

        # =====================================================================
        # 2. INFRAESTRUTURA ESCOLAR E ACESSO À EDUCAÇÃO (PENSE, ODS 4 E PNAD)
        # =====================================================================
        {
            "id": "PENSE_ESCOLA_BIBLIOTECA",
            "group": "INFANCIA_JUVENTUDE_ESCOLAS",
            "name": "PeNSE: Escolares em Escolas com Biblioteca em Condições de Uso (UF e Capitais)",
            "table": 5948,
            "classification": 556,
            "category_source": "P6_PENSE_DEP_ADM",
            "min_year": 2015,
            "max_year": 2015,
            "valid_years": [2015],
            "level": "N3",
            "partial_n6": True,
            "default_cat": 31050,  # Total
            "default_var": 7308,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "PeNSE — Biblioteca Escolar",
            "notice_text": (
                "Proporção e quantitativo de alunos do 9º ano em escolas que informaram possuir biblioteca em uso, "
                "disponível para as 27 UFs (N3) e 27 Capitais Estaduais (N6), segundo rede pública ou privada."
            ),
            "variables": [
                {
                    "id": 7308,
                    "name": "Escolares em Escolas com Biblioteca (%)",
                    "slug": "pense_escola_biblioteca_pct",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
                {
                    "id": 7305,
                    "name": "Total de Escolares em Escolas com Biblioteca",
                    "slug": "pense_escola_biblioteca_total",
                    "unit": "Pessoas",
                    "multiplier": 1.0,
                    "agg_mode": "sum",
                },
            ],
        },
        {
            "id": "PENSE_ESCOLA_INFORMATICA",
            "group": "INFANCIA_JUVENTUDE_ESCOLAS",
            "name": "PeNSE: Escolares em Escolas com Laboratório de Informática (UF e Capitais)",
            "table": 5950,
            "classification": 556,
            "category_source": "P6_PENSE_DEP_ADM",
            "min_year": 2015,
            "max_year": 2015,
            "valid_years": [2015],
            "level": "N3",
            "partial_n6": True,
            "default_cat": 31050,
            "default_var": 7314,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "PeNSE — Informática e Computadores na Escola",
            "notice_text": (
                "Percentual e total de estudantes em estabelecimentos com laboratório de informática em condições de uso, "
                "por rede administrativa, cobrindo Estados (N3) e Capitais (N6)."
            ),
            "variables": [
                {
                    "id": 7314,
                    "name": "Escolares em Escolas com Laboratório de Informática (%)",
                    "slug": "pense_escola_informatica_pct",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
                {
                    "id": 7311,
                    "name": "Total de Escolares em Escolas com Informática",
                    "slug": "pense_escola_informatica_total",
                    "unit": "Pessoas",
                    "multiplier": 1.0,
                    "agg_mode": "sum",
                },
            ],
        },
        {
            "id": "PENSE_ESCOLA_INTERNET",
            "group": "INFANCIA_JUVENTUDE_ESCOLAS",
            "name": "PeNSE: Escolares com Acesso à Internet através da Escola (UF e Capitais)",
            "table": 5952,
            "classification": 556,
            "category_source": "P6_PENSE_DEP_ADM",
            "min_year": 2015,
            "max_year": 2015,
            "valid_years": [2015],
            "level": "N3",
            "partial_n6": True,
            "default_cat": 31050,
            "default_var": 3647,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "PeNSE — Internet para Alunos",
            "notice_text": (
                "Estudantes que possuem acesso à internet através de equipamentos da própria escola, "
                "por rede pública ou privada, em nível Estadual (N3) e nas Capitais (N6)."
            ),
            "variables": [
                {
                    "id": 3647,
                    "name": "Escolares com Acesso à Internet na Escola (%)",
                    "slug": "pense_escola_internet_pct",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
                {
                    "id": 3644,
                    "name": "Total de Escolares com Acesso à Internet na Escola",
                    "slug": "pense_escola_internet_total",
                    "unit": "Pessoas",
                    "multiplier": 1.0,
                    "agg_mode": "sum",
                },
            ],
        },
        {
            "id": "PENSE_ESCOLA_QUADRA_ESPORTES",
            "group": "INFANCIA_JUVENTUDE_ESCOLAS",
            "name": "PeNSE: Escolares em Escolas com Quadra de Esportes em Uso (UF e Capitais)",
            "table": 5956,
            "classification": 556,
            "category_source": "P6_PENSE_DEP_ADM",
            "min_year": 2015,
            "max_year": 2015,
            "valid_years": [2015],
            "level": "N3",
            "partial_n6": True,
            "default_cat": 31050,
            "default_var": 7344,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "PeNSE — Quadra de Esportes",
            "notice_text": (
                "Percentual e total de escolares matriculados em unidades escolares com quadra esportiva disponível, "
                "para Estados (N3) e Capitais (N6)."
            ),
            "variables": [
                {
                    "id": 7344,
                    "name": "Escolares em Escolas com Quadra de Esportes (%)",
                    "slug": "pense_escola_quadra_pct",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
                {
                    "id": 7341,
                    "name": "Total de Escolares em Escolas com Quadra de Esportes",
                    "slug": "pense_escola_quadra_total",
                    "unit": "Pessoas",
                    "multiplier": 1.0,
                    "agg_mode": "sum",
                },
            ],
        },
        {
            "id": "ODS_INFRAESTRUTURA_ESCOLAR",
            "group": "INFANCIA_JUVENTUDE_ESCOLAS",
            "name": "ODS 4.a.1: Infraestrutura Básica das Escolas — Energia, Água, Internet e PCD (UF)",
            "table": 7783,
            "classification": 812,
            "category_source": "P6_7783_812",
            "min_year": 2007,
            "max_year": 2024,
            "valid_years": list(range(2007, 2025)),
            "default_years": [2024],
            "level": "N3",
            "default_cat": 41117,  # Internet pedagógica
            "default_var": 11085,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "ODS 4.a.1 — Infraestrutura Básica Escolar (2007 a 2024)",
            "notice_text": (
                "Série histórica oficial de acompanhamento da Agenda 2030 medindo a proporção de escolas com energia elétrica, "
                "internet, computadores pedagógicos, banheiros, água potável e acessibilidade para pessoas com deficiência."
            ),
            "variables": [
                {
                    "id": 11085,
                    "name": "Proporção de Escolas com o Recurso — Anos Iniciais do EF (%)",
                    "slug": "ods_escolas_infra_anos_iniciais_pct",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
                {
                    "id": 11084,
                    "name": "Proporção de Escolas com o Recurso — Anos Finais do EF (%)",
                    "slug": "ods_escolas_infra_anos_finais_pct",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
                {
                    "id": 11086,
                    "name": "Proporção de Escolas com o Recurso — Ensino Médio (%)",
                    "slug": "ods_escolas_infra_ensino_medio_pct",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
            ],
        },
        {
            "id": "PNAD_FREQ_ESCOLAR_LIQUIDA_UF",
            "group": "INFANCIA_JUVENTUDE_ESCOLAS",
            "name": "PNAD Educação: Taxa Ajustada de Frequência Escolar Líquida por Nível Ideal (UF)",
            "table": 7141,
            "classification": 871,
            "category_source": "P6_7141_871",
            "min_year": 2016,
            "max_year": 2025,
            "valid_years": [2016, 2017, 2018, 2019, 2022, 2023, 2024, 2025],
            "default_years": [2025],
            "level": "N3",
            "default_cat": 47818,  # 15 a 17 anos no ensino médio
            "default_var": 10282,
            "extra_classifications": {"2": 6794},
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "PNAD Contínua Anual — Frequência Escolar Líquida",
            "notice_text": (
                "Mede a proporção de estudantes que frequentam a etapa adequada para a sua faixa de idade: "
                "Ensino Fundamental (6 a 14 anos), Ensino Médio (15 a 17 anos) e Ensino Superior (18 a 24 anos)."
            ),
            "variables": [
                {
                    "id": 10282,
                    "name": "Taxa Ajustada de Frequência Escolar Líquida (%)",
                    "slug": "pnad_freq_escolar_liquida_pct",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
            ],
        },

        # =====================================================================
        # 3. CLIMA ESCOLAR, BULLYING E VIOLÊNCIA (PENSE — 9º ANO)
        # =====================================================================
        {
            "id": "PENSE_BULLYING_SOFRIDO",
            "group": "INFANCIA_JUVENTUDE_ESCOLAS",
            "name": "PeNSE: Escolares que Sofreram Bullying por Motivo da Humilhação (UF e Capitais)",
            "table": 6053,
            "classification": 752,
            "category_source": "P6_6053_752",
            "min_year": 2015,
            "max_year": 2015,
            "valid_years": [2015],
            "level": "N3",
            "partial_n6": True,
            "default_cat": 39832,  # Total
            "default_var": 7497,
            "notice_severity": "info",
            "popup_notice": True,
            "notice_title": "PeNSE — Bullying Sofrido na Escola",
            "notice_text": (
                "Percentual de estudantes do 9º ano que se sentiram humilhados por provocações de colegas, "
                "segundo motivo: cor/raça, religião, aparência do rosto/corpo ou orientação sexual, por UF (N3) e Capitais (N6)."
            ),
            "variables": [
                {
                    "id": 7497,
                    "name": "Escolares que Sofreram Bullying (%)",
                    "slug": "pense_bullying_sofrido_pct",
                    "unit": "%",
                    "multiplier": 1.0,
                    "agg_mode": "mean",
                },
            ],
        },
        _pense_habits_survey(
            survey_id="PENSE_BULLYING_PRATICADO",
            name="PeNSE: Escolares que Praticaram Intimidação ou Bullying contra Colegas (UF e Capitais)",
            table=6054,
            var_id=7500,
            var_name="Escolares que Praticaram Bullying / Intimidação (%)",
            var_slug="pense_bullying_praticado_pct",
            notice_text=(
                "Percentual de alunos do 9º ano que intimidaram, zombaram, esculacharam ou humilharam colegas de escola, "
                "por sexo e dependência administrativa, disponível para Estados (N3) e Capitais (N6)."
            ),
        ),
        _pense_habits_survey(
            survey_id="PENSE_VIOLENCIA_AGRESSAO",
            name="PeNSE: Escolares Vítimas de Agressão Física por Adulto da Família (UF e Capitais)",
            table=6073,
            var_id=7539,
            var_name="Escolares Agredidos Fisicamente por Familiar (%)",
            var_slug="pense_violencia_familiar_pct",
            notice_text=(
                "Proporção de estudantes agredidos fisicamente por adulto da família nos 30 dias anteriores à pesquisa, "
                "por sexo e rede de ensino, para as 27 UFs (N3) e 27 Capitais Estaduais (N6)."
            ),
        ),
        _pense_habits_survey(
            survey_id="PENSE_BRIGAS_AGRESSAO",
            name="PeNSE: Escolares Envolvidos em Brigas com Agressão Física / Armas (UF e Capitais)",
            table=6074,
            var_id=7542,
            var_name="Escolares Envolvidos em Brigas com Agressão / Arma (%)",
            var_slug="pense_brigas_violencia_pct",
            notice_text=(
                "Estudantes que estiveram envolvidos em brigas físicas graves no ambiente escolar ou entorno, "
                "para as 27 Unidades da Federação (N3) e 27 Capitais (N6)."
            ),
        ),

        # =====================================================================
        # 4. SAÚDE MENTAL, HÁBITOS E COMPORTAMENTOS NA ADOLESCÊNCIA (PENSE)
        # =====================================================================
        _pense_habits_survey(
            survey_id="PENSE_SAUDE_MENTAL_SOLIDAO",
            name="PeNSE Saúde Mental: Sentimento de Solidão Frequente nos Escolares (UF e Capitais)",
            table=6102,
            var_id=3457,
            var_name="Escolares com Sentimento de Solidão Frequente (%)",
            var_slug="pense_saude_mental_solidao_pct",
            notice_text=(
                "Percentual de estudantes do 9º ano que relataram se sentir sozinhos na maioria das vezes ou sempre, "
                "indicador fundamental de sofrimento psíquico na adolescência, por UF (N3) e Capitais (N6)."
            ),
        ),
        _pense_habits_survey(
            survey_id="PENSE_SAUDE_MENTAL_INSONIA",
            name="PeNSE Saúde Mental: Perda de Sono por Preocupações e Ansiedade (UF e Capitais)",
            table=6103,
            var_id=3460,
            var_name="Escolares com Perda de Sono por Preocupações (%)",
            var_slug="pense_saude_mental_insonia_pct",
            notice_text=(
                "Proporção de escolares que perderam o sono por preocupações na maioria das vezes ou sempre, "
                "sintoma sentinela de ansiedade e sobrecarga emocional juvenil, por UF (N3) e Capitais (N6)."
            ),
        ),
        _pense_habits_survey(
            survey_id="PENSE_TABACO_EXPERIMENTACAO",
            name="PeNSE Tabagismo: Experimentação de Cigarros entre Escolares (UF e Capitais)",
            table=6023,
            var_id=3295,
            var_name="Escolares que Experimentaram Cigarros (%)",
            var_slug="pense_tabaco_experimentacao_pct",
            notice_text=(
                "Prevalência de experimentação de cigarros convencionais alguma vez na vida entre estudantes do 9º ano, "
                "por sexo e rede de ensino, para Estados (N3) e Capitais (N6)."
            ),
        ),
        _pense_habits_survey(
            survey_id="PENSE_ALCOOL_EXPERIMENTACAO",
            name="PeNSE Álcool: Experimentação de Bebidas Alcoólicas entre Escolares (UF e Capitais)",
            table=6030,
            var_id=3322,
            var_name="Escolares que Experimentaram Bebidas Alcoólicas (%)",
            var_slug="pense_alcool_experimentacao_pct",
            notice_text=(
                "Percentual de escolares que experimentaram bebida alcoólica alguma vez na vida, "
                "mapeado para as 27 UFs (N3) e 27 Capitais Estaduais (N6)."
            ),
        ),
        _pense_habits_survey(
            survey_id="PENSE_DROGAS_EXPERIMENTACAO",
            name="PeNSE Drogas Ilícitas: Experimentação de Drogas entre Escolares (UF e Capitais)",
            table=6035,
            var_id=7476,
            var_name="Escolares que Experimentaram Drogas Ilícitas (%)",
            var_slug="pense_drogas_experimentacao_pct",
            notice_text=(
                "Prevalência de experimentação de drogas ilícitas (maconha, cocaína, crack, inalantes etc.) "
                "entre escolares do 9º ano, por sexo e rede de ensino, para Estados (N3) e Capitais (N6)."
            ),
        ),
        _pense_habits_survey(
            survey_id="PENSE_ATIVIDADE_FISICA_300MIN",
            name="PeNSE Atividade Física: Escolares Ativos com 300 Minutos Semanais (UF e Capitais)",
            table=6018,
            var_id=6630,
            var_name="Escolares com 300 Minutos ou mais de Atividade Física (%)",
            var_slug="pense_atividade_fisica_pct",
            notice_text=(
                "Proporção de estudantes que atingem a recomendação da OMS de ao menos 300 minutos de atividade física "
                "semanal, por sexo e rede administrativa, para Estados (N3) e Capitais (N6)."
            ),
        ),
    ]
