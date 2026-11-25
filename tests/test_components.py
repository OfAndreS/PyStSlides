"""Testes unitários para componentes de estilo, tipografia, mídia, código e dados."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pystslides.assets import AssetManager
from pystslides.components.code import CodeRenderer
from pystslides.components.data import DataRenderer, HighlightLevel, HighlightSpan, apply_highlights
from pystslides.components.interactive import InteractiveRenderer
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
        # card_font_size=None herda paragraph_font_size por padrão (24px)
        self.assertIn("font-size: 24px !important;", css)

    def test_default_editorial_theme_values_and_css(self) -> None:
        css = StyleInjector(PresentationTheme()).build_css()
        self.assertIn("DM Sans", css)
        self.assertIn("color-scheme: light !important;", css)
        self.assertIn("background-color: #ffffff !important;", css)
        self.assertIn("font-size: 76px !important;", css)
        self.assertIn("font-size: 54px !important;", css)
        self.assertIn("letter-spacing: -0.03em !important;", css)
        self.assertIn("text-align: left !important;", css)
        self.assertIn("max-width: 62ch !important;", css)
        self.assertIn('[data-testid="stToolbar"]', css)

    def test_custom_code_and_card_font_sizes(self) -> None:
        theme = PresentationTheme(code_font_size="22px", card_font_size="20px", table_rounded=False)
        css = StyleInjector(theme).build_css()
        self.assertIn("font-size: 22px !important;", css)
        self.assertIn("font-size: 20px !important;", css)
        self.assertIn("border-collapse: collapse !important;", css)

    def test_editorial_secondary_styles_in_default_css(self) -> None:
        css = StyleInjector(PresentationTheme()).build_css()
        self.assertIn("border-collapse: separate !important;", css)
        self.assertIn("border-radius: 12px !important;", css)
        self.assertIn("border: 1.5px solid #000000 !important;", css)
        self.assertIn("border-bottom: 1.5px solid #000000 !important;", css)
        self.assertIn("font-size: 18px !important;", css)
        self.assertIn(".pyst-mark {", css)
        self.assertIn(".pyst-reveal-marker", css)
        self.assertIn(".pyst-reveal-answer", css)
        self.assertIn(".pyst-bullets", css)
        self.assertIn(".pyst-metrics-grid", css)
        self.assertIn(".pyst-pagination-marker", css)

    def test_theme_presets(self) -> None:
        editorial = PresentationTheme.editorial()
        compact = PresentationTheme.compact()
        classic = PresentationTheme.classic()

        self.assertEqual(editorial.topic_font_size, "54px")
        self.assertEqual(editorial.default_border, "black")
        self.assertEqual(compact.paragraph_font_size, "20px")
        self.assertTrue(classic.topic_dividers)
        self.assertFalse(classic.callout_minimal)
        self.assertFalse(classic.table_rounded)

    def test_border_styles_css_and_theme_default_border(self) -> None:
        default_css = StyleInjector(PresentationTheme()).build_css()
        self.assertIn('[data-testid="stCode"]', default_css)
        self.assertIn(".pyst-table.pyst-border-grey", default_css)
        self.assertIn(".pyst-table.pyst-border-none", default_css)
        self.assertIn(".pyst-code-marker.pyst-border-grey", default_css)
        self.assertIn(".pyst-container-marker.pyst-border-black", default_css)
        self.assertIn("1px solid #d6d6d9 !important;", default_css)

        grey_css = StyleInjector(PresentationTheme(default_border="grey")).build_css()
        self.assertIn("border: 1px solid #d6d6d9 !important;", grey_css)

        none_css = StyleInjector(PresentationTheme(default_border="none")).build_css()
        self.assertIn("table.pyst-table {\n    width: 100% !important;", none_css)
        self.assertIn("border: none !important;", none_css)


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

    def test_mermaid_vertical_detection_height_and_borders(self) -> None:
        class FakeComponentsV1:
            def __init__(self) -> None:
                self.calls: list[tuple[str, dict[str, object]]] = []

            def html(self, doc: str, **kwargs: object) -> None:
                self.calls.append((doc, kwargs))

        class FakeComponents:
            def __init__(self) -> None:
                self.v1 = FakeComponentsV1()

        fake_st = FakeStreamlit()
        fake_st.components = FakeComponents()  # type: ignore[attr-defined]
        renderer = MediaRenderer(fake_st, PresentationConfig())

        # LR com rótulos contendo TD/BT não deve ser tratado como vertical
        self.assertFalse(renderer._is_vertical_mermaid("graph LR\n    BTN[Botão] --> HTTP_TD[Endpoint]"))
        self.assertTrue(renderer._is_vertical_mermaid("flowchart TD\n    A --> B"))
        self.assertTrue(renderer._is_vertical_mermaid("graph bt\n    A --> B"))

        # Diagrama TD curto não fica preso no antigo piso de 580px
        renderer.mermaid("graph TD\n    A --> B", border="grey")
        # Diagrama BT longo ultrapassa o antigo teto de 780px
        long_bt = "flowchart BT\n" + "\n".join(f"    N{i} --> N{i + 1}" for i in range(10))
        renderer.mermaid(long_bt, border="none")
        # Altura explícita desativa autoHeight no JS
        renderer.mermaid("graph LR\n    A --> B", height=320)

        calls = fake_st.components.v1.calls  # type: ignore[attr-defined]
        self.assertEqual(len(calls), 3)
        short_doc, short_kw = calls[0]
        long_doc, long_kw = calls[1]
        fixed_doc, fixed_kw = calls[2]

        self.assertLess(int(short_kw["height"]), 580)  # type: ignore[arg-type]
        self.assertGreater(int(long_kw["height"]), 780)  # type: ignore[arg-type]
        self.assertEqual(fixed_kw["height"], 320)
        self.assertIn("const autoHeight = true;", short_doc)
        self.assertIn("const autoHeight = false;", fixed_doc)
        self.assertIn("ResizeObserver", short_doc)
        self.assertIn("MutationObserver", short_doc)

        markdowns = [call.args[0] for call in fake_st.calls_named("markdown")]
        self.assertTrue(any("pyst-container-marker pyst-border-grey" in m for m in markdowns))
        self.assertFalse(any("pyst-border-none" in m for m in markdowns))

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
        markdowns = [call.args[0] for call in fake_st.calls_named("markdown")]
        self.assertTrue(any("pyst-code-marker pyst-border-black" in m for m in markdowns))
        self.assertTrue(any("pyst-container-marker pyst-border-black" in m for m in markdowns))

    def test_code_and_data_border_variants_and_validation(self) -> None:
        fake_st = FakeStreamlit()
        code_renderer = CodeRenderer(fake_st, PresentationConfig())
        data_renderer = DataRenderer(fake_st, PresentationConfig())

        code_renderer.code_block("x = 1", output=1, border="grey", output_border="none")
        code_renderer.output_box("ok", border="grey")

        table_grey = data_renderer.styled_table({"A": [1]}, border="grey")
        table_none = data_renderer.styled_table({"A": [1]}, border="none")
        card_none = data_renderer.highlighted_text("Texto", border="none")
        metrics_grey = data_renderer.metrics([("KPI", "10")], border="grey")

        self.assertIn('class="pyst-table pyst-border-grey"', table_grey)
        self.assertIn('class="pyst-table pyst-border-none"', table_none)
        self.assertIn('class="pyst-card pyst-border-none"', card_none)
        self.assertIn('class="pyst-metric-card pyst-border-grey"', metrics_grey)

        markdowns = [call.args[0] for call in fake_st.calls_named("markdown")]
        self.assertTrue(any("pyst-code-marker pyst-border-grey" in m for m in markdowns))
        self.assertTrue(any("pyst-container-marker pyst-border-grey" in m for m in markdowns))

        with self.assertRaises(ValueError):
            data_renderer.styled_table({"A": [1]}, border="red")  # type: ignore[arg-type]

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

        self.assertIn('&lt;admin@site.com&gt;<span class="pyst-mark-badge">EMAIL · 0.90</span>', rendered)
        self.assertNotIn("OVERLAP", rendered)
        self.assertIn('123<span class="pyst-mark-badge">DOC</span>', rendered)
        self.assertIn('class="pyst-mark"', rendered)

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
        self.assertIn('Ana<span class="pyst-mark-badge">PERSON</span>', html_table)

    def test_styled_table_accepts_dataframe_like_object(self) -> None:
        class FakeDataFrame:
            def to_dict(self, orient: str = "list") -> dict[str, list[str]]:
                assert orient == "list"
                return {"Coluna": ["Valor"]}

        fake_st = FakeStreamlit()
        renderer = DataRenderer(fake_st, PresentationConfig())
        html_table = renderer.styled_table(FakeDataFrame())
        self.assertIn("<td>Valor</td>", html_table)

    def test_metrics_renders_cards_with_accents(self) -> None:
        fake_st = FakeStreamlit()
        renderer = DataRenderer(fake_st, PresentationConfig())
        grid_html = renderer.metrics(
            [
                ("MTTR", "< 7 min", "Piloto"),
                ("SLA", "99.99%"),
            ]
        )
        self.assertIn('class="pyst-metrics-grid"', grid_html)
        self.assertIn("MTTR", grid_html)
        self.assertIn("&lt; 7 min", grid_html)
        self.assertIn("Piloto", grid_html)


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

    def test_kicker_rotates_accent_colors_and_topic_renders_clean_heading(self) -> None:
        fake_st = FakeStreamlit()
        config = PresentationConfig(
            brand_label="Data Discovery",
            repeat_brand_kicker=True,
            auto_number=False,
        )
        tracker = SectionTracker(auto_number=False)
        renderer = TypographyRenderer(fake_st, config, tracker)

        renderer.topic("Amplitude de cobertura")
        renderer.topic("Precisão da Classificação")
        renderer.callout("Texto limpo.", title="Nota", variant="info")

        markdowns = [call.args[0] for call in fake_st.calls_named("markdown")]
        self.assertTrue(any("#3f7bde" in m and "Data Discovery" in m for m in markdowns))
        self.assertTrue(any("#579568" in m and "Data Discovery" in m for m in markdowns))
        self.assertTrue(any('<h1 class="pyst-topic-title">Amplitude de cobertura</h1>' == m for m in markdowns))
        self.assertTrue(any('class="pyst-callout-icon"' in m and "<svg" in m for m in markdowns))
        self.assertFalse(any('<hr class="pyst-divider">' in m for m in markdowns))

    def test_bullets_and_callout_escape_html(self) -> None:
        fake_st = FakeStreamlit()
        renderer = TypographyRenderer(fake_st, PresentationConfig(), SectionTracker())
        renderer.bullets(["Primeiro <b>item</b>", "Segundo"], marker="dot")
        renderer.callout("Use <code>reveal_card</code>", escape_html=False)

        markdowns = [call.args[0] for call in fake_st.calls_named("markdown")]
        self.assertTrue(any('class="pyst-bullets"' in m and "Primeiro <b>item</b>" in m for m in markdowns))
        self.assertTrue(any('class="pyst-bullet-dot"' in m for m in markdowns))
        self.assertTrue(any("<code>reveal_card</code>" in m for m in markdowns))


class TestInteractiveComponent(unittest.TestCase):
    def test_reveal_card_hides_answer_until_toggled(self) -> None:
        fake_st = FakeStreamlit()
        renderer = InteractiveRenderer(fake_st, PresentationConfig())

        opened = renderer.reveal_card(
            "Pergunta inicial",
            "Resposta secreta",
            title="Flashcard",
            kicker="Arquitetura",
            key="card_1",
        )

        self.assertFalse(opened)
        self.assertFalse(fake_st.session_state["pyst_reveal_card_1"])
        markdowns = [call.args[0] for call in fake_st.calls_named("markdown")]
        self.assertTrue(any("Pergunta inicial" in m and "pyst-reveal-marker" in m for m in markdowns))
        self.assertFalse(any("Resposta secreta" in m for m in markdowns))
        self.assertEqual(fake_st.calls_named("button")[0].args[0], "Revelar resposta")

        fake_st.button_clicks.add("pyst_reveal_card_1_btn")
        toggled = renderer.reveal_card(
            "Pergunta inicial",
            "Resposta secreta",
            key="card_1",
        )
        self.assertTrue(toggled)
        self.assertTrue(fake_st.session_state["pyst_reveal_card_1"])
        self.assertEqual(len(fake_st.calls_named("rerun")), 1)

    def test_reveal_card_renders_sequence_callable_and_escapes_html(self) -> None:
        fake_st = FakeStreamlit()
        renderer = InteractiveRenderer(fake_st, PresentationConfig())

        opened = renderer.reveal_card(
            "Qual <tag>?",
            ["Linha <b>1</b>", "Linha 2"],
            initially_revealed=True,
            hide_label="Fechar",
            escape_html=True,
            key="seq",
        )
        self.assertTrue(opened)
        markdowns = [call.args[0] for call in fake_st.calls_named("markdown")]
        self.assertTrue(any("Qual &lt;tag&gt;?" in m for m in markdowns))
        self.assertTrue(any("Linha &lt;b&gt;1&lt;/b&gt;" in m for m in markdowns))
        self.assertEqual(fake_st.calls_named("button")[0].args[0], "Fechar")

        called = []
        renderer.reveal_card(
            "Callable?",
            lambda: called.append("ok"),
            initially_revealed=True,
            key="fn",
        )
        self.assertEqual(called, ["ok"])

    def test_quiz_submission_feedback_and_summary(self) -> None:
        fake_st = FakeStreamlit()
        renderer = InteractiveRenderer(fake_st, PresentationConfig())

        pending = renderer.quiz(
            "Qual porta padrão do HTTP?",
            ["80", "443"],
            answer_index=0,
            explanation="HTTP usa 80; HTTPS usa 443.",
            key="q1",
        )
        self.assertIsNone(pending)

        fake_st.radio_values["pyst_quiz_q1_choice"] = "80"
        fake_st.button_clicks.add("pyst_quiz_q1_submit")
        correct = renderer.quiz(
            "Qual porta padrão do HTTP?",
            ["80", "443"],
            answer_index=0,
            explanation="HTTP usa 80; HTTPS usa 443.",
            key="q1",
        )
        self.assertTrue(correct)

        fake_st.button_clicks.clear()
        fake_st.radio_values["pyst_quiz_q2_choice"] = "Errada"
        fake_st.button_clicks.add("pyst_quiz_q2_submit")
        wrong = renderer.quiz(
            "Segunda pergunta?",
            ["Certa", "Errada"],
            answer_index=0,
            key="q2",
        )
        self.assertFalse(wrong)

        fake_st.button_clicks.clear()
        score, total = renderer.quiz_summary()
        self.assertEqual((score, total), (1, 2))
        markdowns = [call.args[0] for call in fake_st.calls_named("markdown")]
        self.assertTrue(any("1</strong> de <strong>2</strong> acertos" in m for m in markdowns))

    def test_step_tabs_compare_toggle_and_checklist(self) -> None:
        fake_st = FakeStreamlit()
        renderer = InteractiveRenderer(fake_st, PresentationConfig())

        fake_st.button_clicks.add("pyst_stepper_s1_tab_1")
        active = renderer.step_tabs(
            [("Coleta", "Passo 1"), ("Análise", "Passo 2")],
            title="Pipeline",
            key="s1",
        )
        self.assertEqual(active, 1)
        self.assertEqual(fake_st.session_state["pyst_stepper_s1"], 1)

        fake_st.button_clicks.clear()
        fake_st.button_clicks.add("pyst_compare_c1_right")
        side = renderer.compare_toggle("Antes", "Texto A", "Depois", "Texto B", key="c1")
        self.assertEqual(side, "right")
        self.assertEqual(fake_st.session_state["pyst_compare_c1"], "right")

        fake_st.checkbox_values["pyst_check_chk_item_0"] = True
        fake_st.checkbox_values["pyst_check_chk_item_1"] = False
        states = renderer.checklist(["Item 1", "Item 2"], key="chk")
        self.assertEqual(states, [True, False])
        markdowns = [call.args[0] for call in fake_st.calls_named("markdown")]
        self.assertTrue(any("1</strong> de <strong>2</strong> itens concluídos" in m for m in markdowns))


if __name__ == "__main__":
    unittest.main()
