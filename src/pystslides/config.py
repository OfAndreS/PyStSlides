"""Modelos de configuração e tema visual da apresentação."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


TextAlign = Literal["left", "center", "right", "justify"]
PageLayout = Literal["centered", "wide"]


@dataclass
class PresentationTheme:
    """Centraliza tipografia, cores, bordas e proporções visuais da apresentação."""

    font_family: str = "Inter"
    google_font_url: str | None = (
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap"
    )
    paragraph_font_size: str = "25px"
    paragraph_line_height: float = 1.6
    paragraph_align: TextAlign = "justify"
    code_font_size: str = "18px"
    code_line_height: float = 1.55
    card_font_size: str | None = None
    table_font_size: str = "16px"
    divider_color: str = "#2B2B2B"
    divider_thickness: str = "2.5px"
    default_subtopic_spacing_px: int = 80
    card_background: str = "#ffffff"
    card_text_color: str = "#1a1a1a"
    card_border_color: str = "#e5e7eb"
    card_border_radius: str = "12px"
    table_header_bg: str = "#f8fafc"
    table_header_color: str = "#334155"
    table_border_color: str = "#e2e8f0"
    table_hover_bg: str = "#f1f5f9"
    column_ratios: tuple[float, float, float] = (1.0, 7.0, 1.0)


@dataclass
class PresentationConfig:
    """Define metadados, comportamento de numeração e layout da apresentação."""

    title: str = "Apresentação"
    page_icon: str = "📊"
    layout: PageLayout = "wide"
    assets_dir: str | Path | None = None
    auto_number: bool = True
    topic_format: str = "{number:02d} ) - {title}"
    subtopic_format: str = "{number} ) {title}"
    show_toc: bool = False
    toc_title: str = "Sumário"
    theme: PresentationTheme = field(default_factory=PresentationTheme)
