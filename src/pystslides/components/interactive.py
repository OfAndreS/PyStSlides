"""Componentes interativos: flashcards, quizzes, steppers, comparadores e checklists."""

from __future__ import annotations

import html
from typing import Any, Callable, Literal, Sequence

from pystslides.components.base import BaseComponent, create_columns, create_container
from pystslides.components.typography import _build_asterisk_svg


ContentBlock = str | Sequence[str] | Callable[[], None]


class InteractiveRenderer(BaseComponent):
    """Renderiza blocos interativos mantendo o sistema visual editorial do PyStSlides."""

    def __init__(self, st_module: Any, config: Any) -> None:
        super().__init__(st_module, config)
        self._reveal_counter = 0
        self._quiz_counter = 0
        self._stepper_counter = 0
        self._compare_counter = 0
        self._checklist_counter = 0
        self._quiz_entries: list[tuple[str, str]] = []

    @staticmethod
    def _build_header_markup(
        marker_class: str,
        *,
        accent_color: str,
        title: str | None = None,
        kicker: str | None = None,
        prompt: str | None = None,
        escape_html: bool = False,
    ) -> str:
        parts = [f'<span class="{marker_class}" aria-hidden="true"></span>']
        header_text = title or kicker
        if header_text:
            icon_svg = _build_asterisk_svg(accent_color, size=15)
            kicker_badge = (
                f'<span class="pyst-reveal-kicker">{html.escape(kicker)}</span>'
                if (kicker and title)
                else ""
            )
            parts.append(
                f'<div class="pyst-reveal-header">'
                f'<span class="pyst-callout-icon">{icon_svg}</span>'
                f"<span>{html.escape(header_text)}</span>"
                f"{kicker_badge}</div>"
            )
        if prompt:
            prompt_content = html.escape(prompt) if escape_html else prompt
            parts.append(f'<p class="pyst-reveal-prompt">{prompt_content}</p>')
        return "".join(parts)

    def _render_content(
        self,
        content: ContentBlock,
        *,
        accent_color: str,
        escape_html: bool = False,
        boxed: bool = True,
    ) -> None:
        if callable(content):
            content()
            return
        if isinstance(content, str):
            body = html.escape(content) if escape_html else content
        else:
            body = "".join(
                f"<p>{html.escape(item) if escape_html else item}</p>" for item in content
            )
        if boxed:
            self._st.markdown(
                f'<div class="pyst-reveal-answer" style="border-left-color: {accent_color};">'
                f"{body}</div>",
                unsafe_allow_html=True,
            )
        else:
            self._st.markdown(f'<div class="pyst-interactive-body">{body}</div>', unsafe_allow_html=True)

    def _button(self, label: str, *, key: str, button_type: str = "secondary", full_width: bool = False) -> bool:
        kwargs: dict[str, Any] = {"key": key}
        if full_width:
            kwargs["use_container_width"] = True
        if button_type != "secondary":
            kwargs["type"] = button_type
        try:
            return bool(self._st.button(label, **kwargs))
        except TypeError:
            kwargs.pop("type", None)
            kwargs.pop("use_container_width", None)
            return bool(self._st.button(label, **kwargs))

    def _radio(self, label: str, options: Sequence[str], *, key: str) -> str:
        try:
            selected = self._st.radio(
                label,
                list(options),
                key=key,
                label_visibility="collapsed",
            )
        except TypeError:
            selected = self._st.radio(label, list(options), key=key)
        return str(selected) if selected is not None else str(options[0])

    def _checkbox(self, label: str, *, value: bool, key: str) -> bool:
        return bool(self._st.checkbox(label, value=value, key=key))

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
            markup = self._build_header_markup(
                "pyst-reveal-marker",
                accent_color=chosen_accent,
                title=title,
                kicker=kicker,
                prompt=prompt,
                escape_html=escape_html,
            )
            self._st.markdown(markup, unsafe_allow_html=True)

            btn_label = hide_label if is_revealed else reveal_label
            if self._button(btn_label, key=f"{state_key}_btn"):
                new_state = not is_revealed
                if session_state is not None:
                    session_state[state_key] = new_state
                if hasattr(self._st, "rerun"):
                    self._st.rerun()
                return new_state

            if is_revealed:
                self._st.markdown('<hr class="pyst-divider">', unsafe_allow_html=True)
                self._render_content(answer, accent_color=chosen_accent, escape_html=escape_html)

        return is_revealed

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
    ) -> bool | None:
        """Renderiza um questionário de múltipla escolha com verificação imediata e placar."""
        if not options:
            raise ValueError("O quiz precisa de pelo menos uma opção de resposta.")
        if not (0 <= answer_index < len(options)):
            raise IndexError("`answer_index` está fora do intervalo de opções fornecido.")

        self._quiz_counter += 1
        state_key = f"pyst_quiz_{key}" if key else f"pyst_quiz_{self._quiz_counter}"
        chosen_accent = accent_color or self._next_accent_color()

        if all(existing_key != state_key for existing_key, _ in self._quiz_entries):
            self._quiz_entries.append((state_key, question))

        session_state = getattr(self._st, "session_state", None)
        radio_key = f"{state_key}_choice"
        submitted_key = f"{state_key}_submitted"
        result_key = f"{state_key}_correct"

        with create_container(self._st, border=True):
            markup = self._build_header_markup(
                "pyst-quiz-marker",
                accent_color=chosen_accent,
                title=title,
                kicker=kicker,
                prompt=question,
                escape_html=escape_html,
            )
            self._st.markdown(markup, unsafe_allow_html=True)

            selected = self._radio(question, options, key=radio_key)

            if self._button(submit_label, key=f"{state_key}_submit"):
                is_correct = selected == options[answer_index]
                if session_state is not None:
                    session_state[submitted_key] = True
                    session_state[result_key] = is_correct
                if hasattr(self._st, "rerun"):
                    self._st.rerun()
                return is_correct

            is_submitted = bool(session_state.get(submitted_key, False)) if session_state is not None else False
            if not is_submitted:
                return None

            is_correct = bool(session_state.get(result_key, False)) if session_state is not None else False
            correct_option = html.escape(options[answer_index])
            if is_correct:
                status_color = "#579568"
                status_bg = "#f3f9f5"
                status_text = "#1c4529"
                heading = "Resposta correta"
            else:
                status_color = "#d9534f"
                status_bg = "#fdf3f2"
                status_text = "#872421"
                heading = f"Resposta incorreta — esperado: {correct_option}"

            explanation_html = ""
            if explanation:
                exp_content = html.escape(explanation) if escape_html else explanation
                explanation_html = f'<div class="pyst-quiz-explanation">{exp_content}</div>'

            self._st.markdown(
                f'<div class="pyst-quiz-feedback" '
                f'style="background-color: {status_bg}; color: {status_text}; border-left-color: {status_color};">'
                f'<div class="pyst-quiz-feedback-title">{_build_asterisk_svg(status_color, size=14)}'
                f"<span>{heading}</span></div>"
                f"{explanation_html}</div>",
                unsafe_allow_html=True,
            )
            return is_correct

    def quiz_summary(
        self,
        *,
        title: str = "Resumo dos Questionários",
        kicker: str | None = "Desempenho",
        empty_message: str = "Nenhum questionário foi registrado ainda nesta apresentação.",
        accent_color: str | None = None,
    ) -> tuple[int, int]:
        """Exibe o placar consolidado de todos os quizzes respondidos na apresentação."""
        chosen_accent = accent_color or self._next_accent_color()
        session_state = getattr(self._st, "session_state", None) or {}
        total = len(self._quiz_entries)
        correct_count = 0
        answered_count = 0
        rows_html: list[str] = []

        for idx, (state_key, question) in enumerate(self._quiz_entries, start=1):
            submitted = bool(session_state.get(f"{state_key}_submitted", False))
            correct = bool(session_state.get(f"{state_key}_correct", False))
            if submitted:
                answered_count += 1
                if correct:
                    correct_count += 1
                    dot_color, status_label = "#579568", "Correto"
                else:
                    dot_color, status_label = "#d9534f", "Incorreto"
            else:
                dot_color, status_label = "#71717a", "Pendente"
            rows_html.append(
                '<div class="pyst-summary-row">'
                f'<span class="pyst-summary-q">{_build_asterisk_svg(dot_color, size=13)}'
                f"<span>{idx:02d}. {html.escape(question)}</span></span>"
                f'<span class="pyst-summary-badge" style="color: {dot_color};">{status_label}</span>'
                "</div>"
            )

        pct = int(round((correct_count / total) * 100)) if total else 0
        with create_container(self._st, border=True):
            header = self._build_header_markup(
                "pyst-reveal-marker",
                accent_color=chosen_accent,
                title=title,
                kicker=kicker,
            )
            if total == 0:
                self._st.markdown(
                    f'{header}<p class="pyst-reveal-prompt">{html.escape(empty_message)}</p>',
                    unsafe_allow_html=True,
                )
                return 0, 0

            self._st.markdown(
                f"{header}"
                f'<div class="pyst-summary-score">'
                f"<span><strong>{correct_count}</strong> de <strong>{total}</strong> acertos ({pct}%)</span>"
                f'<span class="pyst-summary-answered">{answered_count}/{total} respondidos</span>'
                f"</div>"
                f'<div class="pyst-progress-track">'
                f'<div class="pyst-progress-fill" style="width: {pct}%; background-color: #579568;"></div>'
                f"</div>"
                f'<div class="pyst-summary-list">{"".join(rows_html)}</div>',
                unsafe_allow_html=True,
            )
        return correct_count, total

    def step_tabs(
        self,
        steps: Sequence[tuple[str, ContentBlock]],
        *,
        title: str | None = None,
        kicker: str | None = None,
        accent_color: str | None = None,
        key: str | None = None,
        escape_html: bool = False,
    ) -> int:
        """Renderiza um seletor horizontal de etapas (stepper) dentro de um card editorial."""
        if not steps:
            raise ValueError("`step_tabs` exige ao menos uma etapa.")

        self._stepper_counter += 1
        state_key = f"pyst_stepper_{key}" if key else f"pyst_stepper_{self._stepper_counter}"
        chosen_accent = accent_color or self._next_accent_color()

        session_state = getattr(self._st, "session_state", None)
        if session_state is not None and state_key not in session_state:
            session_state[state_key] = 0

        active_idx = (
            int(session_state.get(state_key, 0)) if session_state is not None else 0
        )
        active_idx = min(max(active_idx, 0), len(steps) - 1)

        with create_container(self._st, border=True):
            header = self._build_header_markup(
                "pyst-stepper-marker",
                accent_color=chosen_accent,
                title=title,
                kicker=kicker,
            )
            self._st.markdown(header, unsafe_allow_html=True)

            cols = create_columns(self._st, len(steps))
            for idx, (col, (step_label, _)) in enumerate(zip(cols, steps)):
                with col:
                    is_active = idx == active_idx
                    if self._button(
                        f"{idx + 1} · {step_label}",
                        key=f"{state_key}_tab_{idx}",
                        button_type="primary" if is_active else "secondary",
                        full_width=True,
                    ):
                        if session_state is not None:
                            session_state[state_key] = idx
                        if hasattr(self._st, "rerun"):
                            self._st.rerun()
                        active_idx = idx

            self._st.markdown('<hr class="pyst-divider">', unsafe_allow_html=True)
            _, content = steps[active_idx]
            self._render_content(
                content,
                accent_color=chosen_accent,
                escape_html=escape_html,
                boxed=False,
            )

        return active_idx

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
    ) -> Literal["left", "right"]:
        """Alterna dinamicamente entre dois cenários (ex.: Antes vs Depois) no mesmo card."""
        self._compare_counter += 1
        state_key = f"pyst_compare_{key}" if key else f"pyst_compare_{self._compare_counter}"
        chosen_accent = accent_color or self._next_accent_color()

        session_state = getattr(self._st, "session_state", None)
        if session_state is not None and state_key not in session_state:
            session_state[state_key] = default_side

        active_side: Literal["left", "right"] = (
            "right"
            if (session_state is not None and session_state.get(state_key) == "right")
            else ("left" if session_state is not None else default_side)
        )

        with create_container(self._st, border=True):
            header = self._build_header_markup(
                "pyst-compare-marker",
                accent_color=chosen_accent,
                title=title,
                kicker=kicker,
            )
            self._st.markdown(header, unsafe_allow_html=True)

            left_col, right_col = create_columns(self._st, 2)
            with left_col:
                if self._button(
                    left_label,
                    key=f"{state_key}_left",
                    button_type="primary" if active_side == "left" else "secondary",
                    full_width=True,
                ):
                    if session_state is not None:
                        session_state[state_key] = "left"
                    if hasattr(self._st, "rerun"):
                        self._st.rerun()
                    active_side = "left"
            with right_col:
                if self._button(
                    right_label,
                    key=f"{state_key}_right",
                    button_type="primary" if active_side == "right" else "secondary",
                    full_width=True,
                ):
                    if session_state is not None:
                        session_state[state_key] = "right"
                    if hasattr(self._st, "rerun"):
                        self._st.rerun()
                    active_side = "right"

            self._st.markdown('<hr class="pyst-divider">', unsafe_allow_html=True)
            chosen_content = left_content if active_side == "left" else right_content
            self._render_content(
                chosen_content,
                accent_color=chosen_accent,
                escape_html=escape_html,
                boxed=False,
            )

        return active_side

    def checklist(
        self,
        items: Sequence[str],
        *,
        title: str | None = "Checklist de Prontidão",
        kicker: str | None = "Autoavaliação",
        default_checked: Sequence[bool] | None = None,
        accent_color: str | None = None,
        key: str | None = None,
    ) -> list[bool]:
        """Renderiza uma lista de verificação interativa com barra de progresso editorial."""
        if not items:
            raise ValueError("`checklist` precisa de pelo menos um item.")

        self._checklist_counter += 1
        state_key = f"pyst_check_{key}" if key else f"pyst_check_{self._checklist_counter}"
        chosen_accent = accent_color or self._next_accent_color()

        with create_container(self._st, border=True):
            header = self._build_header_markup(
                "pyst-checklist-marker",
                accent_color=chosen_accent,
                title=title,
                kicker=kicker,
            )
            self._st.markdown(header, unsafe_allow_html=True)

            states: list[bool] = []
            for idx, item in enumerate(items):
                initial = bool(default_checked[idx]) if default_checked and idx < len(default_checked) else False
                states.append(self._checkbox(item, value=initial, key=f"{state_key}_item_{idx}"))

            done_count = sum(1 for s in states if s)
            total = len(items)
            pct = int(round((done_count / total) * 100))
            self._st.markdown(
                f'<div class="pyst-checklist-footer">'
                f"<span><strong>{done_count}</strong> de <strong>{total}</strong> itens concluídos ({pct}%)</span>"
                f'<div class="pyst-progress-track">'
                f'<div class="pyst-progress-fill" style="width: {pct}%; background-color: {chosen_accent};"></div>'
                f"</div></div>",
                unsafe_allow_html=True,
            )

        return states
