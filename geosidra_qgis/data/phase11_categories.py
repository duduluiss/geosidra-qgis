# -*- coding: utf-8 -*-
"""
Categorias estáticas curadas para as pesquisas da Fase 11 (v0.13.0):
Transporte, Mobilidade Urbana e Frota de Veículos (SENATRAN / MUNIC / ODS).
"""

from typing import Dict, List, Tuple

# MUNIC 2020 T8443 c1086 - Serviços regulares de transporte existentes no município
P11_MUNIC_SERVICOS_TRANSPORTE: List[Tuple[int, str]] = [
    (50238, "Com serviços regulares de transporte"),
    (50201, "Serviços por aplicativo"),
    (50242, "Táxi"),
    (50241, "Mototáxi"),
    (50244, "Van ou micro-ônibus"),
    (50239, "Barco ou transporte hidroviário"),
    (50240, "Metrô"),
    (50243, "Trem"),
    (50245, "Avião"),
    (50246, "Sem os serviços regulares relacionados"),
]

# MUNIC 2020 T8444 c1087 - Tipo de regulamentação do transporte coletivo por ônibus intramunicipal
P11_MUNIC_ONIBUS_REGULAMENTACAO: List[Tuple[int, str]] = [
    (50248, "Com transporte coletivo por ônibus intramunicipal"),
    (50250, "Concessão através de licitação"),
    (50251, "Concessão sem licitação"),
    (50253, "Permissão através de licitação"),
    (50254, "Permissão sem licitação"),
    (50255, "Autorização"),
    (50256, "Operação direta pelo poder público municipal"),
]

# MUNIC 2020 T8445 c1088 - Isenção formal da tarifa do ônibus intramunicipal
P11_MUNIC_ONIBUS_ISENCAO_TARIFA: List[Tuple[int, str]] = [
    (50260, "Com passageiros com isenção formal da tarifa"),
    (50261, "Maiores de 60 ou 65 anos"),
    (50262, "Estudantes da rede pública"),
    (50263, "Estudantes da rede privada"),
    (50265, "Pessoas com deficiência (PCD)"),
    (50268, "Crianças menores de 5 anos"),
    (50267, "Professores"),
    (50266, "Policiais"),
    (50264, "Carteiros"),
    (50270, "Toda a população (Tarifa Zero)"),
    (50271, "Nenhum passageiro com isenção formal"),
]

# MUNIC 2020 T8446 c1090 - Adaptação da frota de ônibus para PCD / acessibilidade
P11_MUNIC_ONIBUS_ADAPTACAO_PCD: List[Tuple[int, str]] = [
    (50273, "Com adaptação da frota para PCD"),
    (50275, "Frota totalmente adaptada para PCD"),
    (50274, "Frota parcialmente adaptada para PCD"),
    (50276, "Frota adaptada com piso baixo"),
]

# MUNIC 2020 T8447 c1091 - Transporte coletivo por ônibus intermunicipal
P11_MUNIC_ONIBUS_INTERMUNICIPAL: List[Tuple[int, str]] = [
    (50282, "Com transporte coletivo por ônibus intermunicipal"),
    (50283, "Atendendo deslocamento entre bairros/distritos municipais"),
    (50284, "Não atendendo deslocamento interno municipal"),
    (50285, "Sem transporte coletivo intermunicipal"),
]

# MUNIC 2020 T8448 c1094 - Infraestrutura cicloviária urbana
P11_MUNIC_CICLOVIAS_BICICLETARIOS: List[Tuple[int, str]] = [
    (50287, "Com ciclovia"),
    (50288, "Com bicicletário público"),
    (50289, "Sem ciclovia ou sem bicicletário público"),
]

# MUNIC 2020 T8453 c1079 - Aspectos e conteúdo do Plano Municipal de Transporte
P11_MUNIC_PLANO_TRANSPORTE_ASPECTOS: List[Tuple[int, str]] = [
    (50192, "Com política de circulação viária e de transportes"),
    (50193, "Com regras de organização do sistema de passageiros"),
    (50194, "Com política tarifária"),
    (50195, "Com normas de utilização do espaço viário público"),
]

# ODS 3.6.1 T4408 c2 - Mortalidade por acidentes de trânsito por sexo
P11_ODS_MORTALIDADE_SEXO: List[Tuple[int, str]] = [
    (6794, "Total (Ambos os sexos)"),
    (4, "Homens"),
    (5, "Mulheres"),
]

PHASE11_STATIC_CATEGORIES: Dict[str, List[Tuple[int, str]]] = {
    "P11_MUNIC_SERVICOS_TRANSPORTE": P11_MUNIC_SERVICOS_TRANSPORTE,
    "P11_MUNIC_ONIBUS_REGULAMENTACAO": P11_MUNIC_ONIBUS_REGULAMENTACAO,
    "P11_MUNIC_ONIBUS_ISENCAO_TARIFA": P11_MUNIC_ONIBUS_ISENCAO_TARIFA,
    "P11_MUNIC_ONIBUS_ADAPTACAO_PCD": P11_MUNIC_ONIBUS_ADAPTACAO_PCD,
    "P11_MUNIC_ONIBUS_INTERMUNICIPAL": P11_MUNIC_ONIBUS_INTERMUNICIPAL,
    "P11_MUNIC_CICLOVIAS_BICICLETARIOS": P11_MUNIC_CICLOVIAS_BICICLETARIOS,
    "P11_MUNIC_PLANO_TRANSPORTE_ASPECTOS": P11_MUNIC_PLANO_TRANSPORTE_ASPECTOS,
    "P11_ODS_MORTALIDADE_SEXO": P11_ODS_MORTALIDADE_SEXO,
}
