import threading
import weakref
import ccai.testbase as testbase

from ccai.testbase.results.model.progressdelivery import SummaryProgressDelivery
from ccai.testbase.results.model.progresscode import ProgressCode
from ccai.interop.protocols.tasker.taskingprogressmonitor import TaskingProgressMonitor


class FailingPromise:
    def __init__(self, monitor: TaskingProgressMonitor):
        self.tasking_id = "failing"
        self._monitor = monitor

    def get_progress(self):
        # Stop the monitor after this call to ensure the loop exits
        self._monitor._pulling_progress = False
        raise RuntimeError("progress failure")


def test_pull_progress_entry_handles_missing_progress() -> None:
    updates = []

    def progress_callback(progress_list):
        updates.append(progress_list)
        return

    summary = SummaryProgressDelivery(progress_interval=0.0, progress_callback=progress_callback)
    monitor = TaskingProgressMonitor(summary, [])

    prom = FailingPromise(monitor)
    monitor._monitored_promise_refs = {prom.tasking_id: weakref.ref(prom)}

    sgate = threading.Event()
    exc = None
    try:
        monitor._pull_progress_entry(sgate)
    except Exception as err:
        exc = err

    testbase.assert_equal(exc, None)
    testbase.assert_equal(len(updates), 1)
    testbase.assert_equal(updates[0], [])
    return


class DummyPromise:
    """Simple promise used to test release logic."""

    def __init__(self, tasking_id: str):
        self.tasking_id = tasking_id

    def get_progress(self):
        return None


class DummyProgress:
    """Lightweight progress object used for monitor callbacks."""

    def __init__(self, tasking_id: str, status):
        self.tasking_id = tasking_id
        self.status = status


class ProgressPromise:
    """Promise that returns predetermined progress and stops the monitor."""

    def __init__(self, monitor: TaskingProgressMonitor | None, progress: DummyProgress):
        self.tasking_id = progress.tasking_id
        self._monitor = monitor
        self._progress = progress

    def get_progress(self):
        if self._monitor is not None:
            self._monitor._pulling_progress = False
        return self._progress


def test_release_removes_promise() -> None:
    summary = SummaryProgressDelivery(progress_interval=0.0, progress_callback=lambda _: None)
    prom = DummyPromise("release")
    monitor = TaskingProgressMonitor(summary, [prom])

    testbase.assert_equal(len(monitor._monitored_promise_refs), 1)
    monitor.release("release")
    testbase.assert_equal(len(monitor._monitored_promise_refs), 0)
    return


def test_pull_progress_entry_collects_completed_progress() -> None:
    updates = []

    def progress_callback(progress_list):
        updates.extend(progress_list)
        return

    summary = SummaryProgressDelivery(progress_interval=0.0, progress_callback=progress_callback)
    monitor = TaskingProgressMonitor(summary, [])

    progress = DummyProgress("done", ProgressCode.Completed)
    prom = ProgressPromise(monitor, progress)
    monitor._monitored_promise_refs = {prom.tasking_id: weakref.ref(prom)}

    sgate = threading.Event()
    monitor._pull_progress_entry(sgate)

    testbase.assert_equal(len(updates), 1)
    testbase.assert_equal(updates[0].tasking_id, "done")
    testbase.assert_equal(len(monitor._monitored_promise_refs), 0)
    return


def test_start_runs_monitor_thread() -> None:
    updates = []

    def progress_callback(progress_list):
        updates.extend(progress_list)
        return

    summary = SummaryProgressDelivery(progress_interval=0.0, progress_callback=progress_callback)

    progress = DummyProgress("thread", ProgressCode.Completed)
    prom = ProgressPromise(None, progress)
    monitor = TaskingProgressMonitor(summary, [prom])
    prom._monitor = monitor

    monitor.start()
    monitor._progress_thread.join(timeout=1)

    testbase.assert_equal(len(updates) >= 1, True)
    testbase.assert_equal(len(monitor._monitored_promise_refs), 0)
    return
