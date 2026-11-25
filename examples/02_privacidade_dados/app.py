"""Site de slides completo #02: Workshop de Data Discovery e Privacidade.

Execute com:
    streamlit run examples/02_privacidade_dados/app.py
"""

from __future__ import annotations

from pathlib import Path

from sections.deteccao_pii import PiiDetectionSection

from pystslides import Presentation


ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def main() -> None:
    with Presentation(
        title="Workshop Data Discovery & LGPD",
        assets_dir=ASSETS_DIR,
        auto_number=False,
        brand_label="Data Discovery",
        show_toc=True,
        toc_title="Tópicos do Workshop",
    ) as deck:
        deck.cover(
            title="Data Discovery & Governança de Dados",
            subtitle="Como detectar e anonimizar informações sensíveis em pipelines corporativos",
            author="Workshop Técnico",
            date="2026",
            image="discovery_cover.png",
            image_position="right",
        )

        deck.split_slide(
            "Amplitude de cobertura",
            "A solução deve mapear todos os ambientes da empresa, incluindo bancos de "
            "dados, pastas compartilhadas, armazenamento em nuvem e estações locais.",
            media="coverage_laptop.png",
            media_position="left",
            kicker="Cobertura",
        )

        deck.split_slide(
            "Precisão da Classificação",
            "O uso de aprendizado de máquina e reconhecimento óptico de caracteres "
            "reduz alertas falsos e melhora a detecção em documentos digitalizados.",
            media="classification_network.png",
            media_position="right",
            kicker="Classificação",
        )

        deck.split_slide(
            "Visibilidade de Acesso",
            "A governança de acesso revela quem possui permissão para abrir cada "
            "documento, permitindo medir e priorizar os riscos mais urgentes.",
            media="access_desk.png",
            media_position="left",
            kicker="Governança",
        )

        deck.split_slide(
            "Capacidade de Correção",
            "Sistemas modernos isolam arquivos, aplicam rótulos ou bloqueiam acessos "
            "automaticamente assim que detectam uma exposição.",
            media="remediation_analytics.png",
            media_position="right",
            title_bottom=True,
            kicker="Automação",
        )

        deck.topic("Pipeline de Proteção no Uso de LLMs", kicker="Privacidade")
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
