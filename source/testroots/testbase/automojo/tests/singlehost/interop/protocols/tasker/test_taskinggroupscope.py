import datetime
import ccai.testbase as testbase

from ccai.testbase.results.model.progressinfo import ProgressInfo
from ccai.testbase.results.model.progresscode import ProgressCode
from ccai.testbase.results.model.progresstype import ProgressType

from ccai.interop.protocols.tasker.taskinggroupscope import TaskingGroupScope, TaskingGroupState


class DummyPromise:
    def __init__(self, tasking_id, fail_cancel=False):
        self.tasking_id = tasking_id
        self.cancel_called = False
        self.fail_cancel = fail_cancel

    def cancel(self):
        self.cancel_called = True
        if self.fail_cancel:
            raise RuntimeError("cancel failure")


class DummyRecorder:
    def __init__(self):
        self.records = []
        self.cleared = None
        self.posted = []
        self.summary_updates = 0

    def record(self, item):
        self.records.append(item)

    def clear_task_progress(self, ids):
        self.cleared = list(ids)

    def update_summary(self):
        self.summary_updates += 1

    def post_task_progress(self, progress_list):
        self.posted.append(progress_list)


class DummyAdapter:
    def __init__(self):
        self.checked = None

    def checkin_tasker_nodes(self, nodes):
        self.checked = list(nodes)


class DummyController:
    def __init__(self):
        self.wait_called = False
        self.promises_waited = None

    def execute_tasking_on_node_list(self, *args, **kwargs):
        return []

    def execute_tasking_on_node(self, *args, **kwargs):
        return None

    def wait_for_tasking_results(self, promises, aspects=None):
        self.wait_called = True
        self.promises_waited = list(promises)
        return ["result"]

    def wait_for_all_to_event(self, event_name, promises):
        return ["all"]

    def wait_for_any_to_event(self, event_name, promises):
        return ["any"]


def make_scope(promises=None):
    adapter = DummyAdapter()
    controller = DummyController()
    recorder = DummyRecorder()

    class TG:
        def __init__(self):
            self.inst_id = "gid"
            self.finalized = False

        def finalize(self):
            self.finalized = True

    tgroup = TG()
    nodes = ["n1", "n2"]
    aspects = None
    scope = TaskingGroupScope(
        name="scope",
        adapter=adapter,
        controller=controller,
        recorder=recorder,
        tgroup=tgroup,
        tnodes=nodes,
        aspects=aspects,
    )
    if promises:
        scope._promises = promises
    return scope, adapter, controller, recorder, tgroup


def test_cancel_tasks_collects_errors() -> None:
    prom1 = DummyPromise("p1")
    prom2 = DummyPromise("p2", fail_cancel=True)
    scope, _, _, _, _ = make_scope([prom1, prom2])
    err = None
    try:
        scope.cancel_tasks()
    except RuntimeError as exc:
        err = exc
    testbase.assert_equal(err is not None, True)
    testbase.assert_equal("p2" in str(err), True)
    testbase.assert_equal(prom1.cancel_called, True)
    testbase.assert_equal(prom2.cancel_called, True)
    return


def test_clear_summary_progress_calls_recorder() -> None:
    prom1 = DummyPromise("a")
    prom2 = DummyPromise("b")
    scope, _, _, recorder, _ = make_scope([prom1, prom2])
    scope._clear_summary_progress()
    testbase.assert_equal(recorder.cleared, ["a", "b"])
    testbase.assert_equal(recorder.summary_updates, 1)
    return


def test_notify_summary_progress_updates_recorder() -> None:
    scope, _, _, recorder, _ = make_scope([])
    pi = ProgressInfo(
        id="tid",
        category="cat",
        moniker="mon",
        ptype=ProgressType.Sequential,
        range_min="0",
        range_max="1",
        position="0",
        status=ProgressCode.Running,
        when=datetime.datetime.now(),
    )
    scope._notify_summary_progress([pi])
    testbase.assert_equal(scope._progress_reported, True)
    testbase.assert_equal(recorder.posted[0], [pi])
    testbase.assert_equal(recorder.summary_updates, 1)
    return


def test_update_group_records_results_once() -> None:
    scope, _, _, recorder, _ = make_scope([])
    scope._results = ["r1", "r2"]
    scope._update_group()
    scope._update_group()
    testbase.assert_equal(recorder.records, ["r1", "r2"])
    return


def test_finalize_sync_checks_in_nodes() -> None:
    prom = DummyPromise("tid")
    scope, adapter, controller, recorder, tgroup = make_scope([prom])
    scope._results = ["r1"]
    scope.finalize(sync=False)
    testbase.assert_equal(tgroup.finalized, True)
    testbase.assert_equal(recorder.records[-1], tgroup)
    testbase.assert_equal(adapter.checked, ["n1", "n2"])
    return

