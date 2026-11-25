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
        font_stack = f"'{t.font_family}', -apple-system, BlinkMacSystemFont, sans-serif"
        chrome_css = (
            """
#MainMenu,
[data-testid="stToolbar"],
[data-testid="stDeployButton"],
[data-testid="stDecoration"],
footer {
    display: none !important;
}
"""
            if t.clean_chrome
            else ""
        )

        return f"""<style>
{font_import}html, body, .stApp, [data-testid="stAppViewContainer"] {{
    background-color: {t.background_color} !important;
    color: {t.text_color} !important;
}}
{chrome_css}
html, body, [class*="st-"], h1, h2, h3, h4, p, li {{
    font-family: {font_stack} !important;
}}

[data-testid="stSidebar"] {{
    background-color: #fafafa !important;
    border-right: 1px solid #e5e7eb !important;
}}

[data-testid="stSidebar"] a {{
    color: {t.muted_text_color} !important;
    text-decoration: none !important;
    font-size: 14px !important;
    line-height: 1.5 !important;
}}

[data-testid="stSidebar"] a:hover {{
    color: {t.text_color} !important;
}}

.stMarkdown h1,
.stMarkdown h2,
.stMarkdown h3 {{
    color: {t.text_color} !important;
    font-weight: {t.topic_font_weight} !important;
    letter-spacing: {t.topic_letter_spacing} !important;
}}

.pyst-kicker {{
    display: inline-flex;
    align-items: center;
    gap: 10px;
    font-size: {t.kicker_font_size};
    font-weight: 400;
    color: {t.text_color};
    letter-spacing: -0.01em;
    margin-bottom: 1.75rem;
}}

.pyst-kicker-icon {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}}

.stMarkdown hr.pyst-divider,
hr.pyst-divider {{
    border: none !important;
    border-top: {t.divider_thickness} solid {t.divider_color} !important;
    height: 0 !important;
    opacity: 1 !important;
    margin: 1rem 0 !important;
}}

.stMarkdown p.pyst-paragraph,
p.pyst-paragraph {{
    font-size: {t.paragraph_font_size} !important;
    font-weight: 400 !important;
    line-height: {t.paragraph_line_height} !important;
    letter-spacing: {t.paragraph_letter_spacing} !important;
    text-align: {t.paragraph_align} !important;
    color: {t.text_color} !important;
    max-width: {t.paragraph_max_width} !important;
    margin-bottom: 1.25rem !important;
}}

.pyst-cover {{
    text-align: left;
    padding: 2.5rem 0 1.5rem 0;
}}

.stMarkdown h1.pyst-cover-title,
h1.pyst-cover-title,
.pyst-cover-title {{
    font-size: {t.cover_title_font_size} !important;
    font-weight: {t.cover_title_font_weight} !important;
    line-height: {t.cover_title_line_height} !important;
    letter-spacing: {t.cover_title_letter_spacing} !important;
    color: {t.text_color} !important;
    margin: 0 0 1.25rem 0 !important;
    overflow-wrap: normal !important;
    word-break: normal !important;
}}

[data-testid="stHorizontalBlock"] .stMarkdown h1.pyst-cover-title,
[data-testid="stHorizontalBlock"] h1.pyst-cover-title {{
    font-size: clamp(44px, 4.3vw, 64px) !important;
}}

.pyst-cover-subtitle {{
    font-size: {t.cover_subtitle_font_size};
    font-weight: 400;
    line-height: 1.45;
    letter-spacing: -0.015em;
    color: {t.muted_text_color};
    margin-bottom: 1rem;
}}

.pyst-cover-meta {{
    font-size: {t.cover_meta_font_size};
    font-weight: 400;
    color: {t.muted_text_color};
    margin-top: 1.5rem;
}}

.stMarkdown h1.pyst-topic-title,
h1.pyst-topic-title {{
    font-size: {t.topic_font_size} !important;
    font-weight: {t.topic_font_weight} !important;
    line-height: {t.topic_line_height} !important;
    letter-spacing: {t.topic_letter_spacing} !important;
    color: {t.text_color} !important;
    text-align: left !important;
    margin: 0 0 1.5rem 0 !important;
    padding: 0 !important;
}}

.stMarkdown .pyst-subtopic-title,
.pyst-subtopic-title {{
    font-size: {t.subtopic_font_size} !important;
    font-weight: {t.subtopic_font_weight} !important;
    line-height: 1.15 !important;
    letter-spacing: {t.subtopic_letter_spacing} !important;
    color: {t.text_color} !important;
    text-align: left !important;
    margin: 0 0 1rem 0 !important;
    padding: 0 !important;
}}

.stMarkdown .pyst-subtopic-level-3,
.pyst-subtopic-level-3 {{
    font-size: 28px !important;
}}

.stMarkdown .pyst-subtopic-level-4,
.pyst-subtopic-level-4,
.stMarkdown .pyst-subtopic-level-5,
.pyst-subtopic-level-5,
.stMarkdown .pyst-subtopic-level-6,
.pyst-subtopic-level-6 {{
    font-size: 24px !important;
}}

.stMarkdown .pyst-card,
.pyst-card {{
    font-size: {card_font_size} !important;
    line-height: 1.6 !important;
    letter-spacing: {t.paragraph_letter_spacing} !important;
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
    padding: 18px 22px;
    border-radius: 10px;
    border: 1px solid #e5e7eb;
    background-color: #fafafa;
    color: #18181b;
    margin: 20px 0;
    font-size: 18px;
    line-height: 1.55;
    max-width: {t.paragraph_max_width};
}}

.pyst-callout-header {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 15px;
    font-weight: 500;
    color: {t.text_color};
    margin-bottom: 6px;
}}

.pyst-callout-dot {{
    width: 8px;
    height: 8px;
    border-radius: 999px;
    display: inline-block;
    flex-shrink: 0;
}}

.pyst-mark-badge {{
    font-size: 0.62em;
    font-weight: 500;
    letter-spacing: 0.02em;
    opacity: 0.85;
    margin-left: 4px;
    vertical-align: middle;
}}

.pyst-nav-indicator {{
    text-align: center;
    font-size: 14px;
    color: {t.muted_text_color};
    padding-top: 6px;
}}

.pyst-table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-family: {font_stack};
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
    border-bottom: 1px solid {t.table_border_color};
    font-weight: 500;
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
    color: {t.text_color};
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
