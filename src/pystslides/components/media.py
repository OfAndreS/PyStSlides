"""Componentes de mídia: imagens, galerias e diagramas Mermaid."""

from __future__ import annotations

import html
import json
import re
import textwrap
from pathlib import Path
from typing import Any, Sequence

from pystslides.assets import AssetManager
from pystslides.components.base import (
    BaseComponent,
    create_bordered_container,
    resolve_border_style,
)
from pystslides.config import BorderStyle, PresentationConfig


ImageItem = str | Path | tuple[str | Path | Any, str] | Any
_VERTICAL_MERMAID_RE = re.compile(
    r"(?:^|\n)\s*(?:graph|flowchart)\s+(?:TD|TB|BT)\b|\bdirection\s+(?:TD|TB|BT)\b",
    re.IGNORECASE,
)


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
        border: BorderStyle | None = None,
    ) -> None:
        """Exibe uma imagem resolvendo seu caminho automaticamente via `AssetManager`."""
        resolved = self._resolve_source(source)
        kwargs: dict[str, Any] = {"caption": caption}
        if width is not None:
            kwargs["width"] = width

        border_style = resolve_border_style(border, theme=self.theme, bordered=bordered)
        if border_style != "none":
            with create_bordered_container(
                self._st,
                border_style=border_style,
                center=center,
            ):
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
        border: BorderStyle | None = None,
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
                self.image(src, caption=cap, width=width, bordered=bordered, border=border)
            return

        for start in range(0, len(normalized), columns):
            row_items = normalized[start : start + columns]
            cols = self._st.columns(columns)
            for col, (src, cap) in zip(cols, row_items):
                with col:
                    self.image(src, caption=cap, width=width, bordered=bordered, border=border)

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

    @staticmethod
    def _is_vertical_mermaid(source: str) -> bool:
        """Detecta diagramas Mermaid verticais (TD, TB ou BT) ignorando rótulos e estilos."""
        non_comment = "\n".join(
            ln for ln in source.splitlines() if not ln.lstrip().startswith("%%")
        )
        return bool(_VERTICAL_MERMAID_RE.search(non_comment))

    @classmethod
    def _estimate_mermaid_height(cls, source: str) -> int:
        """Estima a altura inicial do iframe conforme orientação e linhas lógicas."""
        logic_lines = [
            ln
            for ln in source.splitlines()
            if ln.strip()
            and not ln.lstrip().startswith(("%%", "style ", "classDef ", "linkStyle "))
        ]
        if cls._is_vertical_mermaid(source):
            return max(240, min(1400, len(logic_lines) * 108 + 44))
        extra_rows = max(len(logic_lines) - 3, 0)
        return max(160, min(520, 140 + extra_rows * 24))

    def _build_mermaid_html(self, source: str, *, auto_height: bool = True) -> str:
        bg = self.theme.background_color
        font = self.theme.font_family
        font_link = (
            f'<link rel="stylesheet" href="{html.escape(self.theme.google_font_url)}">'
            if self.theme.google_font_url
            else ""
        )
        escaped_src = html.escape(source)
        src_json = json.dumps(source)
        auto_height_js = "true" if auto_height else "false"
        fixed_svg_css = (
            ""
            if auto_height
            else "\n    max-height: calc(100vh - 24px) !important;\n    width: auto !important;"
        )
        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
{font_link}
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
    display: block;
    max-width: 100%;
    height: auto !important;{fixed_svg_css}
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
    const autoHeight = {auto_height_js};
    const wrap = document.getElementById('pyst-mermaid-wrap');
    let applyingResize = false;
    let lastAppliedHeight = 0;
    let mo = null;

    function measureHeight() {{
      const svg = wrap.querySelector('svg');
      if (svg) {{
        const rectH = svg.getBoundingClientRect().height;
        const vb = svg.viewBox && svg.viewBox.baseVal ? svg.viewBox.baseVal.height : 0;
        const svgH = Math.max(rectH, vb > 0 && rectH === 0 ? vb : 0);
        return Math.max(Math.ceil(Math.max(wrap.getBoundingClientRect().height, svgH + 26)), 80);
      }}
      return Math.max(Math.ceil(wrap.getBoundingClientRect().height), 80);
    }}

    function scaleSvgToViewportIfClipped() {{
      const svg = wrap.querySelector('svg');
      if (!svg || !window.innerHeight) return;
      const svgRect = svg.getBoundingClientRect();
      const maxH = Math.max(120, window.innerHeight - 24);
      if (svgRect.height > maxH + 4) {{
        svg.style.setProperty('max-height', maxH + 'px', 'important');
        svg.style.setProperty('width', 'auto', 'important');
      }}
    }}

    function isElementContainer(el) {{
      if (!el || !el.getAttribute) return false;
      const testId = el.getAttribute('data-testid');
      if (testId === 'stElementContainer' || testId === 'element-container') return true;
      return Boolean(
        el.classList &&
        (el.classList.contains('stElementContainer') || el.classList.contains('element-container'))
      );
    }}

    function isLayoutBoundary(el) {{
      if (!el) return true;
      const tag = el.tagName ? el.tagName.toUpperCase() : '';
      if (tag === 'SECTION' || tag === 'MAIN' || tag === 'BODY' || tag === 'HTML') return true;
      const testId = el.getAttribute ? el.getAttribute('data-testid') : '';
      return (
        testId === 'stVerticalBlock' ||
        testId === 'stVerticalBlockBorderWrapper' ||
        testId === 'stHorizontalBlock' ||
        testId === 'stColumn' ||
        testId === 'column' ||
        testId === 'stMain' ||
        testId === 'stMainBlockContainer' ||
        testId === 'stAppViewContainer'
      );
    }}

    function findInnerWrappersAndContainer(frame) {{
      const wrappers = [];
      let container = null;
      let parent = frame.parentElement;
      for (let i = 0; i < 6 && parent; i++) {{
        if (isElementContainer(parent)) {{
          container = parent;
          break;
        }}
        if (isLayoutBoundary(parent)) {{
          return {{ wrappers: [], container: null }};
        }}
        wrappers.push(parent);
        parent = parent.parentElement;
      }}
      return container ? {{ wrappers, container }} : {{ wrappers: [], container: null }};
    }}

    function observeFrame() {{
      if (mo && window.frameElement) {{
        mo.observe(window.frameElement, {{ attributes: true, attributeFilter: ['height', 'style'] }});
      }}
    }}

    function fitFrame() {{
      if (!autoHeight) {{
        scaleSvgToViewportIfClipped();
        return;
      }}
      if (applyingResize) return;
      applyingResize = true;
      if (mo) mo.disconnect();
      try {{
        const svg = wrap.querySelector('svg');
        if (svg) {{
          svg.style.removeProperty('max-height');
          svg.style.removeProperty('width');
        }}
        const h = measureHeight();
        const targetPx = h + 'px';
        const targetAttr = String(h);
        let resized = false;
        const frame = window.frameElement;
        if (frame) {{
          if (
            frame.style.height !== targetPx ||
            frame.style.minHeight !== '0px' ||
            frame.getAttribute('height') !== targetAttr ||
            lastAppliedHeight !== h
          ) {{
            frame.style.height = targetPx;
            frame.style.minHeight = '0px';
            frame.height = targetAttr;
            const {{ wrappers, container }} = findInnerWrappersAndContainer(frame);
            for (const wrapper of wrappers) {{
              if (wrapper.style) {{
                wrapper.style.height = targetPx;
                wrapper.style.minHeight = '0px';
              }}
            }}
            if (container && container.style) {{
              container.style.height = 'auto';
              container.style.minHeight = '0px';
            }}
            lastAppliedHeight = h;
          }}
          resized = true;
        }}
        if (!resized) {{
          scaleSvgToViewportIfClipped();
        }}
      }} catch (_) {{
        scaleSvgToViewportIfClipped();
      }} finally {{
        if (mo) {{
          mo.takeRecords();
          observeFrame();
        }}
        applyingResize = false;
      }}
    }}

    try {{
      const {{ default: mermaid }} = await import('https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs');
      mermaid.initialize({{
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'loose',
        flowchart: {{ useMaxWidth: true }},
        fontFamily: '{font}, -apple-system, BlinkMacSystemFont, sans-serif'
      }});
      const id = 'pyst_m_' + Math.random().toString(36).slice(2, 10);
      const {{ svg }} = await mermaid.render(id, source);
      wrap.innerHTML = svg;

      if (typeof ResizeObserver !== 'undefined') {{
        const ro = new ResizeObserver(() => fitFrame());
        ro.observe(wrap);
      }}
      if (autoHeight && window.frameElement && typeof MutationObserver !== 'undefined') {{
        mo = new MutationObserver(() => {{
          if (!applyingResize) fitFrame();
        }});
        observeFrame();
      }}
      window.addEventListener('resize', fitFrame);
      if (document.fonts && document.fonts.ready) {{
        document.fonts.ready.then(() => fitFrame());
      }}
      requestAnimationFrame(() => {{
        fitFrame();
        setTimeout(fitFrame, 80);
        setTimeout(fitFrame, 250);
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
        border: BorderStyle | None = None,
    ) -> str:
        """Renderiza um diagrama Mermaid em SVG interativo (com fallback Markdown para testes)."""
        source = self._extract_mermaid_source(diagram)
        markdown_block = f"```mermaid\n{source}\n```"
        border_style = resolve_border_style(border, theme=self.theme, bordered=bordered)
        is_active_fn = getattr(self._st, "is_active", None)
        is_active = is_active_fn() if callable(is_active_fn) else True

        base_st = getattr(self._st, "_st", self._st)
        components_html = getattr(
            getattr(getattr(base_st, "components", None), "v1", None),
            "html",
            None,
        )

        if callable(components_html) and is_active:
            default_height = height or self._estimate_mermaid_height(source)
            html_doc = self._build_mermaid_html(source, auto_height=(height is None))
            if border_style != "none":
                with create_bordered_container(self._st, border_style=border_style):
                    components_html(html_doc, height=default_height, scrolling=False)
            else:
                components_html(html_doc, height=default_height, scrolling=False)
        else:
            if border_style != "none":
                with create_bordered_container(self._st, border_style=border_style):
                    self._st.markdown(markdown_block)
            else:
                self._st.markdown(markdown_block)

        if caption:
            self._st.caption(caption)

        return markdown_block
