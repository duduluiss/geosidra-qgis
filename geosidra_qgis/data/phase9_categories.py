"""Constantes de categorias para as pesquisas da Fase 9 (v0.11.0)."""

from typing import Dict, List, Tuple

# Quantidade do equipamento cultural (Tabela 6478, Classificação 1547)
P9_6478_1547: List[Tuple[str, str]] = [
    ("59153", "Total"),
    ("59154", "1 a 5"),
    ("59155", "6 a 15"),
    ("59156", "16 a 30"),
    ("59157", "31 a 40"),
    ("59158", "41 a 50"),
    ("60038", "Acima de 50"),
    ("59994", "Sem informação"),
]

# Tipos de mídias (Tabela 6477, Classificação 1543)
P9_6477_1543: List[Tuple[str, str]] = [
    ("59114", "Total"),
    ("59115", "Jornal impresso local"),
    ("59116", "Revista impressa local"),
    ("59117", "Rádio AM local"),
    ("59118", "Rádio FM local"),
    ("59119", "Rádio comunitária"),
    ("59120", "TV comunitária"),
    ("59121", "Geradora de TV"),
    ("59122", "Provedor de internet"),
    ("59123", "Nenhum dos itens"),
]

# Existência de pontos de cultura (Tabela 6479, Classificação 1548)
P9_6479_1548: List[Tuple[str, str]] = [
    ("59159", "Total"),
    ("59160", "Sim"),
    ("59161", "1 a 10"),
    ("59162", "11 a 25"),
    ("59163", "26 a 50"),
    ("59164", "51 a 100"),
    ("60037", "101 a 200"),
    ("59165", "201 a 500"),
    ("59166", "acima de 500"),
    ("59167", "A gestão municipal tem ações em parceria com algum Ponto de Cultura"),
    ("59168", "A gestão municipal NÃO tem ações em parceria com algum Ponto de Cultura"),
    ("59169", "Não"),
]

# Atividades culturais (Tabela 6476, Classificação 1541)
P9_6476_1541: List[Tuple[str, str]] = [
    ("59084", "Total"),
    ("59085", "Concurso/prêmio"),
    ("59086", "Apresentação musical"),
    ("59087", "Publicações culturais"),
    ("59088", "Eventos"),
    ("59089", "Feira de livros"),
    ("59090", "Programa radiofônico"),
    ("59091", "Programa de televisão"),
    ("59092", "Desfile de carnaval"),
    ("59093", "Montagem de peças teatrais"),
    ("59094", "Seminário/Simpósio/Encontro/Congresso/Palestra"),
    ("59095", "Festas, celebrações e manifestações tradicionais e populares"),
    ("59096", "Apresentações/oficinas/festivais de teatro online"),
    ("59097", "Apresentações/oficinas/festivais/lives musicais online"),
    ("59098", "Apresentações/oficinas/festivais de poesia/literatura online"),
    ("59099", "Apresentações/oficinas/festivais de artes online"),
    ("59100", "Outras atividades online"),
    ("59101", "Nenhuma das atividades"),
]

# Caracterização do órgão gestor (Tabela 7282, Classificação 1048)
P9_7282_1048: List[Tuple[str, str]] = [
    ("49367", "Total"),
    ("49369", "Secretaria municipal exclusiva"),
    ("49370", "Secretaria municipal em conjunto com outras políticas"),
    ("49371", "Setor subordinado a outra secretaria"),
    ("49372", "Setor subordinado diretamente à chefia do Executivo"),
    ("49373", "Órgão da administração indireta"),
]

# Situação do Conselho Municipal (Tabela 7403, Classificação 1510)
P9_7403_1510: List[Tuple[str, str]] = [
    ("58782", "Total"),
    ("58783", "Ativo"),
    ("58784", "Inativo"),
    ("58785", "Foi criado mas não foi instalado"),
]

# Existência de legislação municipal de proteção ao patrimônio cultural e previsão de tombamento (Tabela 9705, Classificação 1535)
P9_9705_1535: List[Tuple[str, str]] = [
    ("58903", "Total"),
    ("58904", "Sim"),
    ("58905", "Com previsão de tombamento de patrimônio material"),
    ("58906", "Com previsão de tombamento de patrimônio imaterial"),
    ("58907", "Não"),
    ("58908", "Sem informação"),
]

# Realização de Conferência Municipal de Cultura nos últimos 4 anos (Tabela 9702, Classificação 1528)
P9_9702_1528: List[Tuple[str, str]] = [
    ("58866", "Total"),
    ("58867", "Sim"),
    ("58868", "As deliberações das conferências foram consideradas como elementos de referência para a elaboração e desenvolvimento do Plano Municipal de Cultura"),
    ("58869", "As deliberações das conferências não foram consideradas como elementos de referência para a elaboração e desenvolvimento do Plano Municipal de Cultura"),
    ("58870", "As conferências foram realizadas após a elaboração do plano"),
    ("58871", "O município não possui plano"),
    ("58872", "Não"),
]

# Existência de Plano Municipal de Cultura (Tabela 9703, Classificação 1529)
P9_9703_1529: List[Tuple[str, str]] = [
    ("58873", "Total"),
    ("58874", "Sim, por instrumento legal"),
    ("58875", "Sim, mas não é regulamentado por instrumento legal"),
    ("58876", "Em elaboração"),
    ("58877", "Na fase de discussão com a sociedade"),
    ("58878", "Na fase de tramitação no Poder Executivo"),
    ("58879", "Na fase de tramitação na Câmara Municipal"),
    ("58880", "Aguardando sanção pelo Poder Executivo"),
    ("58881", "Não"),
]

# Existência de metas no Plano Municipal de Cultura (Tabela 9704, Classificação 1534)
P9_9704_1534: List[Tuple[str, str]] = [
    ("58899", "Total"),
    ("58900", "Sim"),
    ("58901", "Não"),
    ("58902", "Sem informação"),
]

# Gestão do Fundo Municipal de Cultura (Tabela 9707, Classificação 1538)
P9_9707_1538: List[Tuple[str, str]] = [
    ("58918", "Total"),
    ("58919", "O Conselho Municipal de Cultura é o responsável pela gestão do fundo"),
    ("58920", "O Conselho Municipal de Cultura não é o responsável pela gestão do fundo"),
    ("58921", "O fundo possui um conselho gestor próprio"),
    ("58922", "Sem informação"),
]

# Percentual de execução do orçamento previsto para a cultura no ano anterior ao da pesquisa (Tabela 6480, Classificação 1549)
P9_6480_1549: List[Tuple[str, str]] = [
    ("59170", "0"),
    ("59171", "até 10%"),
    ("59172", "de 11% a 20%"),
    ("59173", "de 21% a 30%"),
    ("59174", "de 31% a 40%"),
    ("59175", "de 41% a 50%"),
    ("59176", "de 51% a 60%"),
    ("59177", "de 61% a 70%"),
    ("59178", "de 71% a 80%"),
    ("59179", "de 81% a 90%"),
    ("59180", "Mais de 90%"),
]

# Instituição de Sistema Municipal de Esporte (Tabela 6812, Classificação 1563)
P9_6812_1563: List[Tuple[str, str]] = [
    ("59279", "Total"),
    ("59280", "Sim"),
    ("59281", "Em 2020 ou 2021"),
    ("59282", "De 2016 a 2019"),
    ("59283", "De 2010 a 2015"),
    ("59284", "Antes de 2010"),
    ("59285", "Não"),
]

# Organismos que integram o SME (Tabela 6984, Classificação 1564)
P9_6984_1564: List[Tuple[str, str]] = [
    ("59286", "Órgão gestor da política de esporte"),
    ("59287", "Conselho Municipal de Esporte"),
    ("59288", "Fórum municipal de esporte"),
    ("59289", "Conferência municipal de esporte"),
    ("59290", "Fundo municipal de esporte"),
    ("59291", "Pessoas físicas e jurídicas de direito privado"),
    ("59292", "Outros"),
    ("59293", "Não sabe informar"),
]

# Regulamentação da área de esporte por meio de instrumento legal (Tabela 8495, Classificação 1567)
P9_8495_1567: List[Tuple[str, str]] = [
    ("59294", "Total"),
    ("59295", "Sim"),
    ("59296", "Concessão de incentivos e isenções fiscais para o esporte"),
    ("59297", "Bolsa atleta"),
    ("59298", "Convênio e/ou parceria"),
    ("59299", "Subvenções concedidas para o esporte"),
    ("59300", "Projetos esportivos"),
    ("59301", "Outros"),
    ("59302", "Nenhuma regulamentação"),
]

# Execução de ações, projetos e programas permanentes de inclusão social através do esporte nos últimos 24 meses (Tabela 9347, Classificação 1570)
P9_9347_1570: List[Tuple[str, str]] = [
    ("59309", "Total"),
    ("59310", "Sim"),
    ("59311", "Não"),
]

# Elaboração de calendário de eventos esportivos (Tabela 9711, Classificação 1574)
P9_9711_1574: List[Tuple[str, str]] = [
    ("59330", "Total"),
    ("59331", "Sim"),
    ("59332", "Para esporte educacional"),
    ("59333", "Para esporte de rendimento"),
    ("59334", "Para esporte de lazer"),
    ("59335", "Não"),
]

# Tipo de instalação esportiva municipal (Tabela 9712, Classificação 1575)
P9_9712_1575: List[Tuple[str, str]] = [
    ("59336", "Academia de boxe"),
    ("59337", "Arena de rodeio e vaquejada"),
    ("59338", "Autódromo"),
    ("59339", "Campo de beisebol"),
    ("59340", "Campo de golfe"),
    ("59341", "Campo de bocha"),
    ("59342", "Campo (futebol/society/rugby/hóquei sobre grama) e/ou estádio (futebol/rugby)"),
    ("59343", "Complexo aquático (natação/polo aquático/saltos ornamentais/nado sincronizado)"),
    ("59345", "Estande de tiro"),
    ("59346", "Ginásio"),
    ("59347", "Kartódromo"),
    ("59348", "Piscina"),
    ("59349", "Pista de atletismo"),
    ("59350", "Pista de BMX"),
    ("59351", "Pista de corrida de cavalo e outros animais"),
    ("59352", "Pista de skate/patins e similares"),
    ("59353", "Pista para hipismo"),
    ("59354", "Quadra de esporte"),
    ("59355", "Raia para remo e canoagem"),
    ("59356", "Salão para prática esportiva"),
    ("59357", "Tanque para salto ornamental"),
    ("59358", "Velódromo"),
    ("59359", "Outras instalações"),
]

# Categorias dos estabelecimentos de hospedagem (Tabela 6599, Classificação 492)
P9_6599_492: List[Tuple[str, str]] = [
    ("40476", "Total"),
    ("12834", "Luxo"),
    ("12835", "Superior/muito confortável"),
    ("12836", "Turístico/médio conforto"),
    ("12837", "Econômico"),
    ("12838", "Simples"),
]

# Características dos estabelecimentos de hospedagem (Tabela 6598, Classificação 794)
P9_6598_794: List[Tuple[str, str]] = [
    ("40477", "Total"),
    ("40478", "Independentes"),
    ("40479", "Integram uma cadeia nacional de hotéis"),
    ("40480", "Integram uma cadeia internacional de hotéis"),
]

# Principal local de hospedagem (Tabela 8463, Classificação 907)
P9_8463_907: List[Tuple[str, str]] = [
    ("48083", "Total"),
    ("57209", "Hotel, resort ou flat"),
    ("48085", "Pousada"),
    ("48086", "Casa de amigo ou parente"),
    ("48087", "Imóvel próprio"),
    ("57210", "Imóvel por temporada ou AirBnB"),
    ("48088", "Outro"),
]

PHASE9_STATIC_CATEGORIES: Dict[str, List[Tuple[str, str]]] = {
    "P9_6478_1547": P9_6478_1547,
    "P9_6477_1543": P9_6477_1543,
    "P9_6479_1548": P9_6479_1548,
    "P9_6476_1541": P9_6476_1541,
    "P9_7282_1048": P9_7282_1048,
    "P9_7403_1510": P9_7403_1510,
    "P9_9705_1535": P9_9705_1535,
    "P9_9702_1528": P9_9702_1528,
    "P9_9703_1529": P9_9703_1529,
    "P9_9704_1534": P9_9704_1534,
    "P9_9707_1538": P9_9707_1538,
    "P9_6480_1549": P9_6480_1549,
    "P9_6812_1563": P9_6812_1563,
    "P9_6984_1564": P9_6984_1564,
    "P9_8495_1567": P9_8495_1567,
    "P9_9347_1570": P9_9347_1570,
    "P9_9711_1574": P9_9711_1574,
    "P9_9712_1575": P9_9712_1575,
    "P9_6599_492": P9_6599_492,
    "P9_6598_794": P9_6598_794,
    "P9_8463_907": P9_8463_907,
}
