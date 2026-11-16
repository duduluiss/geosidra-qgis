# -*- coding: utf-8 -*-
"""
Categorias estáticas curadas da Fase 13 (v0.15.0):
Vulnerabilidade Territorial, Riscos de Desastres e Bancarização (CEMADEN / BACEN / PNSB / Censo Agro / ODS).
"""

from typing import Dict, List, Tuple

PHASE13_STATIC_CATEGORIES: Dict[str, List[Tuple[int, str]]] = {
    "P13_CENSO_AGRO_AGENTES_FINANCEIROS": [
        (115947, "Total de estabelecimentos agropecuários que obtiveram financiamento"),
        (111915, "Bancos (oficiais e comerciais)"),
        (111916, "Cooperativas de crédito"),
        (41047, "Governos (programas governamentais diretos)"),
        (111917, "Comerciantes de matéria prima ou produtos agropecuários"),
        (111918, "Fornecedores de insumos ou equipamentos"),
        (111919, "Empresa integradora ou agroindústria"),
        (111920, "Outras instituições financeiras (exceto bancos e cooperativas)"),
        (111921, "Organizações Não-Governamentais (ONGs)"),
        (111922, "Parentes ou amigos"),
        (111923, "Outro agente financeiro"),
    ],
    "P13_PNSB_AREAS_RISCO_DRENAGEM": [
        (101375, "Total geral de municípios"),
        (101376, "Total com áreas de risco que demandam drenagem urbana especial"),
        (101377, "Áreas em taludes e encostas sujeitas a deslizamento"),
        (101378, "Áreas de baixio sujeitas a inundações e proliferação de vetores"),
        (101379, "Áreas sem infraestrutura de drenagem ou ocupações clandestinas"),
        (101380, "Áreas urbanas com grotões, ravinas e processos erosivos crônicos"),
        (101381, "Outras áreas de risco especial"),
    ],
    "P13_PNSB_INUNDACOES_URBANAS": [
        (8485, "Total geral de municípios"),
        (8486, "Total de municípios com ocorrência de inundações ou alagamentos"),
        (8487, "Áreas urbanas ocupadas inundáveis naturalmente pelos cursos d'água"),
        (8488, "Áreas de baixios naturalmente inundáveis ocupadas inadequadamente"),
        (8489, "Áreas urbanas não usualmente inundáveis"),
        (8490, "Outras áreas urbanas atingidas"),
    ],
    "P13_PNSB_AGRAVANTES_ENCHENTES": [
        (101343, "Total geral de municípios"),
        (101344, "Total de municípios atingidos por inundações nos últimos cinco anos"),
        (101346, "Obstrução de bueiros, galerias e bocas de lobo por detritos e lixo"),
        (101348, "Ocupação intensa e desordenada do solo urbano e encostas"),
        (101345, "Dimensionamento inadequado de projeto das galerias pluviais"),
        (101347, "Obras inadequadas e intervenções viárias sem drenagem"),
        (101349, "Lençol freático alto"),
        (101350, "Existência de interferência física no sistema de drenagem"),
        (8491, "Desmatamento e perda de cobertura vegetal nas bacias"),
        (8492, "Lançamento inadequado de resíduos sólidos urbanos"),
        (101351, "Outro fator agravante"),
    ],
    "P13_ODS_SEXO_BANCARIZACAO": [
        (6794, "Total de adultos (Homens e Mulheres)"),
        (92956, "Homens adultos"),
        (92957, "Mulheres adultas"),
    ],
    "P13_ODS_TRIMESTRES_INADIMPLENCIA": [
        (15619, "Quarto trimestre (4T)"),
        (15618, "Terceiro trimestre (3T)"),
        (15617, "Segundo trimestre (2T)"),
        (15616, "Primeiro trimestre (1T)"),
    ],
}
