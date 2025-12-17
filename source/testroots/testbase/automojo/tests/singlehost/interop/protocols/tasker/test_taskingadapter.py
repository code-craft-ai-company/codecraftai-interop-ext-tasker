import automojo.testbase as testbase
from automojo.interop.protocols.tasker.taskingadapter import TaskingAdapter
from automojo.interop.protocols.tasker.taskernode import TaskerNode
from automojo.interop.protocols.tasker.taskinggroupscope import TaskingGroupScope


class DummyController:
    def __init__(self, nodes):
        self._tasker_nodes = nodes

    @property
    def tasker_nodes(self):
        return self._tasker_nodes


class DummySequencer:
    def __init__(self):
        self.top_scope_id = "root"
        self.recorder = object()
        self.created_groups = []

    def get_top_scope_id(self):
        return self.top_scope_id

    def get_recorder(self):
        return self.recorder

    def create_tasking_group(self, scope_id, name, parent_inst):
        grp = {"scope_id": scope_id, "name": name, "parent": parent_inst}
        self.created_groups.append(grp)
        return grp


def create_adapter(node_count=3):
    nodes = [TaskerNode("127.0.0.1", i) for i in range(node_count)]
    ctrl = DummyController(nodes)
    seq = DummySequencer()
    adapter = TaskingAdapter(ctrl, seq)
    return adapter, ctrl, seq, nodes


def test_available_nodes_after_init():
    adapter, _, _, nodes = create_adapter(2)
    testbase.assert_equal(adapter.available_node_count, 2)
    testbase.assert_equal(adapter.available_nodes, nodes)
    return


def test_checkout_and_checkin_nodes():
    adapter, _, _, nodes = create_adapter(3)
    checked = adapter.checkout_tasker_nodes(2)
    testbase.assert_equal(len(checked), 2)
    testbase.assert_equal(adapter.available_node_count, 1)
    testbase.assert_equal(len(adapter._checked_out), 2)
    adapter.checkin_tasker_nodes(checked)
    testbase.assert_equal(adapter.available_node_count, 3)
    testbase.assert_equal(len(adapter._checked_out), 0)
    return


def test_checkout_nodes_overflow_raises():
    adapter, _, _, _ = create_adapter(1)
    exc = None
    try:
        adapter.checkout_tasker_nodes(2)
    except ValueError as err:
        exc = err
    testbase.assert_equal(isinstance(exc, ValueError), True)
    return


def test_create_tasking_group_scope_uses_nodes_and_sequencer():
    adapter, _, seq, nodes = create_adapter(3)
    scope = adapter.create_tasking_group_scope("grp", node_count=2)
    testbase.assert_equal(isinstance(scope, TaskingGroupScope), True)
    testbase.assert_equal(len(scope.nodes), 2)
    testbase.assert_equal(adapter.available_node_count, 1)
    testbase.assert_equal(len(seq.created_groups), 1)
    testbase.assert_equal(seq.created_groups[0]["name"], "grp")
    return

