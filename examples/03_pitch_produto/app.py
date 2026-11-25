"""Site de slides completo #03: Pitch Executivo de Produto SaaS.

Execute com:
    streamlit run examples/03_pitch_produto/app.py
"""

from __future__ import annotations

from pathlib import Path

from pystslides import Presentation


ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def main() -> None:
    with Presentation(
        title="PulseOps AI — Pitch Executivo",
        assets_dir=ASSETS_DIR,
        auto_number=False,
        brand_label="PulseOps AI",
        show_toc=True,
        toc_title="Roteiro do Pitch",
    ) as deck:
        deck.cover(
            title="PulseOps AI",
            subtitle="Observabilidade preditiva para times de engenharia modernos",
            author="Apresentação Comercial",
            date="2026",
            image="cover_pitch.svg",
            image_position="right",
        )

        deck.topic("O Desafio da Operação em Escala", kicker="Contexto")
        deck.paragraph(
            "Times de SRE recebem milhares de alertas por semana, mas menos de 15% "
            "exigem intervenção humana real. O PulseOps AI correlaciona métricas, logs "
            "e histórico de deploys para apontar o problema antes da indisponibilidade."
        )
        deck.callout(
            "Clientes piloto reduziram o tempo médio de recuperação (MTTR) de 42 minutos "
            "para menos de 7 minutos nos primeiros 60 dias de adoção.",
            title="Resultados em piloto",
            variant="success",
        )
        deck.metrics(
            [
                ("MTTR Médio", "< 7 min", "Antes: 42 min em produção"),
                ("Ruído de Alertas", "-85%", "Triagem automática por deploy"),
                ("SLA Garantido", "99.99%", "Cobertura contínua multi-região"),
            ]
        )

        deck.topic("Principais Recursos da Plataforma", kicker="Plataforma")
        deck.image_gallery(
            [
                ("feat_dashboard.svg", "Detecção preditiva de anomalias"),
                ("feat_alerts.svg", "Triagem inteligente e correlação de deploys"),
            ],
            columns=2,
            bordered=True,
        )

        deck.topic("Planos e Roadmap de Evolução", kicker="Planos & Roadmap")
        deck.subtopic("Comparativo de planos")
        deck.styled_table(
            {
                "Recurso": [
                    "Serviços Monitorados",
                    "Correlação com Deploys",
                    "Retenção de Métricas",
                    "SLA Dedicado",
                ],
                "Starter": ["Até 15", "Incluso", "30 dias", "Comercial"],
                "Growth": ["Até 100", "Incluso + IA", "90 dias", "99.9%"],
                "Enterprise": ["Ilimitado", "Customizado", "365 dias", "99.99% + 24/7"],
            }
        )

        deck.subtopic("Roadmap 2026")
        deck.mermaid(
            """
            flowchart LR
                Q1[Q1: Core Telemetry] --> Q2[Q2: Predictive Alerts]
                Q2 --> Q3[Q3: Auto-Runbooks]
                Q3 --> Q4[Q4: Multi-Cloud FinOps]

                style Q1 fill:#dcfce7,stroke:#16a34a,color:#166534
                style Q2 fill:#dcfce7,stroke:#16a34a,color:#166534
                style Q3 fill:#e0e7ff,stroke:#4f46e5,color:#312e81
                style Q4 fill:#f1f5f9,stroke:#64748b,color:#334155
            """,
            caption="Marcos planejados para o ciclo anual de produto.",
        )


if __name__ == "__main__":
    main()
