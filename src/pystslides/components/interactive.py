"""Componentes interativos: cartões de revelação e elementos dinâmicos."""

from __future__ import annotations

import html
from typing import Any, Callable, Sequence

from pystslides.components.base import BaseComponent, create_container
from pystslides.components.typography import _build_asterisk_svg


class InteractiveRenderer(BaseComponent):
    """Renderiza blocos interativos mantendo o sistema visual editorial do PyStSlides."""

    def __init__(self, st_module: Any, config: Any) -> None:
        super().__init__(st_module, config)
        self._reveal_counter = 0

    def reveal_card(
        self,
        prompt: str | None = None,
        answer: str | Sequence[str] | Callable[[], None] = "",
        *,
        title: str | None = None,
        kicker: str | None = None,
        reveal_label: str = "Revelar resposta",
        hide_label: str = "Ocultar resposta",
        initially_revealed: bool = False,
        accent_color: str | None = None,
        key: str | None = None,
        escape_html: bool = False,
    ) -> bool:
        """Renderiza um cartão de revelação (flashcard) com estado persistente em `session_state`."""
        self._reveal_counter += 1
        state_key = f"pyst_reveal_{key}" if key else f"pyst_reveal_{self._reveal_counter}"
        chosen_accent = accent_color or self._next_accent_color()

        session_state = getattr(self._st, "session_state", None)
        if session_state is not None and state_key not in session_state:
            session_state[state_key] = initially_revealed

        is_revealed = (
            bool(session_state.get(state_key, initially_revealed))
            if session_state is not None
            else initially_revealed
        )

        with create_container(self._st, border=True):
            header_parts = ['<span class="pyst-reveal-marker" aria-hidden="true"></span>']
            header_text = title or kicker
            if header_text:
                icon_svg = _build_asterisk_svg(chosen_accent, size=15)
                kicker_badge = (
                    f'<span class="pyst-reveal-kicker">{html.escape(kicker)}</span>'
                    if (kicker and title)
                    else ""
                )
                header_parts.append(
                    f'<div class="pyst-reveal-header">'
                    f'<span class="pyst-callout-icon">{icon_svg}</span>'
                    f"<span>{html.escape(header_text)}</span>"
                    f"{kicker_badge}</div>"
                )
            if prompt:
                prompt_content = html.escape(prompt) if escape_html else prompt
                header_parts.append(f'<p class="pyst-reveal-prompt">{prompt_content}</p>')

            self._st.markdown("".join(header_parts), unsafe_allow_html=True)

            btn_label = hide_label if is_revealed else reveal_label
            if self._st.button(btn_label, key=f"{state_key}_btn"):
                new_state = not is_revealed
                if session_state is not None:
                    session_state[state_key] = new_state
                if hasattr(self._st, "rerun"):
                    self._st.rerun()
                return new_state

            if is_revealed:
                self._st.markdown('<hr class="pyst-divider">', unsafe_allow_html=True)
                if callable(answer):
                    answer()
                elif isinstance(answer, str):
                    body = html.escape(answer) if escape_html else answer
                    self._st.markdown(
                        f'<div class="pyst-reveal-answer" style="border-left-color: {chosen_accent};">'
                        f"{body}</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    paragraphs = "".join(
                        f"<p>{html.escape(item) if escape_html else item}</p>"
                        for item in answer
                    )
                    self._st.markdown(
                        f'<div class="pyst-reveal-answer" style="border-left-color: {chosen_accent};">'
                        f"{paragraphs}</div>",
                        unsafe_allow_html=True,
                    )

        return is_revealed
