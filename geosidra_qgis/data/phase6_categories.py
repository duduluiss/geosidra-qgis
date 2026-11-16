"""Listas estaticas de categorias para pesquisas da Fase 6 (Infancia, Juventude e Escolas).

Gerado automaticamente via API de metadados do IBGE/SIDRA.
"""

from typing import List, Tuple

P6_10057_11798_CATEGORIES: List[Tuple[int, str]] = [
    (95300, "Total"),
    (95301, "Creche"),
    (107454, "Pré-escolar"),
    (7906, "Regular de ensino fundamental"),
]

P6_10056_58_CATEGORIES: List[Tuple[int, str]] = [
    (95253, "Total"),
    (99749, "0 a 3 anos"),
    (2483, "0 ano"),
    (2484, "1 ano"),
    (2485, "2 anos"),
    (2486, "3 anos"),
    (47813, "4 a 5 anos"),
    (2487, "4 anos"),
    (2488, "5 anos"),
    (31615, "6 a 14 anos"),
    (2489, "6 anos"),
    (2490, "7 anos"),
    (2491, "8 anos"),
    (2492, "9 anos"),
    (2493, "10 anos"),
    (2494, "11 anos"),
    (2495, "12 anos"),
    (2496, "13 anos"),
    (2497, "14 anos"),
    (2792, "15 a 17 anos"),
    (2498, "15 anos"),
    (2499, "16 anos"),
    (2500, "17 anos"),
    (100052, "18 a 24 anos"),
    (2501, "18 anos"),
    (2502, "19 anos"),
    (92958, "20 anos"),
    (92959, "21 anos"),
    (92960, "22 anos"),
    (92961, "23 anos"),
    (92962, "24 anos"),
    (108866, "25 anos ou mais"),
]

P6_10048_2071_CATEGORIES: List[Tuple[int, str]] = [
    (77571, "Total"),
    (77572, "Dinheiro"),
    (77573, "Bolsa de estudo"),
    (77574, "Vaga adquirida pelo governo"),
    (77575, "Outro"),
    (77576, "Não informado"),
]

P6_10046_2068_CATEGORIES: List[Tuple[int, str]] = [
    (77463, "Total"),
    (77464, "Sim"),
    (77465, "Não"),
    (77466, "Não informado"),
]

P6_10036_2040_CATEGORIES: List[Tuple[int, str]] = [
    (73870, "Total"),
    (73871, "Enfrentamento ao bullying"),
    (73872, "Enfrentamento e erradicação do trabalho infantil"),
    (73873, "Enfrentamento à violência física contra crianças e adolescentes"),
    (73874, "Enfrentamento à violência sexual contra crianças e adolescentes (abuso e exploração)"),
    (73875, "Proteção de crianças e adolescentes ameaçados de morte"),
    (73880, "Atendimento à criança e ao adolescente em situação de rua"),
    (73881, "Atendimento socioeducativo ao adolescente em conflito com a lei"),
    (73882, "Busca e localização de crianças e adolescentes desaparecidos"),
    (73883, "Combate ao uso de drogas"),
    (73884, "Nenhuma das ações ou medidas citadas"),
]

P6_10038_2045_CATEGORIES: List[Tuple[int, str]] = [
    (73913, "Total"),
    (73922, "Pela Prefeitura – Assistência Social"),
    (73923, "Pela Prefeitura – Educação"),
    (73924, "Pela Prefeitura – Área Específica de Socioeducação"),
    (73925, "Pela Prefeitura – Saúde"),
    (73926, "Pela Prefeitura - Outra área"),
    (73927, "Pelo Governo Estadual"),
    (73928, "Pelo Poder Judiciário"),
    (73929, "Pelo Centro de Referência Especializado de Assistência Social"),
    (73930, "Por Organização não-governamental"),
    (73931, "Por Consórcio de municípios"),
    (73932, "Não há no município execução de medidas socioeducativas em meio aberto"),
    (73933, "Não informado"),
]

P6_7783_812_CATEGORIES: List[Tuple[int, str]] = [
    (41115, "Total"),
    (41116, "Acesso à eletricidade"),
    (41117, "Acesso à internet para fins pedagógicos"),
    (41118, "Computador para fins pedagógicos"),
    (41119, "Infraestrutura adaptada para alunos portadores de deficiência"),
    (41120, "Abastecimento de água"),
    (41121, "Água Filtrada"),
]

P6_7141_871_CATEGORIES: List[Tuple[int, str]] = [
    (47815, "6 a 14 anos no ensino fundamental"),
    (47816, "6 a 10 anos nos anos iniciais do ensino fundamental"),
    (47817, "11 a 14 anos nos anos finais do ensino fundamental"),
    (47818, "15 a 17 anos no ensino médio"),
    (47819, "18 a 24 no ensino superior"),
]

P6_6053_752_CATEGORIES: List[Tuple[int, str]] = [
    (39832, "Total"),
    (39833, "Cor ou raça"),
    (39834, "Religião"),
    (39835, "Aparência do rosto"),
    (39836, "Aparência do corpo"),
    (39837, "Orientação sexual"),
    (39838, "Região de origem"),
    (39839, "Outro motivo/causa"),
]

P6_PENSE_SEXO_CATEGORIES: List[Tuple[int, str]] = [
    (6794, "Total"),
    (110095, "Masculino"),
    (110096, "Feminino"),
]

P6_PENSE_DEP_ADM_CATEGORIES: List[Tuple[int, str]] = [
    (31050, "Total"),
    (31052, "Pública"),
    (31051, "Privada"),
]

PHASE6_STATIC_CATEGORIES = {
    "P6_10057_11798": P6_10057_11798_CATEGORIES,
    "P6_10056_58": P6_10056_58_CATEGORIES,
    "P6_10048_2071": P6_10048_2071_CATEGORIES,
    "P6_10046_2068": P6_10046_2068_CATEGORIES,
    "P6_10036_2040": P6_10036_2040_CATEGORIES,
    "P6_10038_2045": P6_10038_2045_CATEGORIES,
    "P6_7783_812": P6_7783_812_CATEGORIES,
    "P6_7141_871": P6_7141_871_CATEGORIES,
    "P6_6053_752": P6_6053_752_CATEGORIES,
    "P6_PENSE_SEXO": P6_PENSE_SEXO_CATEGORIES,
    "P6_PENSE_DEP_ADM": P6_PENSE_DEP_ADM_CATEGORIES,
}
