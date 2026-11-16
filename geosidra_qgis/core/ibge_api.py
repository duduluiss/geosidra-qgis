# -*- coding: utf-8 -*-
"""
Cliente otimizado para a API de Malhas v3 e Localidades do IBGE.
Suporta download e cache permanente das malhas:
  - N1 / N3: Estados (27 UFs)
  - N2: Grandes Regiões (5 macrorregiões)
  - N6: Municípios (por UF ou Brasil completo)
  - N7 / N14: Regiões Metropolitanas (20 RMs) e RIDE Grande Teresina (composicao oficial IBGE)
  - N7_N6: Malha combinada de Regiões Metropolitanas + Capitais Isoladas (IPCA / INPC / IPCA-15)
  - N8: Mesorregiões Geográficas (137 no Brasil)
  - N9: Microrregiões Geográficas (558 no Brasil)
"""

import gzip
import hashlib
import http.client
import json
import logging
import os
import shutil
import tempfile
from typing import Any, Callable, Dict, Iterable, List, Optional
from urllib.parse import urlparse

LOGGER = logging.getLogger("GeoSIDRA")

VALID_BRAZIL_UFS = {
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO",
    "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR",
    "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
}

IBGE_MACRO_REGIONS = [
    ("1", "Norte"),
    ("2", "Nordeste"),
    ("3", "Sudeste"),
    ("4", "Sul"),
    ("5", "Centro-Oeste"),
]

IBGE_MACRO_REGION_INFO: Dict[str, tuple] = {
    "1": ("Norte", "N"),
    "2": ("Nordeste", "NE"),
    "3": ("Sudeste", "SE"),
    "4": ("Sul", "S"),
    "5": ("Centro-Oeste", "CO"),
}

IPCA_ISOLATED_CAPITALS = (
    "1200401",  # Rio Branco - AC
    "2111300",  # São Luís - MA
    "2800308",  # Aracaju - SE
    "5002704",  # Campo Grande - MS
    "5208707",  # Goiânia - GO
    "5300108",  # Brasília - DF
)

ALLOWED_IBGE_HOST = "servicodados.ibge.gov.br"


def get_persistent_cache_dir() -> str:
    """Retorna diretório permanente de cache de malhas no perfil do usuário."""
    candidates = [
        os.path.join(os.path.expanduser("~"), ".geosidra", "cache_malhas"),
        os.path.join(tempfile.gettempdir(), "geosidra_ibge_cache"),
    ]
    for path in candidates:
        try:
            os.makedirs(path, exist_ok=True)
            return path
        except OSError:
            continue
    return tempfile.gettempdir()


def _atomic_write_bytes(path: str, data: bytes) -> None:
    """Grava em arquivo temporário e renomeia para atomicidade."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp_path = f"{path}.part"
    with open(tmp_path, "wb") as f:
        f.write(data)
    os.replace(tmp_path, path)


def _atomic_write_json(path: str, obj: Dict[str, Any]) -> None:
    _atomic_write_bytes(path, json.dumps(obj, ensure_ascii=False).encode("utf-8"))


def _extract_polygon_parts(geom: Optional[Dict[str, Any]]) -> List[Any]:
    """Extrai lista de anéis de polígonos a partir de geometria Polygon ou MultiPolygon GeoJSON."""
    if not isinstance(geom, dict):
        return []
    gtype = geom.get("type")
    coords = geom.get("coordinates")
    if not coords:
        return []
    if gtype == "Polygon":
        return [coords]
    if gtype == "MultiPolygon":
        return list(coords)
    if gtype == "GeometryCollection":
        out: List[Any] = []
        for sub in geom.get("geometries", []):
            out.extend(_extract_polygon_parts(sub))
        return out
    return []


class IbgeMalhasClient:
    """Cliente com cache permanente e compressão gzip para download de malhas do IBGE."""

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir or get_persistent_cache_dir()
        os.makedirs(self.cache_dir, exist_ok=True)
        self.shared_cache_dirs = [
            os.path.join(os.path.expanduser("~"), ".geocomex", "cache_malhas"),
            os.path.join(os.path.expanduser("~"), ".geotrabalho", "cache_malhas"),
        ]

    def _check_shared_cache(self, filename: str) -> Optional[str]:
        target = os.path.join(self.cache_dir, filename)
        if os.path.exists(target) and os.path.getsize(target) > 500:
            return target
        for sc in self.shared_cache_dirs:
            candidate = os.path.join(sc, filename)
            if os.path.exists(candidate) and os.path.getsize(candidate) > 500:
                try:
                    shutil.copy2(candidate, target)
                    return target
                except (OSError, shutil.Error):
                    return candidate
        return None

    @staticmethod
    def _fetch_bytes_https(url: str, timeout: int = 180) -> Optional[bytes]:
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.netloc != ALLOWED_IBGE_HOST:
            raise ValueError(f"Host ou protocolo não permitido para API do IBGE: {url}")

        path_query = parsed.path + (f"?{parsed.query}" if parsed.query else "")
        conn = http.client.HTTPSConnection(ALLOWED_IBGE_HOST, timeout=timeout)
        try:
            conn.request(
                "GET",
                path_query,
                headers={
                    "User-Agent": "QGIS-GeoSIDRA-Plugin/0.5",
                    "Accept": "application/vnd.geo+json, application/json",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "close",
                },
            )
            resp = conn.getresponse()
            if resp.status != 200:
                LOGGER.warning("API IBGE retornou HTTP %s para %s", resp.status, url)
                return None
            raw = resp.read()
            if raw[:2] == b"\x1f\x8b":
                raw = gzip.decompress(raw)
            return raw
        except Exception as exc:
            LOGGER.warning("Falha em _fetch_bytes_https (%s): %s", url, exc)
            return None
        finally:
            conn.close()

    @staticmethod
    def _fetch_bytes_qgis(url: str) -> Optional[bytes]:
        try:
            from qgis.core import QgsBlockingNetworkRequest
            from qgis.PyQt.QtCore import QUrl
            from qgis.PyQt.QtNetwork import QNetworkRequest

            qreq = QNetworkRequest(QUrl(url))
            qreq.setRawHeader(b"User-Agent", b"QGIS-GeoSIDRA-Plugin/0.5")
            qreq.setRawHeader(b"Accept", b"application/vnd.geo+json, application/json")
            qreq.setRawHeader(b"Accept-Encoding", b"gzip, deflate")
            blocker = QgsBlockingNetworkRequest()
            err = blocker.get(qreq)
            if err == QgsBlockingNetworkRequest.ErrorCode.NoError:
                raw = bytes(blocker.reply().content())
                if raw[:2] == b"\x1f\x8b":
                    raw = gzip.decompress(raw)
                return raw
        except (ImportError, AttributeError, RuntimeError, OSError):
            return None
        return None

    @classmethod
    def _fetch_raw_geojson_bytes(cls, url: str, timeout: int = 180) -> bytes:
        raw = cls._fetch_bytes_https(url, timeout=timeout)
        if not raw:
            raw = cls._fetch_bytes_qgis(url)
        if not raw:
            raise RuntimeError(f"Não foi possível baixar malha da API do IBGE ({url}). Verifique sua conexão.")
        return raw

    def _fetch_cached_single(
        self,
        filename: str,
        url: str,
        cache_msg: str,
        download_msg: str,
        timeout: int = 120,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> str:
        shared = self._check_shared_cache(filename)
        if shared:
            if progress_callback:
                progress_callback(92, cache_msg)
            return shared

        cache_file = os.path.join(self.cache_dir, filename)
        if progress_callback:
            progress_callback(85, download_msg)
        raw_bytes = self._fetch_raw_geojson_bytes(url, timeout=timeout)
        _atomic_write_bytes(cache_file, raw_bytes)
        return cache_file

    def _normalize_territory_and_quality(self, territory: str, qualidade: str) -> tuple:
        uf_clean = (territory or "BR").strip().upper()
        is_br = uf_clean == "BR" or uf_clean not in VALID_BRAZIL_UFS
        if is_br:
            uf_clean = "BR"
        qual_clean = (qualidade or "auto").strip().lower()
        if qual_clean == "auto" or qual_clean not in ("minima", "intermediaria", "maxima"):
            qual_clean = "minima" if is_br else "intermediaria"
        return uf_clean, is_br, qual_clean

    def fetch_states_geojson(self, progress_callback: Optional[Callable[[int, str], None]] = None) -> str:
        """Baixa e cacheia a malha oficial dos 27 Estados (UFs) do Brasil (N3)."""
        return self._fetch_cached_single(
            filename="malha_estados_BR_minima.geojson",
            url="https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo+json&qualidade=minima&intrarregiao=UF",
            cache_msg="Carregando malha dos estados do cache local...",
            download_msg="Baixando malha dos estados (UFs) da API do IBGE...",
            timeout=60,
            progress_callback=progress_callback,
        )

    def fetch_macro_regions_geojson(self, progress_callback: Optional[Callable[[int, str], None]] = None) -> str:
        """Baixa e cacheia a malha oficial das 5 Grandes Regiões do Brasil (N2)."""
        return self._fetch_cached_single(
            filename="malha_macro_regioes_BR_minima.geojson",
            url="https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo+json&qualidade=minima&intrarregiao=regiao",
            cache_msg="Carregando malha das Grandes Regiões (N2) do cache local...",
            download_msg="Baixando malha das Grandes Regiões (N2) da API do IBGE...",
            timeout=60,
            progress_callback=progress_callback,
        )

    def fetch_mesoregions_geojson(
        self,
        territory: str = "BR",
        qualidade: str = "auto",
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> str:
        """Baixa e cacheia a malha oficial de Mesorregiões Geográficas (N8)."""
        uf_clean, is_br, qual_clean = self._normalize_territory_and_quality(territory, qualidade)
        url = (
            f"https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo+json&qualidade={qual_clean}&intrarregiao=mesorregiao"
            if is_br
            else f"https://servicodados.ibge.gov.br/api/v3/malhas/estados/{uf_clean}?formato=application/vnd.geo+json&qualidade={qual_clean}&intrarregiao=mesorregiao"
        )
        return self._fetch_cached_single(
            filename=f"malha_meso_{uf_clean}_{qual_clean}.geojson",
            url=url,
            cache_msg=f"Carregando malha de mesorregiões ({uf_clean}) do cache local...",
            download_msg=f"Baixando malha de mesorregiões ({uf_clean}) da API do IBGE...",
            timeout=90,
            progress_callback=progress_callback,
        )

    def fetch_microregions_geojson(
        self,
        territory: str = "BR",
        qualidade: str = "auto",
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> str:
        """Baixa e cacheia a malha oficial de Microrregiões Geográficas (N9)."""
        uf_clean, is_br, qual_clean = self._normalize_territory_and_quality(territory, qualidade)
        url = (
            f"https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo+json&qualidade={qual_clean}&intrarregiao=microrregiao"
            if is_br
            else f"https://servicodados.ibge.gov.br/api/v3/malhas/estados/{uf_clean}?formato=application/vnd.geo+json&qualidade={qual_clean}&intrarregiao=microrregiao"
        )
        return self._fetch_cached_single(
            filename=f"malha_micro_{uf_clean}_{qual_clean}.geojson",
            url=url,
            cache_msg=f"Carregando malha de microrregiões ({uf_clean}) do cache local...",
            download_msg=f"Baixando malha de microrregiões ({uf_clean}) da API do IBGE...",
            timeout=90,
            progress_callback=progress_callback,
        )

    def fetch_uf_geojson(
        self,
        uf: str,
        qualidade: str = "auto",
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> str:
        """Baixa e cacheia a malha municipal oficial (N6) de uma UF ou de todo o Brasil."""
        uf_clean, is_br, qual_clean = self._normalize_territory_and_quality(uf, qualidade)
        filename = f"malha_mun_{uf_clean}_{qual_clean}.geojson"
        shared = self._check_shared_cache(filename)
        if shared:
            if progress_callback:
                progress_callback(92, f"Carregando malha municipal ({uf_clean}) do cache local...")
            return shared

        cache_file = os.path.join(self.cache_dir, filename)

        if is_br:
            all_features: List[Dict] = []
            for idx, (reg_code, reg_name) in enumerate(IBGE_MACRO_REGIONS, start=1):
                if progress_callback:
                    progress_callback(
                        82 + int((idx - 1) * 2.4),
                        f"Baixando malha municipal: Região {reg_name} ({idx}/5)...",
                    )
                reg_url = (
                    f"https://servicodados.ibge.gov.br/api/v3/malhas/regioes/{reg_code}"
                    f"?formato=application/vnd.geo+json&qualidade={qual_clean}&intrarregiao=municipio"
                )
                raw_r = self._fetch_raw_geojson_bytes(reg_url, timeout=60)
                data = json.loads(raw_r.decode("utf-8"))
                all_features.extend(data.get("features", []))

            combined_geojson = {"type": "FeatureCollection", "features": all_features}
            _atomic_write_json(cache_file, combined_geojson)
            return cache_file

        url = (
            f"https://servicodados.ibge.gov.br/api/v3/malhas/estados/{uf_clean}"
            f"?formato=application/vnd.geo+json&qualidade={qual_clean}&intrarregiao=municipio"
        )
        raw_bytes = self._fetch_raw_geojson_bytes(url, timeout=120)
        _atomic_write_bytes(cache_file, raw_bytes)
        return cache_file

    @staticmethod
    def load_rm_n7_n14_specs() -> List[Dict[str, Any]]:
        """Carrega o mapeamento oficial das 20 RMs (N7) + RIDE Grande Teresina (N14) para códigos municipais."""
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "rm_n7_n14_municipalities.json",
        )
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_dissolved_rm_cache_path(self) -> str:
        """Retorna caminho do cache persistente de RMs/RIDEs já dissolvidas no QGIS."""
        return os.path.join(self.cache_dir, "malha_rm_n7_n14_dissolved_v1.geojson")

    def _build_or_load_raw_rm_geojson(
        self,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> str:
        """Constrói em Python puro a malha MultiPolygon das 20 RMs (N7) + 1 RIDE (N14) pelos municípios IBGE."""
        dissolved_path = self.get_dissolved_rm_cache_path()
        if os.path.exists(dissolved_path) and os.path.getsize(dissolved_path) > 1000:
            if progress_callback:
                progress_callback(92, "Carregando malha metropolitana (N7/N14) dissolvida do cache...")
            return dissolved_path

        raw_rm_path = os.path.join(self.cache_dir, "malha_rm_n7_n14_raw_v1.geojson")
        if os.path.exists(raw_rm_path) and os.path.getsize(raw_rm_path) > 1000:
            if progress_callback:
                progress_callback(92, "Carregando composição de RMs/RIDEs (N7/N14) do cache...")
            return raw_rm_path

        if progress_callback:
            progress_callback(82, "Obtendo malha municipal base para compor Regiões Metropolitanas (N7/N14)...")

        mun_br_path = self.fetch_uf_geojson("BR", qualidade="minima", progress_callback=progress_callback)
        with open(mun_br_path, "r", encoding="utf-8") as f:
            mun_fc = json.load(f)

        geom_by_mun: Dict[str, Dict[str, Any]] = {}
        for feat in mun_fc.get("features", []):
            code = str((feat.get("properties") or {}).get("codarea") or "").strip().zfill(7)
            if code and feat.get("geometry"):
                geom_by_mun[code] = feat["geometry"]

        specs = self.load_rm_n7_n14_specs()
        rm_features: List[Dict[str, Any]] = []
        for spec in specs:
            poly_parts: List[Any] = []
            for mun_id in spec.get("municipality_ids", []):
                mgeom = geom_by_mun.get(str(mun_id).zfill(7))
                if mgeom:
                    poly_parts.extend(_extract_polygon_parts(mgeom))
            if not poly_parts:
                continue
            rm_features.append({
                "type": "Feature",
                "properties": {
                    "codarea": str(spec["sidra_code"]),
                    "nivel": str(spec["level"]),
                    "nome": str(spec["name"]),
                    "uf": str(spec["uf"]),
                    "dissolved": False,
                },
                "geometry": {
                    "type": "MultiPolygon",
                    "coordinates": poly_parts,
                },
            })

        _atomic_write_json(raw_rm_path, {"type": "FeatureCollection", "features": rm_features})
        return raw_rm_path

    def fetch_metro_geojson(
        self,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> str:
        """Retorna GeoJSON das 20 Regiões Metropolitanas (N7) + RIDE Grande Teresina (N14)."""
        return self._build_or_load_raw_rm_geojson(progress_callback=progress_callback)

    def fetch_metro_and_capitals_geojson(
        self,
        capital_codes: Optional[Iterable[str]] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> str:
        """
        Combina a malha de RMs/RIDEs (N7/N14) com municípios/capitais isoladas (N6)
        para mapear pesquisas híbridas como IPCA, INPC e IPCA-15.
        """
        caps = sorted({str(c).strip().zfill(7) for c in (capital_codes or IPCA_ISOLATED_CAPITALS) if str(c).strip()})
        has_dissolved = os.path.exists(self.get_dissolved_rm_cache_path())
        key_src = f"{'d' if has_dissolved else 'r'}:{','.join(caps)}"
        key = hashlib.sha256(key_src.encode("utf-8")).hexdigest()[:12]
        out_path = os.path.join(self.cache_dir, f"malha_rm_capitais_{key}.geojson")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
            if progress_callback:
                progress_callback(92, "Carregando malha combinada RMs + Capitais do cache...")
            return out_path

        rm_path = self._build_or_load_raw_rm_geojson(progress_callback=progress_callback)
        with open(rm_path, "r", encoding="utf-8") as f:
            rm_fc = json.load(f)

        mun_br_path = self.fetch_uf_geojson("BR", qualidade="minima", progress_callback=progress_callback)
        with open(mun_br_path, "r", encoding="utf-8") as f:
            mun_fc = json.load(f)

        cap_set = set(caps)
        combined_feats: List[Dict[str, Any]] = []
        for feat in rm_fc.get("features", []):
            fcopy = dict(feat)
            props = dict(fcopy.get("properties") or {})
            props.setdefault("nivel", "N7" if len(str(props.get("codarea", ""))) == 4 else "N14")
            fcopy["properties"] = props
            combined_feats.append(fcopy)

        for feat in mun_fc.get("features", []):
            props = feat.get("properties") or {}
            code = str(props.get("codarea") or "").strip().zfill(7)
            if code in cap_set:
                combined_feats.append({
                    "type": "Feature",
                    "properties": {
                        "codarea": code,
                        "nivel": "N6",
                        "dissolved": True,
                    },
                    "geometry": feat.get("geometry"),
                })

        _atomic_write_json(out_path, {"type": "FeatureCollection", "features": combined_feats})
        return out_path

    def fetch_geojson_for_level(
        self,
        level: str,
        territory: str = "BR",
        capital_codes: Optional[Iterable[str]] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> str:
        """Despacha o download/cache da malha IBGE oficial adequada ao nível territorial."""
        lvl = (level or "N6").strip().upper()
        if lvl in ("N1", "N3"):
            return self.fetch_states_geojson(progress_callback=progress_callback)
        if lvl == "N2":
            return self.fetch_macro_regions_geojson(progress_callback=progress_callback)
        if lvl == "N8":
            return self.fetch_mesoregions_geojson(territory=territory, progress_callback=progress_callback)
        if lvl == "N9":
            return self.fetch_microregions_geojson(territory=territory, progress_callback=progress_callback)
        if lvl in ("N7", "N14", "N7_N14"):
            return self.fetch_metro_geojson(progress_callback=progress_callback)
        if lvl == "N7_N6":
            return self.fetch_metro_and_capitals_geojson(
                capital_codes=capital_codes,
                progress_callback=progress_callback,
            )
        return self.fetch_uf_geojson(territory, progress_callback=progress_callback)
