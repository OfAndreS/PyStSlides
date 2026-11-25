"""Site de slides completo #01: Apresentação Técnica de Arquitetura de Software.

Execute com:
    streamlit run examples/01_arquitetura_software/app.py
"""

from __future__ import annotations

from pathlib import Path

from sections.microsservicos import MicroservicesPracticeSection
from sections.resiliencia_interativa import ResilienceInteractiveSection

from pystslides import Presentation


ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def main() -> None:
    with Presentation(
        title="Arquitetura de Microsserviços",
        assets_dir=ASSETS_DIR,
        auto_number=False,
        brand_label="Arquitetura de Software",
        show_toc=True,
        toc_title="Navegação",
    ) as deck:
        deck.cover(
            title="Arquitetura de Microsserviços na Prática",
            subtitle="Padrões de resiliência, mensageria e evolução incremental",
            author="Equipe de Engenharia",
            date="2026",
            image="cover_arch.svg",
            image_position="right",
        )

        deck.topic("Fluxo de Requisições e Desacoplamento", kicker="Topologia")
        deck.paragraph(
            "Em arquiteturas distribuídas, o API Gateway centraliza autenticação, "
            "rate limiting e roteamento, enquanto o barramento de eventos permite "
            "que cada domínio evolua sem acoplamento temporal."
        )
        deck.mermaid(
            """
            graph LR
                Client[Cliente Web / Mobile] --> GW[API Gateway]
                GW --> Orders[Serviço de Pedidos]
                GW --> Catalog[Serviço de Catálogo]
                Orders -->|OrderCreated| Broker((Event Broker))
                Broker --> Billing[Faturamento]
                Broker --> Notify[Notificações]

                style GW fill:#e0f2fe,stroke:#0284c7,color:#0c4a6e
                style Broker fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
                style Billing fill:#dcfce7,stroke:#16a34a,color:#14532d
                style Notify fill:#fef3c7,stroke:#d97706,color:#78350f
            """,
            caption="Comunicação síncrona na borda e assíncrona entre domínios.",
        )

        deck.callout(
            "Defina fronteiras claras de domínio (Bounded Contexts) "
            "antes de separar repositórios e bancos de dados.",
            title="Fronteiras de domínio",
            variant="info",
        )

        deck.topic("Padrões Fundamentais", kicker="Padrões")
        deck.paragraph(
            "Dois padrões frequentemente combinados em sistemas de alta escala são "
            "a separação entre escrita/leitura (CQRS) e a comunicação orientada a eventos."
        )
        deck.image_gallery(
            [
                ("card_cqrs.svg", "Padrão CQRS — escalando leituras e escritas"),
                ("card_events.svg", "Event-Driven — desacoplamento via broker"),
            ],
            columns=2,
            bordered=True,
        )

        deck.add_section(MicroservicesPracticeSection())
        deck.add_section(ResilienceInteractiveSection())


if __name__ == "__main__":
    main()
