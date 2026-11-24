"""Classe base abstrata para modularização de tópicos e slides."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pystslides.presentation import Presentation


class SlideSection(ABC):
    """Permite encapsular cada tópico da apresentação em sua própria classe/módulo.

    Exemplo:
        ```python
        class SecaoIntroducao(SlideSection):
            title = "Introdução"

            def render(self, deck: Presentation) -> None:
                deck.paragraph("Conteúdo do tópico...")
        ```
    """

    title: str | None = None
    auto_topic: bool = True

    def execute(self, presentation: Presentation) -> None:
        """Renderiza opcionalmente o título do tópico e executa `render`."""
        if self.title and self.auto_topic:
            presentation.topic(self.title)
        self.render(presentation)

    @abstractmethod
    def render(self, presentation: Presentation) -> None:
        """Implementa o conteúdo visual da seção usando a fachada `Presentation`."""
