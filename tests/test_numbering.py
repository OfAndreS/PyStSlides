"""Testes unitários para numeração hierárquica e âncoras do SectionTracker."""

from __future__ import annotations

import unittest

from pystslides.exceptions import InvalidSectionLevelError
from pystslides.numbering import SectionTracker


class TestSectionTracker(unittest.TestCase):
    def test_hierarchical_numbering(self) -> None:
        tracker = SectionTracker()
        t1 = tracker.register_topic("Introdução")
        s1_1 = tracker.register_subtopic("Contexto")
        s1_1_1 = tracker.register_subtopic("Detalhes", level=3)
        s1_1_2 = tracker.register_subtopic("Métricas", level=3)
        s1_2 = tracker.register_subtopic("Objetivos", level=2)
        t2 = tracker.register_topic("Conclusão")
        s2_1 = tracker.register_subtopic("Próximos passos")

        self.assertEqual(t1.formatted_title, "01 ) - Introdução")
        self.assertEqual(s1_1.formatted_title, "1.1 ) Contexto")
        self.assertEqual(s1_1_1.formatted_title, "1.1.1 ) Detalhes")
        self.assertEqual(s1_1_2.formatted_title, "1.1.2 ) Métricas")
        self.assertEqual(s1_2.formatted_title, "1.2 ) Objetivos")
        self.assertEqual(t2.formatted_title, "02 ) - Conclusão")
        self.assertEqual(s2_1.formatted_title, "2.1 ) Próximos passos")
        self.assertEqual(len(tracker.entries), 7)

    def test_unnumbered_entries_and_unique_anchors(self) -> None:
        tracker = SectionTracker(auto_number=False)
        first = tracker.register_topic("Atenção")
        second = tracker.register_topic("Atenção")

        self.assertEqual(first.formatted_title, "Atenção")
        self.assertEqual(first.anchor, "pyst-atencao")
        self.assertEqual(second.anchor, "pyst-atencao-2")

    def test_invalid_subtopic_level_raises(self) -> None:
        tracker = SectionTracker()
        with self.assertRaises(InvalidSectionLevelError):
            tracker.register_subtopic("Inválido", level=1)

    def test_reset_clears_state(self) -> None:
        tracker = SectionTracker()
        tracker.register_topic("Primeiro")
        tracker.reset()
        fresh = tracker.register_topic("Recomeço")
        self.assertEqual(fresh.number, "01")
        self.assertEqual(len(tracker.entries), 1)


if __name__ == "__main__":
    unittest.main()
