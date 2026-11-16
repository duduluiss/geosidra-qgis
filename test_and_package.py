# -*- coding: utf-8 -*-
"""
Script de testes automatizados e empacotamento (.zip) do plugin GeoSIDRA.
Sincroniza automaticamente a pasta de plugins do QGIS 4 ativo quando presente.
"""

import json
import os
import shutil
import sys
import tempfile
import zipfile

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

import geosidra_qgis.core as core_pkg
from geosidra_qgis.core.analytics_engine import AnalyticsEngine, fmt_volume_br
from geosidra_qgis.core.ibge_api import IbgeMalhasClient
from geosidra_qgis.core.municipality_mapper import MunicipalityMapper
from geosidra_qgis.core.report_renderer import export_bundle, export_table_csv
from geosidra_qgis.core.sidra_client import SidraClient
from geosidra_qgis.data.catalog import (
    SURVEY_GROUPS,
    SURVEYS,
    get_cempre_cnae_categories,
    get_ipca_c315_categories,
    get_mei_cnae_categories,
    get_pia_prodlist_categories,
    get_survey_by_id,
    get_survey_categories,
    get_survey_extra_classifications,
    get_survey_supported_levels,
    get_survey_valid_years,
    get_survey_year_label,
    get_variable_info,
    get_variable_slug,
    resolve_table_queries,
)


def test_cross_analyzer_removed():
    cross_path = os.path.join(PROJECT_ROOT, "geosidra_qgis", "core", "cross_analyzer.py")
    assert not os.path.exists(cross_path), f"Arquivo cross_analyzer.py ainda existe: {cross_path}"
    assert "CrossAnalyzer" not in getattr(core_pkg, "__all__", []), "CrossAnalyzer ainda exposto em core.__all__"
    assert not hasattr(AnalyticsEngine, "generate_cross_reports"), "generate_cross_reports ainda existe em AnalyticsEngine"
    print("[OK] Módulo GeoComex/CrossAnalyzer removido completamente do plugin.")


def test_catalog_expansion():
    assert len(SURVEY_GROUPS) == 22, f"Esperado 22 grupos (ALL + 21 áreas), obtido {len(SURVEY_GROUPS)}"
    assert len(SURVEYS) == 404, f"Esperado 404 pesquisas no catálogo, obtido {len(SURVEYS)}"
    assert len({s["id"] for s in SURVEYS}) == len(SURVEYS), "IDs de pesquisa duplicados no catálogo"

    cnae = get_cempre_cnae_categories()
    prodlist = get_pia_prodlist_categories()
    mei_cnae = get_mei_cnae_categories()
    ipca_c315 = get_ipca_c315_categories()
    assert len(cnae) == 1067, f"CEMPRE CNAE 2.0 deveria ter 1067 classes, obteve {len(cnae)}"
    assert len(prodlist) == 3764, f"PIA Prodlist deveria ter 3764 itens, obteve {len(prodlist)}"
    assert len(mei_cnae) == 674, f"MEI CNAE 2.0 deveria ter 674 classes, obteve {len(mei_cnae)}"
    assert len(ipca_c315) == 354, f"IPCA/INPC c315 deveria ter 354 itens, obteve {len(ipca_c315)}"

    for survey in SURVEYS:
        cats = get_survey_categories(survey)
        assert len(cats) >= 1, f"Pesquisa {survey['id']} sem categorias"
        valid_years = get_survey_valid_years(survey)
        assert len(valid_years) >= 1, f"Pesquisa {survey['id']} sem anos válidos"
        assert survey.get("variables"), f"Pesquisa {survey['id']} sem variáveis"
        levels = get_survey_supported_levels(survey)
        assert levels and survey.get("level", "N6") in levels, (
            f"Pesquisa {survey['id']} com nível padrão ausente em supported_levels: {levels}"
        )
        assert "classification" in survey, f"Pesquisa {survey['id']} sem chave classification normalizada"
        assert "extra_classifications" in survey, f"Pesquisa {survey['id']} sem chave extra_classifications normalizada"
        # Garante que a extracao de parametros de consulta de todas as 404 pesquisas nao gere KeyError
        var_id = survey["variables"][0]["id"]
        plans, _ = resolve_table_queries(survey, [valid_years[0]], var_id, category_id=cats[0][0])
        assert plans, f"Pesquisa {survey['id']} falhou na geracao de planos de consulta"

    # Testes de resolução histórica + recente e regras de bloqueio temporal
    cempre_cnae = get_survey_by_id("CEMPRE_CNAE")
    plans, skipped = resolve_table_queries(cempre_cnae, [2021, 2022, 2024, 2026], 706)
    assert [(p["table"], p["years"]) for p in plans] == [(6450, [2021]), (9528, [2022, 2024])], plans
    assert skipped == [2026], f"2026 deveria ser ignorado no CEMPRE, obtido {skipped}"

    pia_emp = get_survey_by_id("PIA_EMPRESA_UF")
    plans_706, skipped_706 = resolve_table_queries(pia_emp, [2023, 2024], 706)
    assert [(p["table"], p["query_var"], p["requested_var"]) for p in plans_706] == [
        (1849, 706, 706),
        (10457, 13816, 706),
    ], plans_706
    assert skipped_706 == [], skipped_706

    plans_2086, skipped_2086 = resolve_table_queries(pia_emp, [2023, 2024], 2086)
    assert [(p["table"], p["years"]) for p in plans_2086] == [(10457, [2024])], plans_2086
    assert skipped_2086 == [2023], skipped_2086

    pop_est = get_survey_by_id("POP_ESTIMADA")
    plans_pop, skipped_pop = resolve_table_queries(pop_est, [2021, 2022, 2023, 2026], 9324)
    assert [(p["table"], p["years"]) for p in plans_pop] == [(6579, [2021, 2026])], plans_pop
    assert skipped_pop == [2022, 2023], skipped_pop
    assert pop_est.get("popup_notice") is True
    assert get_survey_by_id("CENSO_AGRO_TIPOLOGIA").get("popup_notice") is True

    # Testes da Fase 2 + Correção de Lacunas: subanuais (LSPA mensal, PNAD, Abate), séries históricas unificadas, 1974+ e subfiltros
    pam = get_survey_by_id("PAM")
    pam_years = get_survey_valid_years(pam)
    assert min(pam_years) == 1974 and 1980 in pam_years, f"PAM deveria incluir 1974..2025, obtido min={min(pam_years)}"

    pib_mun = get_survey_by_id("PIB_MUN")
    assert min(get_survey_valid_years(pib_mun, variable_id=37)) == 1999
    assert min(get_survey_valid_years(pib_mun, variable_id=6575)) == 2002
    plans_pib, skipped_pib = resolve_table_queries(pib_mun, [2000, 2023], 37)
    assert [(p["table"], p["years"]) for p in plans_pib] == [(21, [2000]), (5938, [2023])] and skipped_pib == []

    pib_gini = get_survey_by_id("PIB_GINI_UF")
    assert min(get_survey_valid_years(pib_gini, variable_id=529)) == 1999
    assert min(get_survey_valid_years(pib_gini, variable_id=6568)) == 2002

    lspa = get_survey_by_id("LSPA_SAFRA_UF")
    assert lspa.get("level") == "N3" and lspa.get("popup_notice") is True
    assert lspa.get("periodicity") == "monthly"
    assert len(get_survey_valid_years(lspa)) == 241
    plans_lspa, skipped_lspa = resolve_table_queries(lspa, [2025, 202603, 202609], 35)
    assert [(p["table"], p["years"]) for p in plans_lspa] == [(6588, ["202512", "202603", "202609"])], plans_lspa
    assert skipped_lspa == [], skipped_lspa
    assert get_survey_year_label(lspa, 2025) == "2025 - Fechamento Anual (Dez/2025)"
    assert get_survey_year_label(lspa, 202609) == "Setembro / 2026 (202609 - Previsão Atual)"

    pnad_des = get_survey_by_id("PNAD_DESOCUPACAO_UF")
    assert pnad_des.get("level") == "N3" and pnad_des.get("popup_notice") is True
    assert pnad_des.get("periodicity") == "quarterly"
    plans_pnad_des, _ = resolve_table_queries(pnad_des, [2025, 202602], 4099)
    assert [(p["table"], p["years"]) for p in plans_pnad_des] == [
        (4099, ["202501", "202502", "202503", "202504", "202602"])
    ], plans_pnad_des
    assert get_survey_year_label(pnad_des, 2025, 4099) == "2025 - Média Anual (1T a 4T)"
    assert get_survey_year_label(pnad_des, 202602, 4099) == "2º Trimestre / 2026 (202602)"

    pnad_rend = get_survey_by_id("PNAD_RENDIMENTO_UF")
    assert pnad_rend.get("level") == "N3" and pnad_rend.get("popup_notice") is True
    plans_pnad_rend, skipped_rend = resolve_table_queries(
        pnad_rend, [2020, 202001, 202002, 2021, 2022, 202204, 202602], 5933
    )
    assert [(p["table"], p["years"]) for p in plans_pnad_rend] == [
        (5436, ["202001", "202204", "202602"])
    ], plans_pnad_rend
    assert skipped_rend == [2020, 2021, 2022, 202002], skipped_rend

    abate_bov = get_survey_by_id("ABATE_BOVINOS_UF")
    assert abate_bov.get("level") == "N3" and abate_bov.get("popup_notice") is True
    assert get_survey_valid_years(abate_bov)[:7] == [202602, 202601, 2025, 202504, 202503, 202502, 202501]
    assert get_survey_year_label(abate_bov, 2025, 284) == "2025 - Total Anual (Soma 1T a 4T)"
    assert get_survey_year_label(abate_bov, 2025, 151) == "2025 - Fechamento Anual (4T / Série 1T-4T)"
    plans_abate, _ = resolve_table_queries(abate_bov, [2025, 202504, 202602], 284)
    assert [(p["table"], p["years"]) for p in plans_abate] == [
        (1092, ["202501", "202502", "202503", "202504", "202602"])
    ], plans_abate

    cagro_vp = get_survey_by_id("CAGRO_VALOR_PROD")
    plans_vp, skipped_vp = resolve_table_queries(cagro_vp, [2017, 2024], 1999)
    assert [(p["table"], p["years"]) for p in plans_vp] == [(6897, [2017])], plans_vp
    assert skipped_vp == [2024], skipped_vp

    pac = get_survey_by_id("PAC_COMERCIO_UF")
    pas = get_survey_by_id("PAS_SERVICOS_UF")
    assert pac.get("level") == "N3" and pas.get("level") == "N3"
    assert min(get_survey_valid_years(pac, variable_id=866)) == 2007 and max(get_survey_valid_years(pac, variable_id=866)) == 2024
    assert get_survey_valid_years(pac, variable_id=310) == [2024]
    plans_pac, skip_pac = resolve_table_queries(pac, [2023, 2024], 310)
    assert [(p["table"], p["years"]) for p in plans_pac] == [(10653, [2024])] and skip_pac == [2023]
    assert min(get_survey_valid_years(pas, variable_id=857)) == 2007 and max(get_survey_valid_years(pas, variable_id=857)) == 2024
    plans_pas, _ = resolve_table_queries(pas, [2023, 2024], 857)
    assert [(p["table"], p["query_var"], p["requested_var"]) for p in plans_pas] == [
        (2715, 673, 857),
        (10762, 857, 857),
    ]

    alfa_specs = get_survey_extra_classifications(get_survey_by_id("CENSO22_ALFABETIZACAO"))
    assert len(alfa_specs) == 2 and any(sp["id"] == 86 for sp in alfa_specs)
    assert get_survey_by_id("MUNIC_COMPRAS_AF").get("default_cat") == 79300

    for mei_id in ("MEI_EMPREGO", "MEI_DINAMICA", "MEI_CNAE"):
        mei_s = get_survey_by_id(mei_id)
        assert mei_s.get("level") == "N3", f"{mei_id} deve usar nível N3 (UF)"
        assert mei_s.get("popup_notice") is True, f"{mei_id} deve exigir popup_notice"
    assert get_variable_info("MEI_DINAMICA", 8894).get("allow_negative") is True

    for munic_id, vid in (("MUNIC_PLANO_DIRETOR", 603), ("MUNIC_ALAGAMENTOS", 603), ("MUNIC_COMPRAS_AF", 13191)):
        ms = get_survey_by_id(munic_id)
        assert ms.get("popup_notice") is True
        assert get_variable_info(munic_id, vid).get("is_binary") is True

    # Testes da Fase 3 (v0.4.0): Semestralidade (Estoques), Conjuntura Mensal, Projeções 2000-2060, PNSB/MUNIC/Divórcios
    estoques = get_survey_by_id("ESTOQUES_ARMAZENADOS")
    assert estoques.get("periodicity") == "semiannual" and estoques.get("popup_notice") is True
    est_years = get_survey_valid_years(estoques)
    assert len(est_years) == 37 and est_years[:3] == [2025, 202501, 2024] and est_years[-1] == 2007
    plans_est, skip_est = resolve_table_queries(estoques, [2007, 202501, 2025], 150)
    assert [(p["table"], p["years"]) for p in plans_est] == [(254, ["200702", "202501", "202502"])] and skip_est == []
    assert get_survey_year_label(estoques, 2025) == "2025 - Fechamento Anual (2º Semestre / 202502)"
    assert get_survey_year_label(estoques, 202501) == "1º Semestre / 2025 (202501)"

    sinapi = get_survey_by_id("SINAPI_SEM_DESONERACAO")
    assert sinapi.get("group") == "CONJUNTURA_MENSAL" and sinapi.get("periodicity") == "monthly"
    plans_sin, _ = resolve_table_queries(sinapi, [2025, 202609], 9327)
    assert [(p["table"], p["years"]) for p in plans_sin] == [(6586, ["202512", "202609"])]

    for sid_warn in ("PIM_PF_IND_UF", "PMC_ATIVIDADES_UF", "PMS_TURISMO_UF", "RC_DIVORCIOS", "PNSB_RESIDUOS_SOLIDOS"):
        sw = get_survey_by_id(sid_warn)
        assert sw.get("popup_notice") is True and sw.get("notice_severity") == "warning", sid_warn

    assert get_survey_valid_years(get_survey_by_id("CENSO22_FECUNDIDADE")) == [2022, 2010]
    assert get_survey_valid_years(get_survey_by_id("PNSB_RESIDUOS_SOLIDOS")) == [2008, 2000]
    assert get_survey_valid_years(get_survey_by_id("PROJECAO_VIDA_MORT_UF")) == [2018]
    assert get_survey_by_id("CENSO22_ENTORNO_URBANISTICO").get("default_cat") == 72246

    # Testes v0.5.0: Níveis N2/N7/N14/N8/N9 e IPCA/INPC/IPCA-15 Regionais (N7_N6)
    ipca = get_survey_by_id("IPCA_REGIONAL")
    inpc = get_survey_by_id("INPC_REGIONAL")
    ipca15 = get_survey_by_id("IPCA15_REGIONAL")
    assert ipca.get("level") == "N7_N6" and inpc.get("level") == "N7_N6" and ipca15.get("level") == "N7_N6"
    plans_ipca, skip_ipca = resolve_table_queries(ipca, [2019, 202609], 63)
    assert [(p["table"], p["years"]) for p in plans_ipca] == [(1419, ["201912"]), (7060, ["202609"])] and skip_ipca == []
    plans_inpc, skip_inpc = resolve_table_queries(inpc, [2019, 202609], 44)
    assert [(p["table"], p["years"]) for p in plans_inpc] == [(1100, ["201912"]), (7063, ["202609"])] and skip_inpc == []
    plans_ipca15, skip_ipca15 = resolve_table_queries(ipca15, [202001, 202002, 202610], 355)
    assert [(p["table"], p["years"]) for p in plans_ipca15] == [
        (1705, ["202001"]),
        (7062, ["202002", "202610"]),
    ] and skip_ipca15 == []

    pnad_lvls = get_survey_supported_levels(get_survey_by_id("PNAD_DESOCUPACAO_UF"))
    assert all(lvl in pnad_lvls for lvl in ("N2", "N3", "N7", "N14", "N7_N14", "N6")), pnad_lvls
    pam_lvls = get_survey_supported_levels(get_survey_by_id("PAM"))
    assert all(lvl in pam_lvls for lvl in ("N2", "N3", "N8", "N9", "N6")), pam_lvls

    # Testes v0.6.0 (Fase 4): PAIC, POF, PNAD Anual, Censo 2022 Complementar, MUNIC Complementar e PNS
    paic = get_survey_by_id("PAIC_CONSTRUCAO_UF")
    plans_paic, skip_paic = resolve_table_queries(paic, [2023, 2024], 1243)
    assert [(p["table"], p["query_var"], p["requested_var"]) for p in plans_paic] == [
        (1761, 1243, 1243),
        (10442, 13807, 1243),
    ] and skip_paic == []

    pof_desp = get_survey_by_id("POF_DESPESAS_FAMILIARES_UF")
    assert len(get_survey_categories(pof_desp)) == 93
    assert any(e["id"] == 339 for e in get_survey_extra_classifications(pof_desp))

    pns_hiper = get_survey_by_id("PNS_HIPERTENSAO")
    assert pns_hiper.get("group") == "SAUDE_PNS" and pns_hiper.get("partial_n6") is True
    assert get_survey_supported_levels(pns_hiper) == ["N3", "N6", "N2"]
    assert any(e["id"] == 1 for e in get_survey_extra_classifications(pns_hiper))

    cras = get_survey_by_id("MUNIC_REDE_SUAS_CRAS")
    assert {e["id"] for e in get_survey_extra_classifications(cras)} >= {1906, 1915, 12446}

    # Fase 5: Meio Ambiente, Clima, Biodiversidade e ODS
    p5_surveys = [s for s in SURVEYS if s.get("group") == "MEIO_AMBIENTE_CLIMA_ODS"]
    assert len(p5_surveys) == 13, f"Esperado 13 pesquisas na área MEIO_AMBIENTE_CLIMA_ODS, obtido {len(p5_surveys)}"

    bio = get_survey_by_id("BIO_CONHECIMENTO_UF_MUN")
    assert get_survey_supported_levels(bio) == ["N6", "N3"]
    assert bio.get("valid_years") == [2022, 2025]

    bio_reg = get_survey_by_id("BIO_REGISTROS_OCORRENCIA")
    assert len(get_survey_categories(bio_reg)) == 10

    polin = get_survey_by_id("POLINIZADORES_VALOR_PRODUCAO")
    assert len(get_survey_categories(polin)) == 4
    assert get_survey_supported_levels(polin) == ["N6", "N3", "N2"]

    ar_mun = get_survey_by_id("ODS_QUALIDADE_AR_CIDADES")
    assert ar_mun.get("partial_n6") is True

    muni_def = get_survey_by_id("MUNIC_DEFESA_CIVIL_ESTRUTURA")
    assert {e["id"] for e in get_survey_extra_classifications(muni_def)} >= {12446, 1244}

    # Fase 6: Infância, Juventude, Educação e Saúde do Escolar (PeNSE)
    p6_surveys = [s for s in SURVEYS if s.get("group") == "INFANCIA_JUVENTUDE_ESCOLAS"]
    assert len(p6_surveys) == 26, f"Esperado 26 pesquisas na área INFANCIA_JUVENTUDE_ESCOLAS, obtido {len(p6_surveys)}"

    creche = get_survey_by_id("CENSO22_CRECHE_PREESCOLA")
    assert get_survey_supported_levels(creche) == ["N6", "N3", "N2"]
    assert len(get_survey_categories(creche)) == 4
    assert any(e["id"] == 58 for e in get_survey_extra_classifications(creche))

    freq_esc = get_survey_by_id("CENSO22_TAXA_FREQ_ESCOLAR")
    assert len(get_survey_categories(freq_esc)) == 32

    munic_creche = get_survey_by_id("MUNIC_AUXILIO_CRECHE")
    assert any(e["id"] == 12446 for e in get_survey_extra_classifications(munic_creche))

    pense_bull = get_survey_by_id("PENSE_BULLYING_SOFRIDO")
    assert pense_bull.get("partial_n6") is True
    assert get_survey_supported_levels(pense_bull) == ["N3", "N6", "N2"]

    pense_bib = get_survey_by_id("PENSE_ESCOLA_BIBLIOTECA")
    assert len(get_survey_categories(pense_bib)) == 3

    ods_escola = get_survey_by_id("ODS_INFRAESTRUTURA_ESCOLAR")
    assert len(get_survey_categories(ods_escola)) == 7
    assert get_survey_supported_levels(ods_escola) == ["N3"]

    # Fase 7: Habitação, Favelas, Condições de Moradia e Entorno Urbano
    p7_surveys = [s for s in SURVEYS if s.get("group") == "HABITACAO_FAVELAS"]
    assert len(p7_surveys) == 29, f"Esperado 29 pesquisas na área HABITACAO_FAVELAS, obtido {len(p7_surveys)}"

    fav_num = get_survey_by_id("FAVELAS_NUMERO_COMUNIDADES")
    assert get_survey_supported_levels(fav_num) == ["N6", "N3", "N2"]

    fav_pop = get_survey_by_id("FAVELAS_POPULACAO_COR_RACA")
    assert len(get_survey_categories(fav_pop)) == 7
    assert any(e["id"] == 2 for e in get_survey_extra_classifications(fav_pop))

    fav_esg = get_survey_by_id("FAVELAS_ESGOTAMENTO_SANITARIO")
    assert len(get_survey_categories(fav_esg)) == 10

    censo_esp = get_survey_by_id("CENSO22_DOMICILIOS_ESPECIE")
    assert len(get_survey_categories(censo_esp)) == 13

    censo_par = get_survey_by_id("CENSO22_PAREDES_EXTERNAS")
    assert len(get_survey_categories(censo_par)) == 8

    censo_ent = get_survey_by_id("CENSO22_ENTORNO_BUEIRO_ILUMINACAO")
    assert censo_ent.get("valid_years") == [2010, 2022]

    munic_hab = get_survey_by_id("MUNIC_PLANO_HABITACAO")
    assert any(e["id"] == 12446 for e in get_survey_extra_classifications(munic_hab))

    # Fase 8: Segurança Pública, Vitimização, Justiça e Defesa Social
    p8_surveys = [s for s in SURVEYS if s.get("group") == "SEGURANCA_DEFESA_SOCIAL"]
    assert len(p8_surveys) == 24, f"Esperado 24 pesquisas na área SEGURANCA_DEFESA_SOCIAL, obtido {len(p8_surveys)}"

    ods_hom = get_survey_by_id("ODS_HOMICIDIOS_TAXA")
    assert get_survey_supported_levels(ods_hom) == ["N3", "N2"]
    assert 2024 in ods_hom.get("valid_years")

    pnad_roubo = get_survey_by_id("PNAD_VITIMAS_ROUBO")
    assert pnad_roubo.get("partial_n6") is True
    assert len(get_survey_categories(pnad_roubo)) == 6

    munic_seg = get_survey_by_id("MUNIC_SEGURANCA_ESTRUTURA")
    assert any(e["id"] == 12446 for e in get_survey_extra_classifications(munic_seg))

    munic_guarda = get_survey_by_id("MUNIC_GUARDA_ARMAMENTO")
    assert len(get_survey_categories(munic_guarda)) == 5

    # Fase 9: Cultura, Patrimônio Histórico, Turismo e Esporte
    p9_surveys = [s for s in SURVEYS if s.get("group") == "CULTURA_TURISMO_ESPORTE"]
    assert len(p9_surveys) == 27, f"Esperado 27 pesquisas na área CULTURA_TURISMO_ESPORTE, obtido {len(p9_surveys)}"

    equip = get_survey_by_id("MUNIC_CULTURA_EQUIPAMENTOS")
    assert get_survey_supported_levels(equip) == ["N6", "N1"]
    assert len(equip["variables"]) == 7

    patr = get_survey_by_id("MUNIC_PATRIMONIO_LEGISLACAO_TOMBAMENTO")
    assert len(get_survey_categories(patr)) == 6

    esporte_inst = get_survey_by_id("MUNIC_ESPORTE_TIPOS_INSTALACOES")
    assert len(get_survey_categories(esporte_inst)) == 23

    tur_viagens = get_survey_by_id("PNAD_TURISMO_VIAGENS_HOSPEDAGEM")
    assert get_survey_supported_levels(tur_viagens) == ["N3", "N2", "N1"]
    assert len(get_survey_categories(tur_viagens)) == 7

    # Fase 10: Finanças Públicas e Gestão Fiscal (FINBRA / MUNIC)
    p10_surveys = [s for s in SURVEYS if s.get("group") == "FINANCAS_PUBLICAS"]
    assert len(p10_surveys) == 28, f"Esperado 28 pesquisas na área FINANCAS_PUBLICAS, obtido {len(p10_surveys)}"

    fin_rec = get_survey_by_id("FINBRA_RECEITAS_TOTAIS")
    assert fin_rec.get("provider") == "finbra"
    assert get_survey_supported_levels(fin_rec) == ["N6", "N3"]
    assert 2025 in get_survey_valid_years(fin_rec)

    pib_imp = get_survey_by_id("PIB_IMPOSTOS_PRODUTOS")
    assert 2023 in get_survey_valid_years(pib_imp) and 2002 in get_survey_valid_years(pib_imp)

    munic_trib = get_survey_by_id("MUNIC_LEGISLACAO_TRIBUTARIA_URBANA")
    assert len(get_survey_categories(munic_trib)) == 5

    munic_fdb = get_survey_by_id("MUNIC_CONSELHO_FUNDEB_FISCALIZACAO")
    assert len(get_survey_categories(munic_fdb)) == 2

    ods_rec = get_survey_by_id("ODS_RECEITAS_GOVERNO_PIB")
    assert get_survey_supported_levels(ods_rec) == ["N1"]

    # Fase 11: Transporte, Mobilidade Urbana e Frota de Veículos (SENATRAN / MUNIC / ODS)
    p11_surveys = [s for s in SURVEYS if s.get("group") == "TRANSPORTE_MOBILIDADE"]
    assert len(p11_surveys) == 28, f"Esperado 28 pesquisas na área TRANSPORTE_MOBILIDADE, obtido {len(p11_surveys)}"

    frota_tot = get_survey_by_id("FROTA_TOTAL")
    assert frota_tot.get("provider") == "frota"
    assert get_survey_supported_levels(frota_tot) == ["N6", "N3"]
    assert 2025 in get_survey_valid_years(frota_tot) and 2006 in get_survey_valid_years(frota_tot)

    frota_auto = get_survey_by_id("FROTA_AUTOMOVEIS")
    assert frota_auto.get("table") == "FROTA"

    munic_trans = get_survey_by_id("MUNIC_SERVICOS_REGULARES_TRANSPORTE")
    assert len(get_survey_categories(munic_trans)) == 10

    munic_ciclo = get_survey_by_id("MUNIC_CICLOVIAS_BICICLETARIOS")
    assert len(get_survey_categories(munic_ciclo)) == 3

    ods_trans = get_survey_by_id("ODS_MORTALIDADE_TRANSITO")
    assert get_survey_supported_levels(ods_trans) == ["N3", "N2", "N1"]
    assert 2024 in get_survey_valid_years(ods_trans)

    # Fase 12: Inovação Tecnológica, P&D e Governo Digital (PINTEC / MUNIC / PSTI / ODS)
    p12_surveys = [s for s in SURVEYS if s.get("group") == "INOVACAO_GOV_DIGITAL"]
    assert len(p12_surveys) == 28, f"Esperado 28 pesquisas na área INOVACAO_GOV_DIGITAL, obtido {len(p12_surveys)}"

    pintec_taxa = get_survey_by_id("PINTEC_UF_TAXA_INOVACAO")
    assert pintec_taxa.get("provider") == "pintec_uf"
    assert get_survey_supported_levels(pintec_taxa) == ["N3", "N1"]
    assert 2017 in get_survey_valid_years(pintec_taxa) and 2011 in get_survey_valid_years(pintec_taxa)

    pintec_apoio = get_survey_by_id("PINTEC_APOIO_GOVERNAMENTAL")
    assert len(get_survey_categories(pintec_apoio)) == 11

    pintec_setor = get_survey_by_id("PINTEC_SETOR_INOVACAO")
    assert len(get_survey_categories(pintec_setor)) == 23

    munic_lgpd = get_survey_by_id("MUNIC_LGPD_GOVERNANCA_DADOS")
    assert munic_lgpd.get("provider") == "munic_digital"
    assert get_survey_supported_levels(munic_lgpd) == ["N6"]
    assert 2024 in get_survey_valid_years(munic_lgpd)

    ods_tec = get_survey_by_id("ODS_9B1_INDUSTRIA_ALTA_TEC_UF")
    assert get_survey_supported_levels(ods_tec) == ["N3", "N1"]

    ods_5g = get_survey_by_id("ODS_9C1_COBERTURA_MOVEL_4G_5G")
    assert len(get_survey_categories(ods_5g)) == 4

    # Áreas puras desmembradas: Riscos de Desastres e Sistema Financeiro/Bancarização
    p_riscos = [s for s in SURVEYS if s.get("group") == "RISCOS_DESASTRES_DEFESA_CIVIL"]
    assert len(p_riscos) == 22, f"Esperado 22 pesquisas na área RISCOS_DESASTRES_DEFESA_CIVIL, obtido {len(p_riscos)}"

    p_fin = [s for s in SURVEYS if s.get("group") == "SISTEMA_FINANCEIRO_CREDITO"]
    assert len(p_fin) == 10, f"Esperado 10 pesquisas na área SISTEMA_FINANCEIRO_CREDITO, obtido {len(p_fin)}"

    cem_pop = get_survey_by_id("CEMADEN_POPULACAO_RISCO")
    assert cem_pop.get("provider") == "cemaden"
    assert get_survey_supported_levels(cem_pop) == ["N6", "N3", "N1"]
    assert 2010 in get_survey_valid_years(cem_pop)

    bac_ag = get_survey_by_id("BACEN_AGENCIAS_BANCARIAS")
    assert bac_ag.get("provider") == "bacen"
    assert get_survey_supported_levels(bac_ag) == ["N6", "N3", "N1"]
    assert 2024 in get_survey_valid_years(bac_ag) and 2006 in get_survey_valid_years(bac_ag)

    cag_cred = get_survey_by_id("CENSO_AGRO_CREDITO_AGENTES")
    assert cag_cred["table"] == 6895
    assert len(get_survey_categories(cag_cred)) == 11
    assert get_survey_supported_levels(cag_cred) == ["N6", "N3", "N2", "N1"]

    pnsb_risco = get_survey_by_id("PNSB_AREAS_RISCO_DRENAGEM")
    assert pnsb_risco["table"] == 2252
    assert len(get_survey_categories(pnsb_risco)) == 7

    pnsb_inund = get_survey_by_id("PNSB_INUNDACOES_ALAGAMENTOS_URBANOS")
    assert pnsb_inund["table"] == 1764
    assert len(get_survey_categories(pnsb_inund)) == 6

    munic_pmrr = get_survey_by_id("MUNIC_PMRR_INSTRUMENTOS_RISCO")
    assert munic_pmrr.get("provider") == "munic_digital"
    assert get_survey_supported_levels(munic_pmrr) == ["N6", "N3", "N1"]
    assert 2020 in get_survey_valid_years(munic_pmrr)

    ods_banc = get_survey_by_id("ODS_8102_BANCARIZACAO_ADULTOS")
    assert len(get_survey_categories(ods_banc)) == 3

    ods_perdas = get_survey_by_id("ODS_1152_PERDAS_ECONOMICAS_DESASTRES")
    assert get_survey_supported_levels(ods_perdas) == ["N1"]

    # Fase 14: Territórios Tradicionais, Terras Indígenas e Comunidades Quilombolas (Censo 2022)
    p14_surveys = [s for s in SURVEYS if s.get("group") == "TERRITORIOS_TRADICIONAIS_INDIGENAS_QUILOMBOLAS"]
    assert len(p14_surveys) == 27, f"Esperado 27 pesquisas na Fase 14, obtido {len(p14_surveys)}"

    ind_loc = get_survey_by_id("CENSO22_INDIGENA_LOCALIZACAO")
    assert ind_loc["table"] == 9718
    assert len(get_survey_categories(ind_loc)) == 3
    assert get_survey_supported_levels(ind_loc) == ["N6", "N3", "N2", "N1"]
    assert 2022 in get_survey_valid_years(ind_loc)

    ind_terras = get_survey_by_id("CENSO22_INDIGENA_TERRAS_POPULACAO")
    assert ind_terras["table"] == 9719
    assert len(get_survey_categories(ind_terras)) == 4

    quil_loc = get_survey_by_id("CENSO22_QUILOMBOLA_LOCALIZACAO")
    assert quil_loc["table"] == 9578
    assert len(get_survey_categories(quil_loc)) == 3
    assert get_survey_supported_levels(quil_loc) == ["N6", "N3", "N2", "N1"]
    assert 2022 in get_survey_valid_years(quil_loc)

    quil_agua = get_survey_by_id("CENSO22_QUILOMBOLA_ABASTECIMENTO_AGUA")
    assert quil_agua["table"] == 9804
    assert len(get_survey_categories(quil_agua)) == 16

    print("[OK] Catálogo expandido (404 pesquisas, 20 áreas temáticas, Fases 4-14 e resolve_table_queries) validado.")


def test_unit_formatting():
    assert fmt_volume_br(1500.0, "Mil pessoas") == "1,50 mi"
    assert fmt_volume_br(2500.0, "Mil unidades") == "2,50 mi"
    assert fmt_volume_br(450.0, "Mil domicílios") == "450,0 mil"
    assert fmt_volume_br(12.34, "‰") == "12,34‰"
    assert fmt_volume_br(2500.0, "Quilômetros") == "2,50 mil km"
    assert fmt_volume_br(112.4, "Número-índice") == "112,4"
    assert fmt_volume_br(1.62, "Filhos") == "1,62 filhos"
    assert fmt_volume_br(42.56, "Microgramas por metro cúbico") == "42,6 µg/m³"
    assert fmt_volume_br(18.2, "Óbitos por 100.000 habitantes") == "18,2 / 100 mil hab."
    assert fmt_volume_br(18.2, "por 100 mil habitantes") == "18,2 / 100 mil hab."
    try:
        from geosidra_qgis.core.layer_builder import format_indicator_value
        assert format_indicator_value(1500.0, "Mil pessoas") == "1,50 mi"
        assert format_indicator_value(2500.0, "Mil unidades") == "2,50 mi"
        assert format_indicator_value(450.0, "Mil domicílios") == "450,0 mil"
        assert format_indicator_value(12.34, "‰") == "12,34‰"
        assert format_indicator_value(145.6, "Quilômetros") == "145,6 km"
        assert format_indicator_value(112.4, "Número-índice") == "112,4"
        assert format_indicator_value(1.62, "Filhos") == "1,62 filhos"
        assert format_indicator_value(42.56, "Microgramas por metro cúbico") == "42,6 µg/m³"
        assert format_indicator_value(18.2, "Óbitos por 100.000 habitantes") == "18,2 / 100 mil hab."
    except ImportError:
        pass
    print("[OK] Formatação de unidades Fases 3-5 (Mil pessoas, Mil unidades, ‰, km, Número-índice, Filhos, µg/m³, / 100 mil hab.) validada.")


def test_variable_slugs():
    assert get_variable_slug("PAM", 214) == "quantidade_produzida"
    assert get_variable_slug("PAM", 112) == "rendimento_medio"
    assert get_variable_slug("PEVS_EXTRACAO", 144) == "quantidade_produzida_extracao"
    assert get_variable_slug("PPM_AQUICULTURA", 4146) == "producao_aquicultura"
    assert get_variable_slug("PIB_MUN", 37) == "pib"
    assert get_variable_slug("PIA_EMPRESA_UF", 811) == "vti"
    assert get_variable_slug("POP_ESTIMADA", 9324) == "populacao_estimada"
    assert get_variable_slug("CENSO22_ALFABETIZACAO", 2513) == "taxa_alfabetizacao"
    assert get_variable_slug("LSPA_SAFRA_UF", 35) == "producao_lspa"
    assert get_variable_slug("PNAD_DESOCUPACAO_UF", 4099) == "taxa_desocupacao"
    assert get_variable_slug("MUNIC_PLANO_DIRETOR", 603) == "munic_plano_diretor"
    assert get_variable_slug("RC_NASCIDOS_VIVOS", 217) == "nascidos_vivos"
    assert get_variable_slug("MEI_DINAMICA", 8894) == "saldo_meis"
    assert get_variable_slug("SINAPI_SEM_DESONERACAO", 9327) == "sinapi_custo_m2"
    assert get_variable_slug("PIM_PF_IND_UF", 11604) == "pimpf_var_12m"
    assert get_variable_slug("ESTOQUES_ARMAZENADOS", 150) == "estoques_quantidade"
    assert get_variable_slug("PNAD_OCUPACAO_CARTEIRA_UF", 4090) == "pnad_ocupados_categoria"
    assert get_variable_slug("PROJECAO_VIDA_MORT_UF", 1940) == "proj_mortalidade_infantil"
    assert get_variable_slug("CENSO22_ENTORNO_URBANISTICO", 1009611) == "censo22_entorno_pct"
    assert get_variable_slug("PNSB_REDE_ESGOTO", 10757) == "pnsb_extensao_rede_esgoto"
    assert get_variable_slug("MUNIC_SEGURANCA_PUBLICA", 603) == "munic_seguranca_publica"
    assert get_variable_slug("RC_DIVORCIOS", 393) == "rc_divorcios"
    assert get_variable_slug("CENSO22_INDIGENA_LOCALIZACAO", 350) == "pessoas_indigenas"
    assert get_variable_slug("CENSO22_QUILOMBOLA_LOCALIZACAO", 4709) == "pessoas_quilombolas"
    print("[OK] Slugs de variáveis validados para todas as famílias de pesquisas (incluindo Fases 2-14).")


def test_mapper():
    mapper = MunicipalityMapper.instance()
    info = mapper.get_by_ibge("4208500")
    assert info is not None, "Ituporanga não encontrado por código IBGE 4208500!"
    assert "ITUPORANGA" in info["nome_municipio"].upper(), f"Nome incorreto: {info}"
    print(f"[OK] MunicipalityMapper validado ({info['nome_municipio']} - {info['uf']}).")


def test_live_sidra_series_and_analytics():
    client = SidraClient()

    # 1. PAM (5457) - Cebola SC
    raw_pam = client.query(table=5457, territory="SC", level="N6", variables=[214], years=[2024], classification=782, category=40107)
    parsed_pam = client.parse_records(raw_pam, primary_var=214, agg_mode="sum")
    assert parsed_pam["total"] > 100000
    print(f"[OK] PAM 2024 Cebola SC: {parsed_pam['total']:,.0f} t ({len(parsed_pam['top_producers'])} municípios)")

    # 2. PEVS Extração Vegetal (289) - Açaí PA
    raw_pevs = client.query(table=289, territory="PA", level="N6", variables=[144], years=[2024], classification=193, category=3403)
    parsed_pevs = client.parse_records(raw_pevs, primary_var=144, agg_mode="sum")
    assert parsed_pevs["total"] > 50000
    print(f"[OK] PEVS 2024 Açaí PA: {parsed_pevs['total']:,.0f} t")

    # 3. PPM Aquicultura (3940) - Tilápia PR
    raw_aqui = client.query(table=3940, territory="PR", level="N6", variables=[4146], years=[2024], classification=654, category=32877)
    parsed_aqui = client.parse_records(raw_aqui, primary_var=4146, agg_mode="sum")
    assert parsed_aqui["total"] > 1000000
    print(f"[OK] PPM Aquicultura 2024 Tilápia PR: {parsed_aqui['total']:,.0f} kg")

    # 4. Censo Agro 2017 (6878) com extra_classifications
    cagro = get_survey_by_id("CENSO_AGRO_TIPOLOGIA")
    plans_cagro, _ = resolve_table_queries(cagro, [2017], 183)
    raw_cagro = client.query_series(
        plans_cagro, territory="SC", level="N6",
        classification=cagro["classification"], category=46304,
        extra_classifications=cagro.get("extra_classifications"),
    )
    parsed_cagro = client.parse_records(raw_cagro, primary_var=183, agg_mode="last")
    assert parsed_cagro["total"] > 100000
    print(f"[OK] Censo Agro 2017 SC (Agricultura familiar): {parsed_cagro['total']:,.0f} estabelecimentos")

    # 5. Estimativas de População 2026 (6579)
    raw_pop = client.query(table=6579, territory="SC", level="N6", variables=[9324], years=[2026], classification=None, category=0)
    parsed_pop = client.parse_records(raw_pop, primary_var=9324, agg_mode="last")
    assert parsed_pop["total"] > 7000000
    print(f"[OK] Estimativa População 2026 SC: {parsed_pop['total']:,.0f} hab")

    # 6. Censo 2022 - Crescimento negativo e positivo (4709)
    raw_cres = client.query(table=4709, territory="RS", level="N6", variables=[10605], years=[2022], classification=None, category=0)
    parsed_cres = client.parse_records(raw_cres, primary_var=10605, agg_mode="mean", allow_negative=True)
    parsed_cres["product_name"] = "Taxa de Crescimento Geométrico (RS)"
    parsed_cres["level"] = "N6"
    parsed_cres["agg_mode"] = "mean"
    parsed_cres["allow_negative"] = True
    vals_rs = [r["valor_principal"] for r in parsed_cres["by_mun"].values() if r.get("has_record")]
    assert any(v < 0 for v in vals_rs) and any(v > 0 for v in vals_rs), "Censo 4709 RS deveria conter variações positivas e negativas"
    print(f"[OK] Censo 2022 Crescimento RS: min={min(vals_rs):.2f}% / max={max(vals_rs):.2f}%")

    # 7. Censo 2022 - Alfabetização com extra_classifications (9543)
    c_alfa = get_survey_by_id("CENSO22_ALFABETIZACAO")
    plans_alfa, _ = resolve_table_queries(c_alfa, [2022], 2513)
    raw_alfa = client.query_series(
        plans_alfa, territory="SC", level="N6",
        classification=c_alfa["classification"], category=6794,
        extra_classifications=c_alfa.get("extra_classifications"),
    )
    parsed_alfa = client.parse_records(raw_alfa, primary_var=2513, agg_mode="mean")
    parsed_alfa["product_name"] = "Taxa de Alfabetização 15+"
    parsed_alfa["level"] = "N6"
    parsed_alfa["agg_mode"] = "mean"
    assert 80.0 <= parsed_alfa["mean_value"] <= 99.9, parsed_alfa["mean_value"]
    print(f"[OK] Censo 2022 Alfabetização SC: média municipal {parsed_alfa['mean_value']:.2f}%")

    # 8. CEMPRE CNAE stitching (6450 [2021] + 9528 [2024])
    cempre = get_survey_by_id("CEMPRE_CNAE")
    plans_cem, _ = resolve_table_queries(cempre, [2021, 2024], 706)
    raw_cem = client.query_series(
        plans_cem, territory="SC", level="N6",
        classification=cempre["classification"], category=117897,
    )
    parsed_cem = client.parse_records(raw_cem, primary_var=706, agg_mode="last")
    parsed_cem["product_name"] = "CEMPRE - Total CNAE 2.0 (SC)"
    parsed_cem["level"] = "N6"
    assert sorted(parsed_cem["years"]) == ["2021", "2024"], parsed_cem["years"]
    assert parsed_cem["total"] > 200000
    print(f"[OK] CEMPRE 6450+9528 SC (2021 -> 2024): último ano={parsed_cem['total']:,.0f} unid. locais")

    # 9. PIA-Produto N1 (7752 + 10476)
    pia_prod = get_survey_by_id("PIA_PRODUTO")
    plans_pia, _ = resolve_table_queries(pia_prod, [2023, 2024], 214)
    raw_pia = client.query_series(
        plans_pia, territory="BR", level="N1",
        classification=pia_prod["classification"], category=51741,
    )
    parsed_pia = client.parse_records(raw_pia, primary_var=214, agg_mode="last")
    assert "2023" in parsed_pia["years"] and "2024" in parsed_pia["years"], parsed_pia["years"]
    print(f"[OK] PIA-Produto N1 Carnes Congeladas (2023->2024): {parsed_pia['total']:,.0f} t")

    # 10. Fase 2 - LSPA Safra UF mensal completo 202609 / 202603 / 202512 (6588)
    lspa = get_survey_by_id("LSPA_SAFRA_UF")
    plans_lspa, _ = resolve_table_queries(lspa, [202609], 35)
    raw_lspa = client.query_series(
        plans_lspa, territory="BR", level="N3",
        classification=lspa["classification"], category=lspa["default_cat"],
    )
    parsed_lspa = client.parse_records(raw_lspa, primary_var=35, agg_mode="last")
    assert parsed_lspa["total"] > 100_000_000 and len(parsed_lspa["by_mun"]) == 27
    print(f"[OK] LSPA Set/2026 Soja UF: {parsed_lspa['total']:,.0f} t ({len(parsed_lspa['by_mun'])} UFs)")

    plans_lspa_m, _ = resolve_table_queries(lspa, [202603, 2025], 35)
    raw_lspa_m = client.query_series(
        plans_lspa_m, territory="SC", level="N3",
        classification=lspa["classification"], category=lspa["default_cat"],
    )
    parsed_lspa_m = client.parse_records(raw_lspa_m, primary_var=35, agg_mode="last")
    assert sorted(parsed_lspa_m["years"]) == ["202512", "202603"], parsed_lspa_m["years"]
    print(f"[OK] LSPA Mensal SC (Dez/2025 -> Mar/2026): {parsed_lspa_m['total']:,.0f} t")

    # 10b. Série histórica pré-2001 PAM 1980 + PIB 2000/2023 + PAC/PAS 2023/2024 + subfiltro + BR chunking
    raw_pam80 = client.query(table=5457, territory="SC", level="N6", variables=[214], years=[1980], classification=782, category=40124)
    parsed_pam80 = client.parse_records(raw_pam80, primary_var=214, agg_mode="sum")
    assert parsed_pam80["total"] > 400_000
    print(f"[OK] PAM 1980 (pré-2001) Soja SC: {parsed_pam80['total']:,.0f} t")

    pib_mun = get_survey_by_id("PIB_MUN")
    plans_pib, _ = resolve_table_queries(pib_mun, [2000, 2023], 37)
    raw_pib = client.query_series(plans_pib, territory="SC", level="N6")
    parsed_pib = client.parse_records(raw_pib, primary_var=37, agg_mode="sum")
    assert sorted(parsed_pib["years"]) == ["2000", "2023"] and len(parsed_pib["by_mun"]) == 295
    print(f"[OK] PIB Municipal unificado 21+5938 SC (2000 & 2023): {len(parsed_pib['by_mun'])} municípios")

    pac = get_survey_by_id("PAC_COMERCIO_UF")
    plans_pac, _ = resolve_table_queries(pac, [2023, 2024], 866, category_id=83357)
    raw_pac = client.query_series(plans_pac, territory="BR", level="N3", classification=pac["classification"], category=83357)
    parsed_pac = client.parse_records(raw_pac, primary_var=866, agg_mode="sum")
    assert sorted(parsed_pac["years"]) == ["2023", "2024"] and len(parsed_pac["by_mun"]) == 27
    print(f"[OK] PAC Comércio 1407+10653 BR Veículos (2023+2024): {len(parsed_pac['by_mun'])} UFs")

    pas = get_survey_by_id("PAS_SERVICOS_UF")
    plans_pas, _ = resolve_table_queries(pas, [2023, 2024], 857, category_id=58296)
    raw_pas = client.query_series(plans_pas, territory="BR", level="N3", classification=pas["classification"], category=58296)
    parsed_pas = client.parse_records(raw_pas, primary_var=857, agg_mode="sum")
    assert sorted(parsed_pas["years"]) == ["2023", "2024"] and len(parsed_pas["by_mun"]) == 27
    print(f"[OK] PAS Serviços 2715+10762 BR Famílias/Salários (2023+2024): {len(parsed_pas['by_mun'])} UFs")

    plans_alfa_p, _ = resolve_table_queries(get_survey_by_id("CENSO22_ALFABETIZACAO"), [2022], 2513)
    raw_alfa_p = client.query_series(
        plans_alfa_p, territory="SC", level="N6",
        classification=2, category=5,
        extra_classifications={86: 2777, 287: 100362},
    )
    parsed_alfa_p = client.parse_records(raw_alfa_p, primary_var=2513, agg_mode="mean")
    assert 70.0 <= parsed_alfa_p["mean_value"] <= 99.9
    print(f"[OK] Subfiltro Censo 2022 Alfabetização (Mulheres Pretas SC): {parsed_alfa_p['mean_value']:.2f}%")

    rc_cas = get_survey_by_id("RC_CASAMENTOS")
    plans_rc_br, _ = resolve_table_queries(rc_cas, [2024], 4993)
    raw_rc_br = client.query_series(
        plans_rc_br, territory="BR", level="N6",
        classification=rc_cas["classification"], category=0,
        extra_classifications=rc_cas.get("extra_classifications"),
    )
    parsed_rc_br = client.parse_records(raw_rc_br, primary_var=4993, agg_mode="sum")
    assert len(parsed_rc_br["by_mun"]) > 5000 and parsed_rc_br["total"] > 500_000
    print(f"[OK] Consulta BR/N6 fracionada por UF (Casamentos 4412 2024): {len(parsed_rc_br['by_mun'])} municípios, {parsed_rc_br['total']:,.0f} casamentos")

    # 11. Fase 2 - PNAD Contínua Desocupação UF 202602 (4099) + Abate Bovinos Total 2025 (1T a 4T = soma)
    pnad_des = get_survey_by_id("PNAD_DESOCUPACAO_UF")
    plans_pnad, _ = resolve_table_queries(pnad_des, [202602], 4099)
    raw_pnad = client.query_series(plans_pnad, territory="BR", level="N3")
    parsed_pnad = client.parse_records(raw_pnad, primary_var=4099, agg_mode="mean")
    parsed_pnad["product_name"] = "Taxa de Desocupação (PNAD 2T/2026)"
    parsed_pnad["level"] = "N3"
    parsed_pnad["agg_mode"] = "mean"
    assert 2.0 <= parsed_pnad["mean_value"] <= 20.0 and len(parsed_pnad["by_mun"]) == 27
    print(f"[OK] PNAD Desocupação 2T/2026 UF: média das UFs {parsed_pnad['mean_value']:.2f}%")

    abate_s = get_survey_by_id("ABATE_BOVINOS_UF")
    plans_ab_tot, _ = resolve_table_queries(abate_s, [2025], 284)
    raw_ab_tot = client.query_series(
        plans_ab_tot, territory="SC", level="N3",
        classification=abate_s["classification"], category=992,
        extra_classifications=abate_s.get("extra_classifications"),
    )
    parsed_ab_tot = client.parse_records(raw_ab_tot, primary_var=284, agg_mode="sum")
    plans_ab_q1, _ = resolve_table_queries(abate_s, [202501], 284)
    raw_ab_q1 = client.query_series(
        plans_ab_q1, territory="SC", level="N3",
        classification=abate_s["classification"], category=992,
        extra_classifications=abate_s.get("extra_classifications"),
    )
    parsed_ab_q1 = client.parse_records(raw_ab_q1, primary_var=284, agg_mode="sum")
    assert parsed_ab_tot["total"] > parsed_ab_q1["total"] * 3.0
    assert len(parsed_ab_tot["years"]) == 4 and sorted(parsed_ab_tot["years"]) == ["202501", "202502", "202503", "202504"]
    print(f"[OK] Abate Bovinos SC: 1T/2025={parsed_ab_q1['total']:,.0f} cab | Total Anual 2025 (1T a 4T)={parsed_ab_tot['total']:,.0f} cab")

    # 12. Fase 2 - Censo 2022 Rendimento Domiciliar Per Capita (10295)
    renda_pc = get_survey_by_id("CENSO22_RENDA_PC")
    plans_rpc, _ = resolve_table_queries(renda_pc, [2022], 13431)
    raw_rpc = client.query_series(
        plans_rpc, territory="SC", level="N6",
        classification=renda_pc["classification"], category=95251,
        extra_classifications=renda_pc.get("extra_classifications"),
    )
    parsed_rpc = client.parse_records(raw_rpc, primary_var=13431, agg_mode="mean")
    assert parsed_rpc["mean_value"] > 1500 and len(parsed_rpc["by_mun"]) == 295
    print(f"[OK] Censo 2022 Rendimento Per Capita SC: média municipal R$ {parsed_rpc['mean_value']:,.2f}")

    # 13. Fase 2 - Censo Agro 2017 Valor da Produção (6897)
    cagro_vp = get_survey_by_id("CAGRO_VALOR_PROD")
    plans_vp, _ = resolve_table_queries(cagro_vp, [2017], 1999)
    raw_vp = client.query_series(
        plans_vp, territory="SC", level="N6",
        classification=cagro_vp["classification"], category=114017,
        extra_classifications=cagro_vp.get("extra_classifications"),
    )
    parsed_vp = client.parse_records(raw_vp, primary_var=1999, agg_mode="last")
    assert parsed_vp["total"] > 15_000_000 and len(parsed_vp["by_mun"]) == 295
    print(f"[OK] Censo Agro 2017 Valor da Produção SC: R$ {parsed_vp['total']:,.0f} mil")

    # 14. Fase 2 - PAC Comércio UF 2024 (10653)
    pac = get_survey_by_id("PAC_COMERCIO_UF")
    plans_pac, _ = resolve_table_queries(pac, [2024], 866)
    raw_pac = client.query_series(
        plans_pac, territory="BR", level="N3",
        classification=pac["classification"], category=90071,
    )
    parsed_pac = client.parse_records(raw_pac, primary_var=866, agg_mode="sum")
    assert parsed_pac["total"] > 1_000_000_000 and len(parsed_pac["by_mun"]) == 27
    print(f"[OK] PAC Comércio 2024 UF (Total): R$ {parsed_pac['total']:,.0f} mil")

    # 15. Fase 2 - MEI Dinâmica N3 (9597, allow_negative=True)
    mei_din = get_survey_by_id("MEI_DINAMICA")
    plans_mei, _ = resolve_table_queries(mei_din, [2022], 8894)
    raw_mei = client.query_series(
        plans_mei, territory="BR", level="N3",
        classification=mei_din["classification"], category=59983,
    )
    parsed_mei = client.parse_records(raw_mei, primary_var=8894, agg_mode="last", allow_negative=True)
    parsed_mei["product_name"] = "Saldo de MEIs - Total (UFs)"
    parsed_mei["level"] = "N3"
    parsed_mei["agg_mode"] = "last"
    parsed_mei["allow_negative"] = True
    assert len(parsed_mei["by_mun"]) == 27
    print(f"[OK] MEI Dinâmica N3 (Saldo 2022): {parsed_mei['total']:,.0f} MEIs em {len(parsed_mei['by_mun'])} UFs")

    # 16. Fase 2 - MUNIC Plano Diretor SC 2021 (5882, is_binary=True)
    munic = get_survey_by_id("MUNIC_PLANO_DIRETOR")
    plans_mun, _ = resolve_table_queries(munic, [2021], 603)
    raw_mun = client.query_series(
        plans_mun, territory="SC", level="N6",
        classification=munic["classification"], category=munic["default_cat"],
        extra_classifications=munic.get("extra_classifications"),
    )
    parsed_mun = client.parse_records(raw_mun, primary_var=603, agg_mode="last")
    parsed_mun["product_name"] = "Com Plano Diretor (MUNIC 2021)"
    parsed_mun["variable_name"] = "Município Enquadrado (Indicador Sim = 1)"
    parsed_mun["unit"] = "Municípios"
    parsed_mun["level"] = "N6"
    parsed_mun["agg_mode"] = "last"
    parsed_mun["is_binary"] = True
    assert len(parsed_mun["by_mun"]) == 295 and parsed_mun["total"] == 237.0
    print(f"[OK] MUNIC Plano Diretor 2021 SC (binário): {int(parsed_mun['total'])}/295 municípios com Sim (= 1)")

    # 17. Fase 2 - PNSB 2017 Abastecimento de Água SC (7499)
    pnsb = get_survey_by_id("PNSB_AGUA")
    plans_pnsb, _ = resolve_table_queries(pnsb, [2017], 448)
    raw_pnsb = client.query_series(
        plans_pnsb, territory="SC", level="N6",
        classification=pnsb["classification"], category=48981,
    )
    parsed_pnsb = client.parse_records(raw_pnsb, primary_var=448, agg_mode="last")
    assert parsed_pnsb["total"] > 500_000 and len(parsed_pnsb["by_mun"]) >= 290
    print(f"[OK] PNSB 2017 Água SC: {parsed_pnsb['total']:,.0f} m3/dia ({len(parsed_pnsb['by_mun'])} municípios)")

    # 18. Fase 2 - Registro Civil Nascidos Vivos SC 2024 (2609)
    rc_nv = get_survey_by_id("RC_NASCIDOS_VIVOS")
    plans_rc, _ = resolve_table_queries(rc_nv, [2024], 217)
    raw_rc = client.query_series(
        plans_rc, territory="SC", level="N6",
        classification=rc_nv["classification"], category=0,
        extra_classifications=rc_nv.get("extra_classifications"),
    )
    parsed_rc = client.parse_records(raw_rc, primary_var=217, agg_mode="sum")
    assert parsed_rc["total"] > 50_000 and len(parsed_rc["by_mun"]) == 295
    print(f"[OK] Registro Civil 2024 Nascidos Vivos SC: {parsed_rc['total']:,.0f} registros")

    # 19. Fase 3 - Conjuntura Mensal SINAPI (6586), PIM-PF (8888, negativo) e PMC Total (8880)
    sin_s = get_survey_by_id("SINAPI_SEM_DESONERACAO")
    plans_sin, _ = resolve_table_queries(sin_s, [202609], 9327)
    raw_sin = client.query_series(plans_sin, territory="BR", level="N3", classification=None, category=0)
    parsed_sin = client.parse_records(raw_sin, primary_var=9327, agg_mode="mean")
    assert len(parsed_sin["by_mun"]) == 27 and parsed_sin["mean_value"] > 1500
    print(f"[OK] SINAPI Set/2026 Sem Desoneração N3: média R$ {parsed_sin['mean_value']:,.2f}/m2 (27 UFs)")

    pimpf_s = get_survey_by_id("PIM_PF_IND_UF")
    plans_pim, _ = resolve_table_queries(pimpf_s, [202609], 11604)
    raw_pim = client.query_series(
        plans_pim, territory="BR", level="N3",
        classification=pimpf_s["classification"], category=pimpf_s["default_cat"],
    )
    parsed_pim = client.parse_records(raw_pim, primary_var=11604, agg_mode="mean", allow_negative=True)
    parsed_pim["product_name"] = "Indústria Geral - PIM-PF"
    parsed_pim["variable_name"] = "Variação Acumulada 12m"
    parsed_pim["unit"] = "%"
    parsed_pim["level"] = "N3"
    parsed_pim["agg_mode"] = "mean"
    parsed_pim["allow_negative"] = True
    assert len(parsed_pim["by_mun"]) == 17
    print(f"[OK] PIM-PF Set/2026 Acum. 12m N3: {len(parsed_pim['by_mun'])} UFs com amostra industrial")

    # 20. Fase 3 - Pesquisa de Estoques Semestral SC 2025/202501 (254)
    est_s = get_survey_by_id("ESTOQUES_ARMAZENADOS")
    plans_est, _ = resolve_table_queries(est_s, [2025], 150)
    raw_est = client.query_series(
        plans_est, territory="SC", level="N6",
        classification=est_s["classification"], category=est_s["default_cat"],
        extra_classifications=est_s.get("extra_classifications"),
    )
    parsed_est = client.parse_records(raw_est, primary_var=150, agg_mode="last")
    assert len(parsed_est["by_mun"]) >= 30 and parsed_est["total"] > 100000
    print(f"[OK] Pesquisa de Estoques 2o Sem/2025 SC: {parsed_est['total']:,.0f} t ({len(parsed_est['by_mun'])} mun)")

    # 21. Fase 3 - Couro Trimestral UF (1088) e PNAD Ocupação / Carteira (4097)
    couro_s = get_survey_by_id("COURO_CRU_TRIMESTRAL_UF")
    plans_cou, _ = resolve_table_queries(couro_s, [202602], 622)
    raw_cou = client.query_series(
        plans_cou, territory="BR", level="N3",
        classification=couro_s["classification"], category=couro_s["default_cat"],
        extra_classifications=couro_s.get("extra_classifications"),
    )
    parsed_cou = client.parse_records(raw_cou, primary_var=622, agg_mode="sum")
    assert parsed_cou["total"] > 1_000_000 and len(parsed_cou["by_mun"]) >= 10
    print(f"[OK] Couro Cru 2T/2026 N3: {parsed_cou['total']:,.0f} unidades em {len(parsed_cou['by_mun'])} UFs")

    pnad_cart = get_survey_by_id("PNAD_OCUPACAO_CARTEIRA_UF")
    plans_cart, _ = resolve_table_queries(pnad_cart, [202602], 4090)
    raw_cart = client.query_series(
        plans_cart, territory="BR", level="N3",
        classification=pnad_cart["classification"], category=31722,
    )
    parsed_cart = client.parse_records(raw_cart, primary_var=4090, agg_mode="last")
    assert len(parsed_cart["by_mun"]) == 27 and parsed_cart["total"] > 30_000
    print(f"[OK] PNAD 2T/2026 Empregados c/ Carteira (N3): {parsed_cart['total']:,.0f} mil pessoas")

    # 22. Fase 3 - Censo 2022 Entorno Urbanístico SC (10050) e Projeção Mortalidade Infantil 2026 N3 (7362)
    ent_s = get_survey_by_id("CENSO22_ENTORNO_URBANISTICO")
    plans_ent, _ = resolve_table_queries(ent_s, [2022], 1009611)
    raw_ent = client.query_series(
        plans_ent, territory="SC", level="N6",
        classification=ent_s["classification"], category=ent_s["default_cat"],
        extra_classifications=ent_s.get("extra_classifications"),
    )
    parsed_ent = client.parse_records(raw_ent, primary_var=1009611, agg_mode="mean")
    assert len(parsed_ent["by_mun"]) == 295 and parsed_ent["mean_value"] > 50.0
    print(f"[OK] Censo 2022 Entorno Via Pavimentada SC: média municipal {parsed_ent['mean_value']:.1f}%")

    proj_s = get_survey_by_id("PROJECAO_VIDA_MORT_UF")
    plans_proj, _ = resolve_table_queries(proj_s, [2018], 1940)
    raw_proj = client.query_series(
        plans_proj, territory="BR", level="N3",
        classification=proj_s["classification"], category=49042,
        extra_classifications=proj_s.get("extra_classifications"),
    )
    parsed_proj = client.parse_records(raw_proj, primary_var=1940, agg_mode="mean")
    parsed_proj["product_name"] = "Projeção TMI 2026 (UFs)"
    parsed_proj["variable_name"] = "Taxa de Mortalidade Infantil"
    parsed_proj["unit"] = "‰"
    parsed_proj["level"] = "N3"
    parsed_proj["agg_mode"] = "mean"
    assert len(parsed_proj["by_mun"]) == 27 and 5.0 <= parsed_proj["mean_value"] <= 30.0
    print(f"[OK] Projeção TMI 2026 N3 (c1933=49042): média {parsed_proj['mean_value']:.2f} por mil")

    # 23. Fase 3 - MUNIC Segurança Pública 2023 (10027) e Registro Civil Divórcios SC (1695)
    mun_seg = get_survey_by_id("MUNIC_SEGURANCA_PUBLICA")
    plans_seg, _ = resolve_table_queries(mun_seg, [2023], 603)
    raw_seg = client.query_series(
        plans_seg, territory="SC", level="N6",
        classification=mun_seg["classification"], category=mun_seg["default_cat"],
        extra_classifications=mun_seg.get("extra_classifications"),
    )
    parsed_seg = client.parse_records(raw_seg, primary_var=603, agg_mode="last")
    assert len(parsed_seg["by_mun"]) == 295 and parsed_seg["total"] >= 10
    print(f"[OK] MUNIC 2023 Guarda Municipal SC: {int(parsed_seg['total'])}/295 municípios com Sim (= 1)")

    div_s = get_survey_by_id("RC_DIVORCIOS")
    plans_div, _ = resolve_table_queries(div_s, [2024], 393)
    raw_div = client.query_series(
        plans_div, territory="SC", level="N6",
        classification=div_s["classification"], category=0,
        extra_classifications=div_s.get("extra_classifications"),
    )
    parsed_div = client.parse_records(raw_div, primary_var=393, agg_mode="sum")
    assert len(parsed_div["by_mun"]) >= 200 and parsed_div["total"] > 5000
    print(f"[OK] Registro Civil 2024 Divórcios SC: {parsed_div['total']:,.0f} divórcios")

    # 24. v0.5.0 - IPCA / INPC / IPCA-15 (N7_N6), PNAD em N7_N14 e N2, e PAM em N8/N9 (SC)
    ipca_s = get_survey_by_id("IPCA_REGIONAL")
    plans_ipca_live, _ = resolve_table_queries(ipca_s, [2019, 202609], 63)
    raw_ipca = client.query_series(
        plans_ipca_live, territory="BR", level="N7_N6",
        classification=315, category=7169,
    )
    parsed_ipca = client.parse_records(raw_ipca, primary_var=63, agg_mode="mean", allow_negative=True)
    assert len(parsed_ipca["by_mun"]) == 16, f"IPCA deveria retornar 16 RMs+Capitais, obteve {len(parsed_ipca['by_mun'])}"
    print(f"[OK] IPCA Regional 2019+Set/2026 (N7_N6): {len(parsed_ipca['by_mun'])} áreas (10 RMs + 6 Capitais), média {parsed_ipca['mean_value']:.2f}%")

    inpc_s = get_survey_by_id("INPC_REGIONAL")
    plans_inpc_live, _ = resolve_table_queries(inpc_s, [202609], 44)
    raw_inpc = client.query_series(
        plans_inpc_live, territory="BR", level="N7_N6",
        classification=315, category=7169,
    )
    parsed_inpc = client.parse_records(raw_inpc, primary_var=44, agg_mode="mean", allow_negative=True)
    assert len(parsed_inpc["by_mun"]) == 16, f"INPC deveria retornar 16 RMs+Capitais, obteve {len(parsed_inpc['by_mun'])}"
    print(f"[OK] INPC Regional Set/2026 (N7_N6): {len(parsed_inpc['by_mun'])} áreas, média {parsed_inpc['mean_value']:.2f}%")

    ipca15_s = get_survey_by_id("IPCA15_REGIONAL")
    plans_ipca15_live, _ = resolve_table_queries(ipca15_s, [202001, 202610], 355)
    raw_ipca15 = client.query_series(
        plans_ipca15_live, territory="BR", level="N7_N6",
        classification=315, category=7169,
    )
    parsed_ipca15 = client.parse_records(raw_ipca15, primary_var=355, agg_mode="mean", allow_negative=True)
    assert len(parsed_ipca15["by_mun"]) == 11, f"IPCA-15 deveria retornar 11 áreas (9 RMs + Goiânia/Brasília), obteve {len(parsed_ipca15['by_mun'])}"
    print(f"[OK] IPCA-15 Regional Jan/2020+Out/2026 (N7_N6): {len(parsed_ipca15['by_mun'])} áreas, média {parsed_ipca15['mean_value']:.2f}%")

    pnad_des_s = get_survey_by_id("PNAD_DESOCUPACAO_UF")
    plans_pnad_rm, _ = resolve_table_queries(pnad_des_s, [202602], 4099)
    raw_pnad_rm = client.query_series(plans_pnad_rm, territory="BR", level="N7_N14")
    parsed_pnad_rm = client.parse_records(raw_pnad_rm, primary_var=4099, agg_mode="mean")
    assert len(parsed_pnad_rm["by_mun"]) == 21, f"PNAD N7_N14 deveria retornar 21 RMs+RIDE, obteve {len(parsed_pnad_rm['by_mun'])}"
    print(f"[OK] PNAD Desocupação 2T/2026 em RMs+RIDE (N7_N14): {len(parsed_pnad_rm['by_mun'])} áreas")

    raw_pnad_n2 = client.query_series(plans_pnad_rm, territory="BR", level="N2")
    parsed_pnad_n2 = client.parse_records(raw_pnad_n2, primary_var=4099, agg_mode="mean")
    assert len(parsed_pnad_n2["by_mun"]) == 5, f"PNAD N2 deveria retornar 5 Grandes Regiões, obteve {len(parsed_pnad_n2['by_mun'])}"
    print(f"[OK] PNAD Desocupação 2T/2026 em Grandes Regiões (N2): {len(parsed_pnad_n2['by_mun'])} regiões")

    pam_s = get_survey_by_id("PAM")
    plans_pam_reg, _ = resolve_table_queries(pam_s, [2024], 214)
    raw_pam_n8 = client.query_series(plans_pam_reg, territory="SC", level="N8", classification=782, category=40124)
    parsed_pam_n8 = client.parse_records(raw_pam_n8, primary_var=214, agg_mode="sum")
    assert len(parsed_pam_n8["by_mun"]) == 6 and parsed_pam_n8["total"] > 2_000_000, f"PAM SC N8 esperado 6 mesorregiões, obteve {len(parsed_pam_n8['by_mun'])}"
    raw_pam_n9 = client.query_series(plans_pam_reg, territory="SC", level="N9", classification=782, category=40124)
    parsed_pam_n9 = client.parse_records(raw_pam_n9, primary_var=214, agg_mode="sum")
    assert len(parsed_pam_n9["by_mun"]) == 20 and parsed_pam_n9["total"] > 2_000_000, f"PAM SC N9 esperado 20 microrregiões, obteve {len(parsed_pam_n9['by_mun'])}"
    print(f"[OK] PAM Soja SC 2024: N8={len(parsed_pam_n8['by_mun'])} mesorregiões, N9={len(parsed_pam_n9['by_mun'])} microrregiões")

    # 25. v0.6.0 - Fase 4 Live Checks: PAIC, POF, PNAD Anual Gini/EBIA, PNS (N3/N6 capitais), Censo 2022 e MUNIC SUAS
    paic_s = get_survey_by_id("PAIC_CONSTRUCAO_UF")
    plans_paic_live, _ = resolve_table_queries(paic_s, [2023, 2024], 1243)
    raw_paic = client.query_series(plans_paic_live, territory="BR", level="N3")
    parsed_paic = client.parse_records(raw_paic, primary_var=1243, agg_mode="last")
    assert len(parsed_paic["by_mun"]) == 27 and parsed_paic["total"] > 50_000, f"PAIC BR N3 inválido: {len(parsed_paic['by_mun'])}"
    print(f"[OK] PAIC 2023+2024 (1761->10442 BR N3): {len(parsed_paic['by_mun'])} UFs, {parsed_paic['total']:,.0f} empresas")

    pof_s = get_survey_by_id("POF_DESPESAS_FAMILIARES_UF")
    plans_pof, _ = resolve_table_queries(pof_s, [2018], 1201)
    raw_pof = client.query_series(
        plans_pof, territory="BR", level="N3",
        classification=12190, category=103536, extra_classifications={"339": 7999},
    )
    parsed_pof = client.parse_records(raw_pof, primary_var=1201, agg_mode="mean")
    assert len(parsed_pof["by_mun"]) == 27 and parsed_pof["mean_value"] > 2000
    print(f"[OK] POF 2018 Despesas BR N3: {len(parsed_pof['by_mun'])} UFs, média R$ {parsed_pof['mean_value']:,.2f}")

    gini_s = get_survey_by_id("PNAD_ANUAL_GINI_DOM_PC_UF")
    plans_gini, _ = resolve_table_queries(gini_s, [2025], 10681)
    raw_gini = client.query_series(plans_gini, territory="BR", level="N3")
    parsed_gini = client.parse_records(raw_gini, primary_var=10681, agg_mode="mean")
    assert len(parsed_gini["by_mun"]) == 27 and 0.35 <= parsed_gini["mean_value"] <= 0.65
    print(f"[OK] PNAD Anual Gini 2025 BR N3: {len(parsed_gini['by_mun'])} UFs, média {parsed_gini['mean_value']:.3f}")

    ebia_s = get_survey_by_id("PNAD_ANUAL_SEGURANCA_ALIMENTAR_UF")
    plans_ebia, _ = resolve_table_queries(ebia_s, [2024], 9784)
    raw_ebia = client.query_series(
        plans_ebia, territory="BR", level="N3",
        classification=12404, category=109099, extra_classifications={"1": 6795},
    )
    parsed_ebia = client.parse_records(raw_ebia, primary_var=9784, agg_mode="mean")
    assert len(parsed_ebia["by_mun"]) == 27
    print(f"[OK] PNAD Anual EBIA Insegurança Alimentar 2024 BR N3: média {parsed_ebia['mean_value']:.1f}%")

    pns_s = get_survey_by_id("PNS_HIPERTENSAO")
    plans_pns, _ = resolve_table_queries(pns_s, [2019], 4399)
    raw_pns_uf = client.query_series(
        plans_pns, territory="BR", level="N3",
        classification=2, category=6794, extra_classifications={"1": 6795},
    )
    parsed_pns_uf = client.parse_records(raw_pns_uf, primary_var=4399, agg_mode="mean")
    assert len(parsed_pns_uf["by_mun"]) == 27
    raw_pns_cap = client.query_series(
        plans_pns, territory="BR", level="N6",
        classification=2, category=6794, extra_classifications={"1": 6795},
    )
    parsed_pns_cap = client.parse_records(raw_pns_cap, primary_var=4399, agg_mode="mean")
    assert len(parsed_pns_cap["by_mun"]) == 27
    print(f"[OK] PNS 2019 Hipertensão: {len(parsed_pns_uf['by_mun'])} UFs (N3) + {len(parsed_pns_cap['by_mun'])} Capitais (N6)")

    transp_s = get_survey_by_id("CENSO22_MEIO_TRANSPORTE")
    plans_tr, _ = resolve_table_queries(transp_s, [2022], 1013377)
    raw_tr = client.query_series(
        plans_tr, territory="SC", level="N6",
        classification=2088, category=79194, extra_classifications={"1568": 120704, "86": 95251},
    )
    parsed_tr = client.parse_records(raw_tr, primary_var=1013377, agg_mode="mean")
    assert len(parsed_tr["by_mun"]) >= 250
    print(f"[OK] Censo 2022 Bicicleta SC N6: {len(parsed_tr['by_mun'])} municípios")

    cras_s = get_survey_by_id("MUNIC_REDE_SUAS_CRAS")
    plans_cras, _ = resolve_table_queries(cras_s, [2023], 13139)
    raw_cras = client.query_series(
        plans_cras, territory="SC", level="N6",
        classification=1914, category=72668,
        extra_classifications={"1906": 72643, "1915": 72801, "12446": 47692},
    )
    parsed_cras = client.parse_records(raw_cras, primary_var=13139, agg_mode="last")
    assert len(parsed_cras["by_mun"]) >= 250
    print(f"[OK] MUNIC 2023 SUAS/CRAS SC N6: {len(parsed_cras['by_mun'])} municípios com CRAS")

    etn_s = get_survey_by_id("CENSO22_ETNIAS_LINGUAS_IND")
    plans_etn, _ = resolve_table_queries(etn_s, [2022], 13596)
    raw_etn = client.query_series(plans_etn, territory="BR", level="N3")
    parsed_etn = client.parse_records(raw_etn, primary_var=13596, agg_mode="mean")
    assert len(parsed_etn["by_mun"]) == 27
    print(f"[OK] Censo 2022 Etnias Indígenas BR N3: {len(parsed_etn['by_mun'])} UFs")

    # 26. Fase 5: Meio Ambiente, Clima, Biodiversidade e ODS
    bio_s = get_survey_by_id("BIO_CONHECIMENTO_UF_MUN")
    plans_bio, _ = resolve_table_queries(bio_s, [2025], 2323)
    raw_bio = client.query_series(plans_bio, territory="BR", level="N3")
    parsed_bio = client.parse_records(raw_bio, primary_var=2323, agg_mode="mean")
    assert len(parsed_bio["by_mun"]) == 27
    print(f"[OK] Biodiversidade Conhecimento BR N3: {len(parsed_bio['by_mun'])} UFs")

    polin_s = get_survey_by_id("POLINIZADORES_VALOR_PRODUCAO")
    plans_polin, _ = resolve_table_queries(polin_s, [2023], 13521)
    raw_polin = client.query_series(plans_polin, territory="BR", level="N3", classification=2101, category=79453)
    parsed_polin = client.parse_records(raw_polin, primary_var=13521, agg_mode="mean")
    assert len(parsed_polin["by_mun"]) == 27
    print(f"[OK] Polinizadores Valor BR N3: {len(parsed_polin['by_mun'])} UFs")

    defesa_s = get_survey_by_id("MUNIC_DEFESA_CIVIL_ESTRUTURA")
    plans_defesa, _ = resolve_table_queries(defesa_s, [2020], 603)
    raw_defesa = client.query_series(
        plans_defesa, territory="SC", level="N6",
        classification=1239, category=51203,
        extra_classifications={"12446": 47692, "1244": 51238},
    )
    parsed_defesa = client.parse_records(raw_defesa, primary_var=603, agg_mode="last")
    parsed_defesa["is_binary"] = True
    assert len(parsed_defesa["by_mun"]) >= 280
    print(f"[OK] MUNIC 2020 Defesa Civil SC N6: {len(parsed_defesa['by_mun'])} municípios")

    ucs_s = get_survey_by_id("IDS_UNIDADES_CONSERVACAO_UF")
    plans_ucs, _ = resolve_table_queries(ucs_s, [2016], 6317)
    raw_ucs = client.query_series(plans_ucs, territory="BR", level="N3", classification=713, category=33558)
    parsed_ucs = client.parse_records(raw_ucs, primary_var=6317, agg_mode="mean")
    assert len(parsed_ucs["by_mun"]) == 27
    print(f"[OK] IDS Unidades de Conservação BR N3: {len(parsed_ucs['by_mun'])} UFs")

    desast_ods_s = get_survey_by_id("ODS_POPULACAO_AFETADA_DESASTRES")
    plans_desast, _ = resolve_table_queries(desast_ods_s, [2024], 9619)
    raw_desast = client.query_series(plans_desast, territory="BR", level="N3")
    parsed_desast = client.parse_records(raw_desast, primary_var=9619, agg_mode="mean")
    assert len(parsed_desast["by_mun"]) == 27
    print(f"[OK] ODS 11.5.1 População Afetada por Desastres BR N3: {len(parsed_desast['by_mun'])} UFs")

    ar_s = get_survey_by_id("ODS_QUALIDADE_AR_CIDADES")
    plans_ar, _ = resolve_table_queries(ar_s, [2024], 14035)
    raw_ar = client.query_series(plans_ar, territory="BR", level="N6")
    parsed_ar = client.parse_records(raw_ar, primary_var=14035, agg_mode="mean")
    assert len(parsed_ar["by_mun"]) >= 5
    print(f"[OK] ODS 11.6.2 Qualidade do Ar BR N6 (parcial): {len(parsed_ar['by_mun'])} cidades monitoradas")

    poluic_s = get_survey_by_id("ODS_MORTALIDADE_POLUICAO_AR")
    plans_poluic, _ = resolve_table_queries(poluic_s, [2023], 14195)
    raw_poluic = client.query_series(
        plans_poluic, territory="BR", level="N3",
        classification=2, category=6794,
        extra_classifications={"1481": 82768},
    )
    parsed_poluic = client.parse_records(raw_poluic, primary_var=14195, agg_mode="mean")
    assert len(parsed_poluic["by_mun"]) == 27
    print(f"[OK] ODS 3.9.1 Mortalidade Poluição do Ar BR N3: {len(parsed_poluic['by_mun'])} UFs")

    pobr_s = get_survey_by_id("ODS_POBREZA_VULNERABILIDADE_UF")
    plans_pobr, _ = resolve_table_queries(pobr_s, [2024], 9948)
    raw_pobr = client.query_series(plans_pobr, territory="BR", level="N3")
    parsed_pobr = client.parse_records(raw_pobr, primary_var=9948, agg_mode="mean")
    assert len(parsed_pobr["by_mun"]) == 27
    print(f"[OK] ODS 1.2.1 Linha de Pobreza Nacional BR N3: {len(parsed_pobr['by_mun'])} UFs")

    # 27. Fase 6 Infância, Juventude e Escolas (Censo 2022, MUNIC, PeNSE, ODS)
    creche_s = get_survey_by_id("CENSO22_CRECHE_PREESCOLA")
    plans_creche, _ = resolve_table_queries(creche_s, [2022], 13282)
    raw_creche = client.query_series(
        plans_creche, territory="SC", level="N6",
        classification=11798, category=95301,
        extra_classifications={"58": 99749, "2": 6794, "86": 95251},
    )
    parsed_creche = client.parse_records(raw_creche, primary_var=13282, agg_mode="sum")
    assert len(parsed_creche["by_mun"]) == 295
    print(f"[OK] Censo 2022 Creche e Pré-escola SC N6: {len(parsed_creche['by_mun'])} municípios")

    mun_cr_s = get_survey_by_id("MUNIC_AUXILIO_CRECHE")
    plans_mun_cr, _ = resolve_table_queries(mun_cr_s, [2023], 13279)
    raw_mun_cr = client.query_series(
        plans_mun_cr, territory="SC", level="N6",
        classification=2071, category=77571,
        extra_classifications={"12446": 47692},
    )
    parsed_mun_cr = client.parse_records(raw_mun_cr, primary_var=13279, agg_mode="last")
    parsed_mun_cr["is_binary"] = True
    assert len(parsed_mun_cr["by_mun"]) >= 280
    print(f"[OK] MUNIC 2023 Auxílio Creche SC N6: {len(parsed_mun_cr['by_mun'])} municípios")

    pense_b_s = get_survey_by_id("PENSE_BULLYING_SOFRIDO")
    plans_pense_b, _ = resolve_table_queries(pense_b_s, [2015], 7497)
    raw_pense_b = client.query_series(
        plans_pense_b, territory="BR", level="N3",
        classification=752, category=39832,
    )
    parsed_pense_b = client.parse_records(raw_pense_b, primary_var=7497, agg_mode="mean")
    assert len(parsed_pense_b["by_mun"]) == 27
    print(f"[OK] PeNSE Bullying Sofrido BR N3: {len(parsed_pense_b['by_mun'])} UFs")

    pense_bib_s = get_survey_by_id("PENSE_ESCOLA_BIBLIOTECA")
    plans_pense_bib, _ = resolve_table_queries(pense_bib_s, [2015], 7308)
    raw_pense_bib = client.query_series(
        plans_pense_bib, territory="BR", level="N3",
        classification=556, category=31050,
    )
    parsed_pense_bib = client.parse_records(raw_pense_bib, primary_var=7308, agg_mode="mean")
    assert len(parsed_pense_bib["by_mun"]) == 27
    print(f"[OK] PeNSE Biblioteca Escolar BR N3: {len(parsed_pense_bib['by_mun'])} UFs")

    ods_esc_s = get_survey_by_id("ODS_INFRAESTRUTURA_ESCOLAR")
    plans_ods_esc, _ = resolve_table_queries(ods_esc_s, [2024], 11085)
    raw_ods_esc = client.query_series(
        plans_ods_esc, territory="BR", level="N3",
        classification=812, category=41117,
    )
    parsed_ods_esc = client.parse_records(raw_ods_esc, primary_var=11085, agg_mode="mean")
    assert len(parsed_ods_esc["by_mun"]) == 27
    print(f"[OK] ODS Infraestrutura Escolar BR N3: {len(parsed_ods_esc['by_mun'])} UFs")

    # 28. Fase 7 Habitação, Favelas, Condições de Moradia e Entorno Urbano
    fav_pop_s = get_survey_by_id("FAVELAS_POPULACAO_COR_RACA")
    plans_fav_pop, _ = resolve_table_queries(fav_pop_s, [2022], 9612)
    raw_fav_pop = client.query_series(
        plans_fav_pop, territory="SC", level="N6",
        classification=86, category=95251,
        extra_classifications={"2": 6794, "58": 95253},
    )
    parsed_fav_pop = client.parse_records(raw_fav_pop, primary_var=9612, agg_mode="sum")
    assert len(parsed_fav_pop["by_mun"]) >= 10
    print(f"[OK] Censo 2022 População em Favelas SC N6: {len(parsed_fav_pop['by_mun'])} municípios com registros")

    dom_esp_s = get_survey_by_id("CENSO22_DOMICILIOS_ESPECIE")
    plans_dom_esp, _ = resolve_table_queries(dom_esp_s, [2022], 617)
    raw_dom_esp = client.query_series(
        plans_dom_esp, territory="SC", level="N6",
        classification=3, category=60002,
    )
    parsed_dom_esp = client.parse_records(raw_dom_esp, primary_var=617, agg_mode="sum")
    assert len(parsed_dom_esp["by_mun"]) == 295
    print(f"[OK] Censo 2022 Domicílios Vagos SC N6: {len(parsed_dom_esp['by_mun'])} municípios")

    paredes_s = get_survey_by_id("CENSO22_PAREDES_EXTERNAS")
    plans_paredes, _ = resolve_table_queries(paredes_s, [2022], 381)
    raw_paredes = client.query_series(
        plans_paredes, territory="SC", level="N6",
        classification=137, category=73073,
        extra_classifications={"63": 95826, "125": 2932},
    )
    parsed_paredes = client.parse_records(raw_paredes, primary_var=381, agg_mode="sum")
    assert len(parsed_paredes["by_mun"]) == 295
    print(f"[OK] Censo 2022 Paredes Revestidas SC N6: {len(parsed_paredes['by_mun'])} municípios")

    entorno_s = get_survey_by_id("CENSO22_ENTORNO_BUEIRO_ILUMINACAO")
    plans_entorno, _ = resolve_table_queries(entorno_s, [2022], 9599)
    raw_entorno = client.query_series(
        plans_entorno, territory="SC", level="N6",
        classification=14, category=72250,
        extra_classifications={"11558": 46292},
    )
    parsed_entorno = client.parse_records(raw_entorno, primary_var=9599, agg_mode="sum")
    assert len(parsed_entorno["by_mun"]) == 295
    print(f"[OK] Censo 2022 Entorno com Bueiro/Boca de Lobo SC N6: {len(parsed_entorno['by_mun'])} municípios")

    mun_hab_s = get_survey_by_id("MUNIC_PLANO_HABITACAO")
    plans_mun_hab, _ = resolve_table_queries(mun_hab_s, [2020], 603)
    raw_mun_hab = client.query_series(
        plans_mun_hab, territory="SC", level="N6",
        classification=1329, category=57147,
        extra_classifications={"12446": 47692},
    )
    parsed_mun_hab = client.parse_records(raw_mun_hab, primary_var=603, agg_mode="last")
    parsed_mun_hab["is_binary"] = True
    assert len(parsed_mun_hab["by_mun"]) >= 280
    print(f"[OK] MUNIC 2020 Plano Municipal de Habitação SC N6: {len(parsed_mun_hab['by_mun'])} municípios")

    # 29. Fase 8 Segurança Pública, Vitimização, Justiça e Defesa Social
    ods_hom_s = get_survey_by_id("ODS_HOMICIDIOS_TAXA")
    plans_ods_hom, _ = resolve_table_queries(ods_hom_s, [2024], 13532)
    raw_ods_hom = client.query_series(plans_ods_hom, territory="BR", level="N3")
    parsed_ods_hom = client.parse_records(raw_ods_hom, primary_var=13532, agg_mode="mean")
    assert len(parsed_ods_hom["by_mun"]) == 27
    print(f"[OK] ODS 16 Homicídios Taxa 2024 BR N3: {len(parsed_ods_hom['by_mun'])} UFs, média {parsed_ods_hom['mean_value']:.1f} / 100 mil hab.")

    pnad_v_s = get_survey_by_id("PNAD_VITIMAS_ROUBO")
    plans_pnad_v, _ = resolve_table_queries(pnad_v_s, [2021], 12452)
    raw_pnad_v = client.query_series(
        plans_pnad_v, territory="BR", level="N3",
        classification=1351, category=57304,
    )
    parsed_pnad_v = client.parse_records(raw_pnad_v, primary_var=12452, agg_mode="sum")
    assert len(parsed_pnad_v["by_mun"]) == 27
    print(f"[OK] PNAD Vitimização Roubo 2021 BR N3: {len(parsed_pnad_v['by_mun'])} UFs")

    mun_s_est = get_survey_by_id("MUNIC_SEGURANCA_ESTRUTURA")
    plans_mun_s, _ = resolve_table_queries(mun_s_est, [2023], 8934)
    raw_mun_s = client.query_series(
        plans_mun_s, territory="SC", level="N6",
        classification=1048, category=49367,
        extra_classifications={"12446": 47692},
    )
    parsed_mun_s = client.parse_records(raw_mun_s, primary_var=8934, agg_mode="last")
    parsed_mun_s["is_binary"] = True
    assert len(parsed_mun_s["by_mun"]) >= 280
    print(f"[OK] MUNIC 2023 Estrutura de Segurança SC N6: {len(parsed_mun_s['by_mun'])} municípios")

    mun_inst = get_survey_by_id("MUNIC_INSTITUICOES_SEGURANCA")
    plans_inst, _ = resolve_table_queries(mun_inst, [2023], 603)
    raw_inst = client.query_series(
        plans_inst, territory="SC", level="N6",
        classification=2010, category=73549,
    )
    parsed_inst = client.parse_records(raw_inst, primary_var=603, agg_mode="last")
    parsed_inst["is_binary"] = True
    assert len(parsed_inst["by_mun"]) >= 280
    print(f"[OK] MUNIC 2023 Presença IML/Guarda/Bombeiros SC N6: {len(parsed_inst['by_mun'])} municípios")

    mun_mulh = get_survey_by_id("MUNIC_MULHER_CASAS_ABRIGO")
    plans_mulh, _ = resolve_table_queries(mun_mulh, [2023], 603)
    raw_mulh = client.query_series(
        plans_mulh, territory="SC", level="N6",
        classification=1999, category=73130,
    )
    parsed_mulh = client.parse_records(raw_mulh, primary_var=603, agg_mode="last")
    parsed_mulh["is_binary"] = True
    assert len(parsed_mulh["by_mun"]) >= 280
    print(f"[OK] MUNIC 2023 Casas-Abrigo Violência Mulher SC N6: {len(parsed_mulh['by_mun'])} municípios")

    # 30. Fase 9 Cultura, Patrimônio Histórico, Turismo e Esporte
    equip_s = get_survey_by_id("MUNIC_CULTURA_EQUIPAMENTOS")
    plans_equip, _ = resolve_table_queries(equip_s, [2021], 12836)
    raw_equip = client.query_series(
        plans_equip, territory="SC", level="N6",
        classification=1547, category=59153,
        extra_classifications={"12446": 47692},
    )
    parsed_equip = client.parse_records(raw_equip, primary_var=12836, agg_mode="last")
    parsed_equip["is_binary"] = True
    assert len(parsed_equip["by_mun"]) >= 280
    print(f"[OK] MUNIC 2021 Bibliotecas SC N6: {len(parsed_equip['by_mun'])} municípios")

    patr_s = get_survey_by_id("MUNIC_PATRIMONIO_LEGISLACAO_TOMBAMENTO")
    plans_patr, _ = resolve_table_queries(patr_s, [2021], 603)
    raw_patr = client.query_series(
        plans_patr, territory="SC", level="N6",
        classification=1535, category=58904,
        extra_classifications={"12446": 47692},
    )
    parsed_patr = client.parse_records(raw_patr, primary_var=603, agg_mode="last")
    parsed_patr["is_binary"] = True
    assert len(parsed_patr["by_mun"]) >= 280
    print(f"[OK] MUNIC 2021 Legislação Tombamento SC N6: {len(parsed_patr['by_mun'])} municípios")

    esporte_s = get_survey_by_id("MUNIC_ESPORTE_TIPOS_INSTALACOES")
    plans_esp, _ = resolve_table_queries(esporte_s, [2021], 12849)
    raw_esp = client.query_series(
        plans_esp, territory="SC", level="N6",
        classification=1575, category=59346,
        extra_classifications={"12446": 47692},
    )
    parsed_esp = client.parse_records(raw_esp, primary_var=12849, agg_mode="last")
    parsed_esp["is_binary"] = True
    assert len(parsed_esp["by_mun"]) >= 280
    print(f"[OK] MUNIC 2021 Ginásios Esportivos SC N6: {len(parsed_esp['by_mun'])} municípios")

    hosp_s = get_survey_by_id("PSH_HOSPEDAGEM_CATEGORIAS")
    plans_hosp, _ = resolve_table_queries(hosp_s, [2016], 9298)
    raw_hosp = client.query_series(plans_hosp, territory="SC", level="N6", classification=492, category=40476)
    parsed_hosp = client.parse_records(raw_hosp, primary_var=9298, agg_mode="last")
    assert len(parsed_hosp["by_mun"]) >= 100
    print(f"[OK] PSH 2016 Hospedagem SC N6: {len(parsed_hosp['by_mun'])} municípios com registros")

    viag_s = get_survey_by_id("PNAD_TURISMO_VIAGENS_HOSPEDAGEM")
    plans_viag, _ = resolve_table_queries(viag_s, [2023], 10390)
    raw_viag = client.query_series(plans_viag, territory="BR", level="N3", classification=907, category=48083)
    parsed_viag = client.parse_records(raw_viag, primary_var=10390, agg_mode="sum")
    assert len(parsed_viag["by_mun"]) == 27
    print(f"[OK] PNAD Turismo Viagens 2023 BR N3: {len(parsed_viag['by_mun'])} UFs, {parsed_viag['total']:,.0f} mil viagens")

    # Fase 10 (Finanças Públicas e Gestão Fiscal - FINBRA / PIB / MUNIC)
    fin_rec_s = get_survey_by_id("FINBRA_RECEITAS_TOTAIS")
    plans_fin_rec, _ = resolve_table_queries(fin_rec_s, [2022], 1)
    raw_fin_rec = client.query_series(plans_fin_rec, territory="SC", level="N6")
    parsed_fin_rec = client.parse_records(raw_fin_rec, primary_var=1, agg_mode="sum")
    assert len(parsed_fin_rec["by_mun"]) >= 280
    assert parsed_fin_rec["total"] > 10_000_000_000
    print(f"[OK] FINBRA Receitas Totais 2022 SC N6: {len(parsed_fin_rec['by_mun'])} municípios, R$ {parsed_fin_rec['total']:,.2f}")

    fin_cor_s = get_survey_by_id("FINBRA_RECEITAS_CORRENTES")
    plans_fin_cor, _ = resolve_table_queries(fin_cor_s, [2022], 1)
    raw_fin_cor = client.query_series(plans_fin_cor, territory="BR", level="N3")
    parsed_fin_cor = client.parse_records(raw_fin_cor, primary_var=1, agg_mode="sum")
    assert len(parsed_fin_cor["by_mun"]) == 27
    assert parsed_fin_cor["total"] > 1_000_000_000_000
    print(f"[OK] FINBRA Receitas Correntes 2022 BR N3: {len(parsed_fin_cor['by_mun'])} UFs, R$ {parsed_fin_cor['total']:,.2f}")

    pib_imp_s = get_survey_by_id("PIB_IMPOSTOS_PRODUTOS")
    plans_pib_imp, _ = resolve_table_queries(pib_imp_s, [2023], 543)
    raw_pib_imp = client.query_series(plans_pib_imp, territory="SC", level="N6")
    parsed_pib_imp = client.parse_records(raw_pib_imp, primary_var=543, agg_mode="sum")
    assert len(parsed_pib_imp["by_mun"]) >= 280
    print(f"[OK] PIB Impostos sobre Produtos 2023 SC N6: {len(parsed_pib_imp['by_mun'])} municípios")

    mun_trib_s = get_survey_by_id("MUNIC_LEGISLACAO_TRIBUTARIA_URBANA")
    plans_mun_trib, _ = resolve_table_queries(mun_trib_s, [2021], 603)
    raw_mun_trib = client.query_series(
        plans_mun_trib, territory="SC", level="N6",
        classification=1674, category=59788,
        extra_classifications={"12446": 47692},
    )
    parsed_mun_trib = client.parse_records(raw_mun_trib, primary_var=603, agg_mode="last")
    parsed_mun_trib["is_binary"] = True
    assert len(parsed_mun_trib["by_mun"]) >= 280
    print(f"[OK] MUNIC 2021 Contribuição de Melhoria SC N6: {len(parsed_mun_trib['by_mun'])} municípios")

    mun_fnd_s = get_survey_by_id("MUNIC_CONSELHO_FUNDEB_FISCALIZACAO")
    plans_mun_fnd, _ = resolve_table_queries(mun_fnd_s, [2021], 12817)
    raw_mun_fnd = client.query_series(
        plans_mun_fnd, territory="SC", level="N6",
        classification=1510, category=58783,
        extra_classifications={"1164": 50632, "12446": 47692},
    )
    parsed_mun_fnd = client.parse_records(raw_mun_fnd, primary_var=12817, agg_mode="last")
    parsed_mun_fnd["is_binary"] = True
    assert len(parsed_mun_fnd["by_mun"]) >= 280
    print(f"[OK] MUNIC 2021 Conselho FUNDEB SC N6: {len(parsed_mun_fnd['by_mun'])} municípios")

    # Fase 11 (Transporte, Mobilidade Urbana e Frota de Veículos - SENATRAN / MUNIC / ODS)
    frota_tot_s = get_survey_by_id("FROTA_TOTAL")
    plans_frota_tot, _ = resolve_table_queries(frota_tot_s, [2024], 28120)
    raw_frota_tot = client.query_series(plans_frota_tot, territory="SC", level="N6")
    parsed_frota_tot = client.parse_records(raw_frota_tot, primary_var=28120, agg_mode="sum")
    assert len(parsed_frota_tot["by_mun"]) >= 280
    assert parsed_frota_tot["total"] > 6_000_000
    print(f"[OK] SENATRAN Frota Total 2024 SC N6: {len(parsed_frota_tot['by_mun'])} municípios, {parsed_frota_tot['total']:,.0f} veículos")

    frota_auto_s = get_survey_by_id("FROTA_AUTOMOVEIS")
    plans_frota_auto, _ = resolve_table_queries(frota_auto_s, [2024], 28122)
    raw_frota_auto = client.query_series(plans_frota_auto, territory="BR", level="N3")
    parsed_frota_auto = client.parse_records(raw_frota_auto, primary_var=28122, agg_mode="sum")
    assert len(parsed_frota_auto["by_mun"]) == 27
    assert parsed_frota_auto["total"] > 50_000_000
    print(f"[OK] SENATRAN Automóveis 2024 BR N3: {len(parsed_frota_auto['by_mun'])} UFs, {parsed_frota_auto['total']:,.0f} automóveis")

    frota_moto_s = get_survey_by_id("FROTA_MOTOCICLETAS")
    plans_frota_moto, _ = resolve_table_queries(frota_moto_s, [2024], 28128)
    raw_frota_moto = client.query_series(plans_frota_moto, territory="SC", level="N6")
    parsed_frota_moto = client.parse_records(raw_frota_moto, primary_var=28128, agg_mode="sum")
    assert len(parsed_frota_moto["by_mun"]) >= 280
    print(f"[OK] SENATRAN Motocicletas 2024 SC N6: {len(parsed_frota_moto['by_mun'])} municípios, {parsed_frota_moto['total']:,.0f} motos")

    mun_ciclo_s = get_survey_by_id("MUNIC_CICLOVIAS_BICICLETARIOS")
    plans_mun_ciclo, _ = resolve_table_queries(mun_ciclo_s, [2020], 603)
    raw_mun_ciclo = client.query_series(
        plans_mun_ciclo, territory="SC", level="N6",
        classification=1094, category=50287,
        extra_classifications={"12446": 47692},
    )
    parsed_mun_ciclo = client.parse_records(raw_mun_ciclo, primary_var=603, agg_mode="last")
    parsed_mun_ciclo["is_binary"] = True
    assert len(parsed_mun_ciclo["by_mun"]) >= 280
    print(f"[OK] MUNIC 2020 Ciclovias SC N6: {len(parsed_mun_ciclo['by_mun'])} municípios")

    ods_trans_s = get_survey_by_id("ODS_MORTALIDADE_TRANSITO")
    plans_ods_trans, _ = resolve_table_queries(ods_trans_s, [2024], 9734)
    raw_ods_trans = client.query_series(
        plans_ods_trans, territory="BR", level="N3",
        classification=2, category=6794,
        extra_classifications={"58": 95253},
    )
    parsed_ods_trans = client.parse_records(raw_ods_trans, primary_var=9734, agg_mode="mean")
    assert len(parsed_ods_trans["by_mun"]) == 27
    print(f"[OK] ODS 3.6.1 Taxa Mortalidade Trânsito 2024 BR N3: {len(parsed_ods_trans['by_mun'])} UFs, média {parsed_ods_trans.get('mean_value', 0.0):.1f} / 100 mil")

    # Fase 12 (Inovação Tecnológica, P&D e Governo Digital - PINTEC / MUNIC 2024 / ODS)
    pintec_taxa_s = get_survey_by_id("PINTEC_UF_TAXA_INOVACAO")
    plans_ptx, _ = resolve_table_queries(pintec_taxa_s, [2017], 82735)
    raw_ptx = client.query_series(plans_ptx, territory="BR", level="N3")
    parsed_ptx = client.parse_records(raw_ptx, primary_var=82735, agg_mode="mean")
    assert len(parsed_ptx["by_mun"]) >= 15
    assert 10.0 < parsed_ptx.get("mean_value", 0.0) < 80.0
    print(f"[OK] PINTEC UF Taxa de Inovação 2017 BR N3: {len(parsed_ptx['by_mun'])} UFs, média {parsed_ptx.get('mean_value', 0.0):.1f}%")

    pintec_pd_s = get_survey_by_id("PINTEC_UF_DISPENDIO_PD_INTERNO")
    plans_ppd, _ = resolve_table_queries(pintec_pd_s, [2017], 60214)
    raw_ppd = client.query_series(plans_ppd, territory="BR", level="N3")
    parsed_ppd = client.parse_records(raw_ppd, primary_var=60214, agg_mode="last")
    assert len(parsed_ppd["by_mun"]) >= 15
    assert 1_000_000 < parsed_ppd["total"] < 1e12, f"Sigilo não filtrado no total PINTEC P&D: {parsed_ppd['total']}"
    print(f"[OK] PINTEC UF Dispêndio P&D Interno 2017 BR N3: {len(parsed_ppd['by_mun'])} UFs, R$ {parsed_ppd['total']:,.0f} mil")

    pintec_apoio_s = get_survey_by_id("PINTEC_APOIO_GOVERNAMENTAL")
    plans_pap, _ = resolve_table_queries(pintec_apoio_s, [2017], 6544)
    raw_pap = client.query_series(
        plans_pap, territory="BR", level="N1",
        classification=729, category=39280,
        extra_classifications={"696": 33413},
    )
    parsed_pap = client.parse_records(raw_pap, primary_var=6544, agg_mode="last")
    assert parsed_pap["total"] >= 500
    print(f"[OK] PINTEC Lei do Bem / Apoio P&D 2017 BR N1: {parsed_pap['total']:,.0f} empresas")

    mun_lgpd_s = get_survey_by_id("MUNIC_LGPD_GOVERNANCA_DADOS")
    plans_lgpd, _ = resolve_table_queries(mun_lgpd_s, [2024], 326148)
    raw_lgpd = client.query_series(plans_lgpd, territory="SC", level="N6")
    parsed_lgpd = client.parse_records(raw_lgpd, primary_var=326148, agg_mode="last")
    parsed_lgpd["is_binary"] = True
    assert len(parsed_lgpd["by_mun"]) >= 250
    assert all(len(cd) == 7 for cd in parsed_lgpd["by_mun"].keys()), "Código IBGE de MUNIC 2024 deve ter 7 dígitos"
    print(f"[OK] MUNIC 2024 LGPD SC N6: {len(parsed_lgpd['by_mun'])} municípios")

    ods_tec_s = get_survey_by_id("ODS_9B1_INDUSTRIA_ALTA_TEC_UF")
    plans_otec, _ = resolve_table_queries(ods_tec_s, [2021], 9315)
    raw_otec = client.query_series(plans_otec, territory="BR", level="N3")
    parsed_otec = client.parse_records(raw_otec, primary_var=9315, agg_mode="mean")
    assert len(parsed_otec["by_mun"]) == 27
    print(f"[OK] ODS 9.b.1 Indústria Média/Alta Tecnologia 2021 BR N3: {len(parsed_otec['by_mun'])} UFs, média {parsed_otec.get('mean_value', 0.0):.1f}%")

    # Fase 13: Vulnerabilidade Territorial, Riscos de Desastres e Bancarização (CEMADEN / BACEN / PNSB / Censo Agro / MUNIC / ODS)
    cem_s = get_survey_by_id("CEMADEN_POPULACAO_RISCO")
    plans_cem_sc, _ = resolve_table_queries(cem_s, [2010], 353155)
    raw_cem_sc = client.query_series(plans_cem_sc, territory="SC", level="N6")
    parsed_cem_sc = client.parse_records(raw_cem_sc, primary_var=353155, agg_mode="sum")
    assert len(parsed_cem_sc["by_mun"]) == 79
    assert parsed_cem_sc["total"] > 300_000
    print(f"[OK] CEMADEN População em Risco 2010 SC N6: {len(parsed_cem_sc['by_mun'])} municípios, {parsed_cem_sc['total']:,.0f} pessoas")

    raw_cem_br = client.query_series(plans_cem_sc, territory="BR", level="N3")
    parsed_cem_br = client.parse_records(raw_cem_br, primary_var=353155, agg_mode="sum")
    assert len(parsed_cem_br["by_mun"]) == 27
    assert parsed_cem_br["total"] > 8_000_000
    print(f"[OK] CEMADEN População em Risco 2010 BR N3: {len(parsed_cem_br['by_mun'])} UFs, {parsed_cem_br['total']:,.0f} pessoas no Brasil")

    bac_s = get_survey_by_id("BACEN_AGENCIAS_BANCARIAS")
    plans_bac_sc, _ = resolve_table_queries(bac_s, [2024], 21910)
    raw_bac_sc = client.query_series(plans_bac_sc, territory="SC", level="N6")
    parsed_bac_sc = client.parse_records(raw_bac_sc, primary_var=21910, agg_mode="last")
    assert len(parsed_bac_sc["by_mun"]) >= 150
    assert parsed_bac_sc["total"] >= 500
    print(f"[OK] BACEN Agências Bancárias 2024 SC N6: {len(parsed_bac_sc['by_mun'])} municípios, {parsed_bac_sc['total']:,.0f} agências")

    raw_bac_br = client.query_series(plans_bac_sc, territory="BR", level="N3")
    parsed_bac_br = client.parse_records(raw_bac_br, primary_var=21910, agg_mode="last")
    assert len(parsed_bac_br["by_mun"]) == 27
    assert parsed_bac_br["total"] > 10_000
    print(f"[OK] BACEN Agências Bancárias 2024 BR N3: {len(parsed_bac_br['by_mun'])} UFs, {parsed_bac_br['total']:,.0f} agências no Brasil")

    bac_cr_s = get_survey_by_id("BACEN_OPERACOES_CREDITO")
    plans_bcr, _ = resolve_table_queries(bac_cr_s, [2024], 21912)
    raw_bcr = client.query_series(plans_bcr, territory="BR", level="N3")
    parsed_bcr = client.parse_records(raw_bcr, primary_var=21912, agg_mode="last")
    assert len(parsed_bcr["by_mun"]) == 27
    assert parsed_bcr["total"] > 1_000_000
    print(f"[OK] BACEN Operações de Crédito 2024 BR N3: {len(parsed_bcr['by_mun'])} UFs, R$ {parsed_bcr['total']:,.0f} mil")

    cag_s = get_survey_by_id("CENSO_AGRO_CREDITO_AGENTES")
    plans_cag, _ = resolve_table_queries(cag_s, [2017], 1990)
    raw_cag = client.query_series(
        plans_cag, territory="BR", level="N3",
        classification=12542, category=111915,
        extra_classifications={"829": 46302, "218": 46502, "12517": 113601, "12544": 115949, "220": 110085},
    )
    parsed_cag = client.parse_records(raw_cag, primary_var=1990, agg_mode="sum")
    assert len(parsed_cag["by_mun"]) == 27
    assert parsed_cag["total"] > 50_000
    print(f"[OK] Censo Agro 2017 Crédito Rural Bancos BR N3: {len(parsed_cag['by_mun'])} UFs, {parsed_cag['total']:,.0f} estabelecimentos")

    pnsb_s = get_survey_by_id("PNSB_AREAS_RISCO_DRENAGEM")
    plans_pnsb, _ = resolve_table_queries(pnsb_s, [2008], 1178)
    raw_pnsb = client.query_series(
        plans_pnsb, territory="BR", level="N3",
        classification=12140, category=101376,
    )
    parsed_pnsb = client.parse_records(raw_pnsb, primary_var=1178, agg_mode="last")
    assert len(parsed_pnsb["by_mun"]) == 27
    assert parsed_pnsb["total"] > 100
    print(f"[OK] PNSB Áreas de Risco Drenagem 2008 BR N3: {len(parsed_pnsb['by_mun'])} UFs, {parsed_pnsb['total']:,.0f} municípios")

    pmrr_s = get_survey_by_id("MUNIC_PMRR_INSTRUMENTOS_RISCO")
    plans_pmrr, _ = resolve_table_queries(pmrr_s, [2020], 92534)
    raw_pmrr = client.query_series(plans_pmrr, territory="SC", level="N6")
    parsed_pmrr = client.parse_records(raw_pmrr, primary_var=92534, agg_mode="last")
    parsed_pmrr["is_binary"] = True
    assert len(parsed_pmrr["by_mun"]) >= 250
    print(f"[OK] MUNIC 2020 PMRR SC N6: {len(parsed_pmrr['by_mun'])} municípios")

    # Fase 14: Territórios Tradicionais, Terras Indígenas e Comunidades Quilombolas (Censo 2022)
    # 1. População Indígena (Tabela 9718) em N6 (AM) e N3 (BR)
    ind_s = get_survey_by_id("CENSO22_INDIGENA_LOCALIZACAO")
    plans_ind_am, _ = resolve_table_queries(ind_s, [2022], 350)
    raw_ind_am = client.query_series(
        plans_ind_am, territory="AM", level="N6",
        classification=2661, category=32776,
        extra_classifications={"1714": 60024},
    )
    parsed_ind_am = client.parse_records(raw_ind_am, primary_var=350, agg_mode="sum")
    assert len(parsed_ind_am["by_mun"]) >= 60
    assert parsed_ind_am["total"] > 400_000
    print(f"[OK] Censo 2022 População Indígena AM N6: {len(parsed_ind_am['by_mun'])} municípios, {parsed_ind_am['total']:,.0f} indígenas")

    raw_ind_br = client.query_series(
        plans_ind_am, territory="BR", level="N3",
        classification=2661, category=32776,
        extra_classifications={"1714": 60024},
    )
    parsed_ind_br = client.parse_records(raw_ind_br, primary_var=350, agg_mode="sum")
    assert len(parsed_ind_br["by_mun"]) == 27
    assert parsed_ind_br["total"] > 1_600_000
    print(f"[OK] Censo 2022 População Indígena BR N3: {len(parsed_ind_br['by_mun'])} UFs, {parsed_ind_br['total']:,.0f} indígenas no Brasil")

    # 2. População Quilombola (Tabela 9578) em N6 (BA) e N3 (BR)
    qui_s = get_survey_by_id("CENSO22_QUILOMBOLA_LOCALIZACAO")
    plans_qui_ba, _ = resolve_table_queries(qui_s, [2022], 4709)
    raw_qui_ba = client.query_series(
        plans_qui_ba, territory="BA", level="N6",
        classification=2661, category=32776,
    )
    parsed_qui_ba = client.parse_records(raw_qui_ba, primary_var=4709, agg_mode="sum")
    assert len(parsed_qui_ba["by_mun"]) >= 100
    assert parsed_qui_ba["total"] > 350_000
    print(f"[OK] Censo 2022 População Quilombola BA N6: {len(parsed_qui_ba['by_mun'])} municípios, {parsed_qui_ba['total']:,.0f} quilombolas")

    raw_qui_br = client.query_series(
        plans_qui_ba, territory="BR", level="N3",
        classification=2661, category=32776,
    )
    parsed_qui_br = client.parse_records(raw_qui_br, primary_var=4709, agg_mode="sum")
    assert len(parsed_qui_br["by_mun"]) == 27
    assert parsed_qui_br["total"] > 1_300_000
    print(f"[OK] Censo 2022 População Quilombola BR N3: {len(parsed_qui_br['by_mun'])} UFs, {parsed_qui_br['total']:,.0f} quilombolas no Brasil")

    # 3. Domicílios com Presença Quilombola por Abastecimento de Água (Tabela 9804 em N3)
    qui_agua_s = get_survey_by_id("CENSO22_QUILOMBOLA_ABASTECIMENTO_AGUA")
    plans_qagua, _ = resolve_table_queries(qui_agua_s, [2022], 7081)
    raw_qagua = client.query_series(
        plans_qagua, territory="BR", level="N3",
        classification=1821, category=72129,
        extra_classifications={"2661": 32776},
    )
    parsed_qagua = client.parse_records(raw_qagua, primary_var=7081, agg_mode="sum")
    assert len(parsed_qagua["by_mun"]) == 27
    assert parsed_qagua["total"] > 400_000
    print(f"[OK] Censo 2022 Domicílios com Quilombolas BR N3: {len(parsed_qagua['by_mun'])} UFs, {parsed_qagua['total']:,.0f} domicílios")

    # 31. AnalyticsEngine + ReportRenderer para aditivos, negativos, médias, binários (MUNIC), IPCA N7_N6, Grandes Regiões N2 e Fases 5-14
    reports_bio = AnalyticsEngine.generate_all_reports(parsed_bio, territory_label="Brasil")
    reports_defesa = AnalyticsEngine.generate_all_reports(parsed_defesa, territory_label="Santa Catarina")
    assert any(r.report_id == "ranking_top_producers" for r in reports_bio)
    assert reports_defesa[-1].table_spec and reports_defesa[-1].table_spec.totals_row[1] == "TOTAL SIM (VALOR = 1)"
    reports_creche = AnalyticsEngine.generate_all_reports(parsed_creche, territory_label="Santa Catarina")
    reports_pense = AnalyticsEngine.generate_all_reports(parsed_pense_b, territory_label="Brasil")
    reports_mun_cr = AnalyticsEngine.generate_all_reports(parsed_mun_cr, territory_label="Santa Catarina")
    reports_fav = AnalyticsEngine.generate_all_reports(parsed_fav_pop, territory_label="Santa Catarina")
    reports_dom = AnalyticsEngine.generate_all_reports(parsed_dom_esp, territory_label="Santa Catarina")
    reports_hab = AnalyticsEngine.generate_all_reports(parsed_mun_hab, territory_label="Santa Catarina")
    reports_ods_hom = AnalyticsEngine.generate_all_reports(parsed_ods_hom, territory_label="Brasil")
    reports_pnad_v = AnalyticsEngine.generate_all_reports(parsed_pnad_v, territory_label="Brasil")
    reports_mun_s = AnalyticsEngine.generate_all_reports(parsed_mun_s, territory_label="Santa Catarina")
    reports_equip = AnalyticsEngine.generate_all_reports(parsed_equip, territory_label="Santa Catarina")
    reports_viag = AnalyticsEngine.generate_all_reports(parsed_viag, territory_label="Brasil")
    reports_fin_rec = AnalyticsEngine.generate_all_reports(parsed_fin_rec, territory_label="Santa Catarina")
    reports_fin_cor = AnalyticsEngine.generate_all_reports(parsed_fin_cor, territory_label="Brasil")
    reports_mun_trib = AnalyticsEngine.generate_all_reports(parsed_mun_trib, territory_label="Santa Catarina")
    reports_frota_tot = AnalyticsEngine.generate_all_reports(parsed_frota_tot, territory_label="Santa Catarina")
    reports_frota_auto = AnalyticsEngine.generate_all_reports(parsed_frota_auto, territory_label="Brasil")
    reports_mun_ciclo = AnalyticsEngine.generate_all_reports(parsed_mun_ciclo, territory_label="Santa Catarina")
    reports_ods_trans = AnalyticsEngine.generate_all_reports(parsed_ods_trans, territory_label="Brasil")
    reports_ptx = AnalyticsEngine.generate_all_reports(parsed_ptx, territory_label="Brasil")
    reports_ppd = AnalyticsEngine.generate_all_reports(parsed_ppd, territory_label="Brasil")
    reports_lgpd = AnalyticsEngine.generate_all_reports(parsed_lgpd, territory_label="Santa Catarina")
    reports_otec = AnalyticsEngine.generate_all_reports(parsed_otec, territory_label="Brasil")
    reports_cem = AnalyticsEngine.generate_all_reports(parsed_cem_br, territory_label="Brasil")
    reports_pmrr = AnalyticsEngine.generate_all_reports(parsed_pmrr, territory_label="Santa Catarina")
    reports_ind = AnalyticsEngine.generate_all_reports(parsed_ind_am, territory_label="Amazonas")
    reports_qui = AnalyticsEngine.generate_all_reports(parsed_qui_ba, territory_label="Bahia")
    assert any(r.report_id == "ranking_top_producers" for r in reports_ind)
    assert any(r.report_id == "ranking_top_producers" for r in reports_qui)
    assert any(r.report_id == "lorenz_concentration" for r in reports_ind)
    assert any(r.report_id == "lorenz_concentration" for r in reports_qui)
    assert any(r.report_id == "lorenz_concentration" for r in reports_creche)
    assert any(r.report_id == "lorenz_concentration" for r in reports_dom)
    assert any(r.report_id == "lorenz_concentration" for r in reports_pnad_v)
    assert any(r.report_id == "lorenz_concentration" for r in reports_viag)
    assert any(r.report_id == "lorenz_concentration" for r in reports_fin_rec)
    assert any(r.report_id == "lorenz_concentration" for r in reports_fin_cor)
    assert any(r.report_id == "lorenz_concentration" for r in reports_frota_tot)
    assert any(r.report_id == "lorenz_concentration" for r in reports_frota_auto)
    assert any(r.report_id == "lorenz_concentration" for r in reports_ppd)
    assert any(r.report_id == "lorenz_concentration" for r in reports_cem)
    assert not any(r.report_id == "lorenz_concentration" for r in reports_pense)
    assert not any(r.report_id == "lorenz_concentration" for r in reports_ods_hom)
    assert not any(r.report_id == "lorenz_concentration" for r in reports_ods_trans)
    assert not any(r.report_id == "lorenz_concentration" for r in reports_ptx)
    assert not any(r.report_id == "lorenz_concentration" for r in reports_otec)
    assert reports_mun_cr[-1].table_spec and reports_mun_cr[-1].table_spec.totals_row[1] == "TOTAL SIM (VALOR = 1)"
    assert reports_hab[-1].table_spec and reports_hab[-1].table_spec.totals_row[1] == "TOTAL SIM (VALOR = 1)"
    assert reports_mun_s[-1].table_spec and reports_mun_s[-1].table_spec.totals_row[1] == "TOTAL SIM (VALOR = 1)"
    assert reports_equip[-1].table_spec and reports_equip[-1].table_spec.totals_row[1] == "TOTAL SIM (VALOR = 1)"
    assert reports_mun_trib[-1].table_spec and reports_mun_trib[-1].table_spec.totals_row[1] == "TOTAL SIM (VALOR = 1)"
    assert reports_mun_ciclo[-1].table_spec and reports_mun_ciclo[-1].table_spec.totals_row[1] == "TOTAL SIM (VALOR = 1)"
    assert reports_lgpd[-1].table_spec and reports_lgpd[-1].table_spec.totals_row[1] == "TOTAL SIM (VALOR = 1)"
    assert reports_pmrr[-1].table_spec and reports_pmrr[-1].table_spec.totals_row[1] == "TOTAL SIM (VALOR = 1)"
    reports_add = AnalyticsEngine.generate_all_reports(parsed_cem, territory_label="Santa Catarina")
    reports_neg = AnalyticsEngine.generate_all_reports(parsed_cres, territory_label="Rio Grande do Sul")
    reports_mean = AnalyticsEngine.generate_all_reports(parsed_alfa, territory_label="Santa Catarina")
    reports_pnad = AnalyticsEngine.generate_all_reports(parsed_pnad, territory_label="Brasil")
    reports_mei = AnalyticsEngine.generate_all_reports(parsed_mei, territory_label="Brasil")
    reports_bin = AnalyticsEngine.generate_all_reports(parsed_mun, territory_label="Santa Catarina")
    reports_pim = AnalyticsEngine.generate_all_reports(parsed_pim, territory_label="Brasil")
    reports_proj = AnalyticsEngine.generate_all_reports(parsed_proj, territory_label="Brasil")
    parsed_ipca["level"] = "N7_N6"
    parsed_pnad_n2["level"] = "N2"
    reports_ipca = AnalyticsEngine.generate_all_reports(parsed_ipca, territory_label="Brasil")
    reports_n2 = AnalyticsEngine.generate_all_reports(parsed_pnad_n2, territory_label="Brasil")
    assert any(r.report_id == "lorenz_concentration" for r in reports_add)
    assert not any(r.report_id == "lorenz_concentration" for r in reports_neg), "Taxa negativa não deve gerar Lorenz/Gini"
    assert not any(r.report_id == "lorenz_concentration" for r in reports_mean), "Média não-aditiva não deve gerar Lorenz/Gini"
    assert not any(r.report_id in ("lorenz_concentration", "donut_structure") for r in reports_mei), "Indicador allow_negative não deve gerar Lorenz/Donut"
    assert not any(r.report_id in ("lorenz_concentration", "donut_structure") for r in reports_bin), "Indicador binário não deve gerar Lorenz/Donut"
    assert not any(r.report_id in ("lorenz_concentration", "donut_structure") for r in reports_pim), "PIM-PF allow_negative/mean não deve gerar Lorenz/Donut"
    assert not any(r.report_id in ("lorenz_concentration", "donut_structure") for r in reports_proj), "Projeção mean não deve gerar Lorenz/Donut"
    assert not any(r.report_id in ("lorenz_concentration", "donut_structure") for r in reports_ipca), "IPCA allow_negative/mean não deve gerar Lorenz/Donut"
    assert "Municípios com Sim (= 1)" in reports_bin[0].summary_metrics
    assert reports_bin[-1].table_spec and reports_bin[-1].table_spec.totals_row[1] == "TOTAL SIM (VALOR = 1)"

    with tempfile.TemporaryDirectory() as tmpdir:
        for b in (
            reports_add[0], reports_neg[0], reports_neg[-1], reports_mean[0],
            reports_pnad[0], reports_mei[0], reports_bin[0], reports_bin[-1],
            reports_pim[0], reports_proj[0], reports_ipca[0], reports_ipca[1], reports_n2[0],
            reports_creche[0], reports_pense[0], reports_mun_cr[0],
            reports_fav[0], reports_dom[0], reports_hab[0],
            reports_ods_hom[0], reports_pnad_v[0], reports_mun_s[0],
            reports_equip[0], reports_viag[0],
            reports_fin_rec[0], reports_fin_cor[0], reports_mun_trib[0],
            reports_frota_tot[0], reports_frota_auto[0], reports_mun_ciclo[0],
            reports_ptx[0], reports_ppd[0], reports_lgpd[0], reports_otec[0],
        ):
            png_path = export_bundle(b, out_dir=tmpdir, dpi=150)
            assert os.path.exists(png_path) and os.path.getsize(png_path) > 1000
            if b.table_spec:
                csv_path = os.path.join(tmpdir, f"{b.report_id}.csv")
                export_table_csv(b.table_spec, csv_path)
                assert os.path.exists(csv_path)

    print("[OK] AnalyticsEngine + ReportRenderer validados (aditivo, negativo, média, N2, N3, N7_N6 IPCA, binário MUNIC e Fases 5-12).")


def test_ibge_api():
    client = IbgeMalhasClient()
    path = client.fetch_uf_geojson("SC", qualidade="minima")
    assert os.path.exists(path) and os.path.getsize(path) > 1000, "Malha de SC inválida!"
    st_path = client.fetch_states_geojson()
    assert os.path.exists(st_path) and os.path.getsize(st_path) > 1000, "Malha dos Estados inválida!"

    n2_path = client.fetch_macro_regions_geojson()
    n2_gj = json.load(open(n2_path, encoding="utf-8"))
    assert len(n2_gj.get("features", [])) == 5, f"N2 deveria ter 5 regiões, obteve {len(n2_gj.get('features', []))}"

    n8_path = client.fetch_mesoregions_geojson("SC")
    n8_gj = json.load(open(n8_path, encoding="utf-8"))
    assert len(n8_gj.get("features", [])) == 6, f"SC N8 deveria ter 6 mesorregiões, obteve {len(n8_gj.get('features', []))}"

    n9_path = client.fetch_microregions_geojson("SC")
    n9_gj = json.load(open(n9_path, encoding="utf-8"))
    assert len(n9_gj.get("features", [])) == 20, f"SC N9 deveria ter 20 microrregiões, obteve {len(n9_gj.get('features', []))}"

    rm_path = client.fetch_metro_geojson()
    assert rm_path == client.fetch_geojson_for_level("N7_N14")
    rm_gj = json.load(open(rm_path, encoding="utf-8"))
    rm_codes = {str(f["properties"].get("codarea") or f["properties"].get("cod") or "") for f in rm_gj.get("features", [])}
    assert len(rm_codes) == 21, f"Malha RM N7_N14 deveria conter 21 códigos únicos, obteve {len(rm_codes)}"

    comp_path = client.fetch_metro_and_capitals_geojson()
    comp_gj = json.load(open(comp_path, encoding="utf-8"))
    comp_codes = {str(f["properties"].get("codarea") or f["properties"].get("cod") or "") for f in comp_gj.get("features", [])}
    assert len(comp_codes) == 27, f"Malha N7_N6 base deveria conter 21 RMs+RIDE + 6 capitais = 27 códigos, obteve {len(comp_codes)}"

    print("[OK] IbgeMalhasClient validado (malhas N2, N3, N6, N8, N9, N7_N14 e N7_N6 em cache).")


def package_and_sync():
    plugin_folder = os.path.join(PROJECT_ROOT, "geosidra_qgis")
    out_zip = os.path.join(PROJECT_ROOT, "geosidra_qgis.zip")

    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(plugin_folder):
            dirs[:] = [d for d in dirs if d != "__pycache__" and not d.startswith(".")]
            for file in files:
                if file.endswith((".pyc", ".pyo")) or file.startswith("."):
                    continue
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, PROJECT_ROOT).replace("\\", "/")
                zf.write(abs_path, rel_path)

    print(f"[OK] Pacote ZIP gerado: {out_zip} ({os.path.getsize(out_zip):,} bytes)")

    qgis4_dir = os.path.expandvars(r"%APPDATA%\QGIS\QGIS4\profiles\default\python\plugins\geosidra_qgis")
    if os.path.exists(os.path.dirname(qgis4_dir)):
        if os.path.exists(qgis4_dir):
            shutil.rmtree(qgis4_dir)
        shutil.copytree(plugin_folder, qgis4_dir)
        print(f"[OK] Plugin sincronizado na pasta ativa do QGIS 4: {qgis4_dir}")


if __name__ == "__main__":
    print("=== Iniciando Testes Locais e Empacotamento do GeoSIDRA ===")
    test_cross_analyzer_removed()
    test_catalog_expansion()
    test_variable_slugs()
    test_unit_formatting()
    test_mapper()
    test_live_sidra_series_and_analytics()
    test_ibge_api()
    package_and_sync()
    print("=== Todos os Testes e Empacotamento Concluídos com Sucesso! ===")
