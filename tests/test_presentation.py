"""Testes integrados da fachada Presentation e de SlideSection."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pystslides import HighlightSpan, Presentation, SlideSection

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
        self.assertEqual(
            [s.formatted_title for s in deck.sections],
            ["Slide Dois", "Slide Tres"],
        )


if __name__ == "__main__":
    unittest.main()
