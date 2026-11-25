"""Classe base abstrata para componentes de renderização."""

from __future__ import annotations

from abc import ABC
from contextlib import contextmanager
from typing import Any, Iterator

from pystslides.config import BorderStyle, PresentationConfig, PresentationTheme


def resolve_border_style(
    border: BorderStyle | None,
    *,
    theme: PresentationTheme,
    bordered: bool = True,
) -> BorderStyle:
    """Resolve o estilo categórico de borda (`black`, `grey`, `none`) com fallback no tema."""
    if border is None:
        return theme.default_border if bordered else "none"
    normalized = border.strip().lower()
    if normalized == "gray":
        normalized = "grey"
    if normalized not in ("black", "grey", "none"):
        raise ValueError(
            f"Tipo de borda inválido: {border!r}. Use 'black', 'grey' ou 'none'."
        )
    return normalized  # type: ignore[return-value]


def create_columns(
    st_module: Any,
    spec: Any,
    *,
    vertical_alignment: str = "top",
) -> Any:
    """Cria `st.columns` com alinhamento vertical compatível entre versões do Streamlit."""
    if vertical_alignment != "top":
        try:
            return st_module.columns(spec, vertical_alignment=vertical_alignment)
        except TypeError:
            return st_module.columns(spec)
    return st_module.columns(spec)


def create_container(st_module: Any, *, border: bool = False, center: bool = False) -> Any:
    """Cria um `st.container` compatível com versões antigas e recentes do Streamlit."""
    if center:
        try:
            return st_module.container(border=border, horizontal_alignment="center")
        except TypeError:
            return st_module.container(border=border)
    return st_module.container(border=border)


@contextmanager
def create_bordered_container(
    st_module: Any,
    *,
    border_style: BorderStyle,
    marker_class: str = "pyst-container-marker",
    center: bool = False,
) -> Iterator[Any]:
    """Abre um `st.container` aplicando marcador CSS para o estilo de borda escolhido."""
    use_border = border_style != "none"
    with create_container(st_module, border=use_border, center=center) as container:
        if use_border:
            st_module.markdown(
                f'<span class="{marker_class} pyst-border-{border_style}" aria-hidden="true"></span>',
                unsafe_allow_html=True,
            )
        yield container


class BaseComponent(ABC):
    """Fornece acesso padronizado ao backend Streamlit e às configurações do tema."""

    def __init__(self, st_module: Any, config: PresentationConfig) -> None:
        self._st = st_module
        self._config = config
        self._accent_index = 0

    def _next_accent_color(self) -> str:
        """Retorna a próxima cor de acento da paleta configurada no tema."""
        palette = self.theme.accent_colors or (self.theme.primary_color,)
        color = palette[self._accent_index % len(palette)]
        self._accent_index += 1
        return color

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
