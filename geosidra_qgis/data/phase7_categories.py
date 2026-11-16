"""Constantes e categorias estáticas curadas para a Fase 7 do GeoSIDRA (v0.9.0).

Abrange 25 pesquisas estruturadas em Habitação, Favelas, Condições de Moradia e Entorno Urbano
(Censo Demográfico 2022 e MUNIC).
"""

from typing import Dict, List, Tuple

# Cor ou raça (Favelas) (Tabela 9884, Classificação 86)
P7_9884_86: List[Tuple[str, str]] = [
    ("95251", "Total"),
    ("2776", "Branca"),
    ("2777", "Preta"),
    ("2778", "Amarela"),
    ("2779", "Parda"),
    ("2780", "Indígena"),
    ("2781", "Sem declaração"),
]

# Alfabetização (Favelas) (Tabela 9886, Classificação 59)
P7_9886_59: List[Tuple[str, str]] = [
    ("93024", "Total"),
    ("1023", "Alfabetizadas"),
    ("1024", "Não alfabetizadas"),
]

# Espécie de domicílio (Favelas) (Tabela 9887, Classificação 3)
P7_9887_3: List[Tuple[str, str]] = [
    ("59993", "Total"),
    ("9697", "Particular"),
    ("2504", "Particular permanente"),
    ("59998", "Particular permanente ocupado"),
    ("59999", "Particular permanente ocupado - com entrevista"),
    ("60000", "Particular permanente ocupado - sem entrevista"),
    ("60001", "Particular permanente não ocupado"),
    ("60002", "Particular permanente não ocupado - vago"),
    ("60003", "Particular permanente não ocupado - uso ocasional"),
    ("2505", "Particular improvisado"),
    ("103995", "Coletivo"),
    ("10004", "Coletivo - com morador"),
    ("10005", "Coletivo - sem morador"),
]

# Espécie de estabelecimento (Favelas) (Tabela 9889, Classificação 3)
P7_9889_3: List[Tuple[str, str]] = [
    ("59993", "Total"),
    ("490", "Estabelecimento de ensino"),
    ("491", "Estabelecimento de saúde"),
    ("72411", "Estabelecimento religioso"),
    ("489", "Estabelecimento agropecuário"),
    ("492", "Estabelecimentos de outras finalidades"),
    ("72514", "Edificação em construção ou em reforma"),
]

# Tipo de domicílio (Favelas) (Tabela 9890, Classificação 125)
P7_9890_125: List[Tuple[str, str]] = [
    ("2932", "Total"),
    ("6815", "Casa"),
    ("121264", "Casa de vila ou em condomínio"),
    ("3247", "Apartamento"),
    ("71975", "Habitação em casa de cômodos ou cortiço"),
    ("71976", "Habitação indígena sem paredes ou maloca"),
    ("71977", "Estrutura residencial permanente degradada ou inacabada"),
]

# Forma de abastecimento de água (Favelas) (Tabela 9891, Classificação 301)
P7_9891_301: List[Tuple[str, str]] = [
    ("72053", "Total"),
    ("31471", "Rede geral de distribuição"),
    ("72054", "Poço profundo ou artesiano"),
    ("72055", "Poço raso, freático ou cacimba"),
    ("72088", "Fonte, nascente ou mina"),
    ("31472", "Carro-pipa"),
    ("72089", "Água da chuva armazenada"),
    ("72090", "Rios, açudes, córregos, lagos e igarapés"),
    ("72091", "Outra"),
]

# Tipo de esgotamento sanitário (Favelas) (Tabela 9892, Classificação 11558)
P7_9892_11558: List[Tuple[str, str]] = [
    ("46292", "Total"),
    ("46290", "Rede geral, rede pluvial ou fossa ligada à rede"),
    ("72110", "Rede geral ou pluvial"),
    ("72111", "Fossa séptica ou fossa filtro ligada à rede"),
    ("72112", "Fossa séptica ou fossa filtro não ligada à rede"),
    ("72113", "Fossa rudimentar ou buraco"),
    ("92858", "Vala"),
    ("72114", "Rio, lago, córrego ou mar"),
    ("72115", "Outra forma"),
    ("92861", "Não tinham banheiro nem sanitário"),
]

# Destino do lixo (Favelas) (Tabela 9893, Classificação 67)
P7_9893_67: List[Tuple[str, str]] = [
    ("10972", "Total"),
    ("2520", "Coletado"),
    ("72120", "Coletado no domicílio por serviço de limpeza"),
    ("72121", "Depositado em caçamba de serviço de limpeza"),
    ("72122", "Queimado na propriedade"),
    ("72123", "Enterrado na propriedade"),
    ("72124", "Jogado em terreno baldio, encosta ou área pública"),
    ("1091", "Outro destino"),
]

# Ligação à rede geral de água (Favelas) (Tabela 9894, Classificação 1821)
P7_9894_1821: List[Tuple[str, str]] = [
    ("72129", "Total"),
    ("72144", "Possui ligação à rede geral e a utiliza como forma principal"),
    ("72145", "Possui ligação à rede geral, mas utiliza principalmente outra forma"),
    ("72146", "Possui ligação à rede geral, mas utiliza principalmente outra forma - Poço profundo ou artesiano"),
    ("72147", "Possui ligação à rede geral, mas utiliza principalmente outra forma - Poço raso, freático ou cacimba"),
    ("72148", "Possui ligação à rede geral, mas utiliza principalmente outra forma - Fonte, nascente ou mina"),
    ("72149", "Possui ligação à rede geral, mas utiliza principalmente outra forma - Carro-pipa"),
    ("72150", "Possui ligação à rede geral, mas utiliza principalmente outra forma - Água da chuva armazenada"),
    ("72151", "Possui ligação à rede geral, mas utiliza principalmente outra forma - Rios, açudes, córregos, lagos e igarapés"),
    ("72152", "Possui ligação à rede geral, mas utiliza principalmente outra forma - Outra"),
    ("72153", "Não possui ligação com a rede geral"),
    ("72154", "Não possui ligação com a rede geral - Poço profundo ou artesiano"),
    ("72155", "Não possui ligação com a rede geral - Poço raso, freático ou cacimba"),
    ("72156", "Não possui ligação com a rede geral - Fonte, nascente ou mina"),
    ("72157", "Não possui ligação com a rede geral - Carro-pipa"),
    ("72158", "Não possui ligação com a rede geral - Água da chuva armazenada"),
    ("72159", "Não possui ligação com a rede geral - Rios, açudes, córregos, lagos e igarapés"),
    ("72160", "Não possui ligação com a rede geral - Outra"),
]

# Espécie de domicílio recenseado (Tabela 4711, Classificação 3)
P7_4711_3: List[Tuple[str, str]] = [
    ("59993", "Total"),
    ("9697", "Particular"),
    ("2504", "Particular permanente"),
    ("59998", "Particular permanente ocupado"),
    ("59999", "Particular permanente ocupado - com entrevista"),
    ("60000", "Particular permanente ocupado - sem entrevista"),
    ("60001", "Particular permanente não ocupado"),
    ("60002", "Particular permanente não ocupado - vago"),
    ("60003", "Particular permanente não ocupado - uso ocasional"),
    ("2505", "Particular improvisado"),
    ("103995", "Coletivo"),
    ("10004", "Coletivo - com morador"),
    ("10005", "Coletivo - sem morador"),
]

# Material das paredes externas (Tabela 9928, Classificação 137)
P7_9928_137: List[Tuple[str, str]] = [
    ("13233", "Total"),
    ("73073", "Alvenaria ou taipa com revestimento"),
    ("12194", "Alvenaria sem revestimento"),
    ("73074", "Taipa sem revestimento"),
    ("73075", "Madeira para construção"),
    ("73076", "Madeira aproveitada de tapume, embalagens, andaimes"),
    ("2876", "Outro material"),
    ("13226", "Sem parede"),
]

# Condição de ocupação do domicílio (Tabela 9929, Classificação 63)
P7_9929_63: List[Tuple[str, str]] = [
    ("95826", "Total"),
    ("73554", "Próprio de algum morador"),
    ("73126", "Próprio de algum morador - já pago, herdado ou ganho"),
    ("4343", "Próprio de algum morador - ainda pagando"),
    ("1055", "Alugado"),
    ("73553", "Cedido ou emprestado"),
    ("73127", "Cedido ou emprestado - por empregador"),
    ("73128", "Cedido ou emprestado - por familiar"),
    ("73129", "Cedido ou emprestado - outra forma"),
    ("1058", "Outra condição"),
]

# Número de banheiros de uso exclusivo (Tabela 9931, Classificação 1973)
P7_9931_1973: List[Tuple[str, str]] = [
    ("73081", "Total"),
    ("73082", "Nenhum banheiro"),
    ("73083", "1 banheiro"),
    ("73084", "2 banheiros"),
    ("73085", "3 banheiros ou mais"),
]

# Moradores por dormitório (Tabela 9933, Classificação 1975)
P7_9933_1975: List[Tuple[str, str]] = [
    ("73086", "Total"),
    ("73087", "1 morador"),
    ("73088", "Mais de 1 morador até 2 moradores"),
    ("73089", "Mais de 2 moradores até 3 moradores"),
    ("73090", "Mais de 3 moradores"),
]

# Presença de máquina de lavar roupas (Tabela 9935, Classificação 1977)
P7_9935_1977: List[Tuple[str, str]] = [
    ("73091", "Total"),
    ("73092", "Sim"),
    ("73093", "Não"),
]

# Características do entorno dos domicílios (Tabela 10050, Classificação 14)
P7_10050_14: List[Tuple[str, str]] = [
    ("200", "Total"),
    ("72240", "Capacidade máxima de circulação da via - Caminhão ou ônibus"),
    ("72241", "Capacidade máxima de circulação da via - Carro ou van"),
    ("72242", "Capacidade máxima de circulação da via - Motocicletas, bicicletas e pedestres"),
    ("72243", "Capacidade de circulação da via - Aquavias"),
    ("72244", "Capacidade de circulação da via - Não declarado"),
    ("72246", "Via pavimentada - Existe"),
    ("72247", "Via pavimentada - Não existe"),
    ("72248", "Via pavimentada - Não declarado"),
    ("72250", "Existência de bueiro / boca de lobo - Existe"),
    ("72251", "Existência de bueiro / boca de lobo - Não existe"),
    ("72252", "Existência de bueiro / boca de lobo - Não declarado"),
    ("72254", "Existência de iluminação pública - Existe"),
    ("72255", "Existência de iluminação pública - Não existe"),
    ("72256", "Existência de iluminação pública - Não declarado"),
    ("72258", "Existência de ponto de ônibus / van - Existe"),
    ("72259", "Existência de ponto de ônibus / van - Não existe"),
    ("72260", "Existência de ponto de ônibus / van - Não declarado"),
    ("72262", "Existência de via sinalizada para bicicleta - Existe"),
    ("72263", "Existência de via sinalizada para bicicleta - Não existe"),
    ("72264", "Existência de via sinalizada para bicicleta - Não declarado"),
    ("72266", "Existência de calçada / passeio - Existe"),
    ("72267", "Existência de calçada / passeio - Não existe"),
    ("72268", "Existência de calçada / passeio - Não declarado"),
    ("72270", "Existência de obstáculo na calçada - Existe"),
    ("72271", "Existência de obstáculo na calçada - Não existe"),
    ("72272", "Existência de obstáculo na calçada - Não declarado"),
    ("72274", "Existência de rampa para cadeirante - Existe"),
    ("72275", "Existência de rampa para cadeirante - Não existe"),
    ("72276", "Existência de rampa para cadeirante - Não declarado"),
    ("72278", "Arborização - Sem árvores"),
    ("72279", "Arborização - De 1 a 2 árvores"),
    ("72280", "Arborização - De 3 a 4 árvores"),
    ("72281", "Arborização - 5 ou mais árvores"),
    ("72282", "Arborização - Não declarado"),
]

# Bueiro, iluminação, calçada e rampa cadeirante (Tabela 10054, Classificação 14)
P7_10054_14: List[Tuple[str, str]] = [
    ("200", "Total"),
    ("72250", "Existência de bueiro / boca de lobo - Existe"),
    ("72251", "Existência de bueiro / boca de lobo - Não existe"),
    ("72252", "Existência de bueiro / boca de lobo - Não declarado"),
    ("72254", "Existência de iluminação pública - Existe"),
    ("72255", "Existência de iluminação pública - Não existe"),
    ("72256", "Existência de iluminação pública - Não declarado"),
    ("72266", "Existência de calçada / passeio - Existe"),
    ("72267", "Existência de calçada / passeio - Não existe"),
    ("72268", "Existência de calçada / passeio - Não declarado"),
    ("72274", "Existência de rampa para cadeirante - Existe"),
    ("72275", "Existência de rampa para cadeirante - Não existe"),
    ("72276", "Existência de rampa para cadeirante - Não declarado"),
]

# Existência de Plano Municipal de Habitação/Transporte (Tabela 8431, Classificação 1329)
P7_8431_1329: List[Tuple[str, str]] = [
    ("57146", "Total"),
    ("57147", "Com Plano Municipal de Habitação"),
    ("57148", "Sem Plano Municipal de Habitação"),
    ("57149", "Sem informação na área de habitação"),
    ("57150", "Com Plano Municipal de Transporte"),
    ("57151", "Sem Plano Municipal de Transporte"),
    ("57152", "Sem informação na área de transporte"),
]

# Caracterização do Fundo Municipal de Habitação (Tabela 8438, Classificação 1071)
P7_8438_1071: List[Tuple[str, str]] = [
    ("50129", "Total"),
    ("50131", "Com o Conselho Municipal como gestor do fundo"),
    ("50132", "Com conselho gestor próprio"),
    ("50133", "Com o fundo reunindo todos os recursos orçamentários e de outras fontes destinados aos programas da área"),
]

# Programas e ações municipais de habitação (Tabela 8477, Classificação 1075)
P7_8477_1075: List[Tuple[str, str]] = [
    ("50148", "Total"),
    ("50149", "Com pelo menos um programa ou ação realizado pela prefeitura"),
    ("50150", "Construção de unidades habitacionais"),
    ("50151", "Aquisição de unidades habitacionais"),
    ("50152", "Melhoria de unidades habitacionais"),
    ("50153", "Oferta de material de construção"),
    ("50154", "Oferta de lotes"),
    ("50155", "Regularização fundiária"),
    ("50156", "Urbanização de assentamentos"),
    ("50157", "Sem os programas ou ações relacionados"),
    ("56862", "Municípios sem informação"),
]

PHASE7_STATIC_CATEGORIES: Dict[str, List[Tuple[str, str]]] = {
    "P7_9884_86": P7_9884_86,
    "P7_9886_59": P7_9886_59,
    "P7_9887_3": P7_9887_3,
    "P7_9889_3": P7_9889_3,
    "P7_9890_125": P7_9890_125,
    "P7_9891_301": P7_9891_301,
    "P7_9892_11558": P7_9892_11558,
    "P7_9893_67": P7_9893_67,
    "P7_9894_1821": P7_9894_1821,
    "P7_4711_3": P7_4711_3,
    "P7_9928_137": P7_9928_137,
    "P7_9929_63": P7_9929_63,
    "P7_9931_1973": P7_9931_1973,
    "P7_9933_1975": P7_9933_1975,
    "P7_9935_1977": P7_9935_1977,
    "P7_10050_14": P7_10050_14,
    "P7_10054_14": P7_10054_14,
    "P7_8431_1329": P7_8431_1329,
    "P7_8438_1071": P7_8438_1071,
    "P7_8477_1075": P7_8477_1075,
}
