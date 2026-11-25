"""Gerenciamento centralizado de arquivos estáticos (imagens, dados e mídia)."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Iterable, Literal, Sequence

from pystslides.exceptions import AssetNotFoundError


AssetKind = Literal["all", "png", "svg", "svg_static", "svg_animated"]


DEFAULT_IMAGE_EXTENSIONS: tuple[str, ...] = (
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".svg",
)


class AssetManager:
    """Resolve, valida e lista arquivos estáticos a partir de um diretório base."""

    def __init__(self, base_dir: str | Path) -> None:
        self._base_dir = Path(base_dir).expanduser().resolve()

    @property
    def base_dir(self) -> Path:
        """Retorna o diretório base resolvido para os assets."""
        return self._base_dir

    @classmethod
    def from_file(cls, reference_file: str | Path, relative_dir: str = "../data") -> AssetManager:
        """Cria um AssetManager relativo a um arquivo Python de referência (ex.: `__file__`)."""
        base = Path(reference_file).resolve().parent / relative_dir
        return cls(base)

    def resolve(self, filename: str | Path, *, must_exist: bool = True) -> Path:
        """Resolve o caminho de um asset relativo ao diretório base.

        Se `filename` já for um caminho absoluto existente, ele é retornado diretamente.
        """
        candidate = Path(filename).expanduser()
        resolved = candidate.resolve() if candidate.is_absolute() else (self._base_dir / candidate).resolve()

        if must_exist and not resolved.exists():
            raise AssetNotFoundError(filename=filename, resolved_path=resolved, base_dir=self._base_dir)

        return resolved

    def exists(self, filename: str | Path) -> bool:
        """Verifica se o arquivo informado existe no diretório de assets."""
        try:
            self.resolve(filename, must_exist=True)
            return True
        except AssetNotFoundError:
            return False

    def list_images(
        self,
        subdir: str | Path | None = None,
        extensions: Iterable[str] = DEFAULT_IMAGE_EXTENSIONS,
    ) -> list[Path]:
        """Lista imagens ordenadas por nome dentro do diretório base ou de um subdiretório."""
        target_dir = self._base_dir if subdir is None else (self._base_dir / subdir).resolve()
        if not target_dir.exists() or not target_dir.is_dir():
            raise AssetNotFoundError(filename=subdir or ".", resolved_path=target_dir, base_dir=self._base_dir)

        normalized_exts = {ext.lower() for ext in extensions}
        images = [
            path
            for path in target_dir.iterdir()
            if path.is_file() and path.suffix.lower() in normalized_exts
        ]
        return sorted(images, key=lambda p: p.name.lower())


def get_editorial_assets_dir() -> Path:
    """Retorna o diretório empacotado com os assets editoriais padrão do PyStSlides."""
    return Path(__file__).resolve().parent / "editorial_assets"


def is_animated_svg(path: str | Path) -> bool:
    """Indica se um arquivo é uma variante SVG animada (`*_animated.svg`)."""
    candidate = Path(path)
    return candidate.suffix.lower() == ".svg" and candidate.stem.lower().endswith("_animated")


def _matches_asset_kind(path: Path, kind: AssetKind) -> bool:
    ext = path.suffix.lower()
    if kind == "all":
        return ext in (".png", ".svg")
    if kind == "png":
        return ext == ".png"
    if kind == "svg":
        return ext == ".svg"
    if kind == "svg_static":
        return ext == ".svg" and not is_animated_svg(path)
    if kind == "svg_animated":
        return is_animated_svg(path)
    raise ValueError(f"Tipo de asset inválido: {kind!r}.")


def list_editorial_assets(*, kind: AssetKind = "all") -> list[Path]:
    """Lista os assets editoriais empacotados filtrando por formato ou variante animada."""
    source_dir = get_editorial_assets_dir()
    if not source_dir.exists():
        raise AssetNotFoundError(
            filename="editorial_assets",
            resolved_path=source_dir,
            base_dir=source_dir.parent,
        )
    return [
        src
        for src in sorted(source_dir.iterdir(), key=lambda p: p.name.lower())
        if src.is_file() and _matches_asset_kind(src, kind)
    ]


def export_editorial_assets(
    destination: str | Path,
    *,
    kind: AssetKind = "all",
    overwrite: bool = False,
) -> list[Path]:
    """Copia os assets editoriais incluídos no pacote para um diretório de destino."""
    sources = list_editorial_assets(kind=kind)
    target_dir = Path(destination).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    exported: list[Path] = []
    for src in sources:
        dst = target_dir / src.name
        if dst.exists() and not overwrite:
            exported.append(dst)
            continue
        shutil.copy2(src, dst)
        exported.append(dst)
    return exported


def cli_export_assets(argv: Sequence[str] | None = None) -> int:
    """CLI para exportar rapidamente os assets editoriais para uma pasta local."""
    parser = argparse.ArgumentParser(
        prog="pystslides-assets",
        description="Copia o pacote de ilustrações editoriais do PyStSlides para uma pasta.",
    )
    parser.add_argument(
        "destination",
        nargs="?",
        default="assets",
        help="Diretório de destino para os assets (padrão: ./assets).",
    )
    parser.add_argument(
        "--format",
        dest="kind",
        choices=("all", "png", "svg", "svg_static", "svg_animated"),
        default="all",
        help="Filtra o formato exportado: all, png, svg, svg_static ou svg_animated (padrão: all).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Sobrescreve arquivos existentes no destino.",
    )
    args = parser.parse_args(argv)
    files = export_editorial_assets(
        args.destination,
        kind=args.kind,
        overwrite=args.overwrite,
    )
    print(f"{len(files)} assets disponíveis em: {Path(args.destination).expanduser().resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(cli_export_assets())
