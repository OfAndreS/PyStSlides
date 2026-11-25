"""Exemplo de seção modularizada usando a classe abstrata `SlideSection`."""

from __future__ import annotations

from pystslides import HighlightLevel, HighlightSpan, Presentation, SlideSection


class ArchitectureDemoSection(SlideSection):
    """Demonstra diagramas Mermaid, código com saída e destaques em texto/tabela."""

    title = "Demonstração de Componentes Avançados"

    def render(self, presentation: Presentation) -> None:
        presentation.subtopic("Diagrama Mermaid automatizado")
        presentation.paragraph(
            "Os diagramas Mermaid são limpos automaticamente de indentação excedente e "
            "renderizados dentro de containers padronizados com borda."
        )
        presentation.mermaid(
            """
            graph LR
                A[SlideSection] --> B[Presentation]
                B --> C[TypographyRenderer]
                B --> D[MediaRenderer]
                B --> E[CodeRenderer]
                B --> F[DataRenderer]
            """,
            caption="Fluxo simplificado da fachada PyStSlides",
        )

        presentation.subtopic("Texto com marcações e tabela estilizada")
        presentation.paragraph(
            "Os componentes de dados são genéricos e permitem destacar intervalos "
            "de texto por nível semântico ou pontuação."
        )
        sample_text = "O cliente Eduardo Silva enviou o e-mail eduardo@exemplo.com.br."
        spans = [
            HighlightSpan.from_score(10, 23, label="PERSON", score=0.92),
            HighlightSpan(40, 62, label="EMAIL", level=HighlightLevel.INFO),
        ]
        presentation.highlighted_text(sample_text, spans=spans)

        presentation.styled_table(
            {
                "Componente": ["TypographyRenderer", "MediaRenderer", "DataRenderer", "InteractiveRenderer"],
                "Responsabilidade": [
                    "Tópicos, sub-tópicos, listas, callouts e TOC",
                    "Imagens, galerias e diagramas Mermaid em SVG",
                    "Destaques em texto, KPIs e tabelas estilizadas",
                    "Cartões de revelação interativos com session_state",
                ],
            }
        )

        presentation.subtopic("Cartão de revelação ao vivo")
        presentation.reveal_card(
            prompt="Como reutilizar seções inteiras entre apresentações diferentes?",
            answer=lambda: presentation.code_block(
                """
                class MinhaSecao(SlideSection):
                    title = "Arquitetura"
                    def render(self, deck: Presentation) -> None:
                        deck.bullets(["Modular", "Tipado", "Reutilizável"])
                """,
                language="python",
            ),
            title="Modularização com SlideSection",
            kicker="Flashcard",
            reveal_label="Revelar código",
            hide_label="Ocultar código",
            key="demo_reveal",
        )
