"""Classe base abstrata para componentes de renderização."""

from __future__ import annotations

from abc import ABC
from typing import Any

from pystslides.config import PresentationConfig, PresentationTheme


def create_container(st_module: Any, *, border: bool = False, center: bool = False) -> Any:
    """Cria um `st.container` compatível com versões antigas e recentes do Streamlit."""
    if center:
        try:
            return st_module.container(border=border, horizontal_alignment="center")
        except TypeError:
            return st_module.container(border=border)
    return st_module.container(border=border)


class BaseComponent(ABC):
    """Fornece acesso padronizado ao backend Streamlit e às configurações do tema."""

    def __init__(self, st_module: Any, config: PresentationConfig) -> None:
        self._st = st_module
        self._config = config

    @property
    def st(self) -> Any:
        """Retorna o módulo Streamlit (ou dublê de teste) associado."""
        return self._st

    @property
    def config(self) -> PresentationConfig:
        """Retorna a configuração ativa da apresentação."""
        return self._config

    @property
    def theme(self) -> PresentationTheme:
        """Retorna o tema visual ativo."""
        return self._config.theme
