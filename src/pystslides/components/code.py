"""Componentes para blocos de código, execução interativa e caixas de saída."""

from __future__ import annotations

import textwrap
from contextlib import contextmanager
from typing import Any, Iterator, Literal

from pystslides.components.base import (
    BaseComponent,
    create_bordered_container,
    create_container,
    resolve_border_style,
)
from pystslides.config import BorderStyle


class CodeRenderer(BaseComponent):
    """Renderiza trechos de código limpos, demonstrações ao vivo e containers de saída."""

    @staticmethod
    def clean_code(code: str) -> str:
        """Remove indentação comum e quebras de linha excedentes de um bloco de código."""
        return textwrap.dedent(code).strip("\n")

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
        """Exibe um bloco de código formatado e, opcionalmente, sua saída em um card."""
        cleaned = self.clean_code(code)
        code_border = resolve_border_style(border, theme=self.theme)
        with create_container(self._st, border=False):
            self._st.markdown(
                f'<span class="pyst-code-marker pyst-border-{code_border}" aria-hidden="true"></span>',
                unsafe_allow_html=True,
            )
            try:
                self._st.code(cleaned, language=language, line_numbers=line_numbers)
            except TypeError:
                self._st.code(cleaned, language=language)

        if output is not None:
            resolved_output_border = (
                resolve_border_style(output_border, theme=self.theme)
                if output_border is not None
                else (code_border if bordered_output else "none")
            )
            if callable(output):
                with self.output_container(
                    bordered=bordered_output,
                    border=resolved_output_border,
                ):
                    output()
            else:
                self.output_box(
                    output,
                    bordered=bordered_output,
                    as_markdown=output_as_markdown,
                    border=resolved_output_border,
                )

        return cleaned

    def output_box(
        self,
        *items: Any,
        bordered: bool = True,
        as_markdown: bool = False,
        border: BorderStyle | None = None,
    ) -> None:
        """Renderiza um ou mais resultados dentro de um container padronizado."""
        with self.output_container(bordered=bordered, border=border):
            for item in items:
                if as_markdown and isinstance(item, str):
                    self._st.markdown(item)
                else:
                    self._st.write(item)

    @contextmanager
    def output_container(
        self,
        *,
        bordered: bool = True,
        center: bool = False,
        border: BorderStyle | None = None,
    ) -> Iterator[Any]:
        """Context manager que abre um container estilizado para saídas customizadas."""
        border_style = resolve_border_style(border, theme=self.theme, bordered=bordered)
        with create_bordered_container(
            self._st,
            border_style=border_style,
            center=center,
        ) as container:
            yield container

    def live_code(self, code_location: Literal["above", "below"] = "above") -> Any:
        """Retorna diretamente o context manager `st.echo` para preservar o frame do chamador."""
        return self._st.echo(code_location=code_location)
