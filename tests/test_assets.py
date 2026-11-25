"""Testes unitários para o AssetManager."""

from __future__ import annotations

import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from pystslides.assets import (
    AssetManager,
    cli_export_assets,
    export_editorial_assets,
    get_editorial_assets_dir,
    is_animated_svg,
    list_editorial_assets,
)
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

    def test_editorial_assets_dir_and_export(self) -> None:
        editorial_dir = get_editorial_assets_dir()
        self.assertTrue(editorial_dir.is_dir())
        available = AssetManager(editorial_dir).list_images()
        self.assertEqual(len(available), 49)

        static_svgs = list_editorial_assets(kind="svg_static")
        animated_svgs = list_editorial_assets(kind="svg_animated")
        self.assertEqual(len(static_svgs), 19)
        self.assertEqual(len(animated_svgs), 19)
        self.assertEqual(
            {f"{p.stem}_animated.svg" for p in static_svgs},
            {p.name for p in animated_svgs},
        )
        for svg_path in animated_svgs:
            self.assertTrue(is_animated_svg(svg_path))
            content = svg_path.read_text(encoding="utf-8")
            ET.fromstring(content)
            self.assertIn("<style>", content)
            self.assertIn("@keyframes", content)
            self.assertIn("prefers-reduced-motion", content)

        catalog_path = Path(__file__).resolve().parent.parent / "ASSETS.md"
        catalog_text = catalog_path.read_text(encoding="utf-8")
        for asset in available:
            self.assertIn(asset.name, catalog_text)

        with tempfile.TemporaryDirectory() as tmp:
            png_only = export_editorial_assets(tmp, kind="png")
            self.assertTrue(png_only)
            self.assertTrue(all(p.suffix == ".png" and p.exists() for p in png_only))

            animated_dir = Path(tmp) / "animated_only"
            animated_exported = export_editorial_assets(animated_dir, kind="svg_animated")
            self.assertEqual(len(animated_exported), 19)
            self.assertTrue(all(is_animated_svg(p) for p in animated_exported))

            cli_dest = Path(tmp) / "cli_out"
            exit_code = cli_export_assets([str(cli_dest), "--format", "svg"])
            self.assertEqual(exit_code, 0)
            svg_files = list(cli_dest.glob("*.svg"))
            self.assertEqual(len(svg_files), 38)


if __name__ == "__main__":
    unittest.main()
