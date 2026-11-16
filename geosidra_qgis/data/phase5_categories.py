# -*- coding: utf-8 -*-
"""
Categorias estáticas curadas da Fase 5 (Meio Ambiente, Clima, Biodiversidade e ODS).
Extraídas diretamente dos metadados oficiais da API SIDRA/IBGE v3.
"""

from typing import Dict, List, Tuple

# T10511 c12919: Grupos taxonômicos (10 itens)
P5_10511_12919: List[Tuple[int, str]] = [
    (119371, 'Total'),
    (119357, 'Mamíferos'),
    (119334, 'Aves'),
    (119335, 'Répteis'),
    (119336, 'Anfíbios'),
    (57939, 'Plantas vasculares'),
    (119459, 'Fungos'),
    (57940, 'Peixes ósseos'),
    (119467, 'Moluscos'),
    (57938, 'Artrópodes'),
]

# T10255 c2101: Modo de produção (4 itens)
P5_10255_2101: List[Tuple[int, str]] = [
    (79453, 'Total'),
    (79454, 'Permanente'),
    (79455, 'Temporária'),
    (79456, 'Extração'),
]

# T8536 c1210: Ano do desastre natural de maior impacto para o município (6 itens)
P5_8536_1210: List[Tuple[int, str]] = [
    (50868, '2017'),
    (50869, '2018'),
    (50870, '2019'),
    (50871, '2020'),
    (57733, 'Não sabe'),
    (57734, 'Não possui informação'),
]

# T8539 c1234: Existência de intervenção para evitar ou minimizar os danos causados por escorregamentos ou deslizamentos de encostas (12 itens)
P5_8539_1234: List[Tuple[int, str]] = [
    (57264, 'Total'),
    (57265, 'Com intervenção'),
    (51155, 'Estabilização e proteção de taludes'),
    (51156, 'Retaludamento de encostas'),
    (51157, 'Obras de contenção'),
    (51158, 'Construção de canais de macrodrenagens'),
    (51159, 'Realocação da população que vive em área de risco'),
    (51160, 'Revegetação de encostas'),
    (51161, 'Outra solução'),
    (51162, 'Nenhuma intervenção'),
    (51163, 'Não sabe'),
    (57266, 'Sem informação'),
]

# T8540 c1235: Existência de instrumento de planejamento de gestão de riscos e desastres no município (13 itens)
P5_8540_1235: List[Tuple[int, str]] = [
    (51164, 'Total'),
    (51165, 'Com algum instrumento de planejamento de gestão de riscos e desastres'),
    (51166, 'Com Plano Diretor que contemple a prevenção de enchentes ou inundações graduais, ou enxurradas ou inundações bruscas'),
    (51167, 'Com Lei de Uso e Ocupação do Solo que contemple a prevenção de enchentes ou inundações graduais, ou enxurradas ou inundações bruscas'),
    (51168, 'Com Lei específica que contemple a prevenção de enchentes ou inundações graduais, ou enxurradas ou inundações bruscas'),
    (51169, 'Com Plano Diretor que contemple a prevenção de escorregamentos ou deslizamentos de encostas'),
    (51170, 'Com Lei de Uso e Ocupação do Solo que contemple a prevenção de escorregamentos ou deslizamentos de encostas'),
    (51171, 'Com Lei específica que contemple a prevenção de escorregamentos ou deslizamentos de encostas'),
    (51172, 'Com Plano Municipal de Redução de Riscos'),
    (51173, 'Com Carta geotécnica de aptidão à urbanização'),
    (51174, 'Com Plano de implantação de obras e serviços para redução de riscos de desastres'),
    (51175, 'Nenhum dos instrumentos'),
    (57267, 'Sem informação'),
]

# T8541 c1236: Existência de medidas adotadas em relação à gestão de riscos de desastres decorrentes de enchentes ou inundações graduais, ou enxurradas ou inundações bruscas (11 itens)
P5_8541_1236: List[Tuple[int, str]] = [
    (51176, 'Total'),
    (51177, 'Com alguma das medidas adotadas'),
    (51178, 'Com mapeamentos de áreas de risco de enchentes ou inundações'),
    (51179, 'Com programa habitacional para realocação de população de baixa renda em área de risco'),
    (51180, 'Com mecanismos de controle e fiscalização para evitar ocupação em áreas suscetíveis aos desastres'),
    (51181, 'Com plano de contingência'),
    (51182, 'Com projetos de engenharia relacionados ao evento'),
    (51183, 'Com sistema de alerta antecipado de desastres'),
    (51184, 'Com cadastro de risco'),
    (51185, 'Nenhum dos itens'),
    (57268, 'Sem informação'),
]

# T8542 c1239: Existência de instuições de apoio a gestão de riscos e de desastres (24 itens)
P5_8542_1239: List[Tuple[int, str]] = [
    (51200, 'Total'),
    (51201, 'Com alguma instituição de apoio a gestão de riscos e desastres elencadas'),
    (51202, 'Com Unidade do Corpo de Bombeiros'),
    (51203, 'Com Coordenação Municipal de Proteção e Defesa Civil (COMPDEC) ou órgão similar'),
    (57271, 'O responsável pela coordenação atua exclusivamente nesta função'),
    (57272, 'Realiza ações articuladas e coordenadas do Sistema Municipal de Proteção e Defesa Civil'),
    (57273, 'Conhece o Sistema Integrado de Informações sobre Desastres - S2ID'),
    (57274, 'Utiliza sistema próprio na área de Proteção e Defesa Civil'),
    (57275, 'Há previsão de recursos para ações de proteção e defesa civil na Lei Orçamentária Anual'),
    (57276, 'Há outras fontes de recursos para ações de proteção e defesa civil'),
    (57277, 'Dispõe de espaço físico exclusivo'),
    (57278, 'Dispõe de viatura'),
    (57279, 'Dispõe de computadores'),
    (57280, 'Dispõe de GPS'),
    (57281, 'Dispõe de coletes'),
    (57282, 'Dispõe de servidores com vínculo empregatício'),
    (57283, 'Dispõe de sistema de alerta antecipado de desastres'),
    (57284, 'Nenhum dos itens citados'),
    (57285, 'Não sabe'),
    (51204, 'Com Núcleo de Proteção e Defesa Civil (NUPDECs)'),
    (51205, 'Com Guarda Municipal'),
    (51206, 'Nenhuma das insttuições citadas'),
    (51207, 'Não sabe informar'),
    (57286, 'Sem informação'),
]

# T5625 c713: Tipo de uso da unidade de conservação (3 itens)
P5_5625_713: List[Tuple[int, str]] = [
    (33558, 'Total'),
    (33559, 'Proteção integral'),
    (33560, 'Uso sustentável'),
]

# T10755 c2: Sexo (3 itens)
P5_10755_2: List[Tuple[int, str]] = [
    (6794, 'Total'),
    (92956, 'Homem'),
    (92957, 'Mulher'),
]

PHASE5_STATIC_CATEGORIES: Dict[str, List[Tuple[int, str]]] = {
    "P5_10511_12919": P5_10511_12919,
    "P5_10255_2101": P5_10255_2101,
    "P5_8536_1210": P5_8536_1210,
    "P5_8539_1234": P5_8539_1234,
    "P5_8540_1235": P5_8540_1235,
    "P5_8541_1236": P5_8541_1236,
    "P5_8542_1239": P5_8542_1239,
    "P5_5625_713": P5_5625_713,
    "P5_10755_2": P5_10755_2,
}
