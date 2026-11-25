"""Dublê leve do Streamlit para testar componentes e a fachada Presentation."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Iterator


@dataclass
class RecordedCall:
    """Registra uma chamada executada sobre o backend simulado do Streamlit."""

    method: str
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)


class _DummyContext:
    def __init__(self, recorder: list[RecordedCall], label: str) -> None:
        self._recorder = recorder
        self._label = label

    def __enter__(self) -> _DummyContext:
        self._recorder.append(RecordedCall(f"{self._label}.__enter__"))
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self._recorder.append(RecordedCall(f"{self._label}.__exit__"))


class _FakeSidebar:
    def __init__(self, recorder: list[RecordedCall]) -> None:
        self._recorder = recorder

    def markdown(self, body: str, **kwargs: Any) -> None:
        self._recorder.append(RecordedCall("sidebar.markdown", (body,), kwargs))


class FakeStreamlit:
    """Implementa o subconjunto da API do Streamlit utilizado pelo PyStSlides."""

    def __init__(self) -> None:
        self.calls: list[RecordedCall] = []
        self.sidebar = _FakeSidebar(self.calls)
        self.session_state: dict[str, Any] = {}

    def set_page_config(self, **kwargs: Any) -> None:
        self.calls.append(RecordedCall("set_page_config", (), kwargs))

    def markdown(self, body: str, **kwargs: Any) -> None:
        self.calls.append(RecordedCall("markdown", (body,), kwargs))

    def write(self, *args: Any, **kwargs: Any) -> None:
        self.calls.append(RecordedCall("write", args, kwargs))

    def image(self, image: Any, **kwargs: Any) -> None:
        self.calls.append(RecordedCall("image", (image,), kwargs))

    def code(self, body: str, **kwargs: Any) -> None:
        self.calls.append(RecordedCall("code", (body,), kwargs))

    def caption(self, body: str, **kwargs: Any) -> None:
        self.calls.append(RecordedCall("caption", (body,), kwargs))

    def button(self, label: str, **kwargs: Any) -> bool:
        self.calls.append(RecordedCall("button", (label,), kwargs))
        return False

    def rerun(self) -> None:
        self.calls.append(RecordedCall("rerun"))

    def columns(self, spec: Any, **kwargs: Any) -> list[_DummyContext]:
        self.calls.append(RecordedCall("columns", (spec,), kwargs))
        count = spec if isinstance(spec, int) else len(spec)
        return [_DummyContext(self.calls, f"col[{i}]") for i in range(count)]

    def container(self, **kwargs: Any) -> _DummyContext:
        self.calls.append(RecordedCall("container", (), kwargs))
        return _DummyContext(self.calls, "container")

    @contextmanager
    def echo(self, **kwargs: Any) -> Iterator[None]:
        self.calls.append(RecordedCall("echo", (), kwargs))
        yield

    def calls_named(self, method: str) -> list[RecordedCall]:
        """Filtra chamadas registradas pelo nome do método."""
        return [call for call in self.calls if call.method == method]
