# -*- coding: utf-8 -*-
"""
Tradutor e resolutor oficial de municípios brasileiros (IBGE 7 dígitos, IBGE 6 dígitos, Nome e UF).
"""

import json
import logging
import os
import unicodedata
from typing import Dict, Optional, Tuple

LOGGER = logging.getLogger("GeoSIDRA")


def normalize_text(text: str) -> str:
    """Remove acentos, converte para maiúsculas e padroniza espaços."""
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFKD", str(text))
    ascii_str = nfkd.encode("ASCII", "ignore").decode("ASCII")
    return " ".join(ascii_str.upper().strip().split())


class MunicipalityMapper:
    """Mapeador em memória para todos os municípios brasileiros."""

    _instance = None

    def __init__(self, json_path: Optional[str] = None):
        if json_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            json_path = os.path.join(base_dir, "data", "tse_ibge_municipios.json")

        self.by_ibge: Dict[str, Dict[str, str]] = {}
        self.by_ibge6: Dict[str, Dict[str, str]] = {}
        self.by_uf_name: Dict[str, Dict[str, str]] = {}
        self._load(json_path)

    @classmethod
    def instance(cls) -> "MunicipalityMapper":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load(self, json_path: str) -> None:
        if not os.path.exists(json_path):
            LOGGER.warning("Tabela de municípios não encontrada em: %s", json_path)
            return

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            by_tse = data.get("by_tse", {})
            for tse_code, info in by_tse.items():
                ibge7 = str(info.get("ibge", "")).strip()
                if not ibge7:
                    continue
                ibge6 = ibge7[:6]
                nome = info.get("nome", "")
                uf = info.get("uf", "").upper()

                rec = {
                    "codigo_ibge": ibge7,
                    "codigo_ibge_6": ibge6,
                    "nome_municipio": nome,
                    "uf": uf,
                }

                self.by_ibge[ibge7] = rec
                self.by_ibge6[ibge6] = rec
                norm_key = f"{uf}:{normalize_text(nome)}"
                self.by_uf_name[norm_key] = rec

        except Exception as exc:
            LOGGER.error("Falha ao carregar tse_ibge_municipios.json: %s", exc)

    def get_by_ibge(self, ibge7: str) -> Optional[Dict[str, str]]:
        """Busca município pelo código de 7 dígitos."""
        clean = str(ibge7).strip().zfill(7)
        return self.by_ibge.get(clean)

    def get_by_ibge6(self, ibge6: str) -> Optional[Dict[str, str]]:
        """Busca município pelo código de 6 dígitos."""
        clean = str(ibge6).strip().zfill(6)
        return self.by_ibge6.get(clean)

    def get_by_name(self, uf: str, name: str) -> Optional[Dict[str, str]]:
        """Busca município pelo nome e UF."""
        key = f"{uf.upper().strip()}:{normalize_text(name)}"
        return self.by_uf_name.get(key)
