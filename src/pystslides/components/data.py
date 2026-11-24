"""Componentes visuais de dados: destaques em texto e tabelas HTML estilizadas."""

from __future__ import annotations

import html
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Sequence

from pystslides.components.base import BaseComponent


class HighlightLevel(Enum):
    """Níveis semânticos de destaque com paleta de cores acessível."""

    LOW = ("#fee2e2", "#991b1b")
    MEDIUM = ("#fef08a", "#854d0e")
    HIGH = ("#dcfce7", "#166534")
    INFO = ("#dbeafe", "#1e40af")
    NEUTRAL = ("#f1f5f9", "#334155")

    @property
    def bg_color(self) -> str:
        return self.value[0]

    @property
    def text_color(self) -> str:
        return self.value[1]


@dataclass(frozen=True)
class HighlightSpan:
    """Representa um intervalo de texto a ser destacado com etiqueta e cor."""

    start: int
    end: int
    label: str = ""
    score: float | None = None
    level: HighlightLevel | None = None
    bg_color: str | None = None
    text_color: str | None = None

    @classmethod
    def from_score(
        cls,
        start: int,
        end: int,
        label: str,
        score: float,
        *,
        low_threshold: float = 0.50,
        high_threshold: float = 0.75,
    ) -> HighlightSpan:
        """Cria um `HighlightSpan` mapeando automaticamente uma pontuação para cores."""
        if score < low_threshold:
            level = HighlightLevel.LOW
        elif score <= high_threshold:
            level = HighlightLevel.MEDIUM
        else:
            level = HighlightLevel.HIGH

        return cls(start=start, end=end, label=label, score=score, level=level)

    def resolve_colors(self) -> tuple[str, str]:
        """Determina o par `(cor_de_fundo, cor_do_texto)` para o destaque."""
        if self.bg_color and self.text_color:
            return self.bg_color, self.text_color
        level = self.level or HighlightLevel.INFO
        return self.bg_color or level.bg_color, self.text_color or level.text_color

    def format_badge(self) -> str:
        """Formata o sufixo de etiqueta/pontuação exibido ao lado do trecho marcado."""
        if self.label and self.score is not None:
            return f" [{self.label} : {self.score:.2f}]"
        if self.label:
            return f" [{self.label}]"
        if self.score is not None:
            return f" [{self.score:.2f}]"
        return ""


def apply_highlights(text: str, spans: Sequence[HighlightSpan]) -> str:
    """Aplica tags `<mark>` a um texto removendo sobreposições e escapando HTML."""
    valid_spans = [s for s in spans if 0 <= s.start < s.end <= len(text)]
    if not valid_spans:
        return html.escape(text)

    ordered = sorted(valid_spans, key=lambda s: (s.start, -(s.end - s.start)))
    non_overlapping: list[HighlightSpan] = []
    last_end = 0
    for span in ordered:
        if span.start >= last_end:
            non_overlapping.append(span)
            last_end = span.end

    chunks: list[str] = []
    cursor = 0
    for span in non_overlapping:
        if span.start > cursor:
            chunks.append(html.escape(text[cursor : span.start]))

        bg, fg = span.resolve_colors()
        snippet = html.escape(text[span.start : span.end])
        badge = html.escape(span.format_badge())
        chunks.append(
            f'<mark style="background-color: {bg}; color: {fg}; '
            f'padding: 4px 8px; border-radius: 6px; text-decoration: none;">'
            f"{snippet}{badge}</mark>"
        )
        cursor = span.end

    if cursor < len(text):
        chunks.append(html.escape(text[cursor:]))

    return "".join(chunks)


def _normalize_table_data(data: Any) -> tuple[list[str], list[list[Any]]]:
    """Converte DataFrame, dict de colunas ou lista de dicts em `(colunas, linhas)`."""
    if hasattr(data, "to_dict"):
        data = data.to_dict(orient="list")

    if isinstance(data, Mapping):
        columns = [str(col) for col in data.keys()]
        if not columns:
            return [], []
        column_values = [list(data[col]) for col in data.keys()]
        num_rows = len(column_values[0])
        rows = [
            [col_vals[row_idx] if row_idx < len(col_vals) else "" for col_vals in column_values]
            for row_idx in range(num_rows)
        ]
        return columns, rows

    if isinstance(data, Sequence) and not isinstance(data, (str, bytes)):
        if not data:
            return [], []
        first = data[0]
        if isinstance(first, Mapping):
            columns = [str(k) for k in first.keys()]
            rows = [[row.get(col, "") for col in first.keys()] for row in data]
            return columns, rows

    raise TypeError(
        "Formato de tabela não suportado. Forneça um dict de colunas, "
        "uma lista de dicts ou um DataFrame."
    )


class DataRenderer(BaseComponent):
    """Renderiza cards de texto destacado e tabelas HTML estilizadas."""

    def highlighted_text(
        self,
        text: str,
        spans: Sequence[HighlightSpan] = (),
        *,
        font_size: str | None = None,
    ) -> str:
        """Renderiza um texto com trechos destacados dentro de um card estilizado."""
        rendered_inner = apply_highlights(text, spans)
        style_attr = f' style="font-size: {font_size} !important;"' if font_size else ""
        card_html = f'<div class="pyst-card"{style_attr}>{rendered_inner}</div>'
        self._st.markdown(card_html, unsafe_allow_html=True)
        return card_html

    def styled_table(
        self,
        data: Mapping[str, Sequence[Any]] | Sequence[Mapping[str, Any]] | Any,
        *,
        highlights: Mapping[tuple[str, int], Sequence[HighlightSpan]] | None = None,
    ) -> str:
        """Renderiza uma tabela HTML com bordas arredondadas, hover e destaques opcionais."""
        columns, rows = _normalize_table_data(data)
        highlight_map = highlights or {}

        header_cells = "".join(f"<th>{html.escape(col)}</th>" for col in columns)
        body_rows: list[str] = []

        for row_idx, row in enumerate(rows):
            cells_html: list[str] = []
            for col_name, value in zip(columns, row):
                cell_text = "" if value is None else str(value)
                cell_spans = highlight_map.get((col_name, row_idx), ())
                cells_html.append(f"<td>{apply_highlights(cell_text, cell_spans)}</td>")
            body_rows.append(f"<tr>{''.join(cells_html)}</tr>")

        table_html = (
            '<table class="pyst-table">'
            f"<thead><tr>{header_cells}</tr></thead>"
            f"<tbody>{''.join(body_rows)}</tbody>"
            "</table>"
        )
        self._st.markdown(table_html, unsafe_allow_html=True)
        return table_html
