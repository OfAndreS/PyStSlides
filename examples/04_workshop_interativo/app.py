"""Site de slides completo #04: Workshop Interativo (Quizzes, Stepper, Comparador e Checklist).

Execute com:
    streamlit run examples/04_workshop_interativo/app.py
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st
from sections.avaliacao_pratica import PracticeAssessmentSection
from sections.fluxo_interativo import InteractiveFlowSection

from pystslides import Presentation


ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def main() -> None:
    paginated_mode = st.sidebar.toggle("Modo paginado", value=False)
    with Presentation(
        title="Workshop Interativo — Engenharia & IA Segura",
        assets_dir=ASSETS_DIR,
        auto_number=False,
        brand_label="PyStSlides Interativo",
        paginated=paginated_mode,
        show_toc=True,
        toc_title="Roteiro Interativo",
    ) as deck:
        deck.cover(
            title="Engenharia & IA Segura na Prática",
            subtitle="Slides vivos com quizzes, fluxos por etapa, comparadores e checklists",
            author="Workshop Técnico",
            date="2026",
            image="cover_interactive.svg",
            image_position="right",
            image_vertical_align="center",
        )

        deck.split_slide(
            "Por que apresentações interativas?",
            "Em vez de slides estáticos, o público testa hipóteses, navega etapas em ritmo "
            "controlado e valida conceitos com feedback imediato.",
            media="flow_stepper.svg",
            media_position="left",
            media_vertical_align="center",
            kicker="Dinâmica",
        )

        deck.metrics(
            [
                ("Componentes Interativos", "5", "Quiz, Stepper, Compare, Checklist, Reveal"),
                ("Feedback ao Vivo", "100%", "Estado persistente por session_state"),
                ("Código Único", "Python", "Sem HTML manual ou slides duplicados"),
            ]
        )

        deck.add_section(InteractiveFlowSection())
        deck.add_section(PracticeAssessmentSection())


if __name__ == "__main__":
    main()
