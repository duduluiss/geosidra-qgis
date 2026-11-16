# -*- coding: utf-8 -*-
"""
Cliente oficial da API SIDRA do IBGE (apisidra.ibge.gov.br) com cache local,
suporte a séries em múltiplas tabelas, múltiplas classificações, agregação
estatística (soma/último ano/média) e níveis N6 (Municípios), N9 (Microrregiões),
N8 (Mesorregiões), N7 (Regiões Metropolitanas), N14 (RIDEs), N7_N6, N7_N14,
N3 (UFs), N2 (Grandes Regiões) e N1 (Brasil).
"""

import gzip
import hashlib
import http.client
import json
import logging
import os
import tempfile
from urllib.parse import urlparse
from typing import Any, Callable, Dict, List, Optional

LOGGER = logging.getLogger("GeoSIDRA")

ALLOWED_SIDRA_HOST = "apisidra.ibge.gov.br"
ALLOWED_SERVICODADOS_HOST = "servicodados.ibge.gov.br"

UF_CODE_MAP = {
    "RO": 11, "AC": 12, "AM": 13, "RR": 14, "PA": 15, "AP": 16, "TO": 17,
    "MA": 21, "PI": 22, "CE": 23, "RN": 24, "PB": 25, "PE": 26, "AL": 27,
    "SE": 28, "BA": 29, "MG": 31, "ES": 32, "RJ": 33, "SP": 35, "PR": 41,
    "SC": 42, "RS": 43, "MS": 50, "MT": 51, "GO": 52, "DF": 53
}

UF_NUM_TO_SIGLA = {str(v): k for k, v in UF_CODE_MAP.items()}

ALL_UF_IBGE_CODES: List[str] = [
    "11", "12", "13", "14", "15", "16", "17",
    "21", "22", "23", "24", "25", "26", "27", "28", "29",
    "31", "32", "33", "35",
    "41", "42", "43",
    "50", "51", "52", "53",
]

FINBRA_INDICATOR_NAMES: Dict[int, str] = {
    28141: "Receitas orçamentárias brutas realizadas",
    28144: "Receitas correntes brutas realizadas",
    165603: "Receita tributária municipal (impostos, taxas e contribuição de melhoria)",
    165604: "Impostos municipais arrecadados (IPTU, ISS, ITBI)",
    165605: "Taxas municipais",
    165606: "Contribuição de melhoria",
    165607: "Contribuições municipais",
    165608: "Receita patrimonial",
    165611: "Receita de serviços",
    165612: "Transferências correntes (FPM, ICMS, FUNDEB, IPVA, SUS)",
    165613: "Outras receitas correntes",
    28142: "Receitas de capital",
    165614: "Operações de crédito",
    165615: "Alienação de bens",
    165617: "Transferências de capital",
    28134: "Despesas orçamentárias brutas",
    29749: "Despesas orçamentárias empenhadas",
    28136: "Despesas correntes empenhadas",
    28135: "Despesas de capital empenhadas",
    29748: "Despesas orçamentárias liquidadas",
    29751: "Despesas correntes liquidadas",
    29750: "Despesas de capital liquidadas",
    143223: "Despesas orçamentárias pagas",
    143225: "Despesas correntes pagas",
    143224: "Despesas de capital pagas",
}

# Mapeamento oficial dos indicadores da Pesquisa 22 do IBGE (Frota de Veículos - DENATRAN / SENATRAN)
FROTA_INDICATOR_NAMES: Dict[int, str] = {
    28120: "Frota total de veículos",
    28122: "Automóveis",
    28128: "Motocicletas",
    28129: "Motonetas",
    78164: "Ciclomotores",
    28125: "Caminhonetes",
    28126: "Camionetas",
    28123: "Caminhões",
    28124: "Caminhões-trator",
    28130: "Ônibus",
    28127: "Micro-ônibus",
    78166: "Reboques",
    78167: "Semi-reboques",
    28132: "Utilitários",
    28131: "Tratores de rodas",
}

MACRO_REGION_SIGLAS = {
    "1": "N",
    "2": "NE",
    "3": "SE",
    "4": "S",
    "5": "CO",
}

# Mapeamento oficial dos indicadores da Pesquisa 10064 do IBGE (PINTEC Estadual / UF)
PINTEC_UF_INDICATOR_NAMES: Dict[int, str] = {
    60202: "Número de empresas do universo da pesquisa",
    60203: "Empresas com inovação em produto ou processo",
    82735: "Taxa de inovação de produto ou processo (%)",
    60204: "Empresas com inovação em produto",
    60205: "Taxa de inovação de produto (%)",
    60206: "Empresas com inovação em processo",
    60207: "Taxa de inovação de processo (%)",
    60208: "Empresas com dispêndio em P&D interno",
    60209: "Taxa de incidência de empresas com P&D interno (%)",
    60211: "Dispêndio em atividades inovativas",
    60212: "Relação dispêndio em inovação / receita líquida de vendas (%)",
    60214: "Dispêndio com P&D interno",
    60215: "Relação dispêndio em P&D interno / receita líquida de vendas (%)",
    60216: "Pessoal ocupado em P&D",
}

PINTEC_UF_INDICATOR_UNITS: Dict[int, str] = {
    60202: "Empresas",
    60203: "Empresas",
    82735: "%",
    60204: "Empresas",
    60205: "%",
    60206: "Empresas",
    60207: "%",
    60208: "Empresas",
    60209: "%",
    60211: "Mil R$",
    60212: "%",
    60214: "Mil R$",
    60215: "%",
    60216: "Pessoas",
}

# Mapeamento oficial dos indicadores da Pesquisa 10115 do IBGE (CEMADEN / BATER - População em Áreas de Risco)
CEMADEN_INDICATOR_NAMES: Dict[int, str] = {
    353155: "População residente em áreas de risco geológico e hidrológico",
    353154: "Domicílios particulares ocupados em áreas de risco",
    353157: "População idosa (60 anos ou mais) residente em áreas de risco",
}

CEMADEN_INDICATOR_UNITS: Dict[int, str] = {
    353155: "Pessoas",
    353154: "Domicílios",
    353157: "Pessoas",
}

# Mapeamento oficial dos indicadores da Pesquisa 29 do IBGE (BACEN / ESTBAN - Informações Bancárias)
BACEN_INDICATOR_NAMES: Dict[int, str] = {
    21910: "Número de agências bancárias em funcionamento",
    21912: "Operações de crédito",
    21913: "Depósitos de poupança",
    21907: "Depósitos à vista",
    21906: "Depósitos a prazo",
    21911: "Obrigações por recebimento",
}

BACEN_INDICATOR_UNITS: Dict[int, str] = {
    21910: "Agências",
    21912: "Mil R$",
    21913: "Mil R$",
    21907: "Mil R$",
    21906: "Mil R$",
    21911: "Mil R$",
}

# Mapeamento oficial dos indicadores de TIC, Governo Digital, Inclusao Digital e LGPD da MUNIC 2024 (Pesquisa 1)
MUNIC_DIGITAL_INDICATOR_NAMES: Dict[int, str] = {
    325752: "Estrutura organizacional de TIC na prefeitura",
    325762: "Centro de Processamento de Dados (CPD) próprio",
    325764: "Desenvolveu software interno nos últimos 12 meses",
    325765: "Desenvolveu software para atendimento à sociedade nos últimos 12 meses",
    325779: "Ouvidoria e atendimento ao cidadão na página web",
    325784: "Emissão online de Certidão Negativa de Débito (CND)",
    325785: "Emissão online de alvará pela página web",
    325786: "Emissão de Nota Fiscal Eletrônica (NFS-e) pela internet",
    325787: "Matrícula escolar na rede pública online",
    325788: "Agendamento online de consultas e exames no SUS",
    325789: "Emissão online de guia de pagamento de tributos",
    325817: "Website da prefeitura adaptado para celular (mobile)",
    325824: "Aplicativo de celular da prefeitura para solicitação de serviços",
    325837: "Acesso a alguns serviços digitais com conta GOV.BR",
    325838: "Acesso a todos os serviços digitais com conta GOV.BR",
    325842: "Desenvolve programa ou ação de inclusão digital",
    325859: "Disponibiliza acesso público por Wi-Fi para a população",
    325867: "Realiza consulta pública online para leis e orçamentos",
    325889: "Bilhete eletrônico no transporte público municipal",
    325890: "Ônibus municipais monitorados por dispositivo GPS",
    325891: "Centro de controle operacional (CCO) no município",
    325892: "Sistema de iluminação pública inteligente",
    325893: "Semáforos inteligentes controlados a distância",
    325894: "Sensores de monitoramento de áreas de risco e enchentes",
    325897: "Portal da transparência ativo no município",
    325898: "Portal de dados abertos ativo no município",
    325904: "Tradução para LIBRAS nos serviços digitais da prefeitura",
    326122: "Conselho Municipal de Transparência existente",
    326148: "Área ou pessoa encarregada pela LGPD na prefeitura",
    326150: "Cursos de segurança da informação e proteção de dados",
    326151: "Canal web para o cidadão sobre uso de dados (LGPD)",
    326152: "Lei ou regulamentação municipal específica sobre a LGPD",
    # MUNIC 2020: Gestão de Riscos de Desastres e Defesa Civil
    92534: "Plano Municipal de Redução de Riscos (PMRR)",
    92535: "Carta geotécnica de aptidão à urbanização",
    92536: "Lei de uso e ocupação do solo com diretrizes de risco",
    92539: "Mecanismo de monitoramento e alerta antecipado",
    92540: "Realocação habitacional definitiva de famílias em áreas de risco",
    92544: "Plano de Contingência de Proteção e Defesa Civil (PLANCON)",
    92545: "Simulados de evacuação de áreas de risco",
    92550: "Obras ou intervenções preventivas de contenção de encostas e drenagem",
    92559: "Órgão gestor de Defesa Civil municipal (COMPDEC)",
    92560: "Estrutura exclusiva da Defesa Civil no município",
    92567: "Utilização do Sistema S2ID",
    92569: "Previsão de recursos para Defesa Civil na LOA",
    92572: "Fundo Municipal de Proteção e Defesa Civil (FUMPDEC)",
}

# Mapeamento da classificação c12354 (Grandes regiões e UFs de atuação) usada nas séries históricas PAC (1407) e PAS (2715)
UF_SIGLA_TO_C12354_CAT: Dict[str, int] = {
    "RO": 106775, "AC": 106776, "AM": 106777, "RR": 106778, "PA": 106779,
    "AP": 106780, "TO": 106781, "MA": 106782, "PI": 106783, "CE": 106784,
    "RN": 106785, "PB": 106786, "PE": 106787, "AL": 106788, "SE": 106789,
    "BA": 106790, "MG": 106791, "ES": 106792, "RJ": 106793, "SP": 106794,
    "PR": 106795, "SC": 106796, "RS": 106797, "MS": 106798, "MT": 106799,
    "GO": 106800, "DF": 106801,
}
C12354_CAT_TO_UF_NUM: Dict[str, str] = {
    str(cat_id): str(UF_CODE_MAP[sigla])
    for sigla, cat_id in UF_SIGLA_TO_C12354_CAT.items()
}

# Tabelas municipais (N6) com múltiplas dimensões que excedem timeout do SIDRA quando consultadas em BR inteiro (n6/all)
_HEAVY_BR_N6_TABLES = {
    1695,
    2609, 2654, 4412,
    6778, 6846, 6850, 6851, 6853, 6857, 6866, 6869, 6878, 6881, 6884, 6895, 6897, 6907,
}


def get_sidra_cache_dir() -> str:
    """Diretório permanente de cache de consultas SIDRA."""
    candidates = [
        os.path.join(os.path.expanduser("~"), ".geosidra", "cache_sidra"),
        os.path.join(tempfile.gettempdir(), "geosidra_cache"),
    ]
    for path in candidates:
        try:
            os.makedirs(path, exist_ok=True)
            return path
        except OSError:
            continue
    return tempfile.gettempdir()


class SidraClient:
    """Cliente para a API de Valores do SIDRA/IBGE."""

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir or get_sidra_cache_dir()
        os.makedirs(self.cache_dir, exist_ok=True)

    def build_url(
        self,
        table: int,
        territory: str = "BR",
        level: str = "N6",
        variables: Optional[List[int]] = None,
        years: Optional[List[int]] = None,
        classification: Optional[int] = None,
        category: Optional[int] = None,
        extra_classifications: Optional[Dict[int, int]] = None,
    ) -> str:
        """Constrói a URL da consulta SIDRA de acordo com o nível territorial."""
        terr_clean = (territory or "BR").strip().upper()
        lvl = (level or "N6").upper()

        tbl_upper = str(table).upper()
        if tbl_upper in ("FINBRA", "FROTA", "PINTEC_UF", "MUNIC_DIGITAL", "CEMADEN", "BACEN"):
            pesquisa_map = {
                "FROTA": ("22", "28120", 2024),
                "FINBRA": ("21", "28141", 2022),
                "PINTEC_UF": ("10064", "82735", 2017),
                "MUNIC_DIGITAL": ("1", "326148", 2024),
                "CEMADEN": ("10115", "353155", 2010),
                "BACEN": ("29", "21910", 2024),
            }
            p_id, def_v, def_y = pesquisa_map[tbl_upper]
            years_param = "|".join(str(y) for y in (years or [def_y]))
            vars_param = str(variables[0]) if variables else def_v
            return f"https://{ALLOWED_SERVICODADOS_HOST}/api/v1/pesquisas/{p_id}/periodos/{years_param}/indicadores/{vars_param}/resultados/{terr_clean}"

        if lvl == "N1":
            terr_param = "n1/all"
        elif lvl == "N2":
            terr_param = f"n2/{terr_clean}" if terr_clean in MACRO_REGION_SIGLAS else "n2/all"
        elif lvl == "N14":
            terr_param = "n14/all"
        elif lvl == "N3":
            if terr_clean == "BR" or terr_clean not in UF_CODE_MAP:
                terr_param = "n3/all"
            else:
                uf_num = UF_CODE_MAP[terr_clean]
                terr_param = f"n3/{uf_num}"
        elif lvl in ("N7", "N8", "N9"):
            n_num = lvl[1:]
            if terr_clean == "BR" or terr_clean not in UF_CODE_MAP:
                terr_param = f"n{n_num}/all"
            else:
                uf_num = UF_CODE_MAP[terr_clean]
                terr_param = f"n{n_num}/in%20n3%20{uf_num}"
        else:
            # N6 (Municípios)
            if terr_clean == "BR" or terr_clean not in UF_CODE_MAP:
                terr_param = "n6/all"
            else:
                uf_num = UF_CODE_MAP[terr_clean]
                terr_param = f"n6/in%20n3%20{uf_num}"

        if variables:
            var_param = f"v/{','.join(str(v) for v in variables)}"
        else:
            var_param = "v/allxp"

        if years:
            p_param = f"p/{','.join(str(y) for y in years)}"
        else:
            p_param = "p/last%201"

        url = f"https://{ALLOWED_SIDRA_HOST}/values/t/{table}/{terr_param}/{var_param}/{p_param}"

        if classification is not None and category is not None:
            url += f"/c{classification}/{category}"

        if extra_classifications:
            for cid in sorted(extra_classifications.keys()):
                if classification is not None and int(cid) == int(classification):
                    continue
                raw_cat = extra_classifications[cid]
                if isinstance(raw_cat, (list, tuple)):
                    cat_str = ",".join(str(int(x)) for x in raw_cat)
                else:
                    cat_str = str(raw_cat).strip()
                url += f"/c{int(cid)}/{cat_str}"

        return url

    def _fetch_url(self, url: str, timeout: int = 45) -> bytes:
        """Executa requisição HTTPS validada com QgsBlockingNetworkRequest e fallback http.client."""
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.netloc != ALLOWED_SIDRA_HOST:
            raise ValueError(f"Host ou protocolo não permitido para API do SIDRA: {url}")

        try:
            from qgis.core import QgsBlockingNetworkRequest
            from qgis.PyQt.QtCore import QUrl
            from qgis.PyQt.QtNetwork import QNetworkRequest

            qreq = QNetworkRequest(QUrl(url))
            qreq.setRawHeader(b"User-Agent", b"QGIS-GeoSIDRA-Plugin/0.3")
            qreq.setRawHeader(b"Accept", b"application/json")
            qreq.setRawHeader(b"Accept-Encoding", b"gzip, deflate")
            blocker = QgsBlockingNetworkRequest()
            err = blocker.get(qreq)
            if err == QgsBlockingNetworkRequest.ErrorCode.NoError:
                raw = bytes(blocker.reply().content())
                if raw[:2] == b"\x1f\x8b":
                    raw = gzip.decompress(raw)
                return raw
        except (ImportError, AttributeError, RuntimeError, OSError) as qgis_net_err:
            logger.debug("QgsBlockingNetworkRequest fallback to standard HTTP: %s", qgis_net_err)

        path_query = parsed.path + (f"?{parsed.query}" if parsed.query else "")
        conn = http.client.HTTPSConnection(ALLOWED_SIDRA_HOST, timeout=timeout)
        try:
            conn.request(
                "GET",
                path_query,
                headers={
                    "User-Agent": "QGIS-GeoSIDRA-Plugin/0.3",
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "close",
                },
            )
            resp = conn.getresponse()
            if resp.status != 200:
                raise RuntimeError(f"API SIDRA retornou HTTP {resp.status} para {url}")
            raw = resp.read()
            if raw[:2] == b"\x1f\x8b":
                raw = gzip.decompress(raw)
            return raw
        finally:
            conn.close()

    def _fetch_servicodados_json(self, url: str, timeout: int = 60) -> Optional[Any]:
        """Executa consulta HTTP à API ServicoDados do IBGE com fallback headless e suporte a gzip."""
        parsed = urlparse(url)
        try:
            from qgis.core import QgsBlockingNetworkRequest
            from qgis.PyQt.QtCore import QUrl
            from qgis.PyQt.QtNetwork import QNetworkRequest

            qreq = QNetworkRequest(QUrl(url))
            qreq.setRawHeader(b"User-Agent", b"QGIS-GeoSIDRA-Plugin/0.12")
            qreq.setRawHeader(b"Accept", b"application/json")
            qreq.setRawHeader(b"Accept-Encoding", b"gzip, deflate")
            blocker = QgsBlockingNetworkRequest()
            err = blocker.get(qreq)
            if err == QgsBlockingNetworkRequest.ErrorCode.NoError:
                raw = bytes(blocker.reply().content())
                if raw[:2] == b"\x1f\x8b":
                    raw = gzip.decompress(raw)
                return json.loads(raw.decode("utf-8"))
        except (ImportError, AttributeError, RuntimeError, OSError, json.JSONDecodeError, UnicodeDecodeError) as qgis_net_err:
            logger.debug("QgsBlockingNetworkRequest ServicoDados fallback to standard HTTP: %s", qgis_net_err)

        path_query = parsed.path + (f"?{parsed.query}" if parsed.query else "")
        conn = http.client.HTTPSConnection(ALLOWED_SERVICODADOS_HOST, timeout=timeout)
        try:
            conn.request(
                "GET",
                path_query,
                headers={
                    "User-Agent": "QGIS-GeoSIDRA-Plugin/0.12",
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "close",
                },
            )
            resp = conn.getresponse()
            if resp.status != 200:
                LOGGER.warning("API ServicoDados IBGE retornou HTTP %s para %s", resp.status, url)
                return None
            raw = resp.read()
            if raw[:2] == b"\x1f\x8b":
                raw = gzip.decompress(raw)
            return json.loads(raw.decode("utf-8"))
        except Exception as exc:
            LOGGER.warning("Falha ao consultar ServicoDados IBGE (%s): %s", url, exc)
            return None
        finally:
            conn.close()

    def query_servicodados_pesquisa(
        self,
        pesquisa_id: int,
        indicator: int,
        territory: str = "BR",
        level: str = "N6",
        years: Optional[List[int]] = None,
        unit: str = "Unidades",
        ind_name_map: Optional[Dict[int, str]] = None,
        ind_unit_map: Optional[Dict[int, str]] = None,
        cache_prefix: str = "pesquisa",
        default_year: int = 2022,
        binary_text: bool = False,
        use_cache: bool = True,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> List[Dict]:
        """
        Consulta dados oficiais das pesquisas da API v1 do IBGE (ex: Pesquisa 1 MUNIC,
        Pesquisa 21 FINBRA, Pesquisa 22 Frota, Pesquisa 10064 PINTEC) no formato GeoSIDRA.
        """
        from geosidra_qgis.core.municipality_mapper import MunicipalityMapper

        terr_clean = (territory or "BR").strip().upper()
        lvl_clean = (level or "N6").upper()
        years_list = sorted(years) if years else [default_year]
        years_param = "|".join(str(y) for y in years_list)

        cache_key = hashlib.sha256(
            f"{cache_prefix}_{pesquisa_id}_{indicator}_{terr_clean}_{lvl_clean}_{years_param}".encode("utf-8")
        ).hexdigest()
        cache_file = os.path.join(self.cache_dir, f"{cache_prefix}_{cache_key}.json")

        if use_cache and os.path.exists(cache_file) and os.path.getsize(cache_file) > 100:
            if progress_callback:
                progress_callback(50, f"Carregando dados de {cache_prefix.upper()} do cache local...")
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError, UnicodeDecodeError) as cache_err:
                logger.debug("Cache read failed for %s: %s", cache_file, cache_err)

        ind_name = (ind_name_map or {}).get(int(indicator), f"Indicador {indicator}")
        resolved_unit = (ind_unit_map or {}).get(int(indicator), unit)

        if lvl_clean == "N1":
            d1c_hdr, d1n_hdr = "Brasil (Código)", "Brasil"
        elif lvl_clean == "N3":
            d1c_hdr, d1n_hdr = "Unidade da Federação (Código)", "Unidade da Federação"
        else:
            d1c_hdr, d1n_hdr = "Município (Código)", "Município"

        header = {
            "NC": "Nível Territorial (Código)",
            "NN": "Nível Territorial",
            "D1C": d1c_hdr,
            "D1N": d1n_hdr,
            "D2C": "Variável (Código)",
            "D2N": "Variável",
            "D3C": "Ano (Código)",
            "D3N": "Ano",
            "MN": resolved_unit,
            "V": "Valor",
        }

        mapper = MunicipalityMapper.instance()

        if lvl_clean == "N1" and int(pesquisa_id) == 10064:
            loc_chunks = [["0"]]
            is_mun = False
        elif int(pesquisa_id) == 29:
            if lvl_clean == "N1":
                loc_chunks = [["0"]]
                is_mun = False
            elif lvl_clean == "N3":
                if terr_clean in UF_CODE_MAP:
                    loc_chunks = [[str(UF_CODE_MAP[terr_clean])]]
                else:
                    loc_chunks = [["XX"]]
                is_mun = False
            else:
                loc_chunks = [["XXXXXX"]]
                is_mun = True
        elif lvl_clean == "N3" or (lvl_clean == "N1" and terr_clean == "BR"):
            if lvl_clean == "N3" and terr_clean in UF_CODE_MAP:
                loc_chunks = [[str(UF_CODE_MAP[terr_clean])]]
            else:
                loc_chunks = [ALL_UF_IBGE_CODES]
            is_mun = False
        else:
            is_mun = True
            if int(pesquisa_id) == 1:
                loc_chunks = [["XXXXXX"]]
            elif terr_clean in UF_CODE_MAP:
                muns = [
                    ibge7 for ibge7, info in mapper.by_ibge.items()
                    if info.get("uf") == terr_clean
                ]
                muns.sort()
                loc_chunks = [muns[i:i + 250] for i in range(0, len(muns), 250)]
            else:
                muns = list(mapper.by_ibge.keys())
                muns.sort()
                loc_chunks = [muns[i:i + 250] for i in range(0, len(muns), 250)]

        rows: List[Dict] = []
        total_chunks = max(1, len(loc_chunks))
        for idx, chunk in enumerate(loc_chunks):
            if progress_callback:
                pct = 20 + int((idx / total_chunks) * 70)
                progress_callback(pct, f"Consultando {cache_prefix.upper()} ({idx + 1}/{total_chunks})...")

            piped_locs = "|".join(chunk)
            url = (
                f"https://{ALLOWED_SERVICODADOS_HOST}/api/v1/pesquisas/{pesquisa_id}/"
                f"periodos/{years_param}/indicadores/{indicator}/resultados/{piped_locs}"
            )
            data = self._fetch_servicodados_json(url)
            if not data or not isinstance(data, list):
                continue
            res_list = data[0].get("res", [])
            for item in res_list:
                loc = str(item.get("localidade", "")).strip()
                res_dict = item.get("res", {})
                for yr in years_list:
                    raw_val = res_dict.get(str(yr))
                    if raw_val is None:
                        continue
                    val_str = str(raw_val).strip()
                    if val_str in ("", "-", "..", "...", "X", "null", "None"):
                        continue

                    if binary_text:
                        low_v = val_str.lower()
                        if low_v == "sim":
                            val_str = "1"
                        elif low_v in ("não", "nao", "não possui", "nao possui", "não disponibilizou", "nao disponibilizou"):
                            val_str = "0"
                        elif low_v in ("não informou", "nao informou", "não sabe", "nao sabe", "não sabe informar", "nao sabe informar", "recusa"):
                            continue
                        else:
                            continue
                    else:
                        try:
                            num_chk = float(val_str.replace(",", "."))
                            if abs(num_chk) >= 9e13:
                                continue
                        except (ValueError, TypeError):
                            continue

                    if is_mun:
                        loc6 = loc[:6]
                        info = mapper.by_ibge6.get(loc6) or mapper.by_ibge.get(loc) or {}
                        out_code = str(info.get("codigo_ibge") or info.get("ibge") or loc).strip()
                        if terr_clean in UF_CODE_MAP and not out_code.startswith(str(UF_CODE_MAP[terr_clean])):
                            continue
                        nm_clean = info.get("nome_municipio") or info.get("nome") or loc
                        uf_sigla = info.get("uf", "")
                        nm_label = f"{nm_clean} - {uf_sigla}" if uf_sigla else nm_clean
                        nc_code = "6"
                        nn_label = "Município"
                    elif loc == "0":
                        out_code = "1"
                        nm_label = "Brasil"
                        nc_code = "1"
                        nn_label = "Brasil"
                    else:
                        out_code = loc
                        nm_label = UF_NUM_TO_SIGLA.get(loc, loc)
                        nc_code = "3"
                        nn_label = "Unidade da Federação"
                    rows.append({
                        "NC": nc_code,
                        "NN": nn_label,
                        "D1C": out_code,
                        "D1N": nm_label,
                        "D2C": str(indicator),
                        "D2N": ind_name,
                        "D3C": str(yr),
                        "D3N": str(yr),
                        "MN": resolved_unit,
                        "V": val_str,
                    })

        if not rows:
            raise RuntimeError(
                f"Nenhum dado retornado por {cache_prefix.upper()} para o indicador {indicator} e território {territory}."
            )

        payload = [header] + rows
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False)
        except OSError:
            pass

        return payload

    def query_finbra(
        self,
        indicator: int,
        territory: str = "BR",
        level: str = "N6",
        years: Optional[List[int]] = None,
        use_cache: bool = True,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> List[Dict]:
        """Consulta os dados contábeis municipais e estaduais do FINBRA (Pesquisa 21 do IBGE)."""
        return self.query_servicodados_pesquisa(
            pesquisa_id=21,
            indicator=indicator,
            territory=territory,
            level=level,
            years=years,
            unit="R$",
            ind_name_map=FINBRA_INDICATOR_NAMES,
            cache_prefix="finbra",
            default_year=2022,
            use_cache=use_cache,
            progress_callback=progress_callback,
        )

    def query_frota(
        self,
        indicator: int,
        territory: str = "BR",
        level: str = "N6",
        years: Optional[List[int]] = None,
        use_cache: bool = True,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> List[Dict]:
        """Consulta a frota municipal e estadual de veículos do SENATRAN (Pesquisa 22 do IBGE)."""
        return self.query_servicodados_pesquisa(
            pesquisa_id=22,
            indicator=indicator,
            territory=territory,
            level=level,
            years=years,
            unit="Veículos",
            ind_name_map=FROTA_INDICATOR_NAMES,
            cache_prefix="frota",
            default_year=2024,
            use_cache=use_cache,
            progress_callback=progress_callback,
        )

    def query_pintec_uf(
        self,
        indicator: int,
        territory: str = "BR",
        level: str = "N3",
        years: Optional[List[int]] = None,
        use_cache: bool = True,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> List[Dict]:
        """Consulta os indicadores estaduais e nacionais da PINTEC (Pesquisa 10064 do IBGE)."""
        return self.query_servicodados_pesquisa(
            pesquisa_id=10064,
            indicator=indicator,
            territory=territory,
            level=level,
            years=years,
            unit="Unidades",
            ind_name_map=PINTEC_UF_INDICATOR_NAMES,
            ind_unit_map=PINTEC_UF_INDICATOR_UNITS,
            cache_prefix="pintec_uf",
            default_year=2017,
            use_cache=use_cache,
            progress_callback=progress_callback,
        )

    def query_munic_digital(
        self,
        indicator: int,
        territory: str = "BR",
        level: str = "N6",
        years: Optional[List[int]] = None,
        use_cache: bool = True,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> List[Dict]:
        """Consulta indicadores municipais de TIC, Governo Digital e LGPD da MUNIC 2024 (Pesquisa 1)."""
        return self.query_servicodados_pesquisa(
            pesquisa_id=1,
            indicator=indicator,
            territory=territory,
            level=level,
            years=years,
            unit="Municípios",
            ind_name_map=MUNIC_DIGITAL_INDICATOR_NAMES,
            cache_prefix="munic_digital",
            default_year=2024,
            binary_text=True,
            use_cache=use_cache,
            progress_callback=progress_callback,
        )

    def query_bacen(
        self,
        indicator: int,
        territory: str = "BR",
        level: str = "N6",
        years: Optional[List[int]] = None,
        use_cache: bool = True,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> List[Dict]:
        """Consulta as estatísticas bancárias do BACEN/ESTBAN (Pesquisa 29 do IBGE)."""
        return self.query_servicodados_pesquisa(
            pesquisa_id=29,
            indicator=indicator,
            territory=territory,
            level=level,
            years=years,
            unit="Agências",
            ind_name_map=BACEN_INDICATOR_NAMES,
            ind_unit_map=BACEN_INDICATOR_UNITS,
            cache_prefix="bacen",
            default_year=2024,
            use_cache=use_cache,
            progress_callback=progress_callback,
        )

    def query_cemaden(
        self,
        indicator: int,
        territory: str = "BR",
        level: str = "N6",
        years: Optional[List[int]] = None,
        use_cache: bool = True,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> List[Dict]:
        """Consulta dados de população e domicílios em áreas de risco do CEMADEN/IBGE (Pesquisa 10115)."""
        from geosidra_qgis.core.municipality_mapper import MunicipalityMapper

        terr_clean = (territory or "BR").strip().upper()
        lvl_clean = (level or "N6").upper()
        years_list = sorted(years) if years else [2010]
        years_param = "|".join(str(y) for y in years_list)

        cache_key = hashlib.sha256(
            f"cemaden_10115_{indicator}_{terr_clean}_{lvl_clean}_{years_param}".encode("utf-8")
        ).hexdigest()
        cache_file = os.path.join(self.cache_dir, f"cemaden_{cache_key}.json")

        if use_cache and os.path.exists(cache_file) and os.path.getsize(cache_file) > 100:
            if progress_callback:
                progress_callback(50, "Carregando dados do CEMADEN do cache local...")
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError, UnicodeDecodeError) as cache_err:
                logger.debug("Cache read failed for %s: %s", cache_file, cache_err)

        ind_name = CEMADEN_INDICATOR_NAMES.get(int(indicator), f"Indicador {indicator}")
        resolved_unit = CEMADEN_INDICATOR_UNITS.get(int(indicator), "Pessoas")

        if lvl_clean == "N1":
            d1c_hdr, d1n_hdr = "Brasil (Código)", "Brasil"
        elif lvl_clean == "N3":
            d1c_hdr, d1n_hdr = "Unidade da Federação (Código)", "Unidade da Federação"
        else:
            d1c_hdr, d1n_hdr = "Município (Código)", "Município"

        header = {
            "NC": "Nível Territorial (Código)",
            "NN": "Nível Territorial",
            "D1C": d1c_hdr,
            "D1N": d1n_hdr,
            "D2C": "Variável (Código)",
            "D2N": "Variável",
            "D3C": "Ano (Código)",
            "D3N": "Ano",
            "MN": resolved_unit,
            "V": "Valor",
        }

        if progress_callback:
            progress_callback(30, "Consultando dados municipais de risco do CEMADEN/IBGE...")

        url = f"https://{ALLOWED_SERVICODADOS_HOST}/api/v1/pesquisas/10115/periodos/{years_param}/indicadores/{indicator}/resultados/XXXXXX"
        data = self._fetch_servicodados_json(url)
        if not data or not isinstance(data, list):
            raise RuntimeError(f"Nenhum dado retornado pelo CEMADEN para o indicador {indicator}.")

        res_list = data[0].get("res", [])
        mapper = MunicipalityMapper.instance()

        rows: List[Dict] = []
        if lvl_clean == "N1":
            br_totals: Dict[str, float] = {str(yr): 0.0 for yr in years_list}
            for item in res_list:
                res_dict = item.get("res", {})
                for yr in years_list:
                    raw_val = res_dict.get(str(yr))
                    if raw_val is not None:
                        try:
                            br_totals[str(yr)] += float(str(raw_val).replace(",", "."))
                        except (ValueError, TypeError):
                            pass
            for yr in years_list:
                rows.append({
                    "NC": "1",
                    "NN": "Brasil",
                    "D1C": "1",
                    "D1N": "Brasil",
                    "D2C": str(indicator),
                    "D2N": ind_name,
                    "D3C": str(yr),
                    "D3N": str(yr),
                    "MN": resolved_unit,
                    "V": str(int(round(br_totals[str(yr)]))),
                })
        elif lvl_clean == "N3":
            uf_totals: Dict[str, Dict[str, float]] = {
                sigla: {str(yr): 0.0 for yr in years_list}
                for sigla in sorted(UF_CODE_MAP.keys())
            }
            for item in res_list:
                loc = str(item.get("localidade", ""))[:6]
                res_dict = item.get("res", {})
                info = mapper.by_ibge6.get(loc) or mapper.by_ibge.get(loc) or {}
                uf_sigla = info.get("uf")
                if not uf_sigla or uf_sigla not in uf_totals:
                    continue
                for yr in years_list:
                    raw_val = res_dict.get(str(yr))
                    if raw_val is not None:
                        try:
                            uf_totals[uf_sigla][str(yr)] += float(str(raw_val).replace(",", "."))
                        except (ValueError, TypeError):
                            pass

            for sigla, uf_code in sorted(UF_CODE_MAP.items(), key=lambda x: x[1]):
                if terr_clean in UF_CODE_MAP and sigla != terr_clean:
                    continue
                for yr in years_list:
                    val = uf_totals[sigla][str(yr)]
                    rows.append({
                        "NC": "3",
                        "NN": "Unidade da Federação",
                        "D1C": str(uf_code),
                        "D1N": sigla,
                        "D2C": str(indicator),
                        "D2N": ind_name,
                        "D3C": str(yr),
                        "D3N": str(yr),
                        "MN": resolved_unit,
                        "V": str(int(round(val))),
                    })
        else: # N6
            for item in res_list:
                loc = str(item.get("localidade", ""))[:6]
                res_dict = item.get("res", {})
                info = mapper.by_ibge6.get(loc) or mapper.by_ibge.get(loc) or {}
                cd7 = str(info.get("codigo_ibge") or info.get("ibge") or loc).strip()
                uf_sigla = info.get("uf", "")
                if terr_clean in UF_CODE_MAP and uf_sigla != terr_clean:
                    continue
                nm_clean = info.get("nome_municipio") or info.get("nome") or loc
                nm_label = f"{nm_clean} - {uf_sigla}" if uf_sigla else nm_clean
                for yr in years_list:
                    raw_val = res_dict.get(str(yr))
                    if raw_val is None:
                        continue
                    val_str = str(raw_val).strip()
                    if val_str in ("", "-", "..", "...", "X", "null", "None"):
                        continue
                    try:
                        v_num = float(val_str.replace(",", "."))
                        val_formatted = str(int(round(v_num)))
                    except (ValueError, TypeError):
                        val_formatted = val_str
                    rows.append({
                        "NC": "6",
                        "NN": "Município",
                        "D1C": cd7,
                        "D1N": nm_label,
                        "D2C": str(indicator),
                        "D2N": ind_name,
                        "D3C": str(yr),
                        "D3N": str(yr),
                        "MN": resolved_unit,
                        "V": val_formatted,
                    })

        if not rows:
            raise RuntimeError(
                f"Nenhum dado retornado pelo CEMADEN para o indicador {indicator} e território {territory}."
            )

        payload = [header] + rows
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False)
        except OSError:
            pass

        return payload

    def _query_br_in_uf_chunks(
        self,
        table: int,
        level: str,
        variables: Optional[List[int]],
        years: Optional[List[int]],
        classification: Optional[int],
        category: Optional[int],
        extra_classifications: Optional[Dict[int, Any]],
        use_cache: bool,
        progress_callback: Optional[Callable[[int, str], None]],
    ) -> List[Dict]:
        """Executa consulta Brasil (N6) em 27 lotes por UF para evitar timeout do SIDRA."""
        uf_list = sorted(UF_CODE_MAP.keys())
        header_row: Optional[Dict] = None
        all_rows: List[Dict] = []

        for idx, uf_sigla in enumerate(uf_list):
            if progress_callback:
                pct = 15 + int((idx / len(uf_list)) * 45)
                progress_callback(
                    pct,
                    f"Consultando Brasil por UF ({idx + 1}/{len(uf_list)} - {uf_sigla}, tabela {table})...",
                )
            chunk = self.query(
                table=table,
                territory=uf_sigla,
                level=level,
                variables=variables,
                years=years,
                classification=classification,
                category=category,
                extra_classifications=extra_classifications,
                use_cache=use_cache,
                progress_callback=None,
            )
            if not chunk:
                continue
            if header_row is None:
                header_row = dict(chunk[0])
            if len(chunk) > 1:
                all_rows.extend(chunk[1:])

        if header_row is None:
            raise RuntimeError("A consulta SIDRA por lotes de UF não retornou cabeçalho válido.")
        return [header_row] + all_rows

    def _query_composite_levels(
        self,
        table: int,
        territory: str,
        sub_levels: List[str],
        variables: Optional[List[int]],
        years: Optional[List[int]],
        classification: Optional[int],
        category: Optional[int],
        extra_classifications: Optional[Dict[int, Any]],
        use_cache: bool,
        progress_callback: Optional[Callable[[int, str], None]],
    ) -> List[Dict]:
        """Executa consulta SIDRA combinando múltiplos níveis territoriais (ex.: N7 + N6 ou N7 + N14)."""
        terr_clean = (territory or "BR").strip().upper()
        header_row: Optional[Dict] = None
        all_rows: List[Dict] = []
        last_exc: Optional[Exception] = None

        for idx, sub_lvl in enumerate(sub_levels):
            if sub_lvl == "N14" and terr_clean not in ("BR", "PI", "MA"):
                continue
            if progress_callback:
                progress_callback(
                    18 + idx * 18,
                    f"Consultando SIDRA ({sub_lvl} - Tabela {table})...",
                )
            try:
                chunk = self.query(
                    table=table,
                    territory=terr_clean,
                    level=sub_lvl,
                    variables=variables,
                    years=years,
                    classification=classification,
                    category=category,
                    extra_classifications=extra_classifications,
                    use_cache=use_cache,
                    progress_callback=None,
                )
            except Exception as exc:
                last_exc = exc
                LOGGER.warning("Subconsulta %s na tabela %s sem retorno (%s)", sub_lvl, table, exc)
                continue
            if chunk and len(chunk) > 1:
                if header_row is None:
                    header_row = dict(chunk[0])
                all_rows.extend(chunk[1:])

        if header_row is None:
            if last_exc is not None:
                raise last_exc
            raise RuntimeError("A consulta SIDRA combinada não retornou registros válidos.")
        return [header_row] + all_rows

    def query(
        self,
        table: int,
        territory: str = "BR",
        level: str = "N6",
        variables: Optional[List[int]] = None,
        years: Optional[List[int]] = None,
        classification: Optional[int] = None,
        category: Optional[int] = None,
        extra_classifications: Optional[Dict[int, Any]] = None,
        use_cache: bool = True,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> List[Dict]:
        """Consulta o SIDRA e retorna lista de registros decodificados."""
        terr_clean = (territory or "BR").strip().upper()
        lvl_clean = (level or "N6").upper()

        if str(table).upper() == "FROTA":
            var_id = variables[0] if variables else 28120
            return self.query_frota(
                indicator=var_id,
                territory=terr_clean,
                level=lvl_clean,
                years=years,
                use_cache=use_cache,
                progress_callback=progress_callback,
            )

        if str(table).upper() == "FINBRA":
            var_id = variables[0] if variables else 28141
            return self.query_finbra(
                indicator=var_id,
                territory=terr_clean,
                level=lvl_clean,
                years=years,
                use_cache=use_cache,
                progress_callback=progress_callback,
            )

        if str(table).upper() == "PINTEC_UF":
            var_id = variables[0] if variables else 82735
            return self.query_pintec_uf(
                indicator=var_id,
                territory=terr_clean,
                level=lvl_clean,
                years=years,
                use_cache=use_cache,
                progress_callback=progress_callback,
            )

        if str(table).upper() == "MUNIC_DIGITAL":
            var_id = variables[0] if variables else 326148
            return self.query_munic_digital(
                indicator=var_id,
                territory=terr_clean,
                level=lvl_clean,
                years=years,
                use_cache=use_cache,
                progress_callback=progress_callback,
            )

        if str(table).upper() == "CEMADEN":
            var_id = variables[0] if variables else 353155
            return self.query_cemaden(
                indicator=var_id,
                territory=terr_clean,
                level=lvl_clean,
                years=years,
                use_cache=use_cache,
                progress_callback=progress_callback,
            )

        if str(table).upper() == "BACEN":
            var_id = variables[0] if variables else 21910
            return self.query_bacen(
                indicator=var_id,
                territory=terr_clean,
                level=lvl_clean,
                years=years,
                use_cache=use_cache,
                progress_callback=progress_callback,
            )

        if lvl_clean in ("N7_N14", "N7_N6"):
            sub_levels = ["N7", "N14"] if lvl_clean == "N7_N14" else ["N7", "N6"]
            return self._query_composite_levels(
                table=table,
                territory=terr_clean,
                sub_levels=sub_levels,
                variables=variables,
                years=years,
                classification=classification,
                category=category,
                extra_classifications=extra_classifications,
                use_cache=use_cache,
                progress_callback=progress_callback,
            )

        url = self.build_url(
            table=table,
            territory=terr_clean,
            level=lvl_clean,
            variables=variables,
            years=years,
            classification=classification,
            category=category,
            extra_classifications=extra_classifications,
        )
        cache_key = hashlib.sha256(url.encode("utf-8")).hexdigest()
        cache_file = os.path.join(self.cache_dir, f"sidra_{cache_key}.json")

        if use_cache and os.path.exists(cache_file) and os.path.getsize(cache_file) > 100:
            if progress_callback:
                progress_callback(50, "Carregando dados do SIDRA do cache local...")
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError, UnicodeDecodeError) as cache_err:
                logger.debug("Cache read failed for %s: %s", cache_file, cache_err)

        extra_cnt = len(extra_classifications or {})
        use_uf_chunks = (
            terr_clean == "BR"
            and lvl_clean == "N6"
            and (
                int(table) in _HEAVY_BR_N6_TABLES
                or extra_cnt >= 3
                or (extra_cnt >= 2 and len(years or []) > 1)
            )
        )

        if use_uf_chunks:
            data = self._query_br_in_uf_chunks(
                table=table,
                level=lvl_clean,
                variables=variables,
                years=years,
                classification=classification,
                category=category,
                extra_classifications=extra_classifications,
                use_cache=use_cache,
                progress_callback=progress_callback,
            )
        else:
            if progress_callback:
                progress_callback(20, f"Consultando API SIDRA/IBGE (Tabela {table} - {terr_clean}/{lvl_clean})...")
            try:
                raw = self._fetch_url(url)
                data = json.loads(raw.decode("utf-8"))
            except Exception as exc:
                if exc.__class__.__name__ == "JobCancelled":
                    raise
                if terr_clean == "BR" and lvl_clean == "N6":
                    LOGGER.warning(
                        "Consulta direta BR/N6 na tabela %s falhou (%s); tentando fracionamento por UF...",
                        table,
                        exc,
                    )
                    data = self._query_br_in_uf_chunks(
                        table=table,
                        level=lvl_clean,
                        variables=variables,
                        years=years,
                        classification=classification,
                        category=category,
                        extra_classifications=extra_classifications,
                        use_cache=use_cache,
                        progress_callback=progress_callback,
                    )
                else:
                    raise

        if not isinstance(data, list) or len(data) == 0:
            raise RuntimeError("A API do SIDRA retornou uma resposta vazia ou inválida.")

        try:
            tmp_cache = f"{cache_file}.part"
            with open(tmp_cache, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            os.replace(tmp_cache, cache_file)
        except Exception as exc:
            LOGGER.warning("Não foi possível gravar cache SIDRA: %s", exc)

        return data

    @staticmethod
    def _normalize_uf_clf_chunk(chunk: List[Dict]) -> List[Dict]:
        """Converte dimensão de classificação de UF (c12354) para dimensão N3 padrão (D1C/D1N)."""
        if not chunk:
            return chunk
        header = dict(chunk[0])
        uf_dim = None
        for k, val in header.items():
            if not (k.startswith("D") and k.endswith("C") and k[1:-1].isdigit()):
                continue
            if k == "D1C":
                continue
            txt = str(val or "").lower()
            if "unidade da federa" in txt or "unidades da federa" in txt:
                uf_dim = k[:-1]
                break

        if not uf_dim:
            return chunk

        uf_c_key, uf_n_key = f"{uf_dim}C", f"{uf_dim}N"
        norm_header = dict(header)
        norm_header["NC"] = "3"
        norm_header["NN"] = "Unidade da Federação"
        norm_header["D1C"] = "Unidade da Federação (Código)"
        norm_header["D1N"] = "Unidade da Federação"
        norm_header.pop(uf_c_key, None)
        norm_header.pop(uf_n_key, None)

        norm_rows: List[Dict] = [norm_header]
        for row in chunk[1:]:
            cat_code = str(row.get(uf_c_key, "")).strip()
            uf_ibge = C12354_CAT_TO_UF_NUM.get(cat_code)
            if not uf_ibge:
                continue
            r_copy = dict(row)
            r_copy["NC"] = "3"
            r_copy["NN"] = "Unidade da Federação"
            r_copy["D1C"] = uf_ibge
            r_copy["D1N"] = str(row.get(uf_n_key, "")).strip()
            r_copy.pop(uf_c_key, None)
            r_copy.pop(uf_n_key, None)
            norm_rows.append(r_copy)
        return norm_rows

    def query_series(
        self,
        table_plans: List[Dict[str, Any]],
        territory: str = "BR",
        level: str = "N6",
        classification: Optional[int] = None,
        category: Optional[int] = None,
        extra_classifications: Optional[Dict[int, int]] = None,
        use_cache: bool = True,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> List[Dict]:
        """
        Executa uma ou mais consultas SIDRA (quando a série histórica atravessa
        tabelas antiga e nova) e combina os registros em um único payload SIDRA.
        """
        combined_header: Optional[Dict] = None
        combined_rows: List[Dict] = []

        terr_clean = (territory or "BR").strip().upper()
        total_plans = max(1, len(table_plans))
        for idx, plan in enumerate(table_plans):
            if progress_callback:
                pct = 15 + int((idx / total_plans) * 40)
                progress_callback(
                    pct,
                    f"Consultando Tabela {plan['table']} ({', '.join(str(y) for y in plan['years'])})...",
                )

            seg_cat = category
            cat_overrides = plan.get("cat_overrides") or {}
            if category is not None and int(category) in cat_overrides:
                seg_cat = cat_overrides[int(category)]
                if seg_cat is None:
                    continue

            uf_clf_id = plan.get("uf_classification")
            seg_extra = dict(extra_classifications or {})
            seg_level = level
            seg_terr = territory
            if uf_clf_id is not None:
                if terr_clean in UF_SIGLA_TO_C12354_CAT:
                    seg_extra[int(uf_clf_id)] = UF_SIGLA_TO_C12354_CAT[terr_clean]
                else:
                    seg_extra[int(uf_clf_id)] = list(UF_SIGLA_TO_C12354_CAT.values())
                seg_level = "N1"
                seg_terr = "BR"

            if plan.get("provider") == "frota" or str(plan.get("table", "")).upper() == "FROTA":
                chunk = self.query_frota(
                    indicator=plan["query_var"],
                    territory=terr_clean,
                    level=level,
                    years=plan["years"],
                    use_cache=use_cache,
                    progress_callback=progress_callback,
                )
            elif plan.get("provider") == "finbra" or str(plan.get("table", "")).upper() == "FINBRA":
                chunk = self.query_finbra(
                    indicator=plan["query_var"],
                    territory=terr_clean,
                    level=level,
                    years=plan["years"],
                    use_cache=use_cache,
                    progress_callback=progress_callback,
                )
            elif plan.get("provider") == "pintec_uf" or str(plan.get("table", "")).upper() == "PINTEC_UF":
                chunk = self.query_pintec_uf(
                    indicator=plan["query_var"],
                    territory=terr_clean,
                    level=level,
                    years=plan["years"],
                    use_cache=use_cache,
                    progress_callback=progress_callback,
                )
            elif plan.get("provider") == "munic_digital" or str(plan.get("table", "")).upper() == "MUNIC_DIGITAL":
                chunk = self.query_munic_digital(
                    indicator=plan["query_var"],
                    territory=terr_clean,
                    level=level,
                    years=plan["years"],
                    use_cache=use_cache,
                    progress_callback=progress_callback,
                )
            elif plan.get("provider") == "cemaden" or str(plan.get("table", "")).upper() == "CEMADEN":
                chunk = self.query_cemaden(
                    indicator=plan["query_var"],
                    territory=terr_clean,
                    level=level,
                    years=plan["years"],
                    use_cache=use_cache,
                    progress_callback=progress_callback,
                )
            elif plan.get("provider") == "bacen" or str(plan.get("table", "")).upper() == "BACEN":
                chunk = self.query_bacen(
                    indicator=plan["query_var"],
                    territory=terr_clean,
                    level=level,
                    years=plan["years"],
                    use_cache=use_cache,
                    progress_callback=progress_callback,
                )
            else:
                chunk = self.query(
                    table=plan["table"],
                    territory=seg_terr,
                    level=seg_level,
                    variables=[plan["query_var"]],
                    years=plan["years"],
                    classification=classification,
                    category=seg_cat,
                    extra_classifications=seg_extra or None,
                    use_cache=use_cache,
                    progress_callback=progress_callback if (terr_clean == "BR" and level == "N6") else None,
                )
            if uf_clf_id is not None:
                chunk = self._normalize_uf_clf_chunk(chunk)
            if not chunk:
                continue

            if combined_header is None:
                combined_header = dict(chunk[0])

            req_var = str(plan["requested_var"])
            qry_var = str(plan["query_var"])
            for row in chunk[1:]:
                if req_var != qry_var:
                    r_copy = dict(row)
                    if str(r_copy.get("D2C", "")).strip() == qry_var:
                        r_copy["D2C"] = req_var
                    combined_rows.append(r_copy)
                else:
                    combined_rows.append(row)

        if combined_header is None:
            raise RuntimeError("Nenhum dado retornado para os períodos e filtros selecionados.")

        return [combined_header] + combined_rows

    @staticmethod
    def _detect_dimension_keys(header: Dict[str, Any]) -> tuple:
        """Identifica dinamicamente as chaves de território, variável e período no cabeçalho SIDRA."""
        terr_key = None
        var_key = None
        year_key = None

        d_keys = sorted(
            (k for k in header.keys() if k.startswith("D") and k.endswith("C") and k[1:-1].isdigit()),
            key=lambda x: int(x[1:-1]),
        )
        for k in d_keys:
            prefix = k[:-1]
            lbl = str(header.get(k) or "").strip().lower()
            base = lbl.split("(", 1)[0].strip()
            if var_key is None and base in ("variável", "variavel"):
                var_key = prefix
            elif year_key is None and base in (
                "ano",
                "mês",
                "mes",
                "trimestre",
                "trimestre móvel",
                "trimestre movel",
                "semestre",
                "período",
                "periodo",
            ):
                year_key = prefix
            elif terr_key is None and (
                base in (
                    "município",
                    "municipio",
                    "unidade da federação",
                    "unidade da federacao",
                    "brasil",
                    "grande região",
                    "grande regiao",
                    "mesorregião geográfica",
                    "mesorregiao geografica",
                    "microrregião geográfica",
                    "microrregiao geografica",
                )
                or base.startswith("região metropolitana")
                or base.startswith("regiao metropolitana")
                or base.startswith("região integrada de desenvolvimento")
                or base.startswith("regiao integrada de desenvolvimento")
            ):
                terr_key = prefix

        return terr_key or "D1", var_key or "D2", year_key or "D3"

    @staticmethod
    def parse_records(
        raw_data: List[Dict],
        primary_var: Optional[int] = None,
        agg_mode: str = "sum",
        allow_negative: bool = False,
    ) -> Dict:
        """
        Estrutura e agrega os dados brutos da tabela SIDRA por município, estado ou Brasil.
        Suporta agg_mode:
          - 'sum': soma ao longo dos anos (fluxos: toneladas, R$, área colhida, PIB)
          - 'last': último ano disponível por unidade (estoques: população, rebanho, empresas)
          - 'mean': média aritmética no período (taxas, rendimentos, densidade, Gini)
        """
        if not raw_data or len(raw_data) < 2:
            return {
                "by_mun": {},
                "time_series": {},
                "total": 0.0,
                "mean_value": 0.0,
                "top_producers": [],
                "agg_mode": agg_mode,
                "allow_negative": allow_negative,
            }

        header = raw_data[0]
        rows = raw_data[1:]
        terr_key, var_key, year_key = SidraClient._detect_dimension_keys(header)

        by_mun: Dict[str, Dict] = {}
        ts_sums: Dict[str, float] = {}
        ts_counts: Dict[str, int] = {}
        all_years = set()
        all_variables = set()

        first_prod_name = ""
        first_var_name = ""
        unit_name = ""
        nc_seen = set()

        for row in rows:
            nc = str(row.get("NC", "")).strip()
            cd_item = str(row.get(f"{terr_key}C", "")).strip()
            nm_full = str(row.get(f"{terr_key}N", "")).strip()

            if not cd_item:
                continue

            if nc:
                nc_seen.add(nc)

            if nc == "1":
                cd_mun = "BR"
                nm_mun = "Brasil"
                uf = "BR"
            elif nc == "2":
                cd_mun = cd_item
                nm_mun = nm_full
                uf = MACRO_REGION_SIGLAS.get(cd_mun, "BR")
            elif nc == "3":
                cd_mun = cd_item
                nm_mun = nm_full
                uf = UF_NUM_TO_SIGLA.get(cd_mun, "")
            elif nc == "7":
                cd_mun = cd_item
                if " - " in nm_full:
                    nm_base, uf = nm_full.rsplit(" - ", 1)
                else:
                    nm_base, uf = nm_full, UF_NUM_TO_SIGLA.get(cd_item[:2], "")
                nm_mun = nm_base if "(RM)" in nm_base else f"{nm_base} (RM)"
            elif nc == "14":
                cd_mun = cd_item
                nm_mun = nm_full if "RIDE" in nm_full.upper() else f"{nm_full} (RIDE)"
                uf = "PI/MA" if cd_item == "510" else ""
            elif nc in ("8", "9"):
                cd_mun = cd_item
                if " - " in nm_full:
                    nm_mun, uf = nm_full.rsplit(" - ", 1)
                else:
                    nm_mun, uf = nm_full, UF_NUM_TO_SIGLA.get(cd_item[:2], "")
            else:
                cd_mun = cd_item
                if " - " in nm_full:
                    nm_mun, uf = nm_full.rsplit(" - ", 1)
                else:
                    nm_mun, uf = nm_full, UF_NUM_TO_SIGLA.get(cd_item[:2], "")

            var_code = str(row.get(f"{var_key}C", "")).strip()
            var_label = str(row.get(f"{var_key}N", "")).strip()
            ano = str(row.get(f"{year_key}C", "")).strip()
            val_str = str(row.get("V", "")).strip()
            unit = str(row.get("MN", "") or "").strip()
            prod_name = str(row.get("D4N", "") or "").strip()

            if prod_name and not first_prod_name:
                first_prod_name = prod_name
            if var_label and not first_var_name:
                first_var_name = var_label
            if unit and not unit_name:
                unit_name = unit

            is_valid_num = False
            if val_str in ("-", "..", "...", "X", "", "null", "None"):
                val = 0.0
            else:
                try:
                    val = float(val_str.replace(",", "."))
                    is_valid_num = True
                except (ValueError, TypeError):
                    val = 0.0

            all_years.add(ano)
            all_variables.add(var_code)

            if cd_mun not in by_mun:
                by_mun[cd_mun] = {
                    "cd_mun": cd_mun,
                    "nm_mun": nm_mun,
                    "uf": uf,
                    "vars": {},
                    "years": {},
                    "has_record": False,
                    "valor_principal": 0.0,
                }

            if is_valid_num:
                by_mun[cd_mun]["has_record"] = True
                by_mun[cd_mun]["years"].setdefault(ano, {})[var_code] = val

                if primary_var is None or str(primary_var) == var_code:
                    ts_sums[ano] = ts_sums.get(ano, 0.0) + val
                    ts_counts[ano] = ts_counts.get(ano, 0) + 1

        prim_str = str(primary_var) if primary_var is not None else None
        mode = (agg_mode or "sum").lower()
        total_prod = 0.0
        valid_values_for_mean: List[float] = []

        for mun_data in by_mun.values():
            sorted_yrs = sorted(mun_data["years"].keys())
            for vc in all_variables:
                yr_vals = [
                    mun_data["years"][y][vc]
                    for y in sorted_yrs
                    if vc in mun_data["years"][y]
                ]
                if not yr_vals:
                    agg_v = 0.0
                elif mode == "last":
                    agg_v = yr_vals[-1]
                elif mode == "mean":
                    agg_v = sum(yr_vals) / len(yr_vals)
                else:
                    agg_v = sum(yr_vals)
                mun_data["vars"][vc] = agg_v

            if prim_str and prim_str in mun_data["vars"]:
                mun_data["valor_principal"] = mun_data["vars"][prim_str]
            elif mun_data["vars"]:
                mun_data["valor_principal"] = next(iter(mun_data["vars"].values()))

            vp = mun_data["valor_principal"]
            if mode == "mean":
                if mun_data["has_record"]:
                    valid_values_for_mean.append(vp)
            else:
                total_prod += vp

        mean_val = (sum(valid_values_for_mean) / len(valid_values_for_mean)) if valid_values_for_mean else 0.0

        time_series: Dict[str, float] = {}
        for yr in sorted(ts_sums.keys()):
            if mode == "mean" and ts_counts.get(yr, 0) > 0:
                time_series[yr] = ts_sums[yr] / ts_counts[yr]
            else:
                time_series[yr] = ts_sums[yr]

        if nc_seen == {"1"}:
            level_detected = "N1"
        elif nc_seen == {"2"}:
            level_detected = "N2"
        elif nc_seen == {"3"}:
            level_detected = "N3"
        elif nc_seen == {"7"}:
            level_detected = "N7"
        elif nc_seen == {"8"}:
            level_detected = "N8"
        elif nc_seen == {"9"}:
            level_detected = "N9"
        elif nc_seen == {"14"}:
            level_detected = "N14"
        elif nc_seen == {"7", "14"}:
            level_detected = "N7_N14"
        elif nc_seen == {"7", "6"}:
            level_detected = "N7_N6"
        else:
            level_detected = "N6"

        top_producers = []
        for mun_data in by_mun.values():
            vp = mun_data["valor_principal"]
            if mode != "mean" and not allow_negative and total_prod > 0:
                share = (vp / total_prod * 100.0)
            else:
                share = 0.0
            mun_data["share_pct"] = share

            if allow_negative:
                if mun_data["has_record"]:
                    top_producers.append(mun_data)
            elif vp > 0 or (
                mun_data["has_record"]
                and level_detected in ("N1", "N2", "N3", "N7", "N8", "N9", "N14", "N7_N14", "N7_N6")
            ) or level_detected in ("N1", "N3"):
                top_producers.append(mun_data)

        top_producers.sort(key=lambda x: x["valor_principal"], reverse=True)
        for rank, item in enumerate(top_producers, start=1):
            item["ranking"] = rank

        return {
            "by_mun": by_mun,
            "time_series": time_series,
            "total": total_prod,
            "mean_value": mean_val,
            "top_producers": top_producers,
            "product_name": first_prod_name,
            "variable_name": first_var_name,
            "unit": unit_name,
            "years": sorted(all_years),
            "variables": sorted(all_variables),
            "level": level_detected,
            "agg_mode": mode,
            "allow_negative": allow_negative,
        }
