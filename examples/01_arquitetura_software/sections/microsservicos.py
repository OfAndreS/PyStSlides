"""Seção modular de implementação de microsserviços."""

from __future__ import annotations

from pystslides import Presentation, SlideSection


class MicroservicesPracticeSection(SlideSection):
    """Demonstra código, saída e tabela comparativa em uma seção isolada."""

    title = "Implementação e Comparativo Arquitetural"

    def render(self, presentation: Presentation) -> None:
        presentation.subtopic("Contrato de evento em Python")
        presentation.paragraph(
            "Usar dataclasses imutáveis garante contratos explícitos entre serviços "
            "produtores e consumidores, facilitando validação e versionamento."
        )
        presentation.code_block(
            """
            from dataclasses import dataclass
            from datetime import datetime, timezone

            @dataclass(frozen=True)
            class OrderCreatedEvent:
                order_id: str
                customer_id: str
                total_amount: float
                created_at: str = datetime.now(timezone.utc).isoformat()

            event = OrderCreatedEvent(
                order_id="ORD-2026-01",
                customer_id="USR-88",
                total_amount=249.90,
            )
            print(event)
            """,
            language="python",
            output="OrderCreatedEvent(order_id='ORD-2026-01', customer_id='USR-88', total_amount=249.9)",
        )

        presentation.subtopic("Monólito Modular vs Microsserviços")
        presentation.paragraph(
            "A escolha arquitetural deve equilibrar autonomia das equipes com o custo "
            "operacional de observabilidade, deploy e comunicação em rede."
        )
        presentation.styled_table(
            {
                "Critério": [
                    "Complexidade Inicial",
                    "Escalabilidade Granular",
                    "Deploy Independente",
                    "Observabilidade",
                ],
                "Monólito Modular": [
                    "Baixa — ideal para validar o domínio",
                    "Escala vertical ou réplica inteira",
                    "Pipeline único e coordenado",
                    "Simples (logs e traces locais)",
                ],
                "Microsserviços": [
                    "Alta — exige mensageria e service discovery",
                    "Escala por serviço conforme demanda",
                    "Autonomia total por squad",
                    "Requer tracing distribuído (OpenTelemetry)",
                ],
            }
        )

        presentation.reveal_card(
            prompt="Quando vale manter um Monólito Modular antes de extrair microsserviços?",
            answer=(
                "Enquanto as fronteiras de domínio ainda mudam com frequência ou o time é "
                "pequeno: você preserva deploy simples e evita latência e falhas parciais de rede."
            ),
            title="Critério de Decisão",
            kicker="Discussão",
            key="arch_decision",
        )
