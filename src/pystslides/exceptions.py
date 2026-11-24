"""Exceções customizadas do pacote PyStSlides."""

from __future__ import annotations

from pathlib import Path


class PyStSlidesError(Exception):
    """Exceção base para erros internos do PyStSlides."""


class AssetNotFoundError(PyStSlidesError, FileNotFoundError):
    """Levantada quando um arquivo de mídia ou asset não é encontrado."""

    def __init__(self, filename: str | Path, resolved_path: Path, base_dir: Path) -> None:
        self.filename = str(filename)
        self.resolved_path = resolved_path
        self.base_dir = base_dir
        message = (
            f"Asset '{self.filename}' não encontrado em '{self.resolved_path}' "
            f"(diretório base: '{self.base_dir}')."
        )
        super().__init__(message)


class InvalidSectionLevelError(PyStSlidesError, ValueError):
    """Levantada quando um nível hierárquico de sub-tópico é inválido."""

    def __init__(self, level: int) -> None:
        self.level = level
        super().__init__(
            f"Nível de sub-tópico inválido: {level}. Use um inteiro maior ou igual a 2."
        )
