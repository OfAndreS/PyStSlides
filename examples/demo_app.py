"""Aplicação de exemplo demonstrando os recursos do pacote PyStSlides.

Execute com:
    streamlit run examples/demo_app.py
"""

from __future__ import annotations

import streamlit as st
from sections.demo_section import ArchitectureDemoSection

from pystslides import Presentation, get_editorial_assets_dir


ASSETS_DIR = get_editorial_assets_dir()


def main() -> None:
    paginated_mode = st.sidebar.toggle("Modo paginado", value=False)
    with Presentation(
        title="PyStSlides — Apresentação de Exemplo",
        assets_dir=ASSETS_DIR,
        auto_number=False,
        brand_label="PyStSlides",
        paginated=paginated_mode,
        show_toc=True,
    ) as deck:
        deck.cover(
            title="PyStSlides",
            subtitle="Apresentações em código organizadas com POO sobre Streamlit",
            author="André",
            date="2026",
            image="discovery_analytics.svg",
            image_position="right",
        )

        deck.split_slide(
            "Visão Geral do Pacote",
            "O PyStSlides elimina a repetição de HTML, CSS inline, controle manual de "
            "numeração e manipulação de caminhos de imagem em apresentações criadas "
            "com Streamlit.",
            media="coverage_workspace.svg",
            media_position="left",
            kicker="Visão Geral",
        )
        deck.split_slide(
            "Composição Editorial",
            "Combine texto alinhado à esquerda, ilustrações flat e alternância de "
            "colunas com ou sem título invertido.",
            media="remediation_automation.svg",
            media_position="right",
            title_bottom=True,
            kicker="Layout",
        )
        deck.callout(
            "Use o sumário na barra lateral para navegar diretamente entre os tópicos.",
            title="Navegação",
            variant="info",
        )

        deck.topic("Hierarquia e Estrutura", kicker="Estrutura")
        deck.paragraph(
            "Os tópicos e sub-tópicos suportam numeração automática ou títulos editoriais "
            "limpos, facilitando reordenar slides sem quebrar a apresentação."
        )
        deck.bullets(
            [
                "Tipografia editorial configurada em um único tema (`PresentationTheme`).",
                "Sumário lateral com navegação direta mesmo no modo paginado.",
                "Componentes interativos como cartões de revelação (`reveal_card`).",
            ]
        )

        deck.subtopic("Exemplo de código em bloco")
        deck.code_block(
            """
            with Presentation(title="Minha Palestra", brand_label="Palestra") as deck:
                deck.topic("Introdução")
                deck.paragraph("Conteúdo limpo e padronizado.")
            """,
            language="python",
            output="Apresentação renderizada com sucesso!",
        )

        # Modularização via classe SlideSection
        deck.add_section(ArchitectureDemoSection())


if __name__ == "__main__":
    main()
