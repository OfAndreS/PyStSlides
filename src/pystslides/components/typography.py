"""Componentes tipográficos: títulos, tópicos, parágrafos, callouts e sumário."""

from __future__ import annotations

import html
from typing import Any, Literal, Sequence

from pystslides.components.base import BaseComponent, resolve_border_style
from pystslides.config import BorderStyle, PresentationConfig, TextAlign
from pystslides.numbering import SectionEntry, SectionTracker


CalloutVariant = Literal["info", "success", "warning", "danger", "neutral"]
BulletMarker = Literal["asterisk", "dot", "dash"]
TocLocation = Literal["sidebar", "main"]

_CALLOUT_STYLES: dict[CalloutVariant, tuple[str, str, str]] = {
    "info": ("#f4f7fe", "#1a3668", "#3f7bde"),
    "success": ("#f3f9f5", "#1c4529", "#579568"),
    "warning": ("#fdf7ef", "#734612", "#e19b4d"),
    "danger": ("#fdf3f2", "#872421", "#d9534f"),
    "neutral": ("#fafafa", "#000000", "#000000"),
}


def _build_asterisk_svg(color: str, *, size: int = 18) -> str:
    """Gera o ícone geométrico de asterisco de 8 pontas característico dos slides."""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
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
        title: str | None = None,
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

        parts: list[str] = []
        if title:
            parts.append(f'<h1 class="pyst-cover-title">{html.escape(title)}</h1>')
        if subtitle:
            parts.append(f'<div class="pyst-cover-subtitle">{html.escape(subtitle)}</div>')

        meta_items = [html.escape(item) for item in (author, date) if item]
        if meta_items:
            parts.append(f'<div class="pyst-cover-meta">{" • ".join(meta_items)}</div>')

        if parts:
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
        slide_index: int | None = None,
    ) -> SectionEntry:
        """Renderiza um tópico principal em estilo editorial limpo com numeração opcional."""
        entry = self._tracker.register_topic(title, numbered=numbered, slide_index=slide_index)
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
        slide_index: int | None = None,
    ) -> SectionEntry:
        """Renderiza um sub-tópico hierárquico com espaçamento superior padronizado."""
        entry = self._tracker.register_subtopic(
            title,
            level=level,
            numbered=numbered,
            slide_index=slide_index,
        )
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

    def bullets(
        self,
        items: Sequence[str],
        *,
        marker: BulletMarker = "asterisk",
        accent_color: str | None = None,
        font_size: str | None = None,
        escape_html: bool = False,
    ) -> None:
        """Renderiza uma lista editorial limpa com marcadores geométricos coloridos."""
        if not items:
            return
        palette = self.theme.accent_colors or (self.theme.primary_color,)
        list_style = f' style="font-size: {font_size};"' if font_size else ""
        rows: list[str] = []
        for idx, item in enumerate(items):
            color = accent_color or palette[idx % len(palette)]
            if marker == "asterisk":
                marker_html = _build_asterisk_svg(color, size=14)
            elif marker == "dot":
                marker_html = (
                    f'<span class="pyst-bullet-dot" style="background-color: {color};"></span>'
                )
            else:
                marker_html = (
                    f'<span class="pyst-bullet-dash" style="background-color: {color};"></span>'
                )
            content = html.escape(item) if escape_html else item
            rows.append(
                f'<li class="pyst-bullet-item">'
                f'<span class="pyst-bullet-marker" aria-hidden="true">{marker_html}</span>'
                f'<span>{content}</span></li>'
            )
        self._st.markdown(
            f'<ul class="pyst-bullets"{list_style}>{"".join(rows)}</ul>',
            unsafe_allow_html=True,
        )

    def callout(
        self,
        message: str,
        *,
        title: str | None = None,
        variant: CalloutVariant = "info",
        escape_html: bool = True,
        border: BorderStyle | None = None,
    ) -> None:
        """Renderiza uma caixa de destaque estilizada para notas, alertas ou dicas."""
        bg_color, text_color, accent_color = _CALLOUT_STYLES[variant]
        icon_svg = _build_asterisk_svg(accent_color, size=15)
        body_text = html.escape(message) if escape_html else message
        resolved_border = resolve_border_style(border, theme=self.theme)
        border_cls = f" pyst-border-{resolved_border}" if border is not None else ""
        if self.theme.callout_minimal:
            header_html = (
                f'<div class="pyst-callout-header">'
                f'<span class="pyst-callout-icon">{icon_svg}</span>'
                f"<span>{html.escape(title)}</span></div>"
                if title
                else ""
            )
            body_html = (
                f"<div>{body_text}</div>"
                if title
                else (
                    f'<div style="display:flex;align-items:flex-start;gap:10px;">'
                    f'<span class="pyst-callout-icon" style="margin-top:4px;">{icon_svg}</span>'
                    f"<span>{body_text}</span></div>"
                )
            )
            markup = f'<div class="pyst-callout{border_cls}">{header_html}{body_html}</div>'
        else:
            title_html = (
                f'<div class="pyst-callout-header" style="color: {text_color};">'
                f'<span class="pyst-callout-icon">{icon_svg}</span>'
                f"<span>{html.escape(title)}</span></div>"
                if title
                else ""
            )
            radius = self.theme.card_border_radius
            if border is not None and resolved_border == "none":
                inline_border = "border: none;"
            elif border is not None and resolved_border == "grey":
                inline_border = (
                    f"border: {self.theme.grey_border_width} solid {self.theme.grey_border_color}; "
                    f"border-left: 4px solid {accent_color};"
                )
            else:
                inline_border = f"border: none; border-left: 4px solid {accent_color};"
            markup = (
                f'<div class="pyst-callout" '
                f'style="background-color: {bg_color}; color: {text_color}; '
                f"{inline_border} "
                f'border-radius: 0 {radius} {radius} 0;">'
                f"{title_html}<div>{body_text}</div></div>"
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

        if (
            self._config.paginated
            and location == "sidebar"
            and hasattr(self._st.sidebar, "button")
            and hasattr(self._st, "session_state")
        ):
            active_slide = int(self._st.session_state.get("pyst_slide_index", 0))
            self._st.sidebar.markdown(
                f'<span class="pyst-toc-nav-marker" aria-hidden="true"></span>### {heading}',
                unsafe_allow_html=True,
            )
            for idx, entry in enumerate(entries):
                if entry.slide_index is None:
                    continue
                prefix = "  " * max(entry.level - 1, 0)
                is_current = entry.slide_index == active_slide and entry.level == 1
                label = f"{prefix}{'• ' if is_current else ''}{entry.formatted_title}"
                if self._st.sidebar.button(
                    label,
                    key=f"pyst_toc_btn_{idx}_{entry.anchor}",
                    use_container_width=True,
                ):
                    self._st.session_state["pyst_slide_index"] = entry.slide_index
                    if hasattr(self._st, "rerun"):
                        self._st.rerun()
            return toc_markdown

        target = self._st.sidebar if location == "sidebar" else self._st
        target.markdown(toc_markdown)
        return toc_markdown
