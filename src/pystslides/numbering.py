"""Rastreamento hierárquico, numeração automática e geração de âncoras de seções."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from pystslides.exceptions import InvalidSectionLevelError


@dataclass(frozen=True)
class SectionEntry:
    """Representa um tópico ou sub-tópico registrado na apresentação."""

    level: int
    number: str
    title: str
    formatted_title: str
    anchor: str


class SectionTracker:
    """Controla a numeração automática hierárquica e o índice da apresentação."""

    def __init__(
        self,
        *,
        auto_number: bool = True,
        topic_format: str = "{number:02d} ) - {title}",
        subtopic_format: str = "{number} ) {title}",
    ) -> None:
        self._auto_number = auto_number
        self._topic_format = topic_format
        self._subtopic_format = subtopic_format
        self._counters: list[int] = []
        self._entries: list[SectionEntry] = []
        self._used_anchors: dict[str, int] = {}

    @property
    def entries(self) -> tuple[SectionEntry, ...]:
        """Retorna todas as seções registradas em ordem de aparição."""
        return tuple(self._entries)

    def reset(self) -> None:
        """Reinicia todos os contadores e o histórico de seções."""
        self._counters.clear()
        self._entries.clear()
        self._used_anchors.clear()

    def register_topic(self, title: str, *, numbered: bool | None = None) -> SectionEntry:
        """Registra um tópico principal (nível 1) e retorna sua entrada formatada."""
        use_numbering = self._auto_number if numbered is None else numbered

        if use_numbering:
            next_topic = (self._counters[0] + 1) if self._counters else 1
            self._counters = [next_topic]
            number_str = f"{next_topic:02d}"
            formatted = self._topic_format.format(number=next_topic, title=title)
        else:
            number_str = ""
            formatted = title

        anchor = self._build_unique_anchor(f"{number_str}-{title}" if number_str else title)
        entry = SectionEntry(
            level=1,
            number=number_str,
            title=title,
            formatted_title=formatted,
            anchor=anchor,
        )
        self._entries.append(entry)
        return entry

    def register_subtopic(
        self,
        title: str,
        *,
        level: int = 2,
        numbered: bool | None = None,
    ) -> SectionEntry:
        """Registra um sub-tópico de nível >= 2 (ex.: 4.1, 5.1.1)."""
        if level < 2:
            raise InvalidSectionLevelError(level)

        use_numbering = self._auto_number if numbered is None else numbered

        if use_numbering:
            # Garante que níveis superiores existam antes de incrementar o nível atual.
            while len(self._counters) < level - 1:
                self._counters.append(1)

            if len(self._counters) < level:
                self._counters.append(1)
            else:
                self._counters = self._counters[:level]
                self._counters[level - 1] += 1

            number_str = ".".join(str(value) for value in self._counters)
            formatted = self._subtopic_format.format(number=number_str, title=title)
        else:
            number_str = ""
            formatted = title

        anchor = self._build_unique_anchor(f"{number_str}-{title}" if number_str else title)
        entry = SectionEntry(
            level=level,
            number=number_str,
            title=title,
            formatted_title=formatted,
            anchor=anchor,
        )
        self._entries.append(entry)
        return entry

    def _build_unique_anchor(self, raw_text: str) -> str:
        base_slug = self._slugify(raw_text) or "secao"
        count = self._used_anchors.get(base_slug, 0) + 1
        self._used_anchors[base_slug] = count
        return f"pyst-{base_slug}" if count == 1 else f"pyst-{base_slug}-{count}"

    @staticmethod
    def _slugify(text: str) -> str:
        normalized = unicodedata.normalize("NFKD", text)
        ascii_only = normalized.encode("ascii", "ignore").decode("ascii").lower()
        slug = re.sub(r"[^a-z0-9]+", "-", ascii_only).strip("-")
        return slug
