"""Seção modular de avaliação prática: questionários, checklist e placar final."""

from __future__ import annotations

from pystslides import Presentation, SlideSection


class PracticeAssessmentSection(SlideSection):
    """Demonstra `quiz`, `checklist` e `quiz_summary` com ilustração editorial."""

    title = "Avaliação Prática e Prontidão"

    def render(self, presentation: Presentation) -> None:
        presentation.split_slide(
            "Verificação Contínua",
            "Questionários rápidos e checklists em tempo real transformam palestras e "
            "workshops técnicos em sessões participativas.",
            media="quiz_diagram.svg",
            media_position="right",
            media_vertical_align="center",
            kicker="Interatividade",
        )

        presentation.subtopic("Check-in de conhecimento")
        presentation.quiz(
            "Qual é o principal risco de compartilhar o mesmo banco relacional entre dois microsserviços?",
            [
                "Aumentar o uso de memória RAM no navegador do cliente.",
                "Gerar acoplamento forte de esquema, impedindo deploys e evoluções independentes.",
                "Impedir o uso de JSON em APIs REST.",
            ],
            answer_index=1,
            explanation=(
                "Alterações de coluna ou índice passam a exigir coordenação entre equipes, "
                "anulando a autonomia de entrega."
            ),
            title="Questão 01 — Fronteiras de Dados",
            key="ws_q1",
        )

        presentation.quiz(
            "Em um pipeline de proxy de privacidade para LLMs, quando as entidades PII devem ser restauradas?",
            [
                "Antes de enviar o prompt para o modelo externo.",
                "Apenas no retorno da API externa, dentro da rede interna confiável.",
                "Nunca; os tokens devem ficar permanentes no banco de auditoria.",
            ],
            answer_index=1,
            explanation=(
                "O modelo externo processa apenas tokens sintéticos; a restauração ocorre "
                "exclusivamente na borda interna antes de exibir ao usuário."
            ),
            title="Questão 02 — Proxy de LLMs",
            key="ws_q2",
        )

        presentation.subtopic("Autoavaliação do time")
        presentation.checklist(
            [
                "Catálogo atualizado de dados sensíveis (PII) em produção",
                "Contratos versionados e testados entre produtores e consumidores",
                "Mascaramento automático em logs e prompts de IA",
                "Alertas com triagem e runbooks vinculados",
            ],
            title="Checklist de Prontidão para Produção",
            default_checked=[True, True, False, False],
            key="ws_ready",
        )

        presentation.quiz_summary(title="Placar Consolidado do Workshop")
