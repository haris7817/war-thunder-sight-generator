"""Background execution for the GUI: run heavy work (threshold, trace, export) off
the UI thread so the window never freezes.

Design:

* :class:`Worker` wraps a callable in a ``QRunnable`` and reports back via
  :class:`WorkerSignals` (``finished`` / ``error`` / ``progress``). Because signals
  cross threads, the connected slots run on the receiving (UI) thread.
* :class:`CancellationToken` lets a superseded job (e.g. an old slider position) be
  discarded — the worker will not emit ``finished`` once cancelled.
* :class:`TaskRunner` owns a ``QThreadPool`` and submits workers.
* :class:`Debouncer` coalesces rapid triggers (a slider drag emits dozens of
  ``valueChanged`` events) into one call after a quiet interval (~120 ms).
"""

from __future__ import annotations

import traceback
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QRunnable, QThreadPool, QTimer, Signal, Slot


class CancellationToken:
    """A trivial cooperative-cancellation flag."""

    __slots__ = ("_cancelled",)

    def __init__(self) -> None:
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    @property
    def cancelled(self) -> bool:
        return self._cancelled


class WorkerSignals(QObject):
    """Signals available from a running :class:`Worker`."""

    finished = Signal(object)  # result payload
    error = Signal(str)  # formatted traceback / message
    progress = Signal(int)  # 0-100
    done = Signal()  # always emitted last (success, error, or cancel) — for cleanup


class Worker(QRunnable):
    """Runs ``fn(*args, **kwargs)`` on a thread-pool thread.

    If a ``token`` is supplied and gets cancelled, the result is dropped (no
    ``finished`` emission), so stale work never updates the UI.
    """

    def __init__(
        self,
        fn: Callable[..., Any],
        *args: Any,
        token: CancellationToken | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__()
        self._fn = fn
        self._args = args
        self._kwargs = kwargs
        self.token = token
        self.signals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            if self.token is not None and self.token.cancelled:
                return
            try:
                result = self._fn(*self._args, **self._kwargs)
            except Exception:  # noqa: BLE001 - surface any failure to the UI
                self.signals.error.emit(traceback.format_exc())
                return
            if self.token is not None and self.token.cancelled:
                return
            self.signals.finished.emit(result)
        finally:
            # Always emitted so TaskRunner can release its reference, even when the
            # job was cancelled (and therefore emitted no finished/error).
            self.signals.done.emit()


class TaskRunner:
    """Submits callables to a thread pool and wires their results back to callbacks."""

    def __init__(self, max_thread_count: int | None = None) -> None:
        self._pool = QThreadPool()
        if max_thread_count is not None:
            self._pool.setMaxThreadCount(max_thread_count)
        # Hold references to in-flight workers so their (Python-created) signal
        # objects are not garbage-collected before queued signals are delivered.
        self._active: set[Worker] = set()

    def submit(
        self,
        fn: Callable[..., Any],
        *args: Any,
        on_result: Callable[[Any], None] | None = None,
        on_error: Callable[[str], None] | None = None,
        token: CancellationToken | None = None,
        **kwargs: Any,
    ) -> CancellationToken:
        """Run ``fn`` off-thread; deliver its result/error to callbacks on the UI thread.

        Returns the :class:`CancellationToken` (creates one if not provided) so the
        caller can cancel a superseded job.
        """
        token = token or CancellationToken()
        worker = Worker(fn, *args, token=token, **kwargs)
        if on_result is not None:
            worker.signals.finished.connect(on_result)
        if on_error is not None:
            worker.signals.error.connect(on_error)
        self._active.add(worker)
        worker.signals.done.connect(lambda: self._active.discard(worker))
        self._pool.start(worker)
        return token

    def wait_for_done(self, msecs: int = -1) -> bool:
        """Block until all workers finish (used by tests). -1 waits indefinitely."""
        return self._pool.waitForDone(msecs)

    def shutdown(self) -> None:
        self._pool.clear()
        self._pool.waitForDone()


class Debouncer(QObject):
    """Coalesce rapid triggers into a single deferred call.

    Each :meth:`call` restarts a single-shot timer; only the most recent callable
    fires, once the triggers go quiet for ``interval_ms``.
    """

    def __init__(self, interval_ms: int = 120, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(interval_ms)
        self._pending: Callable[[], None] | None = None
        self._timer.timeout.connect(self._fire)

    def call(self, fn: Callable[[], None]) -> None:
        self._pending = fn
        self._timer.start()

    def flush(self) -> None:
        """Fire any pending call immediately (used by tests)."""
        if self._timer.isActive():
            self._timer.stop()
            self._fire()

    @Slot()
    def _fire(self) -> None:
        fn, self._pending = self._pending, None
        if fn is not None:
            fn()
