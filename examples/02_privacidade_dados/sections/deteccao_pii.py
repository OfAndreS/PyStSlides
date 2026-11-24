"""Seção modular de demonstração de detecção e mascaramento de PII."""

from __future__ import annotations

from pystslides import HighlightLevel, HighlightSpan, Presentation, SlideSection


class PiiDetectionSection(SlideSection):
    """Mostra marcação de spans em texto livre, tabelas e código ao vivo."""

    title = "Detecção Visual em Textos e Tabelas"

    def render(self, presentation: Presentation) -> None:
        presentation.subtopic("Classificação por nível de confiança")
        presentation.paragraph(
            "O componente highlighted_text permite inspecionar rapidamente cada entidade "
            "detectada, colorindo automaticamente conforme a pontuação de confiança."
        )

        email_sample = (
            "Olá RH, sou Eduardo Pereira Silva de Curitiba. "
            "Meu telefone é (41) 98765-1234, e-mail eduardo@empresa.com.br "
            "e CPF 123.456.789-10. Código interno da catraca: 1234 5678."
        )
        def span_for(substring: str, label: str, score: float) -> HighlightSpan:
            start = email_sample.index(substring)
            return HighlightSpan.from_score(start, start + len(substring), label, score)

        spans = [
            span_for("Eduardo Pereira Silva", "PERSON", 0.94),
            span_for("Curitiba", "LOCATION", 0.72),
            span_for("(41) 98765-1234", "PHONE_NUMBER", 0.89),
            span_for("eduardo@empresa.com.br", "EMAIL_ADDRESS", 0.99),
            span_for("123.456.789-10", "CPF", 0.95),
            span_for("1234 5678", "POSSIBLE_ID", 0.41),
        ]
        presentation.highlighted_text(email_sample, spans=spans)

        presentation.callout(
            "Pontuações abaixo de 0.50 (vermelho) ajudam a identificar possíveis falsos "
            "positivos antes de aplicar bloqueios automáticos em produção.",
            title="Atenção a Falsos Positivos",
            variant="warning",
        )

        presentation.subtopic("Varredura em bases tabulares (CSV)")
        presentation.paragraph(
            "A mesma lógica de HighlightSpan pode ser aplicada célula por célula "
            "em relatórios tabulares usando styled_table."
        )

        rows = {
            "Colaborador": ["Mariana Costa", "Rafael Mendes", "Beatriz Lima"],
            "Contato": [
                "mariana@acme.com",
                "(11) 99876-5432",
                "beatriz@acme.com",
            ],
            "Documento": ["321.654.987-00", "456.789.123-45", "Não informado"],
            "Departamento": ["Financeiro", "Engenharia", "Jurídico"],
        }
        cell_highlights = {
            ("Colaborador", 0): [HighlightSpan(0, 13, "PERSON", level=HighlightLevel.HIGH)],
            ("Colaborador", 1): [HighlightSpan(0, 13, "PERSON", level=HighlightLevel.HIGH)],
            ("Colaborador", 2): [HighlightSpan(0, 12, "PERSON", level=HighlightLevel.HIGH)],
            ("Contato", 0): [HighlightSpan.from_score(0, 16, "EMAIL", 0.98)],
            ("Contato", 1): [HighlightSpan.from_score(0, 15, "PHONE", 0.86)],
            ("Contato", 2): [HighlightSpan.from_score(0, 16, "EMAIL", 0.98)],
            ("Documento", 0): [HighlightSpan.from_score(0, 14, "CPF", 0.95)],
            ("Documento", 1): [HighlightSpan.from_score(0, 14, "CPF", 0.95)],
        }
        presentation.styled_table(rows, highlights=cell_highlights)

        presentation.subtopic("Mascaramento demonstrado ao vivo")
        with presentation.live_code():
            import re

            texto = "Documento enviado: 123.456.789-10"
            mascarado = re.sub(r"\d{3}\.\d{3}\.\d{3}-\d{2}", "***.***.***-**", texto)

        presentation.output_box(
            f"**Original:** `{texto}`",
            f"**Protegido:** `{mascarado}`",
            as_markdown=True,
        )
