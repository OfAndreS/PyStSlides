"""Seção modular interativa de resiliência em arquiteturas distribuídas."""

from __future__ import annotations

from pystslides import Presentation, SlideSection


class ResilienceInteractiveSection(SlideSection):
    """Demonstra `step_tabs`, `compare_toggle` e `quiz` sobre resiliência."""

    title = "Resiliência Interativa na Prática"

    def render(self, presentation: Presentation) -> None:
        presentation.subtopic("Mecanismos de proteção por etapa")
        presentation.step_tabs(
            [
                (
                    "Retry com Jitter",
                    "Repete falhas transitórias com backoff exponencial e jitter aleatório "
                    "para evitar tempestades de requisições simultâneas.",
                ),
                (
                    "Circuit Breaker",
                    "Interrompe chamadas para dependências degradadas, retornando fallback "
                    "rápido até que o serviço volte a responder.",
                ),
                (
                    "Dead Letter Queue",
                    "Encaminha eventos que excederam tentativas para uma fila isolada, "
                    "permitindo inspeção e reprocessamento seguro.",
                ),
            ],
            title="Tríade de Resiliência",
            kicker="Padrões",
            key="arch_resilience_steps",
        )

        presentation.subtopic("Síncrono vs. Orientado a Eventos")
        presentation.compare_toggle(
            "Chamada Síncrona (HTTP)",
            "Latência somada em cadeia e disponibilidade acoplada entre todos os serviços do fluxo.",
            "Barramento Assíncrono (Eventos)",
            "Produtor publica o evento e segue operando mesmo que consumidores estejam temporariamente lentos.",
            title="Trade-off de Comunicação",
            key="arch_sync_async",
        )

        presentation.quiz(
            "Qual componente evita sobrecarregar um serviço de faturamento que já está fora do ar?",
            [
                "Aumentar o timeout para 60 segundos.",
                "Circuit Breaker abrindo o circuito após falhas consecutivas.",
                "Remover chaves estrangeiras do banco de pedidos.",
            ],
            answer_index=1,
            explanation="O Circuit Breaker falha rápido localmente e protege o serviço degradado.",
            title="Check-in de Resiliência",
            key="arch_quiz",
        )
