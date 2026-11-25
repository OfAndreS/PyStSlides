"""Fachada principal (`Presentation`) que orquestra toda a apresentação Streamlit."""

from __future__ import annotations

from contextlib import ExitStack, contextmanager, nullcontext
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Literal, Mapping, Sequence

from pystslides.assets import AssetManager
from pystslides.components.base import create_columns, create_container
from pystslides.components.code import CodeRenderer
from pystslides.components.data import DataRenderer, HighlightSpan
from pystslides.components.interactive import ContentBlock, InteractiveRenderer
from pystslides.components.media import ImageItem, MediaRenderer
from pystslides.components.typography import (
    BulletMarker,
    CalloutVariant,
    TocLocation,
    TypographyRenderer,
)
from pystslides.config import (
    BorderStyle,
    PageLayout,
    PresentationConfig,
    PresentationTheme,
    TextAlign,
    VerticalAlign,
)
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

    def is_active(self) -> bool:
        """Indica se o slide atual está ativo para renderização."""
        return self._is_active()

    def rerun(self) -> Any:
        return self._st.rerun()

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
        self._interactive = InteractiveRenderer(self._render_st, self._config)

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
        with create_container(self._st, border=False):
            self._st.markdown(
                '<span class="pyst-pagination-marker" aria-hidden="true"></span>'
                '<hr class="pyst-divider">',
                unsafe_allow_html=True,
            )
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

    def new_slide(self, *, divider: bool = False) -> None:
        """Inicia explicitamente um novo slide no modo paginado (ou divisor opcional)."""
        self._advance_slide()
        if divider and not self._config.paginated:
            self._typography.divider()

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
        image_vertical_align: VerticalAlign | None = None,
        kicker: str | None = None,
    ) -> None:
        """Renderiza o slide de capa com imagem abaixo ou em coluna lateral à direita."""
        self._advance_slide()
        has_header = bool(title or subtitle or author or date)
        if image is not None and image_position == "right":
            effective_kicker = kicker if kicker is not None else self._config.brand_label
            if effective_kicker:
                self._typography.kicker(effective_kicker)
            v_align = image_vertical_align or self._config.theme.default_media_vertical_align
            left_col, right_col = create_columns(
                self._render_st,
                [1.2, 0.8],
                vertical_alignment=v_align,
            )
            with left_col:
                if has_header:
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

        if has_header:
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
        slide_idx = max(self._slide_index, 0) if self._config.paginated else None
        return self._typography.topic(
            title,
            numbered=numbered,
            spacing_after_px=spacing_after_px,
            kicker=kicker,
            slide_index=slide_idx,
        )

    def split_slide(
        self,
        title: str | None = None,
        body: str | Sequence[str] | Callable[[], None] | None = None,
        *,
        media: Any | Callable[[], None] | None = None,
        media_position: Literal["left", "right"] = "right",
        media_vertical_align: VerticalAlign | None = None,
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
        slide_idx = max(self._slide_index, 0) if self._config.paginated else None
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

            v_align = media_vertical_align or self._config.theme.default_media_vertical_align
            entry: SectionEntry | None = None
            if media_position == "left":
                left_ratio, right_ratio = ratio[1], ratio[0]
                media_col, text_col = create_columns(
                    self._render_st,
                    [left_ratio, right_ratio],
                    vertical_alignment=v_align,
                )
            else:
                text_col, media_col = create_columns(
                    self._render_st,
                    list(ratio),
                    vertical_alignment=v_align,
                )

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
                    entry = self._typography.topic(
                        title,
                        numbered=numbered,
                        kicker="",
                        slide_index=slide_idx,
                    )
                _render_body()
                if title_bottom and title:
                    self._typography.spacer(24)
                    entry = self._typography.topic(
                        title,
                        numbered=numbered,
                        kicker="",
                        slide_index=slide_idx,
                    )

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
        slide_idx = max(self._slide_index, 0) if self._config.paginated else None
        return self._typography.subtopic(
            title,
            level=level,
            spacing_px=spacing_px,
            numbered=numbered,
            slide_index=slide_idx,
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

    def bullets(
        self,
        items: Sequence[str],
        *,
        marker: BulletMarker = "asterisk",
        accent_color: str | None = None,
        font_size: str | None = None,
        escape_html: bool = False,
    ) -> None:
        """Renderiza uma lista editorial com marcadores geométricos coloridos."""
        self._typography.bullets(
            items,
            marker=marker,
            accent_color=accent_color,
            font_size=font_size,
            escape_html=escape_html,
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
        """Renderiza um card de destaque/observação."""
        self._typography.callout(
            message,
            title=title,
            variant=variant,
            escape_html=escape_html,
            border=border,
        )

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
        border: BorderStyle | None = None,
    ) -> None:
        """Renderiza uma imagem a partir de nome de asset, `Path`, URL ou objeto PIL."""
        self._media.image(
            source,
            caption=caption,
            width=width,
            bordered=bordered,
            center=center,
            border=border,
        )

    def image_gallery(
        self,
        sources: Sequence[ImageItem],
        *,
        columns: int = 1,
        bordered: bool = False,
        width: int | None = None,
        border: BorderStyle | None = None,
    ) -> None:
        """Renderiza múltiplas imagens em pilha vertical ou grade de colunas."""
        self._media.image_gallery(
            sources,
            columns=columns,
            bordered=bordered,
            width=width,
            border=border,
        )

    def mermaid(
        self,
        diagram: str,
        *,
        bordered: bool = True,
        caption: str | None = None,
        height: int | None = None,
        border: BorderStyle | None = None,
    ) -> str:
        """Renderiza um diagrama Mermaid formatado dentro de um container."""
        return self._media.mermaid(
            diagram,
            bordered=bordered,
            caption=caption,
            height=height,
            border=border,
        )

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
        border: BorderStyle | None = None,
        output_border: BorderStyle | None = None,
    ) -> str:
        """Renderiza um bloco de código limpo com saída opcional."""
        return self._code.code_block(
            code,
            language=language,
            output=output,
            bordered_output=bordered_output,
            output_as_markdown=output_as_markdown,
            line_numbers=line_numbers,
            border=border,
            output_border=output_border,
        )

    def output_box(
        self,
        *items: Any,
        bordered: bool = True,
        as_markdown: bool = False,
        border: BorderStyle | None = None,
    ) -> None:
        """Exibe resultados em um container padronizado com borda."""
        self._code.output_box(
            *items,
            bordered=bordered,
            as_markdown=as_markdown,
            border=border,
        )

    def output_container(
        self,
        *,
        bordered: bool = True,
        center: bool = False,
        border: BorderStyle | None = None,
    ) -> Iterator[Any]:
        """Retorna um context manager de container para saídas customizadas."""
        return self._code.output_container(bordered=bordered, center=center, border=border)

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
        border: BorderStyle | None = None,
    ) -> str:
        """Renderiza um card de texto com marcações/etiquetas coloridas."""
        return self._data.highlighted_text(text, spans=spans, font_size=font_size, border=border)

    def styled_table(
        self,
        data: Mapping[str, Sequence[Any]] | Sequence[Mapping[str, Any]] | Any,
        *,
        highlights: Mapping[tuple[str, int], Sequence[HighlightSpan]] | None = None,
        border: BorderStyle | None = None,
    ) -> str:
        """Renderiza uma tabela HTML estilizada com destaques opcionais por célula."""
        return self._data.styled_table(data, highlights=highlights, border=border)

    def metrics(
        self,
        items: Sequence[tuple[str, str] | tuple[str, str, str]],
        *,
        columns: int | None = None,
        border: BorderStyle | None = None,
    ) -> str:
        """Renderiza uma grade editorial de cartões de métricas/KPIs."""
        return self._data.metrics(items, columns=columns, border=border)

    # ------------------------------------------------------------------
    # Componentes interativos
    # ------------------------------------------------------------------
    def reveal_card(
        self,
        prompt: str | None = None,
        answer: ContentBlock = "",
        *,
        title: str | None = None,
        kicker: str | None = None,
        reveal_label: str = "Revelar resposta",
        hide_label: str = "Ocultar resposta",
        initially_revealed: bool = False,
        accent_color: str | None = None,
        key: str | None = None,
        escape_html: bool = False,
        border: BorderStyle | None = None,
    ) -> bool:
        """Renderiza um cartão de revelação (flashcard) com estado persistente."""
        return self._interactive.reveal_card(
            prompt=prompt,
            answer=answer,
            title=title,
            kicker=kicker,
            reveal_label=reveal_label,
            hide_label=hide_label,
            initially_revealed=initially_revealed,
            accent_color=accent_color,
            key=key,
            escape_html=escape_html,
            border=border,
        )

    def quiz(
        self,
        question: str,
        options: Sequence[str],
        *,
        answer_index: int = 0,
        explanation: str | None = None,
        title: str | None = None,
        kicker: str | None = "Quiz",
        submit_label: str = "Verificar resposta",
        accent_color: str | None = None,
        key: str | None = None,
        escape_html: bool = False,
        border: BorderStyle | None = None,
    ) -> bool | None:
        """Renderiza um questionário de múltipla escolha com verificação imediata."""
        return self._interactive.quiz(
            question,
            options,
            answer_index=answer_index,
            explanation=explanation,
            title=title,
            kicker=kicker,
            submit_label=submit_label,
            accent_color=accent_color,
            key=key,
            escape_html=escape_html,
            border=border,
        )

    def quiz_summary(
        self,
        *,
        title: str = "Resumo dos Questionários",
        kicker: str | None = "Desempenho",
        empty_message: str = "Nenhum questionário foi registrado ainda nesta apresentação.",
        accent_color: str | None = None,
        border: BorderStyle | None = None,
    ) -> tuple[int, int]:
        """Exibe o placar consolidado de todos os quizzes da apresentação."""
        return self._interactive.quiz_summary(
            title=title,
            kicker=kicker,
            empty_message=empty_message,
            accent_color=accent_color,
            border=border,
        )

    def step_tabs(
        self,
        steps: Sequence[tuple[str, ContentBlock]],
        *,
        title: str | None = None,
        kicker: str | None = None,
        accent_color: str | None = None,
        key: str | None = None,
        escape_html: bool = False,
        border: BorderStyle | None = None,
    ) -> int:
        """Renderiza um seletor horizontal de etapas (stepper) em card editorial."""
        return self._interactive.step_tabs(
            steps,
            title=title,
            kicker=kicker,
            accent_color=accent_color,
            key=key,
            escape_html=escape_html,
            border=border,
        )

    def compare_toggle(
        self,
        left_label: str,
        left_content: ContentBlock,
        right_label: str,
        right_content: ContentBlock,
        *,
        title: str | None = None,
        kicker: str | None = "Comparativo",
        default_side: Literal["left", "right"] = "left",
        accent_color: str | None = None,
        key: str | None = None,
        escape_html: bool = False,
        border: BorderStyle | None = None,
    ) -> Literal["left", "right"]:
        """Alterna dinamicamente entre dois cenários no mesmo card editorial."""
        return self._interactive.compare_toggle(
            left_label,
            left_content,
            right_label,
            right_content,
            title=title,
            kicker=kicker,
            default_side=default_side,
            accent_color=accent_color,
            key=key,
            escape_html=escape_html,
            border=border,
        )

    def checklist(
        self,
        items: Sequence[str],
        *,
        title: str | None = "Checklist de Prontidão",
        kicker: str | None = "Autoavaliação",
        default_checked: Sequence[bool] | None = None,
        accent_color: str | None = None,
        key: str | None = None,
        border: BorderStyle | None = None,
    ) -> list[bool]:
        """Renderiza uma lista de verificação interativa com barra de progresso."""
        return self._interactive.checklist(
            items,
            title=title,
            kicker=kicker,
            default_checked=default_checked,
            accent_color=accent_color,
            key=key,
            border=border,
        )

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
