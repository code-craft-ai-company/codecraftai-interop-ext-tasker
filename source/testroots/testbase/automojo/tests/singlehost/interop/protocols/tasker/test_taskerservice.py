import os
from collections import OrderedDict
import tempfile
import ccai.testbase as testbase
from ccai.errors.exceptions import SemanticError
from ccai.interop.protocols.tasker.taskerservice import TaskerService


def create_service(tmpdir: str) -> TaskerService:
    TaskerService.logging_directory = tmpdir
    TaskerService.active_sessions = OrderedDict()
    return TaskerService()


class DummySession:
    def __init__(self):
        self.shutdown_called = False

    def shutdown(self):
        self.shutdown_called = True
        return


def test_locked_get_session_validations() -> None:
    tmpdir = tempfile.mkdtemp()
    service = create_service(tmpdir)

    exc = None
    try:
        service._locked_get_session(None)  # type: ignore[arg-type]
    except ValueError as err:
        exc = err
    testbase.assert_equal(isinstance(exc, ValueError), True)

    exc = None
    try:
        service._locked_get_session("missing")
    except SemanticError as err:
        exc = err
    testbase.assert_equal(isinstance(exc, SemanticError), True)

    dummy_session = object()
    service.active_sessions["sess"] = dummy_session

    exc = None
    try:
        service._locked_get_session("bogus")
    except SemanticError as err:
        exc = err
    testbase.assert_equal(isinstance(exc, SemanticError), True)

    sess = service._locked_get_session("sess")
    testbase.assert_equal(sess is dummy_session, True)
    return


def test_archive_folder_creates_zip() -> None:
    tmpdir = tempfile.mkdtemp()
    service = create_service(tmpdir)

    src_dir = os.path.join(tmpdir, "src")
    os.makedirs(src_dir)
    with open(os.path.join(src_dir, "file.txt"), "w", encoding="utf-8") as f:
        f.write("data")

    dest_dir = os.path.join(tmpdir, "dest")
    archive_path = service.exposed_archive_folder(
        folder_to_archive=src_dir,
        dest_folder=dest_dir,
        archive_name="archive"
    )

    testbase.assert_equal(os.path.isfile(archive_path), True)
    testbase.assert_equal(archive_path.endswith(".zip"), True)
    testbase.assert_equal(os.path.dirname(archive_path), dest_dir)
    return


def test_file_and_folder_exists() -> None:
    tmpdir = tempfile.mkdtemp()
    service = create_service(tmpdir)

    folder = os.path.join(tmpdir, "folder")
    os.makedirs(folder)
    fname = os.path.join(folder, "data.txt")
    with open(fname, "w", encoding="utf-8") as f:
        f.write("info")

    testbase.assert_equal(service.exposed_file_exists(filename=fname), True)
    testbase.assert_equal(service.exposed_file_exists(filename=fname + "x"), False)
    testbase.assert_equal(service.exposed_folder_exists(folder=folder), True)
    testbase.assert_equal(service.exposed_folder_exists(folder=folder + "x"), False)
    return


def test_session_close_all_returns_none_when_no_sessions() -> None:
    tmpdir = tempfile.mkdtemp()
    service = create_service(tmpdir)

    closed_session = service.exposed_session_close_all()

    testbase.assert_equal(closed_session is None, True)
    testbase.assert_equal(len(TaskerService.active_sessions), 0)
    return


def test_session_close_all_returns_last_closed_session() -> None:
    tmpdir = tempfile.mkdtemp()
    service = create_service(tmpdir)

    sess1 = DummySession()
    sess2 = DummySession()

    TaskerService.active_sessions["sess1"] = sess1
    TaskerService.active_sessions["sess2"] = sess2

    closed_session = service.exposed_session_close_all()

    testbase.assert_equal(closed_session, "sess2")
    testbase.assert_equal(len(TaskerService.active_sessions), 0)
    testbase.assert_equal(sess1.shutdown_called, True)
    testbase.assert_equal(sess2.shutdown_called, True)
    return
