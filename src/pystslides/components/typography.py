"""Componentes tipográficos: títulos, tópicos, parágrafos, callouts e sumário."""

from __future__ import annotations

import html
from typing import Any, Literal

from pystslides.components.base import BaseComponent
from pystslides.config import PresentationConfig, TextAlign
from pystslides.numbering import SectionEntry, SectionTracker


CalloutVariant = Literal["info", "success", "warning", "danger", "neutral"]
TocLocation = Literal["sidebar", "main"]

_CALLOUT_STYLES: dict[CalloutVariant, tuple[str, str, str]] = {
    "info": ("#eff6ff", "#1e40af", "#3b82f6"),
    "success": ("#f0fdf4", "#166534", "#22c55e"),
    "warning": ("#fefce8", "#854d0e", "#eab308"),
    "danger": ("#fef2f2", "#991b1b", "#ef4444"),
    "neutral": ("#f8fafc", "#334155", "#94a3b8"),
}


class TypographyRenderer(BaseComponent):
    """Renderiza estrutura textual, hierarquia de tópicos, divisores e sumário."""

    def __init__(
        self,
        st_module: Any,
        config: PresentationConfig,
        tracker: SectionTracker,
    ) -> None:
        super().__init__(st_module, config)
        self._tracker = tracker

    def divider(
        self,
        *,
        color: str | None = None,
        thickness: str | None = None,
    ) -> None:
        """Renderiza uma linha divisória horizontal estilizada."""
        if color is None and thickness is None:
            markup = '<hr class="pyst-divider">'
        else:
            final_color = color or self.theme.divider_color
            final_thickness = thickness or self.theme.divider_thickness
            markup = (
                f'<hr class="pyst-divider" '
                f'style="border-top: {final_thickness} solid {final_color};">'
            )
        self._st.markdown(markup, unsafe_allow_html=True)

    def spacer(self, height_px: int = 40) -> None:
        """Insere espaçamento vertical limpo em pixels sem chamadas repetidas a `st.write`."""
        if height_px > 0:
            self._st.markdown(
                f'<div style="height: {int(height_px)}px;" aria-hidden="true"></div>',
                unsafe_allow_html=True,
            )

    def cover_header(
        self,
        title: str,
        *,
        subtitle: str | None = None,
        author: str | None = None,
        date: str | None = None,
    ) -> None:
        """Renderiza um cabeçalho de capa padronizado com título, subtítulo e metadados."""
        parts = [f'<div class="pyst-cover-title">{html.escape(title)}</div>']
        if subtitle:
            parts.append(f'<div class="pyst-cover-subtitle">{html.escape(subtitle)}</div>')

        meta_items = [html.escape(item) for item in (author, date) if item]
        if meta_items:
            parts.append(f'<div class="pyst-cover-meta">{" • ".join(meta_items)}</div>')

        self._st.markdown(
            f'<div class="pyst-cover">{"".join(parts)}</div>',
            unsafe_allow_html=True,
        )

    def topic(
        self,
        title: str,
        *,
        numbered: bool | None = None,
        spacing_after_px: int = 0,
    ) -> SectionEntry:
        """Renderiza um tópico principal com divisores e numeração automática."""
        entry = self._tracker.register_topic(title, numbered=numbered)
        self._st.markdown(f'<div id="{entry.anchor}"></div>', unsafe_allow_html=True)
        self.divider()
        self._st.markdown(f"# **| {entry.formatted_title}**")
        self.divider()
        if spacing_after_px > 0:
            self.spacer(spacing_after_px)
        return entry

    def subtopic(
        self,
        title: str,
        *,
        level: int = 2,
        spacing_px: int | None = None,
        numbered: bool | None = None,
    ) -> SectionEntry:
        """Renderiza um sub-tópico hierárquico com espaçamento superior padronizado."""
        entry = self._tracker.register_subtopic(title, level=level, numbered=numbered)
        effective_spacing = (
            self.theme.default_subtopic_spacing_px if spacing_px is None else spacing_px
        )
        if effective_spacing > 0:
            self.spacer(effective_spacing)

        self._st.markdown(f'<div id="{entry.anchor}"></div>', unsafe_allow_html=True)
        heading_hashes = "#" * min(level, 6)
        self._st.markdown(f"{heading_hashes} **{entry.formatted_title}**")
        return entry

    def paragraph(
        self,
        text: str,
        *,
        font_size: str | None = None,
        align: TextAlign | None = None,
        escape_html: bool = False,
    ) -> None:
        """Renderiza um parágrafo com tipografia e alinhamento definidos pelo tema."""
        content = html.escape(text) if escape_html else text
        inline_styles: list[str] = []
        if font_size:
            inline_styles.append(f"font-size: {font_size};")
        if align:
            inline_styles.append(f"text-align: {align};")

        style_attr = f' style="{" ".join(inline_styles)}"' if inline_styles else ""
        self._st.markdown(
            f'<p class="pyst-paragraph"{style_attr}>{content}</p>',
            unsafe_allow_html=True,
        )

    def callout(
        self,
        message: str,
        *,
        title: str | None = None,
        variant: CalloutVariant = "info",
    ) -> None:
        """Renderiza uma caixa de destaque estilizada para notas, alertas ou dicas."""
        bg_color, text_color, border_color = _CALLOUT_STYLES[variant]
        title_html = f"<strong>{html.escape(title)}</strong><br>" if title else ""
        markup = (
            f'<div class="pyst-callout" '
            f'style="background-color: {bg_color}; color: {text_color}; '
            f'border-left-color: {border_color};">'
            f"{title_html}{html.escape(message)}</div>"
        )
        self._st.markdown(markup, unsafe_allow_html=True)

    def render_toc(
        self,
        *,
        title: str | None = None,
        location: TocLocation = "sidebar",
    ) -> str:
        """Gera e renderiza o sumário clicável com base nas seções registradas."""
        entries = self._tracker.entries
        if not entries:
            return ""

        heading = title if title is not None else self._config.toc_title
        lines: list[str] = [f"### {heading}", ""]
        for entry in entries:
            indent = "  " * max(entry.level - 1, 0)
            lines.append(f"{indent}- [{entry.formatted_title}](#{entry.anchor})")

        toc_markdown = "\n".join(lines)
        target = self._st.sidebar if location == "sidebar" else self._st
        target.markdown(toc_markdown)
        return toc_markdown
