"""Testes unitários para componentes de estilo, tipografia, mídia, código e dados."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pystslides.assets import AssetManager
from pystslides.components.code import CodeRenderer
from pystslides.components.data import DataRenderer, HighlightLevel, HighlightSpan, apply_highlights
from pystslides.components.media import MediaRenderer
from pystslides.components.typography import TypographyRenderer
from pystslides.config import PresentationConfig, PresentationTheme
from pystslides.numbering import SectionTracker
from pystslides.styles import StyleInjector

from tests.fakes import FakeStreamlit


class TestStyleInjector(unittest.TestCase):
    def test_inject_once_and_contains_theme_values(self) -> None:
        fake_st = FakeStreamlit()
        theme = PresentationTheme(font_family="Poppins", divider_color="#123456")
        injector = StyleInjector(theme)

        self.assertTrue(injector.inject(fake_st))
        self.assertFalse(injector.inject(fake_st))
        self.assertTrue(injector.inject(fake_st, force=True))

        css = injector.build_css()
        self.assertIn("Poppins", css)
        self.assertIn("#123456", css)
        self.assertIn(".pyst-table", css)
        self.assertIn('[data-testid="stCode"] code', css)
        # card_font_size=None herda paragraph_font_size por padrão
        self.assertIn("font-size: 25px !important;", css)

    def test_custom_code_and_card_font_sizes(self) -> None:
        theme = PresentationTheme(code_font_size="22px", card_font_size="20px")
        css = StyleInjector(theme).build_css()
        self.assertIn("font-size: 22px !important;", css)
        self.assertIn("font-size: 20px !important;", css)


class TestMediaAndCodeComponents(unittest.TestCase):
    def test_mermaid_strips_existing_fences_and_dedents(self) -> None:
        fake_st = FakeStreamlit()
        renderer = MediaRenderer(fake_st, PresentationConfig())

        block = renderer.mermaid(
            """
            ```mermaid
            graph TD
                A --> B
            ```
            """,
            caption="Fluxo simples",
        )
        self.assertEqual(block, "```mermaid\ngraph TD\n    A --> B\n```")
        self.assertEqual(len(fake_st.calls_named("container")), 1)
        self.assertEqual(fake_st.calls_named("caption")[0].args[0], "Fluxo simples")

    def test_image_gallery_supports_columns_and_captions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "a.png").write_bytes(b"a")
            (base / "b.png").write_bytes(b"b")

            fake_st = FakeStreamlit()
            renderer = MediaRenderer(fake_st, PresentationConfig(), AssetManager(base))
            renderer.image_gallery([("a.png", "Imagem A"), "b.png"], columns=2)

            images = fake_st.calls_named("image")
            self.assertEqual(len(images), 2)
            self.assertEqual(images[0].kwargs["caption"], "Imagem A")
            self.assertEqual(images[1].kwargs["caption"], "")
            self.assertEqual(len(fake_st.calls_named("columns")), 1)

    def test_code_block_dedents_and_renders_output(self) -> None:
        fake_st = FakeStreamlit()
        renderer = CodeRenderer(fake_st, PresentationConfig())

        cleaned = renderer.code_block(
            """
            x = 1 + 1
            print(x)
            """,
            output=2,
        )
        self.assertEqual(cleaned, "x = 1 + 1\nprint(x)")
        self.assertEqual(fake_st.calls_named("code")[0].args[0], "x = 1 + 1\nprint(x)")
        self.assertEqual(fake_st.calls_named("write")[0].args[0], 2)

    def test_live_code_returns_echo_context_directly(self) -> None:
        fake_st = FakeStreamlit()
        renderer = CodeRenderer(fake_st, PresentationConfig())
        with renderer.live_code(code_location="above"):
            pass
        echo_calls = fake_st.calls_named("echo")
        self.assertEqual(len(echo_calls), 1)
        self.assertEqual(echo_calls[0].kwargs["code_location"], "above")


class TestDataComponent(unittest.TestCase):
    def test_apply_highlights_resolves_overlaps_and_escapes_html(self) -> None:
        text = "Email <admin@site.com> e CPF 123"
        spans = [
            HighlightSpan.from_score(6, 22, "EMAIL", 0.90),
            HighlightSpan.from_score(7, 12, "OVERLAP", 0.40),
            HighlightSpan(29, 32, "DOC", level=HighlightLevel.MEDIUM),
        ]
        rendered = apply_highlights(text, spans)

        self.assertIn("&lt;admin@site.com&gt; [EMAIL : 0.90]", rendered)
        self.assertNotIn("OVERLAP", rendered)
        self.assertIn("123 [DOC]", rendered)

    def test_highlighted_text_supports_custom_font_size(self) -> None:
        fake_st = FakeStreamlit()
        renderer = DataRenderer(fake_st, PresentationConfig())
        card_html = renderer.highlighted_text("Texto", font_size="28px")
        self.assertIn('style="font-size: 28px !important;"', card_html)

    def test_styled_table_accepts_dict_and_list_of_dicts(self) -> None:
        fake_st = FakeStreamlit()
        renderer = DataRenderer(fake_st, PresentationConfig())

        html_table = renderer.styled_table(
            [{"Nome": "Ana", "Papel": "Engenheira"}],
            highlights={("Nome", 0): [HighlightSpan(0, 3, "PERSON", level=HighlightLevel.HIGH)]},
        )
        self.assertIn('<table class="pyst-table">', html_table)
        self.assertIn("<th>Nome</th>", html_table)
        self.assertIn("Ana [PERSON]", html_table)

    def test_styled_table_accepts_dataframe_like_object(self) -> None:
        class FakeDataFrame:
            def to_dict(self, orient: str = "list") -> dict[str, list[str]]:
                assert orient == "list"
                return {"Coluna": ["Valor"]}

        fake_st = FakeStreamlit()
        renderer = DataRenderer(fake_st, PresentationConfig())
        html_table = renderer.styled_table(FakeDataFrame())
        self.assertIn("<td>Valor</td>", html_table)


class TestTypographyComponent(unittest.TestCase):
    def test_render_toc_builds_nested_links(self) -> None:
        fake_st = FakeStreamlit()
        config = PresentationConfig(toc_title="Índice")
        tracker = SectionTracker()
        renderer = TypographyRenderer(fake_st, config, tracker)

        renderer.topic("Fundamentos")
        renderer.subtopic("Conceitos")
        toc = renderer.render_toc(location="sidebar")

        self.assertIn("### Índice", toc)
        self.assertIn("- [01 ) - Fundamentos](#pyst-01-fundamentos)", toc)
        self.assertIn("  - [1.1 ) Conceitos](#pyst-1-1-conceitos)", toc)
        self.assertEqual(len(fake_st.calls_named("sidebar.markdown")), 1)


if __name__ == "__main__":
    unittest.main()
