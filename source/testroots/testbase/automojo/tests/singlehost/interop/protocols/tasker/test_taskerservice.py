import os
import tempfile
import automojo.testbase as testbase
from automojo.errors.exceptions import SemanticError
from automojo.interop.protocols.tasker.taskerservice import TaskerService


def create_service(tmpdir: str) -> TaskerService:
    TaskerService.logging_directory = tmpdir
    return TaskerService()


def test_locked_get_session_validations() -> None:
    tmpdir = tempfile.mkdtemp()
    service = create_service(tmpdir)

    exc = None
    try:
        service._locked_get_session(None)  # type: ignore[arg-type]
    except BaseException as err:  # pylint: disable=broad-except
        exc = err
    testbase.assert_equal(isinstance(exc, ValueError), True)

    exc = None
    try:
        service._locked_get_session("missing")
    except BaseException as err:  # pylint: disable=broad-except
        exc = err
    testbase.assert_equal(isinstance(exc, SemanticError), True)

    dummy_session = object()
    service.active_sessions["sess"] = dummy_session

    exc = None
    try:
        service._locked_get_session("bogus")
    except BaseException as err:  # pylint: disable=broad-except
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
