"""Testes integrados da fachada Presentation e de SlideSection."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pystslides import HighlightSpan, Presentation, PresentationTheme, SlideSection

from tests.fakes import FakeStreamlit


class _CustomSection(SlideSection):
    title = "Seção Modular"

    def render(self, presentation: Presentation) -> None:
        presentation.subtopic("Sub-tópico interno")
        presentation.paragraph("Texto dentro da seção modular.")


class TestPresentationFacade(unittest.TestCase):
    def test_context_manager_lifecycle_and_toc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cover_path = Path(tmp) / "capa.png"
            cover_path.write_bytes(b"img")

            fake_st = FakeStreamlit()
            with Presentation(
                title="Apresentação Teste",
                assets_dir=tmp,
                show_toc=True,
                st_module=fake_st,
            ) as deck:
                deck.cover(title="Capa", subtitle="Subtítulo", image="capa.png")
                deck.topic("Abertura")
                deck.paragraph("Parágrafo inicial.")
                deck.callout("Nota importante.", title="Aviso", variant="warning")
                deck.highlighted_text(
                    "CPF 123.456.789-00",
                    spans=[HighlightSpan.from_score(4, 18, "CPF", 0.95)],
                )
                deck.add_section(_CustomSection())

            self.assertEqual(len(fake_st.calls_named("set_page_config")), 1)
            self.assertEqual(len(fake_st.calls_named("columns")), 1)
            self.assertEqual(len(fake_st.calls_named("image")), 1)
            self.assertEqual(len(fake_st.calls_named("sidebar.markdown")), 1)
            self.assertEqual(
                [s.formatted_title for s in deck.sections],
                [
                    "01 ) - Abertura",
                    "02 ) - Seção Modular",
                    "2.1 ) Sub-tópico interno",
                ],
            )

    def test_editorial_cover_and_split_slide_layouts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            img_path = Path(tmp) / "ilustracao.png"
            img_path.write_bytes(b"img")

            fake_st = FakeStreamlit()
            with Presentation(
                title="Data Discovery",
                assets_dir=tmp,
                auto_number=False,
                brand_label="Data Discovery",
                st_module=fake_st,
            ) as deck:
                deck.cover(
                    title="Data Discovery",
                    date="20 Julho, 2026",
                    image="ilustracao.png",
                    image_position="right",
                )
                deck.split_slide(
                    "Amplitude de cobertura",
                    "A solução deve mapear todos os ambientes.",
                    media="ilustracao.png",
                    media_position="left",
                )
                deck.split_slide(
                    "Capacidade de Correção",
                    "Sistemas modernos aplicam medidas automáticas.",
                    media="ilustracao.png",
                    media_position="right",
                    title_bottom=True,
                )

            # 1 columns() do context manager + 1 da capa + 2 de split_slide
            self.assertEqual(len(fake_st.calls_named("columns")), 4)
            self.assertEqual(len(fake_st.calls_named("image")), 3)
            self.assertEqual(
                [s.formatted_title for s in deck.sections],
                ["Amplitude de cobertura", "Capacidade de Correção"],
            )

    def test_paginated_mode_renders_only_active_slide_and_keeps_full_toc(self) -> None:
        fake_st = FakeStreamlit()
        fake_st.session_state["pyst_slide_index"] = 1

        with Presentation(
            title="Deck Paginado",
            auto_number=False,
            brand_label="Marca",
            paginated=True,
            show_toc=True,
            st_module=fake_st,
        ) as deck:
            deck.cover(title="Slide Capa")
            deck.topic("Slide Dois")
            deck.paragraph("Texto exclusivo do slide dois.")
            deck.topic("Slide Tres")
            deck.paragraph("Texto do slide tres.")

        markdowns = [call.args[0] for call in fake_st.calls_named("markdown")]
        self.assertFalse(any("Slide Capa" in m for m in markdowns))
        self.assertTrue(any("Texto exclusivo do slide dois." in m for m in markdowns))
        self.assertFalse(any("Texto do slide tres." in m for m in markdowns))
        self.assertTrue(any("2 / 3" in m for m in markdowns))
        self.assertEqual(len(fake_st.calls_named("button")), 2)
        self.assertEqual(len(fake_st.calls_named("sidebar.button")), 2)
        self.assertEqual(
            [s.formatted_title for s in deck.sections],
            ["Slide Dois", "Slide Tres"],
        )

    def test_paginated_toc_click_and_new_slide_and_cover_without_title(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            img_path = Path(tmp) / "capa.png"
            img_path.write_bytes(b"img")
            fake_st = FakeStreamlit()
            fake_st.button_clicks.add("pyst_toc_btn_1_pyst-slide-extra")

            with Presentation(
                title="Paginado TOC",
                assets_dir=tmp,
                auto_number=False,
                brand_label="Marca",
                paginated=True,
                show_toc=True,
                st_module=fake_st,
            ) as deck:
                deck.cover(subtitle="Somente subtítulo", image="capa.png", image_position="right")
                deck.topic("Slide Principal")
                deck.new_slide()
                deck.subtopic("Slide Extra")

            self.assertEqual(fake_st.session_state["pyst_slide_index"], 2)
            self.assertEqual(len(fake_st.calls_named("rerun")), 1)
            self.assertEqual(deck.sections[1].slide_index, 2)

    def test_split_slide_and_cover_vertical_alignment_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            img_path = Path(tmp) / "ilustracao.png"
            img_path.write_bytes(b"img")

            fake_st = FakeStreamlit()
            theme = PresentationTheme(default_media_vertical_align="bottom")
            with Presentation(
                title="Alinhamento",
                assets_dir=tmp,
                auto_number=False,
                theme=theme,
                st_module=fake_st,
            ) as deck:
                deck.cover(
                    title="Capa",
                    image="ilustracao.png",
                    image_position="right",
                    image_vertical_align="center",
                )
                deck.split_slide(
                    "No Topo",
                    "Texto",
                    media="ilustracao.png",
                    media_vertical_align="top",
                )
                deck.split_slide(
                    "No Meio",
                    "Texto",
                    media="ilustracao.png",
                    media_vertical_align="center",
                )
                deck.split_slide(
                    "Embaixo pelo Tema",
                    "Texto",
                    media="ilustracao.png",
                )

            col_calls = fake_st.calls_named("columns")
            # col_calls[0] é o container central do __enter__
            self.assertEqual(col_calls[1].kwargs, {"vertical_alignment": "center"})
            self.assertEqual(col_calls[2].kwargs, {})
            self.assertEqual(col_calls[3].kwargs, {"vertical_alignment": "center"})
            self.assertEqual(col_calls[4].kwargs, {"vertical_alignment": "bottom"})

    def test_create_columns_falls_back_when_vertical_alignment_unsupported(self) -> None:
        class LegacyStreamlit(FakeStreamlit):
            def columns(self, spec):  # type: ignore[override]
                return super().columns(spec)

        legacy_st = LegacyStreamlit()
        with Presentation(title="Legacy", st_module=legacy_st) as deck:
            deck.split_slide("Titulo", "Texto", media_vertical_align="bottom")

        self.assertEqual(len(legacy_st.calls_named("columns")), 2)

    def test_reveal_card_integration_and_paginated_mode(self) -> None:
        fake_st = FakeStreamlit()
        fake_st.session_state["pyst_slide_index"] = 1
        fake_st.session_state["pyst_reveal_card_slide_2"] = True

        with Presentation(
            title="Interativo",
            auto_number=False,
            paginated=True,
            st_module=fake_st,
        ) as deck:
            deck.topic("Slide Um")
            deck.reveal_card("Pergunta 1", "Resposta 1", key="card_slide_1")
            deck.topic("Slide Dois")
            revealed = deck.reveal_card("Pergunta 2", "Resposta 2", key="card_slide_2")

        self.assertTrue(revealed)
        markdowns = [call.args[0] for call in fake_st.calls_named("markdown")]
        self.assertFalse(any("Pergunta 1" in m for m in markdowns))
        self.assertTrue(any("Pergunta 2" in m for m in markdowns))
        self.assertTrue(any("Resposta 2" in m for m in markdowns))

    def test_interactive_suite_on_presentation_facade(self) -> None:
        fake_st = FakeStreamlit()
        fake_st.session_state["pyst_quiz_q_fac_submitted"] = True
        fake_st.session_state["pyst_quiz_q_fac_correct"] = True

        with Presentation(title="Interativo Completo", auto_number=False, st_module=fake_st) as deck:
            res = deck.quiz("Pergunta?", ["A", "B"], answer_index=0, key="q_fac")
            idx = deck.step_tabs([("Etapa 1", "Conteúdo 1"), ("Etapa 2", "Conteúdo 2")], key="st_fac")
            side = deck.compare_toggle("Lado A", "A", "Lado B", "B", key="cmp_fac")
            checks = deck.checklist(["Item A"], default_checked=[True], key="chk_fac")
            summary = deck.quiz_summary()

        self.assertTrue(res)
        self.assertEqual(idx, 0)
        self.assertEqual(side, "left")
        self.assertEqual(checks, [True])
        self.assertEqual(summary, (1, 1))

    def test_border_parameter_across_facade_secondary_elements(self) -> None:
        fake_st = FakeStreamlit()
        with Presentation(title="Bordas", auto_number=False, st_module=fake_st) as deck:
            deck.callout("Nota", border="grey")
            deck.code_block("a = 1", output=1, border="grey", output_border="none")
            deck.styled_table({"Col": ["Val"]}, border="none")
            deck.highlighted_text("Texto", border="grey")
            deck.metrics([("SLA", "99%")], border="none")
            deck.mermaid("graph BT\n    A --> B", border="grey")
            deck.reveal_card("Pergunta", "Resposta", border="none", key="b_rev")

        markdowns = [call.args[0] for call in fake_st.calls_named("markdown")]
        self.assertTrue(any('class="pyst-callout pyst-border-grey"' in m for m in markdowns))
        self.assertTrue(any("pyst-code-marker pyst-border-grey" in m for m in markdowns))
        self.assertTrue(any('<table class="pyst-table pyst-border-none">' in m for m in markdowns))
        self.assertTrue(any('class="pyst-card pyst-border-grey"' in m for m in markdowns))
        self.assertTrue(any('class="pyst-metric-card pyst-border-none"' in m for m in markdowns))
        self.assertTrue(any("pyst-container-marker pyst-border-grey" in m for m in markdowns))
        self.assertTrue(any("pyst-reveal-marker pyst-border-none" in m for m in markdowns))


if __name__ == "__main__":
    unittest.main()
