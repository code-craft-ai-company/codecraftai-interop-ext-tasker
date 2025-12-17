import automojo.testbase as testbase

from automojo.interop.protocols.tasker.taskingevent import TaskingEvent


def test_properties_return_values() -> None:
    evt = TaskingEvent("tid1", "started", {"k": "v"})
    testbase.assert_equal(evt.tasking_id, "tid1")
    testbase.assert_equal(evt.event_name, "started")
    testbase.assert_equal(evt.payload, {"k": "v"})
    return


def test_as_dict_serialization() -> None:
    evt = TaskingEvent("tid2", "progress", {"p": 1})
    expected = {"event-name": "progress", "payload": {"p": 1}, "tasking-id": "tid2"}
    testbase.assert_equal(evt.as_dict(), expected)
    return


def test_from_dict_creates_equivalent_event() -> None:
    src_evt = TaskingEvent("tid3", "done", None)
    data = src_evt.as_dict()
    new_evt = TaskingEvent.from_dict(data)
    testbase.assert_equal(new_evt.tasking_id, "tid3")
    testbase.assert_equal(new_evt.event_name, "done")
    testbase.assert_equal(new_evt.payload, None)
    return
