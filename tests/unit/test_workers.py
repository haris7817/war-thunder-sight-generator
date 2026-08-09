"""Tests for the background worker infrastructure (M5)."""

from __future__ import annotations

import threading
import time

from app.infrastructure.workers import CancellationToken, Debouncer, TaskRunner


def test_worker_delivers_result(qtbot):
    runner = TaskRunner()
    results: list[int] = []
    runner.submit(lambda: 42, on_result=results.append)
    runner.wait_for_done(3000)
    qtbot.wait(50)  # let the queued finished-signal deliver on the main thread
    assert results == [42]


def test_result_delivered_on_main_thread(qtbot):
    runner = TaskRunner()
    threads: list[threading.Thread] = []
    runner.submit(lambda: 1, on_result=lambda _r: threads.append(threading.current_thread()))
    runner.wait_for_done(3000)
    qtbot.wait(50)
    assert threads == [threading.main_thread()]


def test_cancelled_worker_drops_result(qtbot):
    runner = TaskRunner()
    results: list[int] = []
    token = CancellationToken()

    def slow():
        time.sleep(0.15)
        return 7

    runner.submit(slow, on_result=results.append, token=token)
    token.cancel()
    runner.wait_for_done(3000)
    qtbot.wait(50)
    assert results == []


def test_worker_error_surfaces_via_signal(qtbot):
    runner = TaskRunner()
    errors: list[str] = []

    def boom():
        raise ValueError("kaboom")

    runner.submit(boom, on_error=errors.append)
    runner.wait_for_done(3000)
    qtbot.wait(50)
    assert errors and "ValueError" in errors[0] and "kaboom" in errors[0]


def test_debouncer_fires_only_latest(qtbot):
    calls: list[int] = []
    d = Debouncer(interval_ms=40)
    d.call(lambda: calls.append(1))
    d.call(lambda: calls.append(2))
    d.call(lambda: calls.append(3))
    qtbot.wait(120)
    assert calls == [3]


def test_debouncer_flush(qtbot):
    calls: list[int] = []
    d = Debouncer(interval_ms=1000)
    d.call(lambda: calls.append(9))
    d.flush()
    assert calls == [9]
