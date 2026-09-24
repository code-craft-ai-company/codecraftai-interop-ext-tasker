import json
import logging
import os
import queue
import tempfile

import ccai.testbase as testbase
import ccai.interop.protocols.tasker.tasking as tasking_module
from ccai.errors.exceptions import SemanticError
from ccai.interop.protocols.tasker.tasking import (
    Tasking,
    TaskingIdentity,
    instantiate_tasking,
)
from ccai.interop.protocols.tasker.examples.helloworldtasking import HelloWorldTasking
from ccai.testbase.mocking import create_module_patch
from ccai.testbase.results.model.progresscode import ProgressCode


class DummyTasking(Tasking):
    """Simple Tasking used for unit tests."""

    def perform(self) -> bool:  # pragma: no cover - not called
        return False


def create_tasking(tmpdir):
    logdir = os.path.join(tmpdir, "logs")
    os.makedirs(logdir, exist_ok=True)
    logfile = os.path.join(logdir, "task.log")

    logger = logging.getLogger("dummy")
    logger.addHandler(logging.NullHandler())

    task = DummyTasking(
        worker="w",
        wref="r",
        tasking_id="tid",
        parent_id="pid",
        output_dir=tmpdir,
        logdir=logdir,
        logfile=logfile,
        logger=logger,
        events_endpoint=None,
    )
    return task


def test_instantiate_tasking_returns_instance():
    tmp_path = tempfile.mkdtemp()
    outdir = os.path.join(tmp_path, "out")
    logdir = os.path.join(tmp_path, "logs")
    os.makedirs(logdir, exist_ok=True)
    logfile = os.path.join(logdir, "task.log")

    task = instantiate_tasking(
        worker="w",
        wref="r",
        module_name="ccai.interop.protocols.tasker.examples.helloworldtasking",
        tasking_name="HelloWorldTasking",
        tasking_id="tid",
        parent_id="pid",
        output_dir=str(outdir),
        logdir=str(logdir),
        logfile=str(logfile),
        log_level=logging.INFO,
        events_endpoint=None,
        notify_url=None,
        notify_headers=None,
    )

    testbase.assert_equal(isinstance(task, HelloWorldTasking), True)
    return


def test_instantiate_tasking_missing_returns_none():
    tmp_path = tempfile.mkdtemp()
    outdir = os.path.join(tmp_path, "out")
    logdir = os.path.join(tmp_path, "logs")
    os.makedirs(logdir, exist_ok=True)
    logfile = os.path.join(logdir, "task.log")

    task = instantiate_tasking(
        worker="w",
        wref="r",
        module_name="os",
        tasking_name="MissingClass",
        tasking_id="tid",
        parent_id="pid",
        output_dir=str(outdir),
        logdir=str(logdir),
        logfile=str(logfile),
        log_level=logging.INFO,
        events_endpoint=None,
        notify_url=None,
        notify_headers=None,
    )

    testbase.assert_equal(task, None)
    return


def test_taskingidentity_as_tuple():
    ident = TaskingIdentity(module_name="m", tasking_name="t")
    testbase.assert_equal(ident.as_tuple(), ("m", "t"))
    return


def test_get_identity_and_full_name():
    tmp_path = tempfile.mkdtemp()
    task = create_tasking(tmp_path)
    ident = task.get_identity()
    testbase.assert_equal(ident.module_name, DummyTasking.__module__)
    testbase.assert_equal(ident.tasking_name, DummyTasking.__name__)
    testbase.assert_equal(task.full_name, f"{DummyTasking.__module__}@{DummyTasking.__name__}")
    return


def test_write_metrics_creates_file():
    tmp_path = tempfile.mkdtemp()
    task = create_tasking(tmp_path)
    task.add_metrics_stream("m", "json")
    metrics_file = os.path.join(task._logdir, "m.jsos")
    metrics = {"a": 1}
    task.write_metrics("m", metrics)

    with open(metrics_file, "r") as mf:
        content = mf.read()

    data = content.split("\x1e\n")[0]
    testbase.assert_equal(json.loads(data), metrics)
    return


def test_write_metrics_unknown_stream_raises():
    tmp_path = tempfile.mkdtemp()
    task = create_tasking(tmp_path)
    err = None
    try:
        task.write_metrics("missing", {"a": 1})
    except SemanticError as exc:
        err = exc
    testbase.assert_equal(isinstance(err, SemanticError), True)
    return


def test_mark_progress_state_transitions():
    tmp_path = tempfile.mkdtemp()
    task = create_tasking(tmp_path)
    task.mark_progress_start()
    testbase.assert_equal(task.task_status, ProgressCode.Running)
    task.mark_progress_paused()
    testbase.assert_equal(task.task_status, ProgressCode.Paused)
    task.mark_progress_running()
    testbase.assert_equal(task.task_status, ProgressCode.Running)
    task.mark_progress_complete()
    testbase.assert_equal(task.task_status, ProgressCode.Completed)
    return


def _fail_traceback_detail(ex_inst: BaseException):
    """
        Stands in for ``create_traceback_detail`` when the traceback detail cannot be created.
    """
    raise RuntimeError("traceback detail unavailable")


def test_mark_errored_records_a_fallback_detail_when_the_traceback_detail_fails():
    """
        When a traceback detail cannot be created for the error, mark_errored still records the original
        error in the tasking result (its type and the formatted traceback text) and reports the tasking as
        errored, instead of failing with a NameError for the missing detail.
    """
    tmp_path = tempfile.mkdtemp()
    task = create_tasking(tmp_path)
    task._result = task.create_tasking_result("tid", task.full_name, "pid", DummyTasking.PREFIX)
    task._progress_queue = queue.Queue()
    task.mark_progress_start()

    with create_module_patch(tasking_module, "create_traceback_detail") as detail_patch:
        detail_patch.configure(side_effect=_fail_traceback_detail)

        try:
            raise ValueError("original problem")
        except ValueError as err:
            task.mark_errored(err)

    errors = task.result.errors
    testbase.assert_equal(len(errors), 1)

    detail = errors[0]
    testbase.assert_equal(detail.extype, "ValueError")
    testbase.assert_equal(len(detail.exargs), 1)
    testbase.assert_true("original problem" in detail.exargs[0], "the backup traceback text names the original error")
    testbase.assert_equal(detail.traces, [])

    testbase.assert_equal(task.task_status, ProgressCode.Errored)
    progress = task._progress_queue.get_nowait()
    testbase.assert_equal(progress.status, ProgressCode.Errored)
    return


class RecordingHandler(logging.Handler):
    """
        A logging handler that keeps the records it receives.
    """

    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.records = []
        return

    def emit(self, record: logging.LogRecord):
        self.records.append(record)
        return


def _create_recording_tasking(tmpdir, logger_name: str):
    """
        Creates a tasking, ready to be marked errored or failed, whose logger records what it logs.
    """
    task = create_tasking(tmpdir)

    handler = RecordingHandler()
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.addHandler(handler)
    task._logger = logger

    task._result = task.create_tasking_result("tid", task.full_name, "pid", DummyTasking.PREFIX)
    task._progress_queue = queue.Queue()
    task.mark_progress_start()
    return task, handler


def _assert_logged_traceback_text(handler: RecordingHandler, extype: str, exmsg: str):
    """
        Checks that the error logged for the tasking is the traceback text and not the repr of a list of lines.
    """
    testbase.assert_equal(len(handler.records), 1)
    logged = handler.records[0].getMessage()

    testbase.assert_true(isinstance(handler.records[0].msg, str), "the logged message is a string")
    first_line = logged.split(os.linesep)[0]
    testbase.assert_true(first_line.startswith(f"{extype}: "), "the log starts with the exception line")
    testbase.assert_true(exmsg in first_line, "the exception line carries the exception message")
    testbase.assert_true(os.linesep + "Traceback (most recent call first):" in logged, "the traceback lines are joined")
    testbase.assert_equal(logged.startswith("["), False)
    return


def test_mark_errored_logs_the_traceback_as_text():
    """
        mark_errored logs the formatted traceback as lines of text instead of the repr of the list returned by
        format_traceback_detail.
    """
    tmp_path = tempfile.mkdtemp()
    task, handler = _create_recording_tasking(tmp_path, "test_mark_errored_logs_the_traceback_as_text")

    try:
        raise ValueError("errored problem")
    except ValueError as err:
        task.mark_errored(err)

    _assert_logged_traceback_text(handler, "ValueError", "errored problem")
    testbase.assert_equal(task.task_status, ProgressCode.Errored)
    return


def test_mark_failed_logs_the_traceback_as_text():
    """
        mark_failed logs the formatted traceback as lines of text instead of the repr of the list returned by
        format_traceback_detail.
    """
    tmp_path = tempfile.mkdtemp()
    task, handler = _create_recording_tasking(tmp_path, "test_mark_failed_logs_the_traceback_as_text")

    try:
        raise AssertionError("failed check")
    except AssertionError as err:
        task.mark_failed(err)

    _assert_logged_traceback_text(handler, "AssertionError", "failed check")
    testbase.assert_equal(task.task_status, ProgressCode.Failed)
    return
