"""Fachada principal (`Presentation`) que orquestra toda a apresentação Streamlit."""

from __future__ import annotations

from contextlib import ExitStack, contextmanager, nullcontext
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Literal, Mapping, Sequence

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


class _NoOpColumn:
    def __enter__(self) -> _NoOpColumn:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        return None


class _GatedStreamlit:
    """Proxy que suprime chamadas de renderização fora do slide ativo no modo paginado."""

    def __init__(self, st_module: Any, is_active: Callable[[], bool]) -> None:
        self._st = st_module
        self._is_active = is_active

    @property
    def sidebar(self) -> Any:
        return self._st.sidebar

    def columns(self, spec: Any, **kwargs: Any) -> list[Any]:
        if self._is_active():
            return self._st.columns(spec, **kwargs)
        count = spec if isinstance(spec, int) else len(spec)
        return [_NoOpColumn() for _ in range(count)]

    def container(self, **kwargs: Any) -> Any:
        if self._is_active():
            return self._st.container(**kwargs)
        return nullcontext()

    @contextmanager
    def echo(self, **kwargs: Any) -> Iterator[None]:
        if self._is_active():
            with self._st.echo(**kwargs):
                yield
        else:
            yield

    def __getattr__(self, name: str) -> Any:
        target = getattr(self._st, name)
        if not callable(target):
            return target

        def _guarded(*args: Any, **kwargs: Any) -> Any:
            if self._is_active():
                return target(*args, **kwargs)
            return None

        return _guarded


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
        page_icon: str | None = None,
        layout: PageLayout = "wide",
        assets_dir: str | Path | None = None,
        auto_number: bool = True,
        brand_label: str | None = None,
        repeat_brand_kicker: bool = False,
        paginated: bool = False,
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
                brand_label=brand_label,
                repeat_brand_kicker=repeat_brand_kicker,
                paginated=paginated,
                show_toc=show_toc,
                toc_title=toc_title,
                theme=theme or PresentationTheme(),
            )

        self._st = st_module if st_module is not None else _load_streamlit()
        self._slide_index = -1
        self._active_slide = 0
        self._in_split_slide = False
        self._render_st = (
            _GatedStreamlit(self._st, self._is_active_slide)
            if self._config.paginated
            else self._st
        )

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

        self._typography = TypographyRenderer(self._render_st, self._config, self._tracker)
        self._media = MediaRenderer(self._render_st, self._config, self._assets)
        self._code = CodeRenderer(self._render_st, self._config)
        self._data = DataRenderer(self._render_st, self._config)

        self._initialized = False
        self._context_stack: ExitStack | None = None

    def _is_active_slide(self) -> bool:
        if not self._config.paginated:
            return True
        current = max(self._slide_index, 0)
        return current == self._active_slide

    def _advance_slide(self) -> None:
        if self._config.paginated and not self._in_split_slide:
            self._slide_index += 1

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
        if self._config.paginated and hasattr(self._st, "session_state"):
            self._active_slide = int(self._st.session_state.get("pyst_slide_index", 0))
        stack = ExitStack()
        _, center_col, _ = self._st.columns(list(self._config.theme.column_ratios))
        stack.enter_context(center_col)
        stack.enter_context(create_container(self._st, border=False, center=True))
        self._context_stack = stack
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is None and self._config.paginated:
            self._render_pagination_bar()
        if self._context_stack is not None:
            self._context_stack.close()
            self._context_stack = None
        if exc_type is None and self._config.show_toc and self._tracker.entries:
            self.render_toc(location="sidebar")

    def _render_pagination_bar(self) -> None:
        total_slides = max(self._slide_index + 1, 1)
        if total_slides <= 1 or not hasattr(self._st, "button"):
            return
        self._active_slide = min(max(self._active_slide, 0), total_slides - 1)
        self._st.markdown('<hr class="pyst-divider">', unsafe_allow_html=True)
        prev_col, info_col, next_col = self._st.columns([1.0, 2.0, 1.0])
        with prev_col:
            if self._st.button(
                "← Anterior",
                disabled=self._active_slide <= 0,
                key="pyst_slide_prev",
                use_container_width=True,
            ):
                self._st.session_state["pyst_slide_index"] = self._active_slide - 1
                if hasattr(self._st, "rerun"):
                    self._st.rerun()
        with info_col:
            self._st.markdown(
                f'<div class="pyst-nav-indicator">{self._active_slide + 1} / {total_slides}</div>',
                unsafe_allow_html=True,
            )
        with next_col:
            if self._st.button(
                "Próximo →",
                disabled=self._active_slide >= total_slides - 1,
                key="pyst_slide_next",
                use_container_width=True,
            ):
                self._st.session_state["pyst_slide_index"] = self._active_slide + 1
                if hasattr(self._st, "rerun"):
                    self._st.rerun()

    # ------------------------------------------------------------------
    # Tipografia, estrutura e navegação
    # ------------------------------------------------------------------
    def kicker(self, label: str, *, accent_color: str | None = None) -> None:
        """Renderiza o cabeçalho discreto de marca/seção com ícone geométrico."""
        self._typography.kicker(label, accent_color=accent_color)

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
        image_position: Literal["below", "right"] = "below",
        kicker: str | None = None,
    ) -> None:
        """Renderiza o slide de capa com imagem abaixo ou em coluna lateral à direita."""
        self._advance_slide()
        if image is not None and image_position == "right" and title:
            effective_kicker = kicker if kicker is not None else self._config.brand_label
            if effective_kicker:
                self._typography.kicker(effective_kicker)
            left_col, right_col = self._render_st.columns([1.2, 0.8])
            with left_col:
                self._typography.cover_header(
                    title=title,
                    subtitle=subtitle,
                    author=author,
                    date=date,
                    kicker="",
                )
            with right_col:
                self._media.image(image, caption=caption, width=image_width)
            return

        if title:
            self._typography.cover_header(
                title=title,
                subtitle=subtitle,
                author=author,
                date=date,
                kicker=kicker,
            )
        if image is not None:
            self._media.image(image, caption=caption, width=image_width)

    def topic(
        self,
        title: str,
        *,
        numbered: bool | None = None,
        spacing_after_px: int = 0,
        kicker: str | None = None,
    ) -> SectionEntry:
        """Renderiza um tópico principal em estilo editorial limpo."""
        self._advance_slide()
        return self._typography.topic(
            title,
            numbered=numbered,
            spacing_after_px=spacing_after_px,
            kicker=kicker,
        )

    def split_slide(
        self,
        title: str | None = None,
        body: str | Sequence[str] | Callable[[], None] | None = None,
        *,
        media: Any | Callable[[], None] | None = None,
        media_position: Literal["left", "right"] = "right",
        title_bottom: bool = False,
        numbered: bool | None = None,
        kicker: str | None = None,
        ratio: tuple[float, float] = (1.15, 0.85),
        media_caption: str = "",
        media_width: int | None = None,
    ) -> SectionEntry | None:
        """Renderiza um slide editorial de duas colunas (texto e ilustração/mídia)."""
        self._advance_slide()
        self._in_split_slide = True
        try:
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
                self._typography.kicker(effective_kicker)

            entry: SectionEntry | None = None
            if media_position == "left":
                left_ratio, right_ratio = ratio[1], ratio[0]
                media_col, text_col = self._render_st.columns([left_ratio, right_ratio])
            else:
                text_col, media_col = self._render_st.columns(list(ratio))

            def _render_body() -> None:
                if body is None:
                    return
                if callable(body):
                    body()
                elif isinstance(body, str):
                    self._typography.paragraph(body)
                else:
                    for paragraph_text in body:
                        self._typography.paragraph(paragraph_text)

            with text_col:
                if not title_bottom and title:
                    entry = self._typography.topic(title, numbered=numbered, kicker="")
                _render_body()
                if title_bottom and title:
                    self._typography.spacer(24)
                    entry = self._typography.topic(title, numbered=numbered, kicker="")

            with media_col:
                if callable(media):
                    media()
                elif media is not None:
                    self._media.image(media, caption=media_caption, width=media_width)

            return entry
        finally:
            self._in_split_slide = False

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

    def live_code(self, code_location: Literal["above", "below"] = "above") -> Any:
        """Retorna o context manager `st.echo` diretamente para demonstrações ao vivo."""
        return self._code.live_code(code_location=code_location)

    # ------------------------------------------------------------------
    # Dados estruturados e texto marcado
    # ------------------------------------------------------------------
    def highlighted_text(
        self,
        text: str,
        spans: Sequence[HighlightSpan] = (),
        *,
        font_size: str | None = None,
    ) -> str:
        """Renderiza um card de texto com marcações/etiquetas coloridas."""
        return self._data.highlighted_text(text, spans=spans, font_size=font_size)

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
