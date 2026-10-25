"""Small event scope that can release all room bindings at once."""


class InputScope:
    def __init__(self) -> None:
        # Imported lazily so pure contract tests do not require Panda3D.
        from direct.showbase.DirectObject import DirectObject

        self._object = DirectObject()
        self._closed = False

    def bind(self, event, method, extra_args=None) -> None:
        if self._closed:
            raise RuntimeError("input scope is closed")
        self._object.accept(event, method, extraArgs=extra_args or [])

    def clear(self) -> None:
        if self._closed:
            return
        self._object.ignoreAll()
        self._closed = True

