"""PyStSlides: pacote orientado a objetos sobre Streamlit para apresentações em código."""

from pystslides.assets import (
    AssetManager,
    export_editorial_assets,
    get_editorial_assets_dir,
    is_animated_svg,
    list_editorial_assets,
)
from pystslides.components.data import HighlightLevel, HighlightSpan, apply_highlights
from pystslides.config import BorderStyle, PresentationConfig, PresentationTheme
from pystslides.exceptions import AssetNotFoundError, InvalidSectionLevelError, PyStSlidesError
from pystslides.numbering import SectionEntry, SectionTracker
from pystslides.presentation import Presentation
from pystslides.section import SlideSection
from pystslides.styles import StyleInjector

__version__ = "1.5.0"

__all__ = [
    "AssetManager",
    "AssetNotFoundError",
    "BorderStyle",
    "HighlightLevel",
    "HighlightSpan",
    "InvalidSectionLevelError",
    "Presentation",
    "PresentationConfig",
    "PresentationTheme",
    "PyStSlidesError",
    "SectionEntry",
    "SectionTracker",
    "SlideSection",
    "StyleInjector",
    "__version__",
    "apply_highlights",
    "export_editorial_assets",
    "get_editorial_assets_dir",
    "is_animated_svg",
    "list_editorial_assets",
]
