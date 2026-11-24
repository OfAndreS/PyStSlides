"""Gerenciamento centralizado de arquivos estáticos (imagens, dados e mídia)."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from pystslides.exceptions import AssetNotFoundError


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
