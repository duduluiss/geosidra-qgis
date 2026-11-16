# -*- coding: utf-8 -*-
"""
Categorias estáticas curadas para as pesquisas da Fase 10 (v0.12.0):
Finanças Públicas, Receitas e Despesas Municipais (FINBRA / MUNIC / PIB / ODS).
"""

from typing import Dict, List, Tuple

# MUNIC 2021 T5883 c1674 - Instrumentos Tributários e Urbanísticos Municipais
P10_MUNIC_LEGISLACAO_TRIBUTARIA: List[Tuple[int, str]] = [
    (59788, "Contribuição de melhoria"),
    (59787, "Solo criado ou outorga onerosa do direito de construir"),
    (59789, "Operação urbana consorciada"),
    (59793, "Servidão administrativa"),
    (59790, "Estudo de impacto de vizinhança"),
]

# MUNIC 2021 T7423 c1519 - Responsabilidade pela Ordenação de Despesas da Educação
P10_MUNIC_EDUCACAO_ORDENACAO: List[Tuple[int, str]] = [
    (58827, "Secretário(a) de educação"),
    (58825, "Prefeito(a)"),
    (58828, "Diretor(a) de escola"),
    (58829, "Gestão compartilhada"),
]

# MUNIC 2021 T6480 c1549 - Faixas de Execução Orçamentária da Cultura
P10_MUNIC_CULTURA_EXEC_ORCAMENTO: List[Tuple[int, str]] = [
    (59170, "0% de execução orçamentária"),
    (59171, "Até 10% de execução"),
    (59172, "De 11% a 20% de execução"),
    (59173, "De 21% a 30% de execução"),
    (59174, "De 31% a 40% de execução"),
    (59175, "De 41% a 50% de execução"),
    (59176, "De 51% a 60% de execução"),
    (59177, "De 61% a 70% de execução"),
    (59178, "De 71% a 80% de execução"),
    (59179, "De 81% a 90% de execução"),
    (59180, "Mais de 90% de execução"),
]

# MUNIC 2020 T8486 c1166 - Recursos Financeiros Próprios para Meio Ambiente
P10_MUNIC_MEIO_AMBIENTE_RECURSOS: List[Tuple[int, str]] = [
    (50645, "Com recursos financeiros próprios para meio ambiente"),
    (50646, "Sem recursos financeiros próprios"),
]

# MUNIC 2020 T8438 c1071 - Características do Fundo Municipal e Gestão Financeira
P10_MUNIC_FUNDOS_GESTAO: List[Tuple[int, str]] = [
    (50133, "Com o fundo reunindo todos os recursos orçamentários"),
    (50131, "Conselho municipal como gestor do fundo"),
    (50132, "Conselho gestor próprio"),
]

# MUNIC 2021 T9495 c1510 - Situação do Conselho Municipal de Acompanhamento Social do FUNDEB
P10_MUNIC_FUNDEB_SITUACAO: List[Tuple[int, str]] = [
    (58783, "Ativo"),
    (58784, "Inativo"),
]

PHASE10_STATIC_CATEGORIES: Dict[str, List[Tuple[int, str]]] = {
    "P10_MUNIC_LEGISLACAO_TRIBUTARIA": P10_MUNIC_LEGISLACAO_TRIBUTARIA,
    "P10_MUNIC_EDUCACAO_ORDENACAO": P10_MUNIC_EDUCACAO_ORDENACAO,
    "P10_MUNIC_CULTURA_EXEC_ORCAMENTO": P10_MUNIC_CULTURA_EXEC_ORCAMENTO,
    "P10_MUNIC_MEIO_AMBIENTE_RECURSOS": P10_MUNIC_MEIO_AMBIENTE_RECURSOS,
    "P10_MUNIC_FUNDOS_GESTAO": P10_MUNIC_FUNDOS_GESTAO,
    "P10_MUNIC_FUNDEB_SITUACAO": P10_MUNIC_FUNDEB_SITUACAO,
}
