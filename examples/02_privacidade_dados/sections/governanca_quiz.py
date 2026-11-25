"""Seção modular interativa de governança LGPD e avaliação de privacidade."""

from __future__ import annotations

from pystslides import Presentation, SlideSection


class GovernanceQuizSection(SlideSection):
    """Combina `checklist`, `quiz` e `quiz_summary` no workshop de privacidade."""

    title = "Prontidão LGPD e Verificação"

    def render(self, presentation: Presentation) -> None:
        presentation.subtopic("Checklist de maturidade em privacidade")
        presentation.checklist(
            [
                "Inventário automatizado de bases contendo CPF, e-mail e telefone",
                "Proxy de mascaramento antes do envio para APIs externas de IA",
                "Revisão periódica de falsos positivos com limiar calibrado",
            ],
            title="Controles Essenciais",
            default_checked=[True, True, False],
            key="lgpd_checklist",
        )

        presentation.subtopic("Quiz rápido do workshop")
        presentation.quiz(
            "Para que serve o limiar de confiança (score) em detectores de PII?",
            [
                "Substituir completamente a criptografia em repouso.",
                "Equilibrar cobertura de detecção e revisão manual de possíveis falsos positivos.",
                "Compactar arquivos CSV antes do upload.",
            ],
            answer_index=1,
            explanation=(
                "Pontuações intermediárias ou baixas sinalizam casos ambíguos que merecem "
                "revisão humana antes de bloqueios automáticos."
            ),
            title="Calibração de Detectores",
            key="lgpd_quiz_score",
        )

        presentation.quiz_summary(title="Placar do Workshop LGPD")
