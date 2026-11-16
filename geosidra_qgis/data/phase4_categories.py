# -*- coding: utf-8 -*-
"""
Categorias estáticas curadas da Fase 4 de expansão do catálogo GeoSIDRA.
Extraídas diretamente dos metadados oficiais da API SIDRA/IBGE v3:
POF 2017-2018, PNAD Contínua Anual, Censo 2022 Complementar, MUNIC e PNS.
"""

from typing import Dict, List, Tuple

# T6715 c12190: Tipos de despesa (93 itens)
P4_6715_12190: List[Tuple[int, str]] = [
    (103536, '1 Despesa total'),
    (103537, '2 Despesas correntes'),
    (103538, '2.1 Despesas de consumo'),
    (103539, '2.1.1 Alimentação'),
    (103540, '2.1.2 Habitação'),
    (103541, '2.1.2.1 Aluguel'),
    (8007, '2.1.2.1.1 Aluguel monetário'),
    (8008, '2.1.2.1.2 Aluguel não-monetário'),
    (8009, '2.1.2.2 Condomínio'),
    (8017, '2.1.2.3 Serviços e taxas'),
    (8018, '2.1.2.3.1 Energia elétrica'),
    (8019, '2.1.2.3.2 Telefone fixo'),
    (8020, '2.1.2.3.3 Telefone celular'),
    (8021, '2.1.2.3.4 Pacote de telefone, TV e internet'),
    (8022, '2.1.2.3.5 Gás doméstico'),
    (8010, '2.1.2.3.6 Água e esgoto'),
    (8023, '2.1.2.3.7 Outros'),
    (8024, '2.1.2.4 Manutenção do lar'),
    (8025, '2.1.2.5 Artigos de limpeza'),
    (8026, '2.1.2.6 Mobiliários e artigos do lar'),
    (111442, '2.1.2.7 Eletrodomésticos'),
    (8027, '2.1.2.8 Consertos de artigos do lar'),
    (103554, '2.1.3 Vestuário'),
    (103555, '2.1.3.1 Roupa de homem'),
    (103556, '2.1.3.2 Roupa de mulher'),
    (103557, '2.1.3.3 Roupa de criança'),
    (103558, '2.1.3.4 Calçados e apetrechos'),
    (103559, '2.1.3.5 Jóias e bijuterias'),
    (103560, '2.1.3.6 Tecidos e armarinhos'),
    (103561, '2.1.4 Transporte'),
    (103562, '2.1.4.1 Transporte urbano'),
    (103563, '2.1.4.2 Gasolina - veículo próprio'),
    (103564, '2.1.4.3 Álcool - veículo próprio'),
    (8011, '2.1.4.4 Manutenção e acessórios'),
    (103566, '2.1.4.5 Aquisição de veículos'),
    (8012, '2.1.4.6 Viagens esporádicas'),
    (103568, '2.1.4.7 Outras'),
    (103569, '2.1.5 Higiene e cuidados pessoais'),
    (103570, '2.1.5.1 Perfume'),
    (103571, '2.1.5.2 Produtos para cabelo'),
    (103572, '2.1.5.3 Sabonete'),
    (103573, '2.1.5.4 Instrumentos e produtos de uso pessoal'),
    (103574, '2.1.6 Assistência à saude'),
    (103575, '2.1.6.1 Remédios'),
    (103576, '2.1.6.2 Plano/Seguro saúde'),
    (103577, '2.1.6.3 Consulta e tratamento dentário'),
    (103578, '2.1.6.4 Consulta médica'),
    (8013, '2.1.6.5 Tratamento médico e ambulatorial'),
    (103580, '2.1.6.6 Serviços de cirurgia'),
    (103581, '2.1.6.7 Hospitalização'),
    (103582, '2.1.6.8 Exames diversos'),
    (103583, '2.1.6.9 Material de tratamento'),
    (103584, '2.1.6.10 Outras'),
    (103585, '2.1.7 Educação'),
    (103586, '2.1.7.1 Cursos regulares'),
    (103587, '2.1.7.2 Cursos superiores'),
    (8014, '2.1.7.3 Outros cursos e atividades'),
    (103589, '2.1.7.4 Livros didáticos e revistas técnicas'),
    (103590, '2.1.7.5 Artigos escolares'),
    (103591, '2.1.7.6 Outras'),
    (103592, '2.1.8 Recreação e cultura'),
    (103593, '2.1.8.1 Brinquedos e jogos'),
    (103594, '2.1.8.2 Celular e acessórios'),
    (8015, '2.1.8.3 Periódicos, livros e revistas não-didáticas'),
    (8016, '2.1.8.4 Recreações e esportes'),
    (103597, '2.1.8.5 Outras'),
    (103598, '2.1.9 Fumo'),
    (103599, '2.1.10 Serviços pessoais'),
    (103600, '2.1.10.1 Cabeleireiro'),
    (103601, '2.1.10.2 Manicuro e pedicuro'),
    (103602, '2.1.10.3 Consertos de artigos pessoais'),
    (103603, '2.1.10.4 Outras'),
    (103604, '2.1.11 Despesas diversas'),
    (103605, '2.1.11.1 Jogos e apostas'),
    (103606, '2.1.11.2 Comunicação'),
    (103607, '2.1.11.3 Cerimônias e festas'),
    (103608, '2.1.11.4 Serviços profissionais'),
    (103609, '2.1.11.5 Imóveis de uso ocasional'),
    (103610, '2.1.11.6 Outras'),
    (103611, '2.2 Outras despesas correntes'),
    (103612, '2.2.1 Impostos'),
    (103613, '2.2.2 Contribuições trabalhistas'),
    (103614, '2.2.3 Serviços bancários'),
    (103615, '2.2.4 Pensões, mesadas e doações'),
    (103616, '2.2.5 Previdência privada'),
    (103617, '2.2.6 Outras'),
    (103618, '2.3 Aumento do ativo'),
    (103619, '2.3.1 Imóvel (aquisição)'),
    (103620, '2.3.2 Imóvel (reforma)'),
    (103621, '2.3.3 Outros investimentos'),
    (103622, '2.4 Diminuição do passivo'),
    (103623, '2.4.1 Empréstimo e carnê'),
    (103624, '2.4.2 Prestação de imóvel'),
]

# T6974 c4908: Origem dos rendimentos (17 itens)
P4_6974_4908: List[Tuple[int, str]] = [
    (8049, 'Rendimento total e variação patrimonial'),
    (103423, 'Rendimento total'),
    (103424, 'Rendimento do trabalho'),
    (103425, 'Rendimento do trabalho - empregado'),
    (103426, 'Rendimento do trabalho - empregador'),
    (103427, 'Rendimento do trabalho - conta própria'),
    (103428, 'Transferência'),
    (8050, 'Transferência - aposentadoria, pensão do INSS'),
    (103429, 'Transferência - aposentadoria, pensão da previdência pública'),
    (103430, 'Transferência - aposentadoria, pensão da previdência privada'),
    (8051, 'Transferência - programas sociais federais'),
    (103432, 'Transferência - pensão alimentícia, mesada ou doação'),
    (8052, 'Transferência - outras transferências'),
    (103434, 'Rendimento de aluguel'),
    (8053, 'Outras rendas'),
    (103442, 'Rendimento não monetário'),
    (8054, 'Variação do ativo'),
]

# T10332 c2088: Meio de transporte em que passa mais tempo para chegar ao local de trabalho (15 itens)
P4_10332_2088: List[Tuple[int, str]] = [
    (79488, 'Total'),
    (79193, 'A pé'),
    (79194, 'Bicicleta'),
    (79195, 'Motocicleta'),
    (79196, 'Mototáxi'),
    (79197, 'Automóvel'),
    (79198, 'Táxi ou assemelhados'),
    (79207, 'Van, perua ou assemelhados'),
    (79208, 'Ônibus'),
    (79209, 'BRT ou ônibus de trânsito rápido'),
    (79210, 'Trem ou metrô'),
    (79211, 'Caminhonete ou caminhão adaptado (pau de arara)'),
    (79212, 'Embarcação de médio e grande porte (acima de 20 pessoas)'),
    (79213, 'Embarcação de pequeno porte (até 20 pessoas)'),
    (79214, 'Outros'),
]

# T9552 c12404: Situação de segurança alimentar existente no domicílio (6 itens)
P4_9552_12404: List[Tuple[int, str]] = [
    (109106, 'Total'),
    (109098, 'Com segurança alimentar'),
    (109099, 'Com insegurança alimentar'),
    (109100, 'Com insegurança alimentar leve'),
    (109101, 'Com insegurança alimentar moderada'),
    (109102, 'Com insegurança alimentar grave'),
]

# T7334 c58: Grupo de idade (9 itens)
P4_7334_58: List[Tuple[int, str]] = [
    (95253, 'Total'),
    (118282, '10 a 13 anos'),
    (104869, '14 a 19 anos'),
    (1144, '20 a 24 anos'),
    (1145, '25 a 29 anos'),
    (3299, '30 a 39 anos'),
    (3300, '40 a 49 anos'),
    (3301, '50 a 59 anos'),
    (3302, '60 anos ou mais'),
]

# T7113 c58: Grupo de idade (5 itens)
P4_7113_58: List[Tuple[int, str]] = [
    (2795, '15 anos ou mais'),
    (100452, '18 anos ou mais'),
    (108866, '25 anos ou mais'),
    (109012, '40 anos ou mais'),
    (3302, '60 anos ou mais'),
]

# T7138 c58: Grupo de idade (8 itens)
P4_7138_58: List[Tuple[int, str]] = [
    (95253, 'Total'),
    (41126, '0 a 5 anos'),
    (99749, '0 a 3 anos'),
    (47813, '4 a 5 anos'),
    (31615, '6 a 14 anos'),
    (2792, '15 a 17 anos'),
    (100052, '18 a 24 anos'),
    (108866, '25 anos ou mais'),
]

# T10160 c58: Grupo de idade (17 itens)
P4_10160_58: List[Tuple[int, str]] = [
    (95253, 'Total'),
    (1141, '5 a 9 anos'),
    (1142, '10 a 14 anos'),
    (1143, '15 a 19 anos'),
    (1144, '20 a 24 anos'),
    (1145, '25 a 29 anos'),
    (1146, '30 a 34 anos'),
    (1147, '35 a 39 anos'),
    (1148, '40 a 44 anos'),
    (1149, '45 a 49 anos'),
    (1150, '50 a 54 anos'),
    (1151, '55 a 59 anos'),
    (1152, '60 a 64 anos'),
    (1153, '65 a 69 anos'),
    (1154, '70 a 74 anos'),
    (1155, '75 a 79 anos'),
    (2503, '80 anos ou mais'),
]

# T10185 c464: Estado conjugal (3 itens)
P4_10185_464: List[Tuple[int, str]] = [
    (50292, 'Total'),
    (12108, 'Viviam em união'),
    (12109, 'Não viviam em união'),
]

# T6731 c825: Principal fonte de abastecimento de água (6 itens)
P4_6731_825: List[Tuple[int, str]] = [
    (47937, 'Total'),
    (46285, 'Rede geral de distribuição'),
    (46286, 'Poço profundo ou artesiano'),
    (46287, 'Poço raso, freático ou cacimba'),
    (46288, 'Fonte ou nascente'),
    (46289, 'Outra'),
]

# T7192 c11558: Tipo de esgotamento sanitário (5 itens)
P4_7192_11558: List[Tuple[int, str]] = [
    (46292, 'Total'),
    (47930, 'Rede geral ou rede pluvial'),
    (47931, 'Fossa séptica ligada à rede'),
    (47936, 'Fossa séptica não ligada à rede'),
    (119522, 'Outro tipo'),
]

# T6736 c67: Destino do lixo (5 itens)
P4_6736_67: List[Tuple[int, str]] = [
    (10972, 'Total'),
    (4661, 'Coletado diretamente por serviço de limpeza'),
    (92864, 'Coletado em caçamba de serviço de limpeza'),
    (1087, 'Queimado (na propriedade)'),
    (1091, 'Outro destino'),
]

# T6737 c827: Fonte de energia elétrica (2 itens)
P4_6737_827: List[Tuple[int, str]] = [
    (46296, 'Rede geral ou fonte alternativa'),
    (46297, 'Rede geral'),
]

# T9998 c1914: Unidades físicas presentes no município, da rede socioassistencial (pública ou privada), para executar os serviços (21 itens)
P4_9998_1914: List[Tuple[int, str]] = [
    (72667, 'Total'),
    (72668, 'Centro de Referência da Assistência Social (CRAS)'),
    (72669, 'Centro de convivência'),
    (72670, 'Centro de Referência Especializado de Assistência Social (CREAS)'),
    (72671, 'Centro de Referência Especializado para População em Situação de Rua'),
    (72672, 'Centro dia'),
    (72673, 'Unidade de atendimento ao adolescente em conflito com a lei'),
    (72674, 'Abrigo institucional ou Casa lar para crianças e adolescentes'),
    (72675, 'Abrigo institucional para pessoas com deficiência'),
    (72676, 'Residência inclusiva'),
    (72677, 'Abrigo institucional ou Casa de passagem para população em situação de rua'),
    (72678, 'República para adultos em processo de saída das ruas'),
    (72679, 'Abrigo institucional ou Casa de passagem para migrantes e/ou refugiados'),
    (72697, 'Abrigo para famílias desabrigadas/ desalojadas vítimas de desastres'),
    (72698, 'Abrigo institucional para mulheres em situação de violência'),
    (72699, 'Abrigo institucional ou Casa lar para idosos'),
    (72700, 'República para jovens egressos de serviço de acolhimento'),
    (72701, 'Centro de múltiplo uso'),
    (72702, 'República para idosos'),
    (72703, 'Unidades exclusivas de cadastramento e/ou revisão cadastral'),
    (72704, 'Nenhuma unidade física'),
]

# T9997 c1903: Existência de concessão de benefícios eventuais (7 itens)
P4_9997_1903: List[Tuple[int, str]] = [
    (72636, 'Total'),
    (72637, 'Sim'),
    (72638, 'Benefício eventual por situação de morte'),
    (72639, 'Benefício eventual por situação de natalidade'),
    (72640, 'Benefício eventual para situação de calamidade pública'),
    (72641, 'Outros benefícios eventuais para famílias em situação de vulnerabilidade temporária'),
    (72642, 'Não'),
]

# T10388 c1510: Situação do Conselho Municipal (4 itens)
P4_10388_1510: List[Tuple[int, str]] = [
    (58782, 'Total'),
    (58783, 'Ativo'),
    (58784, 'Inativo'),
    (58785, 'Foi criado mas não foi instalado'),
]

# T10037 c2041: Quantidade de conselhos tutelares no município (8 itens)
P4_10037_2041: List[Tuple[int, str]] = [
    (73885, 'Total'),
    (73886, '1'),
    (73887, '2'),
    (73888, '3'),
    (73889, '4'),
    (73890, '5'),
    (73907, 'Acima de 5'),
    (73908, 'Não informado'),
]

# T8444 c1087: Existência de transporte coletivo por ônibus intramunicipal (13 itens)
P4_8444_1087: List[Tuple[int, str]] = [
    (50247, 'Total'),
    (50248, 'Com transporte coletivo por ônibus intramunicipal'),
    (50249, 'Com tipo de regulamentação na forma de concessão'),
    (50250, 'Com tipo de regulamentação na forma de concessão concedida através de licitação'),
    (50251, 'Com tipo de regulamentação na forma de concessão concedida sem licitação'),
    (50252, 'Com tipo de regulamentação na forma de permissão'),
    (50253, 'Com tipo de regulamentação na forma de permissão concedida através de licitação'),
    (50254, 'Com tipo de regulamentação na forma de permissão concedida sem licitação'),
    (50255, 'Com tipo de regulamentação na forma de autorização'),
    (50256, 'Com tipo de regulamentação na forma de serviço prestado diretamente pela prefeitura'),
    (50257, 'Não regulamentado'),
    (50258, 'Sem transporte coletivo por ônibus intramunicipal'),
    (56958, 'Municípios sem informação'),
]

# T9703 c1529: Existência de Plano Municipal de Cultura (9 itens)
P4_9703_1529: List[Tuple[int, str]] = [
    (58873, 'Total'),
    (58874, 'Sim, por instrumento legal'),
    (58875, 'Sim, mas não é regulamentado por instrumento legal'),
    (58876, 'Em elaboração'),
    (58877, 'Na fase de discussão com a sociedade'),
    (58878, 'Na fase de tramitação no Poder Executivo'),
    (58879, 'Na fase de tramitação na Câmara Municipal'),
    (58880, 'Aguardando sanção pelo Poder Executivo'),
    (58881, 'Não'),
]

# T9706 c1536: Existência de Fundo Municipal de cultura e saúde (6 itens)
P4_9706_1536: List[Tuple[int, str]] = [
    (58909, 'Com Fundo Municipal de Cultura'),
    (58910, 'Sem Fundo Municipal de Cultura'),
    (58914, 'Sem informação na área da cultura'),
    (58915, 'Com Fundo Municipal de Saúde'),
    (58916, 'Sem Fundo Municipal de Saúde'),
    (58917, 'Sem informação na área de saúde'),
]

# T9710 c1572: Existência de instalações esportivas municipais (9 itens)
P4_9710_1572: List[Tuple[int, str]] = [
    (59321, 'Total'),
    (59322, 'Sim'),
    (59323, 'De 1 a 10'),
    (59324, 'De 11 a 25'),
    (59325, 'De 26 a 50'),
    (59326, 'De 51 a 100'),
    (59327, 'De 101 a 250'),
    (59328, 'Acima de 250'),
    (59329, 'Não'),
]

# T4938 c2: Sexo (3 itens)
P4_PNS_SEXO: List[Tuple[int, str]] = [
    (6794, 'Total'),
    (110095, 'Masculino'),
    (110096, 'Feminino'),
]

# T5249 c1568: Nível de instrução (5 itens)
P4_5249_1568: List[Tuple[int, str]] = [
    (120704, 'Total'),
    (9493, 'Sem instrução e fundamental incompleto'),
    (9494, 'Fundamental completo e médio incompleto'),
    (9495, 'Médio completo e superior incompleto'),
    (99713, 'Superior completo'),
]

PHASE4_STATIC_CATEGORIES: Dict[str, List[Tuple[int, str]]] = {
    "P4_6715_12190": P4_6715_12190,
    "P4_6974_4908": P4_6974_4908,
    "P4_10332_2088": P4_10332_2088,
    "P4_9552_12404": P4_9552_12404,
    "P4_7334_58": P4_7334_58,
    "P4_7113_58": P4_7113_58,
    "P4_7138_58": P4_7138_58,
    "P4_10160_58": P4_10160_58,
    "P4_10185_464": P4_10185_464,
    "P4_6731_825": P4_6731_825,
    "P4_7192_11558": P4_7192_11558,
    "P4_6736_67": P4_6736_67,
    "P4_6737_827": P4_6737_827,
    "P4_9998_1914": P4_9998_1914,
    "P4_9997_1903": P4_9997_1903,
    "P4_10388_1510": P4_10388_1510,
    "P4_10037_2041": P4_10037_2041,
    "P4_8444_1087": P4_8444_1087,
    "P4_9703_1529": P4_9703_1529,
    "P4_9706_1536": P4_9706_1536,
    "P4_9710_1572": P4_9710_1572,
    "P4_PNS_SEXO": P4_PNS_SEXO,
    "P4_5249_1568": P4_5249_1568,
}
