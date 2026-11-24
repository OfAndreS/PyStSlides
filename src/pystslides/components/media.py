"""Componentes de mídia: imagens, galerias e diagramas Mermaid."""

from __future__ import annotations

import re
import textwrap
from pathlib import Path
from typing import Any, Sequence

from pystslides.assets import AssetManager
from pystslides.components.base import BaseComponent, create_container
from pystslides.config import PresentationConfig


ImageItem = str | Path | tuple[str | Path | Any, str] | Any


class MediaRenderer(BaseComponent):
    """Renderiza imagens únicas, sequências/grades de imagens e diagramas Mermaid."""

    def __init__(
        self,
        st_module: Any,
        config: PresentationConfig,
        asset_manager: AssetManager | None = None,
    ) -> None:
        super().__init__(st_module, config)
        self._assets = asset_manager

    def _resolve_source(self, source: Any) -> Any:
        if isinstance(source, str) and source.startswith(("http://", "https://")):
            return source
        if isinstance(source, (str, Path)):
            if self._assets is not None:
                return str(self._assets.resolve(source))
            return str(Path(source))
        return source

    def image(
        self,
        source: Any,
        *,
        caption: str = "",
        width: int | None = None,
        bordered: bool = False,
        center: bool = True,
    ) -> None:
        """Exibe uma imagem resolvendo seu caminho automaticamente via `AssetManager`."""
        resolved = self._resolve_source(source)
        kwargs: dict[str, Any] = {"caption": caption}
        if width is not None:
            kwargs["width"] = width

        if bordered:
            with create_container(self._st, border=True, center=center):
                self._st.image(resolved, **kwargs)
        else:
            self._st.image(resolved, **kwargs)

    def image_gallery(
        self,
        sources: Sequence[ImageItem],
        *,
        columns: int = 1,
        bordered: bool = False,
        width: int | None = None,
    ) -> None:
        """Renderiza uma sequência vertical ou grade em colunas de imagens.

        Cada item pode ser um nome de arquivo/`Path` ou uma tupla `(fonte, caption)`.
        """
        if columns < 1:
            raise ValueError("O número de colunas da galeria deve ser maior ou igual a 1.")

        normalized: list[tuple[Any, str]] = []
        for item in sources:
            if isinstance(item, tuple) and len(item) == 2:
                normalized.append((item[0], str(item[1])))
            else:
                normalized.append((item, ""))

        if columns == 1:
            for src, cap in normalized:
                self.image(src, caption=cap, width=width, bordered=bordered)
            return

        for start in range(0, len(normalized), columns):
            row_items = normalized[start : start + columns]
            cols = self._st.columns(columns)
            for col, (src, cap) in zip(cols, row_items):
                with col:
                    self.image(src, caption=cap, width=width, bordered=bordered)

    @staticmethod
    def format_mermaid(diagram: str) -> str:
        """Normaliza a indentação de um diagrama Mermaid e o envolve em bloco Markdown."""
        cleaned = textwrap.dedent(diagram).strip()
        fenced_match = re.match(r"^```mermaid\s*\n(.*?)\n```$", cleaned, flags=re.DOTALL)
        if fenced_match:
            cleaned = textwrap.dedent(fenced_match.group(1)).strip()
        return f"```mermaid\n{cleaned}\n```"

    def mermaid(
        self,
        diagram: str,
        *,
        bordered: bool = True,
        caption: str | None = None,
    ) -> str:
        """Renderiza um diagrama Mermaid em um container padronizado."""
        markdown_block = self.format_mermaid(diagram)
        if bordered:
            with create_container(self._st, border=True):
                self._st.markdown(markdown_block)
        else:
            self._st.markdown(markdown_block)

        if caption:
            self._st.caption(caption)

        return markdown_block
