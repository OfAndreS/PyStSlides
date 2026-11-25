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

    font_family: str = "DM Sans"
    google_font_url: str | None = (
        "https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,700;1,9..40,400&display=swap"
    )
    background_color: str = "#ffffff"
    text_color: str = "#000000"
    muted_text_color: str = "#52525b"
    primary_color: str = "#3f7bde"
    accent_colors: tuple[str, ...] = ("#3f7bde", "#579568", "#e19b4d", "#8461f0")
    cover_title_font_size: str = "76px"
    cover_title_font_weight: int = 400
    cover_title_line_height: float = 1.05
    cover_title_letter_spacing: str = "-0.035em"
    cover_subtitle_font_size: str = "24px"
    cover_meta_font_size: str = "14px"
    topic_font_size: str = "54px"
    topic_font_weight: int = 400
    topic_line_height: float = 1.08
    topic_letter_spacing: str = "-0.03em"
    topic_dividers: bool = False
    subtopic_font_size: str = "34px"
    subtopic_font_weight: int = 400
    subtopic_letter_spacing: str = "-0.02em"
    kicker_font_size: str = "15px"
    paragraph_font_size: str = "24px"
    paragraph_line_height: float = 1.55
    paragraph_letter_spacing: str = "-0.01em"
    paragraph_align: TextAlign = "left"
    code_font_size: str = "16px"
    code_line_height: float = 1.55
    card_font_size: str | None = None
    table_font_size: str = "16px"
    divider_color: str = "#e5e7eb"
    divider_thickness: str = "1px"
    default_subtopic_spacing_px: int = 48
    paragraph_max_width: str = "62ch"
    callout_minimal: bool = True
    clean_chrome: bool = True
    card_background: str = "#ffffff"
    card_text_color: str = "#000000"
    card_border_color: str = "#e5e7eb"
    card_border_radius: str = "12px"
    table_header_bg: str = "#f8fafc"
    table_header_color: str = "#18181b"
    table_border_color: str = "#e5e7eb"
    table_hover_bg: str = "#f9fafb"
    column_ratios: tuple[float, float, float] = (0.75, 8.5, 0.75)


@dataclass
class PresentationConfig:
    """Define metadados, comportamento de numeração e layout da apresentação."""

    title: str = "Apresentação"
    page_icon: str | None = None
    layout: PageLayout = "wide"
    assets_dir: str | Path | None = None
    auto_number: bool = True
    brand_label: str | None = None
    repeat_brand_kicker: bool = False
    paginated: bool = False
    topic_format: str = "{number:02d} ) - {title}"
    subtopic_format: str = "{number} ) {title}"
    show_toc: bool = False
    toc_title: str = "Sumário"
    theme: PresentationTheme = field(default_factory=PresentationTheme)
