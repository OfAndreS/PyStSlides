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


if __name__ == "__main__":
    unittest.main()
