"""Aplicação de exemplo demonstrando os recursos do pacote PyStSlides.

Execute com:
    streamlit run examples/demo_app.py
"""

from __future__ import annotations

from pathlib import Path

from sections.demo_section import ArchitectureDemoSection

from pystslides import Presentation, PresentationTheme


ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def main() -> None:
    theme = PresentationTheme(
        font_family="Inter",
        paragraph_font_size="22px",
        default_subtopic_spacing_px=64,
    )

    with Presentation(
        title="PyStSlides — Apresentação de Exemplo",
        page_icon="🎬",
        assets_dir=ASSETS_DIR,
        show_toc=True,
        theme=theme,
    ) as deck:
        deck.cover(
            title="PyStSlides",
            subtitle="Apresentações em código organizadas com POO sobre Streamlit",
            author="André",
            date="2026",
            image="sample_cover.svg",
            caption="Imagem de capa carregada via AssetManager",
        )

        deck.topic("Visão Geral do Pacote")
        deck.paragraph(
            "O PyStSlides elimina a repetição de HTML, CSS inline, controle manual de "
            "numeração e manipulação de caminhos de imagem em apresentações criadas "
            "com Streamlit."
        )
        deck.callout(
            "Use o sumário na barra lateral para navegar diretamente entre os tópicos.",
            title="Dica de navegação",
            variant="info",
        )

        deck.subtopic("Hierarquia automática")
        deck.paragraph(
            "Os tópicos e sub-tópicos são numerados automaticamente em múltiplos níveis, "
            "evitando duplicidades e facilitando reordenar slides."
        )

        deck.subtopic("Sub-nível detalhado", level=3)
        deck.code_block(
            """
            with Presentation(title="Minha Palestra", assets_dir="data") as deck:
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
