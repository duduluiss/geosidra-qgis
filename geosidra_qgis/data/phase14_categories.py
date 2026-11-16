# -*- coding: utf-8 -*-
"""
Categorias estáticas curadas da Fase 14 (v0.16.0):
Povos Indígenas e Comunidades Quilombolas em Territórios Oficialmente Delimitados (Censo Demográfico 2022).
"""

from typing import Dict, List, Tuple

PHASE14_STATIC_CATEGORIES: Dict[str, List[Tuple[int, str]]] = {
    # Classificação 2661: Localização do domicílio para Povos Indígenas (Censo 2022)
    "P14_INDIGENA_LOCALIZACAO": [
        (32776, "Total (Dentro e Fora de Terras Indígenas)"),
        (12869, "Em terras indígenas"),
        (12870, "Fora de terras indígenas"),
    ],
    # Classificação 2661: Localização do domicílio para Comunidades Quilombolas (Censo 2022)
    "P14_QUILOMBOLA_LOCALIZACAO": [
        (32776, "Total (Dentro e Fora de Territórios Quilombolas)"),
        (60027, "Em territórios quilombolas oficialmente delimitados"),
        (60028, "Fora de territórios quilombolas"),
    ],
    # Classificação 1714: Quesito de declaração indígena (Censo 2022)
    "P14_DECLARACAO_INDIGENA": [
        (60024, "Total (Todas as formas de declaração indígena)"),
        (60025, "Cor ou raça indígena"),
        (60026, "Se considera indígena (Quesito complementar de pertencimento)"),
        (60029, "Não se declarou indígena"),
    ],
    # Classificação 2: Sexo (Censo 2022)
    "P14_TRADICIONAL_SEXO": [
        (6794, "Total (Ambos os sexos)"),
        (4, "Homens"),
        (5, "Mulheres"),
    ],
    # Classificação 59: Alfabetização de pessoas de 15 anos ou mais (Censo 2022 Quilombola)
    "P14_QUILOMBOLA_ALFABETIZACAO": [
        (93024, "Total (15 anos ou mais de idade)"),
        (1023, "Pessoas alfabetizadas"),
        (1024, "Pessoas não alfabetizadas"),
    ],
    # Classificação 125: Tipo de domicílio (Censo 2022)
    "P14_TIPO_DOMICILIO_TRADICIONAL": [
        (31448, "Total de domicílios particulares permanentes ocupados"),
        (31449, "Casa"),
        (31450, "Casa de vila ou em condomínio"),
        (31451, "Apartamento"),
        (31452, "Habitação em casa de cômodos ou cortiço"),
        (31453, "Habitação indígena sem paredes"),
        (31454, "Estrutura residencial permanente degradada ou inacabada"),
    ],
    # Classificação 301: Principal forma de abastecimento de água (Censo 2022)
    "P14_ABASTECIMENTO_AGUA_TRADICIONAL": [
        (72053, "Total de domicílios"),
        (31471, "Rede geral de distribuição"),
        (72054, "Poço profundo ou artesiano"),
        (72055, "Poço raso, freático ou cacimba"),
        (72088, "Fonte, nascente ou mina"),
        (31472, "Carro-pipa"),
        (72089, "Água da chuva armazenada em cisterna ou reservatório"),
        (72090, "Rios, açudes, córregos, lagos e igarapés"),
        (72091, "Outra forma de abastecimento"),
    ],
    # Classificação 1821: Existência de ligação à rede geral e principal forma de abastecimento de água
    "P14_REDE_E_ABASTECIMENTO_AGUA": [
        (72129, "Total de domicílios"),
        (72144, "Possui ligação à rede geral e a utiliza como forma principal"),
        (72145, "Possui ligação à rede geral, mas utiliza principalmente outra forma"),
        (72146, "Possui ligação à rede geral, mas utiliza principalmente poço profundo"),
        (72147, "Possui ligação à rede geral, mas utiliza principalmente poço raso/cacimba"),
        (72148, "Possui ligação à rede geral, mas utiliza principalmente fonte/mina"),
        (72149, "Possui ligação à rede geral, mas utiliza principalmente carro-pipa"),
        (72150, "Possui ligação à rede geral, mas utiliza principalmente água de chuva"),
        (72151, "Possui ligação à rede geral, mas utiliza rios, açudes ou igarapés"),
        (72152, "Não possui ligação à rede geral - Poço profundo ou artesiano"),
        (72153, "Não possui ligação à rede geral - Poço raso, freático ou cacimba"),
        (72154, "Não possui ligação à rede geral - Fonte, nascente ou mina"),
        (72155, "Não possui ligação à rede geral - Carro-pipa"),
        (72156, "Não possui ligação à rede geral - Água da chuva armazenada"),
        (72157, "Não possui ligação à rede geral - Rios, açudes, córregos ou igarapés"),
        (72158, "Não possui ligação à rede geral - Outra forma"),
    ],
    # Classificação 1817: Existência de canalização de água
    "P14_CANALIZACAO_AGUA": [
        (72125, "Total de domicílios"),
        (72126, "Canalizada até dentro da casa, apartamento ou habitação"),
        (72127, "Canalizada, mas apenas no terreno"),
        (72128, "Sem água canalizada"),
    ],
    # Classificação 11558: Tipo de esgotamento sanitário (Censo 2022)
    "P14_ESGOTAMENTO_SANITARIO_TRADICIONAL": [
        (72109, "Total de domicílios"),
        (72110, "Rede geral, rede pluvial ou fossa ligada à rede"),
        (72111, "Fossa séptica ou fossa filtro não ligada à rede"),
        (72112, "Fossa rudimentar ou buraco"),
        (72113, "Vala a céu aberto"),
        (72114, "Rio, lago, córrego ou mar"),
        (72115, "Outro esgotamento sanitário"),
        (72116, "Não tinham banheiro nem sanitário"),
    ],
    # Classificação 67: Destino do lixo (Censo 2022)
    "P14_DESTINO_LIXO_TRADICIONAL": [
        (10972, "Total de domicílios"),
        (72120, "Coletado no domicílio por serviço de limpeza"),
        (72121, "Depositado em caçamba de serviço de limpeza"),
        (72122, "Queimado na propriedade"),
        (72123, "Enterrado na propriedade"),
        (72124, "Jogado em terreno baldio, encosta ou área pública"),
        (72130, "Outro destino"),
    ],
    # Classificação 458: Existência de banheiro ou sanitário
    "P14_BANHEIROS_USO_EXCLUSIVO": [
        (72092, "Total de domicílios"),
        (72093, "Tinham banheiro de uso exclusivo do domicílio"),
        (72099, "Tinham apenas sanitário ou buraco para dejeções"),
        (72100, "Não tinham banheiro nem sanitário"),
    ],
    # Classificação 287: Grupos de idade decenais curados
    "P14_IDADE_GRUPOS_DECENAIS": [
        (100362, "Total (Todas as idades)"),
        (93070, "0 a 4 anos"),
        (93084, "5 a 9 anos"),
        (93085, "10 a 14 anos"),
        (93086, "15 a 19 anos"),
        (93087, "20 a 24 anos"),
        (93088, "25 a 29 anos"),
        (93089, "30 a 34 anos"),
        (93090, "35 a 39 anos"),
        (93091, "40 a 44 anos"),
        (93092, "45 a 49 anos"),
        (93093, "50 a 54 anos"),
        (93094, "55 a 59 anos"),
        (93095, "60 a 64 anos"),
        (93096, "65 a 69 anos"),
        (93097, "70 a 74 anos"),
        (93098, "75 a 79 anos"),
        (49108, "80 a 84 anos"),
        (49109, "85 a 89 anos"),
        (60040, "90 a 94 anos"),
        (60041, "95 a 99 anos"),
        (6653, "100 anos ou mais de idade"),
    ],
}
