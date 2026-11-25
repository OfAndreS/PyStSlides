"""Componentes de renderização do PyStSlides."""

from pystslides.components.base import BaseComponent
from pystslides.components.code import CodeRenderer
from pystslides.components.data import DataRenderer, HighlightLevel, HighlightSpan, apply_highlights
from pystslides.components.interactive import InteractiveRenderer
from pystslides.components.media import MediaRenderer
from pystslides.components.typography import TypographyRenderer

__all__ = [
    "BaseComponent",
    "CodeRenderer",
    "DataRenderer",
    "HighlightLevel",
    "HighlightSpan",
    "InteractiveRenderer",
    "MediaRenderer",
    "TypographyRenderer",
    "apply_highlights",
]
