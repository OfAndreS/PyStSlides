"""Seção modular interativa: fluxo em etapas, comparativo e flashcard com código."""

from __future__ import annotations

from pystslides import HighlightSpan, Presentation, SlideSection


class InteractiveFlowSection(SlideSection):
    """Demonstra `step_tabs`, `compare_toggle` e `reveal_card` com conteúdo dinâmico."""

    title = "Fluxo Interativo de Engenharia"

    def render(self, presentation: Presentation) -> None:
        presentation.subtopic("Pipeline em etapas selecionáveis")
        presentation.paragraph(
            "Em apresentações ao vivo, dividir fluxos extensos em abas interativas evita "
            "poluição visual e mantém o foco da audiência em um estágio por vez."
        )

        presentation.step_tabs(
            [
                (
                    "Descoberta",
                    lambda: (
                        presentation.paragraph(
                            "Mapeia tabelas, buckets e logs para localizar campos sensíveis antes "
                            "de qualquer integração externa."
                        ),
                        presentation.bullets(
                            [
                                "Conectores para PostgreSQL, S3 e Kafka",
                                "Classificação automática por contexto e regex",
                            ]
                        ),
                    ),
                ),
                (
                    "Mascaramento",
                    lambda: presentation.code_block(
                        """
                        def mask_cpf(value: str) -> str:
                            return "***.***.***-" + value[-2:]
                        """,
                        language="python",
                        output="mask_cpf('123.456.789-10') -> '***.***.***-10'",
                    ),
                ),
                (
                    "Auditoria",
                    lambda: presentation.mermaid(
                        """
                        flowchart LR
                            Proxy[Proxy PII] --> Log[Trilha Imutável]
                            Log --> Alerta[SIEM / Alertas]
                        """
                    ),
                ),
            ],
            title="Jornada de Proteção de Dados",
            kicker="Stepper",
            key="ws_pipeline",
        )

        raw_prompt = "Prompt enviado: Analisar contrato de Eduardo Silva (CPF 123.456.789-10)."
        masked_prompt = "Prompt enviado: Analisar contrato de <PERSON_01> (CPF <CPF_01>)."

        def _span(text: str, sub: str, label: str, score: float) -> HighlightSpan:
            idx = text.index(sub)
            return HighlightSpan.from_score(idx, idx + len(sub), label, score, low_threshold=0.5, high_threshold=0.75)

        presentation.subtopic("Comparativo direto de cenários")
        presentation.compare_toggle(
            "Sem Proxy de Privacidade",
            lambda: presentation.highlighted_text(
                raw_prompt,
                spans=[
                    _span(raw_prompt, "Eduardo Silva", "PERSON", 0.94),
                    _span(raw_prompt, "123.456.789-10", "CPF", 0.99),
                ],
            ),
            "Com Proxy Anonimizado",
            lambda: presentation.highlighted_text(
                masked_prompt,
                spans=[
                    _span(masked_prompt, "<PERSON_01>", "TOKEN", 0.99),
                    _span(masked_prompt, "<CPF_01>", "TOKEN", 0.99),
                ],
            ),
            title="Impacto na chamada de LLM externo",
            kicker="Antes vs Depois",
            key="ws_compare",
        )

        presentation.reveal_card(
            prompt="Como restaurar os valores originais na resposta final da IA?",
            answer=(
                "O proxy mantém um mapa efêmero em memória por requisição "
                "(`<PERSON_01>` → nome real) e substitui os tokens antes de devolver à interface interna."
            ),
            title="Restauração segura",
            kicker="Flashcard",
            key="ws_restore",
        )
