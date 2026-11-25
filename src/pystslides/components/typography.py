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
    "info": ("#f0f6fe", "#1e3a8a", "#3f7bde"),
    "success": ("#f2f9f4", "#1b4332", "#579568"),
    "warning": ("#fef8f0", "#7c4a15", "#e19b4d"),
    "danger": ("#fef2f2", "#991b1b", "#ef4444"),
    "neutral": ("#f8fafc", "#18181b", "#52525b"),
}


def _build_asterisk_svg(color: str) -> str:
    """Gera o ícone geométrico de asterisco de 8 pontas característico dos slides."""
    return (
        f'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
        f'<g stroke="{html.escape(color)}" stroke-width="3.2" stroke-linecap="round">'
        f'<line x1="12" y1="2.5" x2="12" y2="21.5"/>'
        f'<line x1="2.5" y1="12" x2="21.5" y2="12"/>'
        f'<line x1="5.3" y1="5.3" x2="18.7" y2="18.7"/>'
        f'<line x1="18.7" y1="5.3" x2="5.3" y2="18.7"/>'
        f"</g></svg>"
    )


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
        self._kicker_index = 0

    def _next_accent_color(self) -> str:
        palette = self.theme.accent_colors or (self.theme.primary_color,)
        color = palette[self._kicker_index % len(palette)]
        self._kicker_index += 1
        return color

    def kicker(self, label: str, *, accent_color: str | None = None) -> None:
        """Renderiza o cabeçalho discreto no topo esquerdo com ícone geométrico colorido."""
        if not label:
            return
        color = accent_color or self._next_accent_color()
        icon_svg = _build_asterisk_svg(color)
        markup = (
            f'<div class="pyst-kicker">'
            f'<span class="pyst-kicker-icon">{icon_svg}</span>'
            f"<span>{html.escape(label)}</span>"
            f"</div>"
        )
        self._st.markdown(markup, unsafe_allow_html=True)

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
        kicker: str | None = None,
    ) -> None:
        """Renderiza um cabeçalho de capa editorial com título, subtítulo e metadados."""
        effective_kicker = (
            kicker
            if kicker is not None
            else (
                self._config.brand_label
                if (self._config.repeat_brand_kicker or self._config.paginated)
                else None
            )
        )
        if effective_kicker:
            self.kicker(effective_kicker)

        parts = [f'<h1 class="pyst-cover-title">{html.escape(title)}</h1>']
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
        kicker: str | None = None,
    ) -> SectionEntry:
        """Renderiza um tópico principal em estilo editorial limpo com numeração opcional."""
        entry = self._tracker.register_topic(title, numbered=numbered)
        self._st.markdown(f'<div id="{entry.anchor}"></div>', unsafe_allow_html=True)

        effective_kicker = (
            kicker
            if kicker is not None
            else (
                self._config.brand_label
                if (self._config.repeat_brand_kicker or self._config.paginated)
                else None
            )
        )
        if effective_kicker:
            self.kicker(effective_kicker)

        if self.theme.topic_dividers:
            self.divider()
        self._st.markdown(
            f'<h1 class="pyst-topic-title">{html.escape(entry.formatted_title)}</h1>',
            unsafe_allow_html=True,
        )
        if self.theme.topic_dividers:
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
        tag_level = min(max(level, 2), 6)
        self._st.markdown(
            f'<h{tag_level} class="pyst-subtopic-title pyst-subtopic-level-{tag_level}">'
            f"{html.escape(entry.formatted_title)}</h{tag_level}>",
            unsafe_allow_html=True,
        )
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
        bg_color, text_color, accent_color = _CALLOUT_STYLES[variant]
        if self.theme.callout_minimal:
            header_html = (
                f'<div class="pyst-callout-header">'
                f'<span class="pyst-callout-dot" style="background-color: {accent_color};"></span>'
                f"<span>{html.escape(title)}</span></div>"
                if title
                else ""
            )
            markup = (
                f'<div class="pyst-callout">'
                f"{header_html}"
                f"<div>{html.escape(message)}</div></div>"
            )
        else:
            title_html = f"<strong>{html.escape(title)}</strong><br>" if title else ""
            markup = (
                f'<div class="pyst-callout" '
                f'style="background-color: {bg_color}; color: {text_color}; '
                f'border: none; border-left: 4px solid {accent_color};">'
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
