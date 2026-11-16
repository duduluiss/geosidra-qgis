"""Constantes e categorias estáticas curadas para a Fase 8 do GeoSIDRA (v0.10.0).

Abrange 22 pesquisas estruturadas em Segurança Pública, Vitimização, Justiça e Defesa Social
(ODS 16, PNAD Contínua Vitimização e MUNIC 2023).
"""

from typing import Dict, List, Tuple

# Sexo (ODS Homicídios) (Tabela 7875, Classificação 2)
P8_7875_2: List[Tuple[str, str]] = [
    ("4", "Homens"),
    ("5", "Mulheres"),
]

# Grupo de idade (ODS Homicídios) (Tabela 7877, Classificação 58)
P8_7877_58: List[Tuple[str, str]] = [
    ("1140", "0 a 4 anos"),
    ("1141", "5 a 9 anos"),
    ("1142", "10 a 14 anos"),
    ("1143", "15 a 19 anos"),
    ("1144", "20 a 24 anos"),
    ("1145", "25 a 29 anos"),
    ("1146", "30 a 34 anos"),
    ("1147", "35 a 39 anos"),
    ("1148", "40 a 44 anos"),
    ("1149", "45 a 49 anos"),
    ("1150", "50 a 54 anos"),
    ("1151", "55 a 59 anos"),
    ("1152", "60 a 64 anos"),
    ("1153", "65 a 69 anos"),
    ("1154", "70 a 74 anos"),
    ("1155", "75 a 79 anos"),
    ("2503", "80 anos ou mais"),
]

# Sexo (Mortalidade Homicídios/Trânsito) (Tabela 899, Classificação 2)
P8_899_2: List[Tuple[str, str]] = [
    ("6794", "Total"),
    ("4", "Homens"),
    ("5", "Mulheres"),
]

# Tipo de roubo (PNAD Vitimização) (Tabela 8502, Classificação 1351)
P8_8502_1351: List[Tuple[str, str]] = [
    ("57304", "Total"),
    ("57305", "Carro"),
    ("57306", "Moto"),
    ("57307", "Bicicleta"),
    ("57308", "Domicílio"),
    ("57309", "Fora do domicílio"),
]

# Tipo de furto (PNAD Vitimização) (Tabela 8510, Classificação 1353)
P8_8510_1353: List[Tuple[str, str]] = [
    ("57310", "Total"),
    ("57311", "Carro"),
    ("57312", "Moto"),
    ("57313", "Bicicleta"),
    ("57314", "Domicílio"),
    ("57315", "Fora do domicílio"),
]

# Existência de dispositivo de segurança (PNAD) (Tabela 8689, Classificação 1371)
P8_8689_1371: List[Tuple[str, str]] = [
    ("57492", "Total"),
    ("57493", "Existia"),
    ("57494", "Não existia"),
]

# Tipo de dispositivo de segurança (PNAD) (Tabela 8690, Classificação 1373)
P8_8690_1373: List[Tuple[str, str]] = [
    ("57496", "Funcionário contratado para vigilância"),
    ("57497", "Alarme ou câmera de vídeo"),
    ("57498", "Muro ou grade altos, cacos de vidro ou arame farpado"),
    ("57499", "Cerca elétrica"),
    ("57500", "Trava, tranca, fechadura reforçada ou grade (porta, janela ou portão)"),
    ("57501", "Cachorro ou outro animal para proteger o domicílio"),
    ("57502", "Arma de fogo"),
    ("57503", "Outro"),
]

# Caracterização do órgão gestor de segurança (MUNIC) (Tabela 9982, Classificação 1048)
P8_9982_1048: List[Tuple[str, str]] = [
    ("49367", "Total"),
    ("49369", "Secretaria municipal exclusiva"),
    ("49370", "Secretaria municipal em conjunto com outras políticas"),
    ("49371", "Setor subordinado a outra secretaria"),
    ("49372", "Setor subordinado diretamente à chefia do Executivo"),
    ("49373", "Órgão da administração indireta"),
    ("15483", "Câmara Intersetorial de Segurança Alimentar e Nutricional"),
]

# Existência de Plano Municipal de Segurança (MUNIC) (Tabela 9985, Classificação 1329)
P8_9985_1329: List[Tuple[str, str]] = [
    ("57146", "Total"),
    ("15608", "Com Plano Municipal de Segurança Alimentar e Nutricional"),
    ("15609", "Sem Plano Municipal de Segurança Alimentar e Nutricional"),
    ("15675", "Sem informação na área de segurança alimentar"),
    ("15676", "Com Plano Municipal de Política para Mulheres"),
    ("15677", "Sem Plano Municipal de Política para Mulheres"),
    ("15678", "Sem informação na área de política para mulheres"),
    ("15679", "Com Plano Municipal de Direitos Humanos"),
    ("15680", "Sem Plano Municipal de Direitos Humanos"),
    ("15681", "Sem informação na área de direitos humanos"),
    ("15682", "Com Plano Municipal de Segurança Pública"),
    ("15683", "Sem Plano Municipal de Segurança Pública"),
    ("15684", "Sem informação na área de segurança pública"),
    ("15685", "Com Plano Municipal para a Primeira Infância"),
    ("15686", "Sem Plano Municipal para a Primeira Infância"),
    ("15687", "Sem informação na área de primeira infância"),
]

# Existência de Conselho Municipal de Segurança (MUNIC) (Tabela 9987, Classificação 1328)
P8_9987_1328: List[Tuple[str, str]] = [
    ("57131", "Total"),
    ("77667", "Com Conselho Municipal de Assistência Social"),
    ("77668", "Sem Conselho Municipal de Assistência Social"),
    ("77669", "Sem informação sobre Conselho Municipal de Assistência Social"),
    ("77670", "Com Conselho Municipal de Segurança Alimentar e Nutricional"),
    ("77671", "Sem Conselho Municipal de Segurança Alimentar e Nutricional"),
    ("77672", "Sem informação sobre Conselho Municipal de Segurança Alimentar e Nutricional"),
    ("77673", "Com Conselho Municipal de Direitos da Mulher"),
    ("77674", "Sem Conselho Municipal de Direitos da Mulher"),
    ("77675", "Sem informação sobre Conselho Municipal de Direitos da Mulher"),
    ("77676", "Com Conselho Municipal de Segurança Pública"),
    ("77677", "Sem Conselho Municipal de Segurança Pública"),
    ("77678", "Sem informação sobre Conselho Municipal de Segurança Pública"),
    ("77679", "Com Conselho Comunitário de Segurança"),
    ("77680", "Sem Conselho Comunitário de Segurança"),
    ("77681", "Sem informação sobre Conselho Comunitário de Segurança"),
    ("77682", "Com Conselho Municipal de Direitos Humanos"),
    ("77683", "Sem Conselho Municipal de Direitos Humanos"),
    ("77684", "Sem informação sobre Conselho Municipal de Direitos Humanos"),
    ("77685", "Com Conselho Municipal de Direitos da Criança e do Adolescente"),
    ("77686", "Sem Conselho Municipal de Direitos da Criança e do Adolescente"),
    ("77687", "Sem informação sobre Conselho Municipal de Direitos da Criança e do Adolescente"),
    ("77688", "Com Conselho Municipal de Direitos da Pessoa Idosa"),
    ("77689", "Sem Conselho Municipal de Direitos da Pessoa Idosa"),
    ("77690", "Sem informação sobre Conselho Municipal de Direitos da Pessoa Idosa"),
    ("77691", "Com Conselho Municipal de Direitos da Pessoa com Deficiência"),
    ("77692", "Sem Conselho Municipal de Direitos da Pessoa com Deficiência"),
    ("77693", "Sem informação sobre Conselho Municipal de Direitos da Pessoa com Deficiência"),
    ("77694", "Com Conselho Municipal de Direitos de Lésbicas, Gays, Bissexuais, Travestis e Transexuais"),
    ("77695", "Sem Conselho Municipal de Direitos de Lésbicas, Gays, Bissexuais, Travestis e Transexuais"),
    ("77696", "Sem informação sobre Conselho Municipal de Direitos de Lésbicas, Gays, Bissexuais, Travestis e Transexuais"),
    ("77697", "Com Conselho Municipal de Igualdade Racial"),
    ("77698", "Sem Conselho Municipal de Igualdade Racial"),
    ("77699", "Sem informação sobre Conselho Municipal de Igualdade Racial"),
    ("77700", "Com Conselho Municipal dos Povos e Comunidades Tradicionais"),
    ("77701", "Sem Conselho Municipal dos Povos e Comunidades Tradicionais"),
    ("77702", "Sem informação sobre Conselho Municipal dos Povos e Comunidades Tradicionais"),
]

# Existência de Fundo Municipal de Segurança (MUNIC) (Tabela 9991, Classificação 1331)
P8_9991_1331: List[Tuple[str, str]] = [
    ("57153", "Total"),
    ("77624", "Com Fundo Municipal de Assistência Social"),
    ("77625", "Sem Fundo Municipal de Assistência Social"),
    ("77626", "Sem informação sobre Fundo Municipal de Assistência Social"),
    ("77631", "Com Fundo Municipal de Segurança Pública"),
    ("77632", "Sem Fundo Municipal de Segurança Pública"),
    ("77633", "Sem informação sobre Fundo Municipal de Segurança Pública"),
    ("77634", "Com Fundo Municipal de Direitos Humanos"),
    ("77635", "Sem Fundo Municipal de Direitos Humanos"),
    ("77636", "Sem informação sobre Fundo Municipal de Direitos Humanos"),
    ("77637", "Com Fundo Municipal de Direitos da Criança e do Adolescente"),
    ("77638", "Sem Fundo Municipal de Direitos da Criança e do Adolescente"),
    ("77639", "Sem informação sobre Fundo Municipal de Direitos da Criança e do Adolescente"),
    ("77640", "Com Fundo Municipal de Direitos do Idoso"),
    ("77653", "Sem Fundo Municipal de Direitos do Idoso"),
    ("77654", "Sem informação sobre Fundo Municipal de Direitos do Idoso"),
    ("77655", "Com Fundo Municipal de Direitos da Pessoa com Deficiência"),
    ("77656", "Sem Fundo Municipal de Direitos da Pessoa com Deficiência"),
    ("77657", "Sem informação sobre Fundo Municipal de Direitos da Pessoa com Deficiência"),
    ("77664", "Com Fundo Municipal de Promoção da Igualdade Racial"),
    ("77665", "Sem Fundo Municipal de Promoção da Igualdade Racial"),
    ("77666", "Sem informação sobre Fundo Municipal de Promoção da Igualdade Racial"),
]

# Instituições de apoio à segurança (MUNIC) (Tabela 10027, Classificação 2010)
P8_10027_2010: List[Tuple[str, str]] = [
    ("73548", "Total"),
    ("73549", "Com Instituto Médico Legal"),
    ("77722", "Sem Instituto Médico Legal"),
    ("73550", "Com município como sede de comarca"),
    ("77723", "Sem município como sede de comarca"),
    ("73551", "Com unidade do Corpo de Bombeiros"),
    ("77724", "Sem unidade do Corpo de Bombeiros"),
    ("73552", "Com Guarda Municipal"),
    ("77725", "Sem Guarda Municipal"),
]

# Delegacias especializadas no município (MUNIC) (Tabela 10026, Classificação 2009)
P8_10026_2009: List[Tuple[str, str]] = [
    ("73535", "Total"),
    ("73536", "Delegacia de Polícia Civil"),
    ("73537", "Delegacia de Homicídios"),
    ("73538", "Delegacia de Proteção à Pessoa Idosa"),
    ("73539", "Delegacia de Proteção à Criança e ao Adolescente (DPCA)"),
    ("73540", "Delegacia da Criança e do Adolescente (especialidades não separadas)"),
    ("73541", "Delegacia de Proteção ao Meio Ambiente"),
    ("73542", "Delegacia de Polícia Especializada no Atendimento à Mulher"),
    ("73543", "Delegacia da Criança e do Adolescente (DCA)"),
    ("73544", "Delegacia Especializada em Pessoas Desaparecidas"),
    ("73545", "Delegacia de Repressão aos Crimes de Informática"),
    ("73546", "Nenhuma das citadas"),
    ("73547", "Não informado"),
]

# Utilização de armas pela Guarda Municipal (MUNIC) (Tabela 10030, Classificação 2016)
P8_10030_2016: List[Tuple[str, str]] = [
    ("73604", "Total"),
    ("73605", "Apenas arma de fogo"),
    ("73606", "Apenas armas não letais"),
    ("73607", "Armas de fogo e não letais"),
    ("73608", "Nenhum tipo de arma"),
]

# Utilização de veículos pela Guarda Municipal (MUNIC) (Tabela 10031, Classificação 2023)
P8_10031_2023: List[Tuple[str, str]] = [
    ("73655", "Total"),
    ("73656", "Automóvel"),
    ("73657", "Motocicleta"),
    ("73658", "Bicicleta"),
    ("73659", "Cavalo"),
    ("73660", "Barco"),
    ("73661", "Outros"),
    ("73662", "Não utiliza nenhum meio de transporte"),
    ("73663", "Não informado"),
]

# Casas-abrigo para mulheres em situação de violência (MUNIC) (Tabela 10021, Classificação 1999)
P8_10021_1999: List[Tuple[str, str]] = [
    ("73130", "Total"),
    ("73131", "Sim"),
    ("73132", "Não"),
    ("73133", "Não informado"),
]

# Serviços especializados de violência contra mulher (MUNIC) (Tabela 10023, Classificação 2006)
P8_10023_2006: List[Tuple[str, str]] = [
    ("73167", "Total"),
    ("73168", "Centros de Referência/Especializados ou Núcleos Integrados de Atendimento às Mulheres em Situação de Violência"),
    ("73169", "Serviços Especializados de Atendimento à Violência Sexual"),
    ("73170", "Centro Integrado de Serviços de Atendimento a Mulheres em Situação de Violência"),
    ("73171", "Unidades Móveis de Atendimento à Mulher"),
    ("73516", "Casas de Acolhimento de Curta Duração (Casa de Passagem)"),
]

# Órgão ao qual o conselho é vinculado administrativamente (MUNIC) (Tabela 10020, Classificação 1969)
P8_10020_1969: List[Tuple[str, str]] = [
    ("73064", "Total"),
    ("73065", "Ao órgão gestor de política para mulheres"),
    ("73066", "Ao órgão gestor da assistência social"),
    ("73067", "Ao órgão gestor dos direitos humanos"),
    ("73068", "A outro órgão"),
]

# Ações de direitos humanos para grupos específicos (MUNIC) (Tabela 10032, Classificação 2024)
P8_10032_2024: List[Tuple[str, str]] = [
    ("73664", "Total"),
    ("73665", "Ciganos"),
    ("73666", "Crianças e Adolescentes"),
    ("73667", "Mulheres"),
    ("73668", "Pessoas idosas"),
    ("73669", "Pessoa com deficiência"),
    ("73670", "Lésbicas, Gays, Bissexuais, Travestis e Transexuais"),
    ("73671", "População em situação de rua"),
    ("73672", "População negra"),
    ("73673", "Povos indígenas"),
    ("73674", "Comunidades quilombolas"),
    ("73675", "Povos de terreiro/matriz africana"),
    ("73676", "Outros povos e comunidades tradicionais"),
    ("73677", "Não executa"),
    ("73678", "Não informado"),
]

# Ações de enfrentamento à violência contra idoso (MUNIC) (Tabela 10040, Classificação 2053)
P8_10040_2053: List[Tuple[str, str]] = [
    ("74019", "Total"),
    ("74020", "Enfrentamento à violência"),
    ("74021", "Vacinação contra a gripe e a pneumonia"),
    ("74022", "Promoção da saúde e do cuidado de si"),
    ("74023", "Promoção da acessibilidade ou isenção de tarifas no transporte público"),
    ("74024", "Promoção à participação e integração na comunidade"),
    ("74025", "Capacitação de cuidador"),
    ("74026", "Acesso à recreação, ao lazer e aos bens culturais"),
    ("74027", "Garantia de alimentação adequada"),
    ("74080", "Nenhuma das ações ou medidas citadas"),
    ("74081", "Não informado"),
]

PHASE8_STATIC_CATEGORIES: Dict[str, List[Tuple[str, str]]] = {
    "P8_7875_2": P8_7875_2,
    "P8_7877_58": P8_7877_58,
    "P8_899_2": P8_899_2,
    "P8_8502_1351": P8_8502_1351,
    "P8_8510_1353": P8_8510_1353,
    "P8_8689_1371": P8_8689_1371,
    "P8_8690_1373": P8_8690_1373,
    "P8_9982_1048": P8_9982_1048,
    "P8_9985_1329": P8_9985_1329,
    "P8_9987_1328": P8_9987_1328,
    "P8_9991_1331": P8_9991_1331,
    "P8_10027_2010": P8_10027_2010,
    "P8_10026_2009": P8_10026_2009,
    "P8_10030_2016": P8_10030_2016,
    "P8_10031_2023": P8_10031_2023,
    "P8_10021_1999": P8_10021_1999,
    "P8_10023_2006": P8_10023_2006,
    "P8_10020_1969": P8_10020_1969,
    "P8_10032_2024": P8_10032_2024,
    "P8_10040_2053": P8_10040_2053,
}
