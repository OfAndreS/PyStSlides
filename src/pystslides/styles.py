"""Geração e injeção única de folhas de estilo CSS no Streamlit."""

from __future__ import annotations

from typing import Any

from pystslides.config import PresentationTheme


class StyleInjector:
    """Compila o tema da apresentação em CSS e injeta uma única vez por execução."""

    def __init__(self, theme: PresentationTheme) -> None:
        self._theme = theme
        self._injected = False

    @property
    def injected(self) -> bool:
        """Indica se o CSS global já foi injetado."""
        return self._injected

    def build_css(self) -> str:
        """Gera o bloco `<style>` completo baseado no `PresentationTheme`."""
        t = self._theme
        font_import = f"@import url('{t.google_font_url}');\n" if t.google_font_url else ""
        card_font_size = t.card_font_size or t.paragraph_font_size

        return f"""<style>
{font_import}html, body, [class*="st-"] {{
    font-family: '{t.font_family}', sans-serif !important;
}}

.stMarkdown hr.pyst-divider,
hr.pyst-divider {{
    border: none !important;
    border-top: {t.divider_thickness} solid {t.divider_color} !important;
    height: 0 !important;
    opacity: 1 !important;
    margin: 0.75rem 0 !important;
}}

.stMarkdown p.pyst-paragraph,
p.pyst-paragraph {{
    font-size: {t.paragraph_font_size} !important;
    line-height: {t.paragraph_line_height} !important;
    text-align: {t.paragraph_align} !important;
    margin-bottom: 1rem !important;
}}

.pyst-cover {{
    text-align: center;
    padding: 2rem 1rem 1.5rem 1rem;
}}

.pyst-cover-title {{
    font-size: 2.8rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}}

.pyst-cover-subtitle {{
    font-size: 1.35rem;
    color: #475569;
    margin-bottom: 0.75rem;
}}

.pyst-cover-meta {{
    font-size: 1rem;
    color: #64748b;
}}

.stMarkdown .pyst-card,
.pyst-card {{
    font-size: {card_font_size} !important;
    line-height: 2.0 !important;
    padding: 24px;
    background-color: {t.card_background};
    color: {t.card_text_color};
    border: 1px solid {t.card_border_color};
    border-radius: {t.card_border_radius};
    white-space: pre-wrap;
    margin-bottom: 20px;
}}

[data-testid="stCode"] pre,
[data-testid="stCode"] code,
.stCode pre,
.stCode code {{
    font-size: {t.code_font_size} !important;
    line-height: {t.code_line_height} !important;
}}

.pyst-callout {{
    padding: 16px 20px;
    border-radius: 10px;
    border-left: 5px solid;
    margin: 16px 0;
    font-size: 18px;
    line-height: 1.55;
}}

.pyst-table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-family: '{t.font_family}', sans-serif;
    font-size: {t.table_font_size};
    text-align: left;
    background-color: {t.card_background};
    border: 1px solid {t.table_border_color};
    border-radius: {t.card_border_radius};
    margin-bottom: 20px;
}}

.pyst-table th {{
    background-color: {t.table_header_bg};
    color: {t.table_header_color};
    padding: 16px;
    border-bottom: 2px solid {t.table_border_color};
    font-weight: 600;
}}

.pyst-table th:first-child {{
    border-top-left-radius: 11px;
}}

.pyst-table th:last-child {{
    border-top-right-radius: 11px;
}}

.pyst-table td {{
    padding: 16px;
    border-bottom: 1px solid {t.table_border_color};
    color: #1e293b;
    vertical-align: middle;
}}

.pyst-table tr:last-child td {{
    border-bottom: none;
}}

.pyst-table tr:last-child td:first-child {{
    border-bottom-left-radius: 11px;
}}

.pyst-table tr:last-child td:last-child {{
    border-bottom-right-radius: 11px;
}}

.pyst-table tr:hover td {{
    background-color: {t.table_hover_bg};
}}
</style>"""

    def inject(self, st_module: Any, *, force: bool = False) -> bool:
        """Injeta o CSS no Streamlit caso ainda não tenha sido aplicado."""
        if self._injected and not force:
            return False
        st_module.markdown(self.build_css(), unsafe_allow_html=True)
        self._injected = True
        return True
