"""
    .. module:: taskinggroupscope
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: taskinggroupscope module.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []

from typing import List, Optional, Type, Union, TYPE_CHECKING

from ccai.xmodules.xlogging.enhancedloggers import getEnhancedLogger
import os
import weakref

from ccai.errors.exceptions import SemanticError
from ccai.errors.xtraceback import format_exception

from ccai.testbase.results.model.taskinggroup import TaskingGroup
from ccai.testbase.results.model.taskingresult import TaskingResult
from ccai.testbase.results.model.progressinfo import ProgressInfo

from ccai.testbase.results.recorders.resultrecorder import ResultRecorder

from ccai.interop.protocols.tasker.taskeraspects import TaskerAspects

from ccai.interop.protocols.tasker.taskernode import TaskerNode
from ccai.interop.protocols.tasker.tasking import Tasking, TaskingIdentity
from ccai.interop.protocols.tasker.taskingresultpromise import TaskingResultPromise
from ccai.interop.protocols.tasker.taskercontroller import TaskerController
from ccai.interop.protocols.tasker.taskingevent import TaskingEvent

if TYPE_CHECKING:
    from ccai.testbase.sequencing.testsequencer import TestSequencer
    from ccai.interop.protocols.tasker.taskingadapter import TaskingAdapter


logger = getEnhancedLogger()


class TaskingGroupState:
    """
        Enumeration values describing the state of a tasking group.
    """

    NotStarted = 0
    Running = 1
    Completed = 2


class TaskingGroupScope:
    """
        Context manager used to coordinate the execution of a group of taskings.
    """

    def __init__(
        self,
        name: str,
        adapter: "TaskingAdapter",
        controller: TaskerController,
        recorder: ResultRecorder,
        tgroup: TaskingGroup,
        tnodes: List[TaskerNode],
        aspects: TaskerAspects,
        sequencer: Optional["TestSequencer"] = None,
    ):
        """
            Creates a :class:`TaskingGroupScope` used to manage a set of tasks.
            
            :param name: The name of the tasking group.
            :param adapter: Adapter providing access to tasker nodes.
            :param controller: Controller used to dispatch taskings.
            :param recorder: Result recorder for this group.
            :param tgroup: The :class:`TaskingGroup` result container.
            :param tnodes: Nodes the tasking will execute on.
            :param aspects: Default aspects for task execution.
            :param sequencer: Optional test sequencer instance.
        """

        self._name = name
        self._adapter_ref = weakref.ref(adapter)
        self._controller = controller
        self._recorder = recorder
        self._tgroup = tgroup
        self._tnodes: List[TaskerNode] = tnodes
        self._aspects = aspects
        self._sequencer = sequencer

        self._state = TaskingGroupState.NotStarted
        self._promises: List[TaskingResultPromise] = []
        self._results = None
        self._results_written = False

        self._progress_reported = False

        return

    @property
    def adapter(self) -> "TaskingAdapter":
        """
            Returns the adapter that owns this scope.

            :returns: The owning :class:`TaskingAdapter` instance.
        """
        return self._adapter_ref()

    @property
    def name(self) -> str:
        """
            Name of the tasking group.

            :returns: The tasking group name.
        """
        return self._name

    @property
    def promises(self) -> List[TaskingResultPromise]:
        """
            List of promises associated with the group.

            :returns: A list of :class:`TaskingResultPromise` objects.
        """
        plist = [p for p in self._promises]
        return plist

    @property
    def sequencer(self) -> "TestSequencer":
        """
            Return the associated test sequencer.

            :returns: The :class:`TestSequencer` instance or ``None``.
        """
        return self._sequencer

    @property
    def nodes(self) -> List[TaskerNode]:
        """
            List of tasker nodes used by the group.

            :returns: List of :class:`TaskerNode` objects.
        """
        return self._tnodes

    def __enter__(self) -> "TaskingGroupScope":
        """Initializes and returns this context manager.

        :returns: This :class:`TaskingGroupScope` instance.
        """
        self.initialize()
        return self

    def __exit__(self, ex_type, ex_inst, ex_tb) -> bool:
        """Context manager exit handler.

        :returns: ``False`` to allow exceptions to propagate.
        """
        if ex_inst is not None:
            err_msg = format_exception(ex_inst)
            logger.error(err_msg)

            self.cancel_tasks()

            # We don't want to handle exceptions here; if any AssertionError types come through,
            # they are likely due to a consolidated check, and they should be allowed to propagate.

        if self._progress_reported:
            self._clear_summary_progress()

        self.finalize()
        return False

    def initialize(self):
        """
            Records the initial task group state.
        """
        self._recorder.record(self._tgroup)
        return

    def cancel_tasks(self):
        """
            Cancel all running taskings in the group.
        """
        errors = []

        for promise in self._promises:
            try:
                promise.cancel()
            except Exception as xcpt:
                errors.append((promise.tasking_id, xcpt))

        if len(errors) > 0:
            errmsg_lines = [
                "Errors encountered while attempting to cancel tasks.",
                "ERRORS:",
            ]

            for tasking_id, xcpt in errors:
                message = str(xcpt)
                errmsg_lines.append(f"    {tasking_id}: {message}")

            err_msg = os.linesep.join(errmsg_lines)
            raise RuntimeError(err_msg)

        return

    def execute_tasking(
        self,
        *,
        tasking: Union[TaskingIdentity, Type[Tasking]],
        ncount: int = 1,
        aspects: Optional[TaskerAspects] = None,
        **kwargs,
    ) -> List[TaskingResultPromise]:
        """
            Execute a tasking across multiple nodes.

            :param tasking: The tasking identity or class to execute.
            :param ncount: Number of instances to execute.
            :param aspects: Execution aspects for the task.
            :param kwargs: Additional keyword arguments for the task.

            :returns: A list of :class:`TaskingResultPromise` objects.
        """

        if aspects is None:
            aspects = self._aspects

        if self._state != TaskingGroupState.NotStarted:
            errmsg = f"The tasking group '{self._name}' has already been started."
            raise SemanticError(errmsg)

        parent_id = self._tgroup.inst_id

        new_promises = self._controller.execute_tasking_on_node_list(
            self._tnodes,
            tasking=tasking,
            ncount=ncount,
            parent_id=parent_id,
            aspects=aspects,
            **kwargs,
        )
        self._promises.extend(new_promises)

        return new_promises

    def execute_tasking_on_node(
        self,
        node: TaskerNode,
        *,
        tasking: Union[TaskingIdentity, Type[Tasking]],
        ncount: int = 1,
        aspects: Optional[TaskerAspects] = None,
        **kwargs,
    ) -> List[TaskingResultPromise]:
        """
            Execute a tasking on a single node.

            :param node: Node where the tasking will run.
            :param tasking: The tasking identity or class to execute.
            :param ncount: Number of instances to execute.
            :param aspects: Execution aspects for the task.
            :param kwargs: Additional keyword arguments for the task.

            :returns: A :class:`TaskingResultPromise` object.
        """

        if aspects is None:
            aspects = self._aspects

        if self._state != TaskingGroupState.NotStarted:
            errmsg = f"The tasking group '{self._name}' has already been started."
            raise SemanticError(errmsg)

        parent_id = self._tgroup.inst_id

        promise = self._controller.execute_tasking_on_node(
            node,
            tasking=tasking,
            ncount=ncount,
            parent_id=parent_id,
            aspects=aspects,
            **kwargs,
        )
        self._promises.append(promise)

        return promise

    def finalize(self, sync: bool = True):
        """
            Finalize the task group and optionally synchronize.
        """

        adapter = self.adapter

        if sync:
            self.synchronize()

        self._tgroup.finalize()
        self._recorder.record(self._tgroup)

        adapter.checkin_tasker_nodes(self._tnodes)

        return

    def mark_activity(
        self, activity_name: str, target: str = "NA", detail: Optional[dict] = None
    ):
        """
            A convenience method for marking activity in the current test scope.
        """
        if self._sequencer is not None:
            self._sequencer.mark_activity(activity_name, target=target, detail=detail)
        return

    def synchronize(self):
        """
            Synchronize results for all promises.
        """
        if len(self._promises) > 0:
            self.wait_for_tasking_results()

        return

    def wait_for_all_to_event(
        self, event_name: str, aspects: Optional[TaskerAspects] = None
    ) -> List[TaskingEvent]:
        """
            Wait for all taskings to fire a specific event.
        """

        if aspects is None:
            aspects = self._aspects

        events_found = self._controller.wait_for_all_to_event(
            event_name, self._promises, aspects=aspects
        )

        return events_found

    def wait_for_any_to_event(
        self, event_name: str, aspects: Optional[TaskerAspects] = None
    ) -> List[TaskingEvent]:
        """
            Wait for any tasking to fire a specific event.
        """

        if aspects is None:
            aspects = self._aspects

        events_found = self._controller.wait_for_any_to_event(
            event_name, self._promises, aspects=aspects
        )

        return events_found

    def wait_for_tasking_results(
        self, aspects: Optional[TaskerAspects] = None
    ) -> List[TaskingResult]:
        """
            Wait for completion and return all tasking results.
        """

        if aspects is None:
            aspects = self._aspects

        if self._results is None:
            self._results = self._controller.wait_for_tasking_results(
                self._promises, aspects=aspects
            )
            self._update_group()

        return self._results

    def _clear_summary_progress(self):
        """
            Clear summary progress information.
        """

        task_ids = []

        # Collect the progress
        for p in self._promises:
            task_ids.append(p.tasking_id)

        self._recorder.clear_task_progress(task_ids)
        self._recorder.update_summary()

        return

    def _notify_summary_progress(self, progress_list: List[ProgressInfo]):
        """
            Update summary progress information using the result recorder.

            :param progress_list: List of :class:`ProgressInfo` objects to post.
        """
        self._progress_reported = True

        self._recorder.post_task_progress(progress_list)
        self._recorder.update_summary()

        return

    def _update_group(self):
        """
            Record results for the group once.
        """

        if not self._results_written:
            self._results_written = True
            for res in self._results:
                self._recorder.record(res)

        return
