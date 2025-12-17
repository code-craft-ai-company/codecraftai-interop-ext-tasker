import json
import logging
import os
import tempfile

import automojo.testbase as testbase
from automojo.errors.exceptions import SemanticError
from automojo.interop.protocols.tasker.tasking import (
    Tasking,
    TaskingIdentity,
    instantiate_tasking,
)
from automojo.interop.protocols.tasker.examples.helloworldtasking import HelloWorldTasking
from automojo.testbase.results.model.progresscode import ProgressCode


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
        module_name="automojo.interop.protocols.tasker.examples.helloworldtasking",
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
    except BaseException as exc:
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
