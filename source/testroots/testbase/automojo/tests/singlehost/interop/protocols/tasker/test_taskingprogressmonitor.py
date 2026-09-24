import threading
import weakref

from datetime import datetime

import ccai.testbase as testbase

from ccai.testbase.results.model.progressdelivery import SummaryProgressDelivery
from ccai.testbase.results.model.progresscode import ProgressCode
from ccai.testbase.results.model.progressinfo import ProgressInfo, ProgressType
from ccai.testbase.results.model.taskingresult import TaskingResult
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


class SequencePromise:
    """
        Promise that returns a scripted sequence of progress values and stops the monitor after the last one.
    """

    def __init__(self, tasking_id: str, progress_values: list):
        self.tasking_id = tasking_id
        self.monitor = None
        self._progress_values = list(progress_values)

    def get_progress(self):
        progress = self._progress_values.pop(0)
        if len(self._progress_values) == 0 and self.monitor is not None:
            self.monitor._pulling_progress = False
        return progress


def test_add_promise_registers_the_promise() -> None:
    summary = SummaryProgressDelivery(progress_interval=0.0, progress_callback=lambda _: None)
    monitor = TaskingProgressMonitor(summary, [])

    prom = DummyPromise("added")
    monitor.add_promise(prom)

    testbase.assert_equal(list(monitor._monitored_promise_refs.keys()), ["added"])
    testbase.assert_true(monitor._monitored_promise_refs["added"]() is prom, "the monitor references the promise")
    return


def test_release_of_an_unmonitored_tasking_is_ignored() -> None:
    """
        Releasing a tasking the monitor already dropped (it completed, or it was released before) does not
        raise, so a promise can always release itself when it is closed.
    """
    summary = SummaryProgressDelivery(progress_interval=0.0, progress_callback=lambda _: None)
    prom = DummyPromise("once")
    monitor = TaskingProgressMonitor(summary, [prom])

    monitor.release("once")
    monitor.release("once")
    monitor.release("never-monitored")

    testbase.assert_equal(len(monitor._monitored_promise_refs), 0)
    return


def test_pull_progress_entry_completes_a_tasking_from_its_progress_info() -> None:
    """
        A tasking with no progress yet is skipped, and a real :class:`ProgressInfo` (which carries the tasking
        id in 'id') that reports completion ends the monitoring of the tasking.
    """
    updates = []

    def progress_callback(progress_list):
        updates.append(progress_list)
        return

    summary = SummaryProgressDelivery(progress_interval=0.0, progress_callback=progress_callback)
    monitor = TaskingProgressMonitor(summary, [])

    done = ProgressInfo("pinfo", "cat", "mod@Task", ProgressType.NumericRange, 0, 1, 1,
                        ProgressCode.Completed, datetime.now(), {})
    prom = SequencePromise("pinfo", [None, done])
    prom.monitor = monitor
    monitor.add_promise(prom)

    monitor._pull_progress_entry(threading.Event())

    testbase.assert_equal(updates, [[], [done]])
    testbase.assert_equal(len(monitor._monitored_promise_refs), 0)
    return


def test_pull_progress_entry_completes_a_tasking_from_its_result() -> None:
    """
        Once the session replaced the progress of a finished tasking with its :class:`TaskingResult`, the
        tasking is complete and the result is not delivered as a progress entry.
    """
    updates = []

    def progress_callback(progress_list):
        updates.append(progress_list)
        return

    summary = SummaryProgressDelivery(progress_interval=0.0, progress_callback=progress_callback)
    monitor = TaskingProgressMonitor(summary, [])

    result = TaskingResult("tresult", "Task", "parent", "worker")
    prom = SequencePromise("tresult", [result])
    prom.monitor = monitor
    monitor.add_promise(prom)

    monitor._pull_progress_entry(threading.Event())

    testbase.assert_equal(updates, [[]])
    testbase.assert_equal(len(monitor._monitored_promise_refs), 0)
    return
