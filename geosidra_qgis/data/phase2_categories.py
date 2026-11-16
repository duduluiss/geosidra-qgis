# -*- coding: utf-8 -*-
"""
Tabelas de categorias verificadas na API IBGE/SIDRA para a expansão do GeoSIDRA.
"""

from typing import Dict, List, Tuple

LSPA_PRODUTOS_CATEGORIES: List[Tuple[int, str]] = [
    (0, "Total"),
    (39428, "1 Cereais, leguminosas e oleaginosas"),
    (39429, "1.1 Algodão herbáceo"),
    (39430, "1.2 Amendoim (1ª Safra)"),
    (39431, "1.3 Amendoim (2ª Safra)"),
    (39432, "1.4 Arroz"),
    (39433, "1.5 Aveia"),
    (82223, "1.6 Canola"),
    (39434, "1.7 Centeio"),
    (39435, "1.8 Cevada"),
    (39436, "1.9 Feijão (1ª Safra)"),
    (39437, "1.10 Feijão (2ª Safra)"),
    (39438, "1.11 Feijão (3ª Safra)"),
    (82224, "1.12 Gergelim"),
    (39439, "1.13 Girassol"),
    (39440, "1.14 Mamona"),
    (39441, "1.15 Milho (1ª Safra)"),
    (39442, "1.16 Milho (2ª Safra)"),
    (39443, "1.17 Soja"),
    (39444, "1.18 Sorgo"),
    (39445, "1.19 Trigo"),
    (39446, "1.20 Triticale"),
    (39447, "2 Abacaxi"),
    (39448, "3 Alho"),
    (39449, "4 Banana"),
    (39450, "5 Batata - inglesa (1ª Safra)"),
    (39451, "6 Batata - inglesa (2ª Safra)"),
    (39452, "7 Batata - inglesa (3ª Safra)"),
    (39453, "8 Cacau"),
    (40527, "9/10 Café total"),
    (39454, "9 Café arábica"),
    (39455, "10 Café canephora"),
    (39456, "11 Cana-de-açúcar"),
    (39457, "12 Castanha-de-caju"),
    (39458, "13 Cebola"),
    (39459, "14 Coco-da-baía"),
    (39460, "15 Fumo"),
    (39461, "16 Guaraná"),
    (39462, "17 Juta"),
    (39463, "18 Laranja"),
    (39464, "19 Maçã"),
    (39465, "20 Malva"),
    (39467, "21 Mandioca"),
    (39468, "22 Pimenta-do-reino"),
    (39469, "23 Sisal ou agave"),
    (39470, "24 Tomate"),
    (39471, "25 Uva"),
]

CAGRO_TIPO_PROD_CATEGORIES: List[Tuple[int, str]] = [
    (114017, "Total"),
    (111995, "Animal"),
    (111996, "Animal - de grande porte"),
    (111997, "Animal - de médio porte"),
    (111998, "Animal - aves"),
    (116238, "Animal - pequenos animais"),
    (111999, "Vegetal"),
    (112000, "Vegetal - lavouras permanentes"),
    (112001, "Vegetal - lavouras temporárias"),
    (112002, "Vegetal - horticultura"),
    (116239, "Vegetal - floricultura"),
    (112003, "Vegetal - silvicultura"),
    (112004, "Vegetal - extração vegetal"),
]

CAGRO_IRRIG_METODO_CATEGORIES: List[Tuple[int, str]] = [
    (118477, "Total"),
    (45916, "Irrigação localizada - gotejamento"),
    (45917, "Irrigação localizada - microaspersão"),
    (45918, "Irrigação localizada - outros métodos"),
    (45919, "Irrigação por superfície - inundação"),
    (45920, "Irrigação por superfície - sulcos"),
    (45921, "Irrigação por superfície - outros métodos"),
    (45922, "Irrigação por aspersão - autopropelido/carretel enrolador"),
    (45923, "Irrigação por aspersão - pivô central"),
    (45924, "Irrigação por aspersão - aspersão convencional"),
    (45925, "Outros métodos de irrigação - subsuperficial"),
    (45926, "Outros métodos de irrigação - molhação"),
]

CAGRO_ATIVIDADE_CATEGORIES: List[Tuple[int, str]] = [
    (113601, "Total"),
    (111519, "Produção de lavouras temporárias"),
    (111520, "Horticultura e floricultura"),
    (111521, "Produção de lavouras permanentes"),
    (111522, "Produção de sementes e mudas certificadas"),
    (111523, "Pecuária e criação de outros animais"),
    (111524, "Produção florestal - florestas plantadas"),
    (111525, "Produção florestal - florestas nativas"),
    (114349, "Pesca"),
    (111526, "Aquicultura"),
]

CAGRO_AGROTOXICOS_CATEGORIES: List[Tuple[int, str]] = [
    (46556, "Total"),
    (111611, "Utilizou"),
    (111612, "Não utilizou"),
    (46557, "Não utilizou - não usa"),
    (46558, "Não utilizou - usa, mas não precisou utilizar"),
]

CAGRO_TRATORES_CATEGORIES: List[Tuple[int, str]] = [
    (113521, "Total"),
    (113522, "Menos de 100 cv"),
    (113523, "De 100 cv e mais"),
]

CAGRO_ENERGIA_CATEGORIES: List[Tuple[int, str]] = [
    (10969, "Total"),
    (3011, "Tinham"),
    (3018, "Não tinham"),
    (47176, "Não se aplica"),
]

ABATE_BOVINO_CATEGORIES: List[Tuple[int, str]] = [
    (992, "Total"),
    (55, "Bois"),
    (56, "Vacas"),
    (111734, "Novilhos"),
    (111735, "Novilhas"),
    (57, "Vitelos e vitelas"),
]

INSPECAO_SAN_CATEGORIES: List[Tuple[int, str]] = [
    (118225, "Total"),
    (111737, "Federal"),
    (111738, "Estadual"),
    (111739, "Municipal"),
]

OVOS_FINALIDADE_CATEGORIES: List[Tuple[int, str]] = [
    (72208, "Total"),
    (72207, "Consumo"),
    (72206, "Incubação"),
]

PAC_COMERCIO_CATEGORIES: List[Tuple[int, str]] = [
    (90071, "1. Total"),
    (83357, "2. Comércio de veículos automotores e motocicletas"),
    (90077, "3. Comércio por atacado"),
    (7135, "3.1 Representantes e agentes do comércio (exceto de veículos e motocicletas)"),
    (7136, "3.2 Comércio de matérias-primas agrícolas e animais vivos"),
    (83358, "3.3 Comércio especializado em produtos alimentícios, bebidas e fumo"),
    (83359, "3.4 Comércio de produtos de consumo não alimentar"),
    (83360, "3.5 Comércio de equipamentos e produtos de tecnologia de informação e comunicação"),
    (83361, "3.6 Comércio de máquinas, aparelhos e equipamentos (exceto de tecnologia de informação e comunicação)"),
    (83362, "3.7 Comércio de produtos intermediários, resíduos e sucatas"),
    (83363, "3.7.1 Comércio de outros produtos intermediários"),
    (83364, "3.7.2 Comércio de combustíveis e lubrificantes"),
    (83365, "3.8 Comércio atacadista não especializado"),
    (90084, "4. Comércio varejista"),
    (83366, "4.1 Comércio varejista não especializado"),
    (83367, "4.1.1 Comércio em hipermercados e supermercados"),
    (83368, "4.1.2 Outros tipos de comércio não especializado"),
    (83369, "4.2 Comércio de produtos alimentícios, bebidas e fumo"),
    (83370, "4.3 Comércio de combustíveis e lubrificantes"),
    (90088, "4.4 Comércio de outros produtos em lojas especializadas"),
    (83371, "4.5 Comércio de equipamentos de informática e comunicação"),
    (83372, "4.6 Comércio de artigos de vestuário e calçados"),
    (83373, "4.7 Comércio de outros produtos novos e usados"),
]

PAS_SERVICOS_CATEGORIES: List[Tuple[int, str]] = [
    (107071, "Total"),
    (58296, "1. Serviços prestados principalmente às famílias"),
    (106870, "1.1 Serviços de alojamento e alimentação"),
    (9308, "1.2 Atividades culturais, recreativas e esportivas"),
    (106872, "1.3 Serviços pessoais"),
    (106873, "1.4 Atividades de ensino continuado"),
    (106874, "2. Serviços de informação e comunicação"),
    (31399, "3. Serviços profissionais, administrativos e complementares"),
    (106876, "4. Transportes, serviços auxiliares aos transportes e correio"),
    (106877, "4.1 Transporte rodoviário"),
    (106878, "4.2 Outros transportes"),
    (106879, "4.3 Armazenamento e serviços auxiliares aos transportes"),
    (106880, "4.4 Correio e outras atividades de entrega"),
    (9309, "5. Atividades imobiliárias"),
    (106882, "6. Serviços de manutenção e reparação"),
    (106883, "7. Outras atividades de serviços"),
]

FASFIL_CATEGORIES: List[Tuple[int, str]] = [
    (128557, "Total"),
    (128522, "01 Habitação"),
    (128523, "01.0 Habitação"),
    (128524, "02 Saúde"),
    (128525, "02.1 Hospitais"),
    (128526, "02.2 Outros serviços de saúde"),
    (128527, "03 Cultura e recreação"),
    (128528, "03.1 Cultura e arte"),
    (128529, "03.2 Esporte e recreação"),
    (128530, "04 Educação e pesquisa"),
    (128531, "04.1 Educação infantil"),
    (128532, "04.2 Ensino fundamental"),
    (128533, "04.3 Ensino médio"),
    (128534, "04.4 Educação superior"),
    (128535, "04.6 Estudos e pesquisas"),
    (128536, "04.7 Educação profissional"),
    (128537, "04.8 Outras formas de educação/ensino"),
    (128538, "05 Assistência social"),
    (128539, "05.0 Assistência social"),
    (128540, "06 Religião"),
    (128541, "06.0 Religião"),
    (128542, "07 Associações patronais, profissionais e de produtores rurais"),
    (128543, "07.3 Associações empresariais e patronais"),
    (128544, "07.4 Associações profissionais"),
    (128545, "07.5 Associações de produtores rurais"),
    (128546, "08 Meio ambiente e proteção animal"),
    (128547, "08.0 Meio ambiente e proteção animal"),
    (128548, "09 Desenvolvimento e defesa de direitos"),
    (128549, "09.1 Associações de moradores"),
    (128550, "09.2 Centros e associações comunitárias"),
    (128551, "09.3 Desenvolvimento rural"),
    (128552, "09.4 Emprego e treinamento"),
    (128553, "09.5 Defesa de direitos de grupos e minorias"),
    (128554, "09.6 Outras formas de desenvolvimento e defesa de direitos"),
    (128555, "10 Outras instituições privadas sem fins lucrativos"),
    (128556, "10.8 Outras instituições privadas sem fins lucrativos não especificadas anteriormente"),
]

MEI_SECAO_CNAE_CATEGORIES: List[Tuple[int, str]] = [
    (59983, "Total"),
    (48591, "A Agricultura, pecuária, produção florestal, pesca e aquicultura"),
    (48592, "B - E Indústria geral"),
    (48593, "B Indústrias extrativas"),
    (59960, "C Indústrias de transformação"),
    (59961, "D Eletricidade e gás"),
    (59962, "E Água, esgoto, atividades de gestão de resíduos e descontaminação"),
    (59963, "F Construção"),
    (59964, "G Comércio; reparação de veículos automotores e motocicletas"),
    (59965, "H - U Serviços"),
    (59966, "H Transporte, armazenagem e correio"),
    (59967, "I Alojamento e alimentação"),
    (59968, "J - N Informação, comunicação e atividades financeiras, imobiliárias, profissionais e administrativas"),
    (59969, "J Informação e comunicação"),
    (59970, "K Atividades financeiras, de seguros e serviços relacionados"),
    (59971, "L Atividades imobiliárias"),
    (59972, "M Atividades profissionais, científicas e técnicas"),
    (59973, "N Atividades administrativas e serviços complementares"),
    (59974, "O - Q Administração pública, defesa e seguridade social, educação, saúde humana e serviços sociais"),
    (59975, "O Administração pública, defesa e seguridade social"),
    (59976, "P Educação"),
    (59977, "Q Saúde humana e serviços sociais"),
    (59978, "R - U Outros serviços"),
    (59979, "R Artes, cultura, esporte e recreação"),
    (59980, "S Outras atividades de serviços"),
    (59981, "T Serviços domésticos"),
    (59982, "U Organismos internacionais e outras instituições extraterritoriais"),
]

CENSO22_CNAE_CATEGORIES: List[Tuple[int, str]] = [
    (95371, "Total"),
    (12640, "Agricultura, pecuária, produção florestal, pesca e aquicultura"),
    (12641, "Indústrias extrativas"),
    (12642, "Indústrias de transformação"),
    (12643, "Eletricidade e gás"),
    (12644, "Água, esgoto, atividades de gestão de resíduos e descontaminação"),
    (95377, "Construção"),
    (12645, "Comércio; reparação de veículos automotores e motocicletas"),
    (12646, "Transporte, armazenagem e correio"),
    (95379, "Alojamento e alimentação"),
    (12647, "Informação e comunicação"),
    (12648, "Atividades financeiras, de seguros e serviços relacionados"),
    (9205, "Atividades imobiliárias"),
    (12649, "Atividades profissionais, científicas e técnicas"),
    (12650, "Atividades administrativas e serviços complementares"),
    (95383, "Administração pública, defesa e seguridade social"),
    (95384, "Educação"),
    (12651, "Saúde humana e serviços sociais"),
    (12652, "Artes, cultura, esporte e recreação"),
    (12653, "Outras atividades de serviços"),
    (95387, "Serviços domésticos"),
    (99809, "Organismos internacionais e outras instituições extraterritoriais"),
    (99810, "Atividades mal especificadas"),
]

CENSO22_FORCA_CATEGORIES: List[Tuple[int, str]] = [
    (32385, "Total"),
    (32386, "Força de trabalho"),
    (32387, "Força de trabalho - ocupada"),
    (32446, "Força de trabalho - desocupada"),
    (32447, "Fora da força de trabalho"),
]

CENSO22_DESLOCAMENTO_CATEGORIES: List[Tuple[int, str]] = [
    (31609, "Total"),
    (19429, "Até cinco minutos"),
    (79189, "De seis minutos até quinze minutos"),
    (79190, "Mais de quinze minutos até meia hora"),
    (19431, "Mais de meia hora até uma hora"),
    (19432, "Mais de uma hora até duas horas"),
    (79191, "Mais de duas horas até quatro horas"),
    (79192, "Mais de quatro horas"),
]

CENSO22_INSTRUCAO_CATEGORIES: List[Tuple[int, str]] = [
    (120704, "Total"),
    (9493, "Sem instrução e fundamental incompleto"),
    (9494, "Fundamental completo e médio incompleto"),
    (9495, "Médio completo e superior incompleto"),
    (99713, "Superior completo"),
]

CENSO22_IDADE_ESTUDO_CATEGORIES: List[Tuple[int, str]] = [
    (95253, "Total"),
    (14433, "11 a 14 anos"),
    (2792, "15 a 17 anos"),
    (100052, "18 a 24 anos"),
    (2793, "18 a 19 anos"),
    (1144, "20 a 24 anos"),
    (108866, "25 anos ou mais"),
    (100754, "25 a 64 anos"),
    (1145, "25 a 29 anos"),
    (1146, "30 a 34 anos"),
    (1147, "35 a 39 anos"),
    (1148, "40 a 44 anos"),
    (1149, "45 a 49 anos"),
    (1150, "50 a 54 anos"),
    (1151, "55 a 59 anos"),
    (1152, "60 a 64 anos"),
    (6798, "65 anos ou mais"),
    (1153, "65 a 69 anos"),
    (1154, "70 a 74 anos"),
    (1155, "75 a 79 anos"),
    (2503, "80 anos ou mais"),
]

CENSO22_COR_RACA_CATEGORIES: List[Tuple[int, str]] = [
    (95251, "Total"),
    (2776, "Branca"),
    (2777, "Preta"),
    (2778, "Amarela"),
    (2779, "Parda"),
    (2780, "Indígena"),
]

CENSO22_INDIGENA_CATEGORIES: List[Tuple[int, str]] = [
    (60024, "Total"),
    (60025, "Cor ou raça indígena"),
    (60026, "Se considera indígena"),
    (60029, "Não se declarou indígena"),
]

CENSO22_QUILOMBOLA_LOC_CATEGORIES: List[Tuple[int, str]] = [
    (32776, "Total"),
    (60027, "Em territórios quilombolas"),
    (60028, "Fora de territórios quilombolas"),
]

CENSO22_RELIGIAO_CATEGORIES: List[Tuple[int, str]] = [
    (95278, "Total"),
    (95263, "Católica Apostólica Romana"),
    (95277, "Evangélicas"),
    (2826, "Espírita"),
    (2827, "Umbanda e Candomblé"),
    (95274, "Tradições indígenas"),
    (95275, "Outras religiosidades"),
    (2836, "Sem religião"),
    (12890, "Não sabe"),
    (2837, "Sem declaração"),
]

CENSO22_OCUP_DOM_CATEGORIES: List[Tuple[int, str]] = [
    (95826, "Total"),
    (73554, "Próprio de algum morador"),
    (73126, "Próprio de algum morador - já pago, herdado ou ganho"),
    (4343, "Próprio de algum morador - ainda pagando"),
    (1055, "Alugado"),
    (73553, "Cedido ou emprestado"),
    (73127, "Cedido ou emprestado - por empregador"),
    (73128, "Cedido ou emprestado - por familiar"),
    (73129, "Cedido ou emprestado - outra forma"),
    (1058, "Outra condição"),
]

PNSB_AGUA_LIG_CATEGORIES: List[Tuple[int, str]] = [
    (48981, "Total"),
    (48982, "Residencial"),
    (48984, "Comercial"),
    (48985, "Industrial"),
    (48986, "Órgãos públicos"),
    (48987, "Outro(s)"),
]

PNSB_ESGOTO_LIG_CATEGORIES: List[Tuple[int, str]] = [
    (48981, "Total"),
    (48982, "Residencial"),
]

MUNIC_PLANO_DIRETOR_CATEGORIES: List[Tuple[int, str]] = [
    (58278, "Total"),
    (58279, "Com Plano Diretor"),
    (58280, "O plano foi revisto"),
    (58281, "O plano não foi revisto"),
    (58282, "Sem Plano Diretor"),
    (58283, "Está elaborando o Plano Diretor"),
    (58284, "Não está elaborando o Plano Diretor"),
]

MUNIC_ALAGAMENTO_CATEGORIES: List[Tuple[int, str]] = [
    (50805, "Total"),
    (50806, "Atingidos por alagamentos nos últimos 4 anos"),
    (50807, "Não atingidos por alagamentos nos últimos 4 anos"),
    (57257, "Sem informação"),
]

MUNIC_AAF_PROG_CATEGORIES: List[Tuple[int, str]] = [
    (79300, "Total"),
    (79301, "Programa Nacional de Alimentação Escolar (PNAE)"),
    (79302, "Programa de Aquisição de Alimentos (PAA)"),
    (79303, "Programas estaduais"),
    (79304, "Programas próprios"),
    (79305, "Não informado"),
]

RC_IDADE_MAE_CATEGORIES: List[Tuple[int, str]] = [
    (0, "Total"),
    (5370, "Menos de 15 anos"),
    (5414, "15 a 19 anos"),
    (5371, "15 anos"),
    (5372, "16 anos"),
    (5373, "17 anos"),
    (5374, "18 anos"),
    (5375, "19 anos"),
    (5376, "20 a 24 anos"),
    (5377, "20 anos"),
    (5378, "21 anos"),
    (5379, "22 anos"),
    (5380, "23 anos"),
    (5381, "24 anos"),
    (5382, "25 a 29 anos"),
    (5383, "25 anos"),
    (5384, "26 anos"),
    (5385, "27 anos"),
    (5386, "28 anos"),
    (5387, "29 anos"),
    (5388, "30 a 34 anos"),
    (5389, "30 anos"),
    (5390, "31 anos"),
    (5391, "32 anos"),
    (5392, "33 anos"),
    (5393, "34 anos"),
    (5394, "35 a 39 anos"),
    (5395, "35 anos"),
    (5396, "36 anos"),
    (5397, "37 anos"),
    (5398, "38 anos"),
    (5399, "39 anos"),
    (5400, "40 a 44 anos"),
    (5401, "40 anos"),
    (5402, "41 anos"),
    (5403, "42 anos"),
    (5404, "43 anos"),
    (5405, "44 anos"),
    (5406, "45 a 49 anos"),
    (5407, "45 anos"),
    (5408, "46 anos"),
    (5409, "47 anos"),
    (5410, "48 anos"),
    (5411, "49 anos"),
    (5412, "50 anos ou mais"),
    (5413, "Ignorada"),
]

RC_OBITO_NAT_CATEGORIES: List[Tuple[int, str]] = [
    (0, "Total"),
    (26877, "Natural"),
    (99818, "Não natural"),
    (26881, "Outra"),
    (26882, "Ignorado"),
]

RC_ESTADO_CIVIL_CATEGORIES: List[Tuple[int, str]] = [
    (0, "Total"),
    (32960, "Solteiro"),
    (32961, "Viúvo"),
    (32962, "Divorciado"),
    (32963, "Sem declaração"),
]

PHASE2_STATIC_CATEGORIES: Dict[str, List[Tuple[int, str]]] = {
    "LSPA_PRODUTOS_CATEGORIES": LSPA_PRODUTOS_CATEGORIES,
    "CAGRO_TIPO_PROD_CATEGORIES": CAGRO_TIPO_PROD_CATEGORIES,
    "CAGRO_IRRIG_METODO_CATEGORIES": CAGRO_IRRIG_METODO_CATEGORIES,
    "CAGRO_ATIVIDADE_CATEGORIES": CAGRO_ATIVIDADE_CATEGORIES,
    "CAGRO_AGROTOXICOS_CATEGORIES": CAGRO_AGROTOXICOS_CATEGORIES,
    "CAGRO_TRATORES_CATEGORIES": CAGRO_TRATORES_CATEGORIES,
    "CAGRO_ENERGIA_CATEGORIES": CAGRO_ENERGIA_CATEGORIES,
    "ABATE_BOVINO_CATEGORIES": ABATE_BOVINO_CATEGORIES,
    "INSPECAO_SAN_CATEGORIES": INSPECAO_SAN_CATEGORIES,
    "OVOS_FINALIDADE_CATEGORIES": OVOS_FINALIDADE_CATEGORIES,
    "PAC_COMERCIO_CATEGORIES": PAC_COMERCIO_CATEGORIES,
    "PAS_SERVICOS_CATEGORIES": PAS_SERVICOS_CATEGORIES,
    "FASFIL_CATEGORIES": FASFIL_CATEGORIES,
    "MEI_SECAO_CNAE_CATEGORIES": MEI_SECAO_CNAE_CATEGORIES,
    "CENSO22_CNAE_CATEGORIES": CENSO22_CNAE_CATEGORIES,
    "CENSO22_FORCA_CATEGORIES": CENSO22_FORCA_CATEGORIES,
    "CENSO22_DESLOCAMENTO_CATEGORIES": CENSO22_DESLOCAMENTO_CATEGORIES,
    "CENSO22_INSTRUCAO_CATEGORIES": CENSO22_INSTRUCAO_CATEGORIES,
    "CENSO22_IDADE_ESTUDO_CATEGORIES": CENSO22_IDADE_ESTUDO_CATEGORIES,
    "CENSO22_COR_RACA_CATEGORIES": CENSO22_COR_RACA_CATEGORIES,
    "CENSO22_INDIGENA_CATEGORIES": CENSO22_INDIGENA_CATEGORIES,
    "CENSO22_QUILOMBOLA_LOC_CATEGORIES": CENSO22_QUILOMBOLA_LOC_CATEGORIES,
    "CENSO22_RELIGIAO_CATEGORIES": CENSO22_RELIGIAO_CATEGORIES,
    "CENSO22_OCUP_DOM_CATEGORIES": CENSO22_OCUP_DOM_CATEGORIES,
    "PNSB_AGUA_LIG_CATEGORIES": PNSB_AGUA_LIG_CATEGORIES,
    "PNSB_ESGOTO_LIG_CATEGORIES": PNSB_ESGOTO_LIG_CATEGORIES,
    "MUNIC_PLANO_DIRETOR_CATEGORIES": MUNIC_PLANO_DIRETOR_CATEGORIES,
    "MUNIC_ALAGAMENTO_CATEGORIES": MUNIC_ALAGAMENTO_CATEGORIES,
    "MUNIC_AAF_PROG_CATEGORIES": MUNIC_AAF_PROG_CATEGORIES,
    "RC_IDADE_MAE_CATEGORIES": RC_IDADE_MAE_CATEGORIES,
    "RC_OBITO_NAT_CATEGORIES": RC_OBITO_NAT_CATEGORIES,
    "RC_ESTADO_CIVIL_CATEGORIES": RC_ESTADO_CIVIL_CATEGORIES,
}
