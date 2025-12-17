import pickle
from datetime import datetime
import automojo.testbase as testbase

from automojo.interop.protocols.tasker.taskersession import TaskerSession
from automojo.interop.protocols.tasker.taskeraspects import TaskerAspects
from automojo.testbase.results.model.progressinfo import ProgressInfo
from automojo.testbase.results.model.progresscode import ProgressCode
from automojo.testbase.results.model.progresstype import ProgressType
from automojo.testbase.results.model.taskingresult import TaskingResult
from automojo.testbase.results.model.resultcode import ResultCode
from automojo.errors.exceptions import SemanticError


class DummyLogger:
    def __init__(self) -> None:
        self.entries = []

    def error(self, msg: str) -> None:
        self.entries.append(("error", msg))

    def info(self, msg: str) -> None:
        self.entries.append(("info", msg))


class DummyService:
    logger = DummyLogger()

    @classmethod
    def log_error(cls, message: str) -> None:
        cls.logger.error(message)

    @classmethod
    def log_info(cls, message: str) -> None:
        cls.logger.info(message)


class DummyTasking:
    def __init__(self) -> None:
        self.shutdown_called = False

    def shutdown(self) -> None:
        self.shutdown_called = True
        return

def make_session() -> TaskerSession:
    aspects = TaskerAspects(inactivity_timeout=0.1)
    return TaskerSession(DummyService, "worker", "wref", "/tmp", 10, aspects=aspects)


def test_post_and_get_tasking_events() -> None:
    session = make_session()
    event = {"tasking-id": "tid", "info": "hi"}
    session.post_event(event)

    data = session.get_tasking_events("tid")
    events = pickle.loads(data)

    testbase.assert_equal(events, [event])
    return


def test_get_tasking_progress_returns_progress() -> None:
    session = make_session()
    prog = ProgressInfo(
        "tid",
        "cat",
        "mon",
        ProgressType.Sequential,
        "0",
        "1",
        "0",
        ProgressCode.Running,
        datetime.now(),
    )
    session._progress_table["tid"] = prog

    pkl = session.get_tasking_progress("tid")
    progress = pickle.loads(pkl)

    testbase.assert_equal(progress.id, "tid")
    testbase.assert_equal(progress.status, ProgressCode.Running)
    return


def test_cancel_tasking_invokes_shutdown_when_running() -> None:
    session = make_session()
    task = DummyTasking()
    session._taskings_table["tid"] = task
    session._status_table["tid"] = "Running"

    session.cancel_tasking("tid")

    testbase.assert_equal(task.shutdown_called, True)
    return


def test_cancel_tasking_raises_unknown_tasking() -> None:
    session = make_session()
    exc = None
    try:
        session.cancel_tasking("missing")
    except RuntimeError as err:
        exc = err

    testbase.assert_equal(isinstance(exc, RuntimeError), True)
    return


def test_dispose_tasking_removes_and_shutdown() -> None:
    session = make_session()
    task = DummyTasking()
    session._taskings_table["tid"] = task

    session.dispose_tasking("tid")

    testbase.assert_equal(task.shutdown_called, True)
    testbase.assert_equal("tid" in session._taskings_table, False)
    return


def test_has_completed_and_result_ready_checks() -> None:
    session = make_session()
    result = TaskingResult("tid", "name", "parent", "worker", result_code=ResultCode.PASSED)
    session._status_table["tid"] = "Completed"
    session._results_table["tid"] = result

    ready = session.has_completed_and_result_ready("tid")

    testbase.assert_equal(ready, True)
    return


def test_get_tasking_result_raises_when_not_complete() -> None:
    session = make_session()
    session._taskings_table["tid"] = DummyTasking()
    session._status_table["tid"] = "Running"

    exc = None
    try:
        session.get_tasking_result("tid")
    except SemanticError as err:
        exc = err

    testbase.assert_equal(isinstance(exc, SemanticError), True)
    return

