"""Componentes de mídia: imagens, galerias e diagramas Mermaid."""

from __future__ import annotations

import html
import json
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
    def _extract_mermaid_source(diagram: str) -> str:
        cleaned = textwrap.dedent(diagram).strip()
        fenced_match = re.match(r"^```mermaid\s*\n(.*?)\n```$", cleaned, flags=re.DOTALL)
        if fenced_match:
            cleaned = textwrap.dedent(fenced_match.group(1)).strip()
        return cleaned

    @classmethod
    def format_mermaid(cls, diagram: str) -> str:
        """Normaliza a indentação de um diagrama Mermaid e o envolve em bloco Markdown."""
        return f"```mermaid\n{cls._extract_mermaid_source(diagram)}\n```"

    def _build_mermaid_html(self, source: str) -> str:
        bg = self.theme.background_color
        font = self.theme.font_family
        escaped_src = html.escape(source)
        src_json = json.dumps(source)
        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  html, body {{
    margin: 0;
    padding: 0;
    background: {bg};
    font-family: '{font}', -apple-system, BlinkMacSystemFont, sans-serif;
    overflow: hidden;
  }}
  #pyst-mermaid-wrap {{
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 12px 8px;
    width: 100%;
    box-sizing: border-box;
  }}
  #pyst-mermaid-wrap svg {{
    max-width: 100%;
    height: auto;
  }}
  pre.fallback {{
    margin: 0;
    padding: 16px;
    background: #fafafa;
    border-radius: 8px;
    font-size: 14px;
    color: #18181b;
    overflow-x: auto;
    width: 100%;
  }}
</style>
</head>
<body>
  <div id="pyst-mermaid-wrap"><pre class="fallback">{escaped_src}</pre></div>
  <script type="module">
    const source = {src_json};
    const wrap = document.getElementById('pyst-mermaid-wrap');
    function fitFrame() {{
      try {{
        const svg = wrap.querySelector('svg');
        const svgH = svg ? svg.getBoundingClientRect().height + 28 : 0;
        const h = Math.max(Math.ceil(Math.max(wrap.getBoundingClientRect().height, svgH)), 80);
        if (window.frameElement) {{
          window.frameElement.style.height = h + 'px';
          window.frameElement.style.minHeight = h + 'px';
          window.frameElement.height = String(h);
          let parent = window.frameElement.parentElement;
          for (let i = 0; i < 4 && parent; i++) {{
            if (parent.getAttribute && parent.getAttribute('data-testid') === 'stElementContainer') {{
              parent.style.height = 'auto';
              parent.style.minHeight = h + 'px';
              break;
            }}
            if (parent.style) {{
              parent.style.height = h + 'px';
              parent.style.minHeight = h + 'px';
            }}
            parent = parent.parentElement;
          }}
        }}
      }} catch (_) {{}}
    }}
    try {{
      const {{ default: mermaid }} = await import('https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs');
      mermaid.initialize({{
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'loose',
        fontFamily: '{font}, -apple-system, BlinkMacSystemFont, sans-serif'
      }});
      const id = 'pyst_m_' + Math.random().toString(36).slice(2, 10);
      const {{ svg }} = await mermaid.render(id, source);
      wrap.innerHTML = svg;
      requestAnimationFrame(() => {{
        fitFrame();
        setTimeout(fitFrame, 80);
      }});
    }} catch (_) {{
      fitFrame();
    }}
  </script>
</body>
</html>"""

    def mermaid(
        self,
        diagram: str,
        *,
        bordered: bool = True,
        caption: str | None = None,
        height: int | None = None,
    ) -> str:
        """Renderiza um diagrama Mermaid em SVG interativo (com fallback Markdown para testes)."""
        source = self._extract_mermaid_source(diagram)
        markdown_block = f"```mermaid\n{source}\n```"
        is_active_fn = getattr(self._st, "is_active", None)
        is_active = is_active_fn() if callable(is_active_fn) else True

        base_st = getattr(self._st, "_st", self._st)
        components_html = getattr(
            getattr(getattr(base_st, "components", None), "v1", None),
            "html",
            None,
        )

        if callable(components_html) and is_active:
            is_vertical = any(k in source for k in ("TD", "TB", "BT"))
            logic_lines = [
                ln
                for ln in source.splitlines()
                if ln.strip() and not ln.strip().startswith(("style ", "classDef "))
            ]
            default_height = height or (
                max(580, min(780, len(logic_lines) * 115)) if is_vertical else 160
            )
            html_doc = self._build_mermaid_html(source)
            if bordered:
                with create_container(self._st, border=True):
                    components_html(html_doc, height=default_height, scrolling=False)
            else:
                components_html(html_doc, height=default_height, scrolling=False)
        else:
            if bordered:
                with create_container(self._st, border=True):
                    self._st.markdown(markdown_block)
            else:
                self._st.markdown(markdown_block)

        if caption:
            self._st.caption(caption)

        return markdown_block
