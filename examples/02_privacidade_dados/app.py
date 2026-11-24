"""Site de slides completo #02: Workshop de Data Discovery e Privacidade.

Execute com:
    streamlit run examples/02_privacidade_dados/app.py
"""

from __future__ import annotations

from pathlib import Path

from sections.deteccao_pii import PiiDetectionSection

from pystslides import Presentation, PresentationTheme


ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def main() -> None:
    theme = PresentationTheme(
        font_family="Inter",
        paragraph_font_size="22px",
        divider_color="#1e3a8a",
        default_subtopic_spacing_px=56,
    )

    with Presentation(
        title="Workshop Data Discovery & LGPD",
        page_icon="🛡️",
        assets_dir=ASSETS_DIR,
        show_toc=True,
        toc_title="Tópicos do Workshop",
        theme=theme,
    ) as deck:
        deck.cover(
            title="Data Discovery & Governança de Dados",
            subtitle="Como detectar e anonimizar informações sensíveis em pipelines corporativos",
            author="Workshop Técnico",
            date="2026",
            image="cover_privacy.svg",
        )

        deck.topic("Pipeline de Proteção no Uso de LLMs")
        deck.paragraph(
            "Antes que prompts contendo dados de clientes saiam da infraestrutura "
            "interna para APIs externas de Inteligência Artificial, um motor de "
            "anonimização intercepta e mascara entidades sensíveis."
        )
        deck.mermaid(
            """
            graph TD
                A[Texto do Usuário] --> B[Motor de Detecção PII]
                B -->|Dados Mascarados| C((API Externa de IA))
                C -->|Resposta Mascarada| D[Motor de Restauração]
                D -->|Resposta Final| E[Interface Interna]

                style A fill:#f8fafc,stroke:#94a3b8,color:#0f172a
                style B fill:#fef08a,stroke:#eab308,color:#854d0e
                style C fill:#e0f2fe,stroke:#0284c7,color:#0c4a6e
                style D fill:#dcfce7,stroke:#16a34a,color:#166534
                style E fill:#f8fafc,stroke:#94a3b8,color:#0f172a
            """,
            caption="Arquitetura de proxy de privacidade para modelos de linguagem.",
        )

        deck.add_section(PiiDetectionSection())


if __name__ == "__main__":
    main()
