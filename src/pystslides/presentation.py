"""Fachada principal (`Presentation`) que orquestra toda a apresentação Streamlit."""

from __future__ import annotations

from contextlib import ExitStack
from pathlib import Path
from typing import Any, Iterable, Iterator, Literal, Mapping, Sequence

from pystslides.assets import AssetManager
from pystslides.components.base import create_container
from pystslides.components.code import CodeRenderer
from pystslides.components.data import DataRenderer, HighlightSpan
from pystslides.components.media import ImageItem, MediaRenderer
from pystslides.components.typography import CalloutVariant, TocLocation, TypographyRenderer
from pystslides.config import PageLayout, PresentationConfig, PresentationTheme, TextAlign
from pystslides.numbering import SectionEntry, SectionTracker
from pystslides.section import SlideSection
from pystslides.styles import StyleInjector


def _load_streamlit() -> Any:
    import streamlit as st

    return st


class Presentation:
    """Fachada orientada a objetos para criar apresentações estruturadas no Streamlit.

    Pode ser utilizada diretamente ou como context manager:

    ```python
    with Presentation(title="Minha Apresentação", assets_dir="data", show_toc=True) as deck:
        deck.topic("Introdução")
        deck.paragraph("Texto formatado automaticamente.")
    ```
    """

    def __init__(
        self,
        title: str = "Apresentação",
        *,
        page_icon: str = "📊",
        layout: PageLayout = "wide",
        assets_dir: str | Path | None = None,
        auto_number: bool = True,
        show_toc: bool = False,
        toc_title: str = "Sumário",
        theme: PresentationTheme | None = None,
        config: PresentationConfig | None = None,
        st_module: Any | None = None,
    ) -> None:
        if config is not None:
            self._config = config
        else:
            self._config = PresentationConfig(
                title=title,
                page_icon=page_icon,
                layout=layout,
                assets_dir=assets_dir,
                auto_number=auto_number,
                show_toc=show_toc,
                toc_title=toc_title,
                theme=theme or PresentationTheme(),
            )

        self._st = st_module if st_module is not None else _load_streamlit()
        self._assets = (
            AssetManager(self._config.assets_dir)
            if self._config.assets_dir is not None
            else None
        )
        self._tracker = SectionTracker(
            auto_number=self._config.auto_number,
            topic_format=self._config.topic_format,
            subtopic_format=self._config.subtopic_format,
        )
        self._styles = StyleInjector(self._config.theme)

        self._typography = TypographyRenderer(self._st, self._config, self._tracker)
        self._media = MediaRenderer(self._st, self._config, self._assets)
        self._code = CodeRenderer(self._st, self._config)
        self._data = DataRenderer(self._st, self._config)

        self._initialized = False
        self._context_stack: ExitStack | None = None

    # ------------------------------------------------------------------
    # Propriedades de acesso controlado
    # ------------------------------------------------------------------
    @property
    def config(self) -> PresentationConfig:
        """Retorna a configuração completa da apresentação."""
        return self._config

    @property
    def theme(self) -> PresentationTheme:
        """Retorna o tema visual aplicado."""
        return self._config.theme

    @property
    def assets(self) -> AssetManager | None:
        """Retorna o gerenciador de assets, quando configurado."""
        return self._assets

    @property
    def tracker(self) -> SectionTracker:
        """Retorna o rastreador de numeração e seções."""
        return self._tracker

    @property
    def sections(self) -> tuple[SectionEntry, ...]:
        """Retorna todas as seções já renderizadas."""
        return self._tracker.entries

    # ------------------------------------------------------------------
    # Ciclo de vida e Context Manager
    # ------------------------------------------------------------------
    def setup(self, *, configure_page: bool = True) -> Presentation:
        """Configura a página do Streamlit e injeta o CSS global uma única vez."""
        if not self._initialized:
            if configure_page:
                self._st.set_page_config(
                    page_title=self._config.title,
                    page_icon=self._config.page_icon,
                    layout=self._config.layout,
                )
            self._styles.inject(self._st)
            self._initialized = True
        return self

    def __enter__(self) -> Presentation:
        self.setup()
        stack = ExitStack()
        _, center_col, _ = self._st.columns(list(self._config.theme.column_ratios))
        stack.enter_context(center_col)
        stack.enter_context(create_container(self._st, border=False, center=True))
        self._context_stack = stack
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._context_stack is not None:
            self._context_stack.close()
            self._context_stack = None
        if exc_type is None and self._config.show_toc and self._tracker.entries:
            self.render_toc(location="sidebar")

    # ------------------------------------------------------------------
    # Tipografia, estrutura e navegação
    # ------------------------------------------------------------------
    def cover(
        self,
        *,
        title: str | None = None,
        subtitle: str | None = None,
        author: str | None = None,
        date: str | None = None,
        image: Any | None = None,
        caption: str = "",
        image_width: int | None = None,
    ) -> None:
        """Renderiza o slide de capa com imagem e/ou cabeçalho tipográfico."""
        if title:
            self._typography.cover_header(
                title=title,
                subtitle=subtitle,
                author=author,
                date=date,
            )
        if image is not None:
            self._media.image(image, caption=caption, width=image_width)

    def topic(
        self,
        title: str,
        *,
        numbered: bool | None = None,
        spacing_after_px: int = 0,
    ) -> SectionEntry:
        """Renderiza um tópico principal numerado automaticamente."""
        return self._typography.topic(
            title,
            numbered=numbered,
            spacing_after_px=spacing_after_px,
        )

    def subtopic(
        self,
        title: str,
        *,
        level: int = 2,
        spacing_px: int | None = None,
        numbered: bool | None = None,
    ) -> SectionEntry:
        """Renderiza um sub-tópico hierárquico (ex.: 1.1, 1.1.1)."""
        return self._typography.subtopic(
            title,
            level=level,
            spacing_px=spacing_px,
            numbered=numbered,
        )

    def paragraph(
        self,
        text: str,
        *,
        font_size: str | None = None,
        align: TextAlign | None = None,
        escape_html: bool = False,
    ) -> None:
        """Renderiza um parágrafo estilizado conforme o tema."""
        self._typography.paragraph(
            text,
            font_size=font_size,
            align=align,
            escape_html=escape_html,
        )

    def callout(
        self,
        message: str,
        *,
        title: str | None = None,
        variant: CalloutVariant = "info",
    ) -> None:
        """Renderiza um card de destaque/observação."""
        self._typography.callout(message, title=title, variant=variant)

    def divider(self, *, color: str | None = None, thickness: str | None = None) -> None:
        """Renderiza uma linha divisória estilizada."""
        self._typography.divider(color=color, thickness=thickness)

    def spacer(self, height_px: int = 40) -> None:
        """Adiciona espaçamento vertical em pixels."""
        self._typography.spacer(height_px=height_px)

    def render_toc(
        self,
        *,
        title: str | None = None,
        location: TocLocation = "sidebar",
    ) -> str:
        """Renderiza o sumário clicável das seções registradas."""
        return self._typography.render_toc(title=title, location=location)

    # ------------------------------------------------------------------
    # Mídia e diagramas
    # ------------------------------------------------------------------
    def image(
        self,
        source: Any,
        *,
        caption: str = "",
        width: int | None = None,
        bordered: bool = False,
        center: bool = True,
    ) -> None:
        """Renderiza uma imagem a partir de nome de asset, `Path`, URL ou objeto PIL."""
        self._media.image(
            source,
            caption=caption,
            width=width,
            bordered=bordered,
            center=center,
        )

    def image_gallery(
        self,
        sources: Sequence[ImageItem],
        *,
        columns: int = 1,
        bordered: bool = False,
        width: int | None = None,
    ) -> None:
        """Renderiza múltiplas imagens em pilha vertical ou grade de colunas."""
        self._media.image_gallery(
            sources,
            columns=columns,
            bordered=bordered,
            width=width,
        )

    def mermaid(
        self,
        diagram: str,
        *,
        bordered: bool = True,
        caption: str | None = None,
    ) -> str:
        """Renderiza um diagrama Mermaid formatado dentro de um container."""
        return self._media.mermaid(diagram, bordered=bordered, caption=caption)

    # ------------------------------------------------------------------
    # Código e demonstrações
    # ------------------------------------------------------------------
    def code_block(
        self,
        code: str,
        *,
        language: str = "python",
        output: Any = None,
        bordered_output: bool = True,
        output_as_markdown: bool = False,
        line_numbers: bool = False,
    ) -> str:
        """Renderiza um bloco de código limpo com saída opcional."""
        return self._code.code_block(
            code,
            language=language,
            output=output,
            bordered_output=bordered_output,
            output_as_markdown=output_as_markdown,
            line_numbers=line_numbers,
        )

    def output_box(
        self,
        *items: Any,
        bordered: bool = True,
        as_markdown: bool = False,
    ) -> None:
        """Exibe resultados em um container padronizado com borda."""
        self._code.output_box(*items, bordered=bordered, as_markdown=as_markdown)

    def output_container(self, *, bordered: bool = True, center: bool = False) -> Iterator[Any]:
        """Retorna um context manager de container para saídas customizadas."""
        return self._code.output_container(bordered=bordered, center=center)

    def live_code(self, code_location: Literal["above", "below"] = "above") -> Iterator[None]:
        """Retorna um context manager baseado em `st.echo`."""
        return self._code.live_code(code_location=code_location)

    # ------------------------------------------------------------------
    # Dados estruturados e texto marcado
    # ------------------------------------------------------------------
    def highlighted_text(
        self,
        text: str,
        spans: Sequence[HighlightSpan] = (),
    ) -> str:
        """Renderiza um card de texto com marcações/etiquetas coloridas."""
        return self._data.highlighted_text(text, spans=spans)

    def styled_table(
        self,
        data: Mapping[str, Sequence[Any]] | Sequence[Mapping[str, Any]] | Any,
        *,
        highlights: Mapping[tuple[str, int], Sequence[HighlightSpan]] | None = None,
    ) -> str:
        """Renderiza uma tabela HTML estilizada com destaques opcionais por célula."""
        return self._data.styled_table(data, highlights=highlights)

    # ------------------------------------------------------------------
    # Modularização de seções
    # ------------------------------------------------------------------
    def add_section(self, section: SlideSection) -> None:
        """Executa e renderiza uma instância de `SlideSection`."""
        section.execute(self)

    def add_sections(self, sections: Iterable[SlideSection]) -> None:
        """Executa e renderiza uma sequência de `SlideSection` em ordem."""
        for section in sections:
            self.add_section(section)
