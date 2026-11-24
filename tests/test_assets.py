"""Testes unitários para o AssetManager."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pystslides.assets import AssetManager
from pystslides.exceptions import AssetNotFoundError


class TestAssetManager(unittest.TestCase):
    def test_resolve_and_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            img = base / "slide1.png"
            img.write_bytes(b"fake-png")

            manager = AssetManager(base)
            self.assertEqual(manager.resolve("slide1.png"), img.resolve())
            self.assertTrue(manager.exists("slide1.png"))
            self.assertFalse(manager.exists("inexistente.png"))

    def test_resolve_missing_raises_asset_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manager = AssetManager(tmp)
            with self.assertRaises(AssetNotFoundError) as ctx:
                manager.resolve("missing.png")
            self.assertIn("missing.png", str(ctx.exception))

    def test_from_file_resolves_relative_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src_dir = root / "src"
            data_dir = root / "data"
            src_dir.mkdir()
            data_dir.mkdir()
            app_file = src_dir / "app.py"
            app_file.write_text("", encoding="utf-8")
            sample = data_dir / "logo.png"
            sample.write_bytes(b"png")

            manager = AssetManager.from_file(app_file, "../data")
            self.assertEqual(manager.resolve("logo.png"), sample.resolve())

    def test_list_images_filters_and_sorts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "02.png").write_bytes(b"")
            (base / "01.jpg").write_bytes(b"")
            (base / "notas.txt").write_text("texto", encoding="utf-8")

            manager = AssetManager(base)
            listed = [p.name for p in manager.list_images()]
            self.assertEqual(listed, ["01.jpg", "02.png"])


if __name__ == "__main__":
    unittest.main()
