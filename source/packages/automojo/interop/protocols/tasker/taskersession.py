"""
    .. module:: taskersession
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`TaskerSession` class which is used to
    store the tasking data associated with a session.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
    
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING


import json
import multiprocessing

import os
import pickle
import threading
import traceback
import weakref

from collections import OrderedDict
from datetime import datetime
from functools import partial
from http.server import HTTPServer, BaseHTTPRequestHandler
from uuid import uuid4

from http import HTTPStatus

from automojo.errors.exceptions import SemanticError

from automojo.errors.xtraceback import create_traceback_detail, format_traceback_detail

from automojo.testbase.results.model.progresscode import ProgressCode
from automojo.testbase.results.model.progressinfo import ProgressInfo
from automojo.testbase.results.model.resultcode import ResultCode
from automojo.testbase.results.model.taskingresult import TaskingResult

from automojo.xmodules.ximport import import_by_name

from automojo.interop.protocols.tasker.taskingresultpromise import TaskingRef
from automojo.interop.protocols.tasker.taskeraspects import (
    TaskerAspects,
    DEFAULT_TASKER_ASPECTS,
)
from automojo.interop.protocols.tasker.tasking import Tasking, TaskingManager

if TYPE_CHECKING:
    from automojo.interop.protocols.tasker.taskerservice import TaskerService


class EventNotificationHandler(BaseHTTPRequestHandler):
    """
        Handles HTTP callbacks used to deliver task progress events.
    """

    def __init__(self, service_class, session, *args, **kwargs):
        """
            Initialize the notification handler used for event callbacks.
            
            :param service_class: Service class controlling this session.
            :param session: Owning :class:`TaskerSession` instance.
        """

        self._service_class = service_class
        self._tasker_session_ref = weakref.ref(session)
        self._logger = self._service_class.logger
        super().__init__(*args, **kwargs)
        return

    @property
    def tasker_session(self) -> "TaskerSession":
        """Return the owning :class:`TaskerSession` instance.

        :returns: The associated :class:`TaskerSession` object.
        """
        return self._tasker_session_ref()

    def do_POST(self):
        """
            Handle HTTP POST callbacks containing progress events.
        """

        if "Content-Type" in self.headers:
            content_type = self.headers["Content-Type"].lower()
            if content_type == "application/json":

                file_length = int(self.headers["Content-Length"])

                content = self.rfile.read(file_length)

                try:
                    event = json.loads(content)
                    self.tasker_session.post_event(event)

                    self.send_response(HTTPStatus.ACCEPTED, "Accepted")
                    self.end_headers()
                except Exception as xcpt:
                    errdetail = traceback.format_exc()
                    self._logger.error(errdetail)
                    self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR, errdetail)
                    self.end_headers()
        return


class TaskerSession:
    """
        Manages tasking operations for a specific worker session.
    """

    def __init__(
        self,
        service_class: "TaskerService",
        worker: str,
        wref: str,
        output_directory: str,
        log_level: int,
        notify_url: str = None,
        notify_headers: Dict[str, str] = None,
        aspects: TaskerAspects = DEFAULT_TASKER_ASPECTS,
    ):
        """
            Creates a session for managing taskings on a tasker service.
            
            :param service_class: The service class controlling this session.
            :param worker: Worker name for logging and identification.
            :param wref: Worker reference value.
            :param output_directory: Directory for output files.
            :param log_level: Logging level for taskings.
            :param notify_url: Optional notification callback URL.
            :param notify_headers: Optional HTTP headers for notifications.
            :param aspects: Default aspects for task execution.
        """

        self._service_class = service_class

        self._worker = worker
        self._wref = wref
        self._output_directory = os.path.abspath(
            os.path.expandvars(os.path.expanduser(output_directory))
        )

        self._log_level = log_level

        self._notify_url = notify_url
        self._notify_headers = notify_headers

        self._aspects = aspects

        self._session_id = str(uuid4())

        self._start = datetime.now()
        self._last_activity = datetime.now()

        self._taskings_table = OrderedDict()
        self._results_table = OrderedDict()
        self._status_table = OrderedDict()
        self._progress_table = OrderedDict()
        self._events_table = {}

        self._session_lock = threading.Lock()

        self._events_server = None
        self._events_endpoint = None

        return

    @property
    def aspects(self):
        """
            Default aspects used for task execution.

            :returns: The :class:`TaskerAspects` assigned to this session.
        """
        return self._aspects

    @property
    def last_activity(self) -> datetime:
        """
            Timestamp of the last session activity.

            :returns: The :class:`datetime` of the most recent activity.
        """
        return self._last_activity

    @property
    def output_directory(self):
        """
            Directory where task outputs are written.

            :returns: The absolute path to the output directory.
        """
        return self._output_directory

    @property
    def progresses(self) -> OrderedDict:
        """
            Dictionary mapping tasking ids to progress info.

            :returns: Ordered dictionary of :class:`ProgressInfo` objects.
        """
        return self._progress_table

    @property
    def results(self) -> OrderedDict:
        """
            Dictionary of task results.

            :returns: Ordered dictionary of :class:`TaskingResult` objects.
        """
        return self._results_table

    @property
    def session_id(self) -> str:
        """
            Identifier for this session.

            :returns: Session identifier string.
        """
        return self._session_id

    @property
    def start(self) -> datetime:
        """
            Timestamp when the session was created.

            :returns: The :class:`datetime` the session was started.
        """
        return self._start

    @property
    def statuses(self) -> OrderedDict:
        """
            Dictionary mapping tasking ids to status codes.

            :returns: Ordered dictionary of task status values.
        """
        return self._status_table

    @property
    def taskings(self) -> OrderedDict:
        """
            Dictionary of active tasking objects.

            :returns: Ordered dictionary of :class:`Tasking` objects.
        """
        return self._taskings_table

    @property
    def log_level(self) -> int:
        """
            Logging level used for task output.

            :returns: The numeric logging level.
        """
        return self._log_level

    def dispose_tasking(self, tasking_id: str):
        """
            Dispose of a tasking and release its resources.
            
            :param tasking_id: Identifier of the tasking to dispose.
        """

        self._session_lock.acquire()

        try:
            if tasking_id in self.taskings:

                task: Tasking = self.taskings[tasking_id]
                del self.taskings[tasking_id]

                self._session_lock.release()
                try:
                    task.shutdown()
                finally:
                    self._session_lock.acquire()
        finally:
            self._session_lock.release()

        return

    def cancel_tasking(self, tasking_id: str):
        """
            Cancel a running tasking if it is in a cancellable state.
            
            :param tasking_id: Identifier of the tasking to cancel.
        """

        self._session_lock.acquire()

        try:

            if tasking_id in self._taskings_table:
                tasking: Tasking = self._taskings_table[tasking_id]

                if tasking_id in self._status_table:
                    tstatus = self._status_table[tasking_id]

                    if tstatus in [
                        ProgressCode.NotStarted,
                        ProgressCode.Paused,
                        ProgressCode.Running,
                    ]:
                        tasking.shutdown()
                else:
                    errmsg = f"Unable to cancel tasking. No status found for tasking_id={tasking_id}."
                    raise RuntimeError(errmsg)
            else:
                errmsg = (
                    f"Unable to cancel tasking for unknown tasking_id={tasking_id}."
                )
                raise RuntimeError(errmsg)
        finally:
            self._session_lock.release()

        return

    def get_tasking(self, tasking_id: str) -> Tasking:
        """
            Retrieve the tasking instance for a given tasking identifier.
            
            :param tasking_id: Identifier of the tasking to retrieve.
            
            :returns: The :class:`Tasking` object for the id.
        """

        tasking = None

        self._session_lock.acquire()

        try:

            if tasking_id in self._taskings_table:
                tasking = self._taskings_table[tasking_id]
            else:
                errmsg = (
                    f"Unable to cancel tasking for unknown tasking_id={tasking_id}."
                )
                raise RuntimeError(errmsg)
        finally:
            self._session_lock.release()

        return tasking

    def execute_tasking(
        self,
        module_name: str,
        tasking_name: str,
        parent_id: Optional[str] = None,
        aspects: Optional[TaskerAspects] = None,
        **kwargs,
    ) -> TaskingRef:
        """
            Instantiate and execute a tasking in a separate process.
            
            :param module_name: Module containing the tasking class.
            :param tasking_name: Name of the tasking class to instantiate.
            :param parent_id: Optional parent tasking identifier.
            :param aspects: Tasker aspects controlling execution parameters.
            :param kwargs: Additional keyword arguments for the tasking.
            
            :returns: A :class:`TaskingRef` referencing the running task.
        """

        if aspects is None:
            aspects = self._aspects

        taskref: TaskingRef = None

        # Make sure the requested "Tasking" actually exists before we attempt to instantiate one in a remote
        # process.
        module = import_by_name(module_name)

        if hasattr(module, tasking_name):

            tasking_type = getattr(module, tasking_name)

            tasking_id = str(uuid4())

            log_dir = None

            if not os.path.exists(self._output_directory):
                os.makedirs(self._output_directory)

            prefix = tasking_type.PREFIX

            log_dir = os.path.join(
                self._output_directory, "taskings", f"{prefix}-{tasking_id}"
            )
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            log_file: str = os.path.join(log_dir, f"tasking-{tasking_id}.log")

            taskref = TaskingRef(module_name, tasking_id, tasking_name, log_dir)

            # Create an instance of a TaskingManager to manage the remote process, we will manage the scope
            # if this instance by delegating it to a thread that will execute the task and monitor its lifespan
            mpctx = multiprocessing.get_context("spawn")
            tasking_manager = TaskingManager(ctx=mpctx)
            tasking_manager.start()

            start_msg_lines = [
                "=============================== Instantiating Task ===============================",
                f"worker: {self._worker}",
                f"worker-ref: {self._wref}",
                f"module_name: {module_name}",
                f"tasking_name: {tasking_name}",
                f"tasking_id: {tasking_id}",
                f"parent_id: {parent_id}",
                f"output_directory: {self._output_directory}",
                f"log_dir: {log_dir}",
                f"log_file: {log_file}",
                f"notify_url: {self._notify_url}",
                f"notify_headers: {repr(self._notify_headers)}",
                f"log_level: {self._log_level}",
                "==================================================================================",
            ]
            start_msg = os.linesep.join(start_msg_lines)

            with open(log_file, "+a") as tlogf:
                tlogf.write(start_msg)

            tasking = tasking_manager.instantiate_tasking(
                self._worker,
                self._wref,
                module_name,
                tasking_name,
                tasking_id,
                parent_id,
                self._output_directory,
                log_dir,
                log_file,
                self._log_level,
                self._events_endpoint,
                self._notify_url,
                self._notify_headers,
                aspects=aspects,
            )

            self._session_lock.acquire()
            try:
                self.statuses[tasking_id] = str(ProgressCode.NotStarted.value)
                self.taskings[tasking_id] = tasking
            finally:
                self._session_lock.release()

            sgate = threading.Event()
            sgate.clear()

            dargs = (
                sgate,
                tasking_manager,
                tasking,
                tasking_name,
                tasking_id,
                prefix,
                parent_id,
                log_file,
                kwargs,
                aspects,
            )

            # We have to dispatch the task with a thread, because we need to leave a local thread running
            # to monitor the progress of the task.
            taskthread = threading.Thread(
                target=self._dispatch_task, args=dargs, daemon=True
            )
            taskthread.start()

            sgate.wait()

        else:
            errmsg = f"The specified tasking 'module' was not found. module={module_name} tasking={tasking_name}"
            raise ValueError(errmsg)

        return taskref

    def get_tasking_events(self, tasking_id: str) -> str:
        """
            Retrieve all events posted for a tasking.
            
            :param tasking_id: Identifier of the tasking to query.
            
            :returns: Pickled list of event dictionaries.
        """

        events = []

        self._session_lock.acquire()
        try:
            if tasking_id in self._events_table:
                events = self._events_table[tasking_id]
        finally:
            self._session_lock.release()

        events_str = pickle.dumps(events)

        return events_str

    def get_tasking_progress(self, tasking_id: str) -> str:
        """
            Obtain the progress information for a running tasking.
            
            :param tasking_id: Identifier of the tasking to query.
            
            :returns: Pickled :class:`ProgressInfo` or ``None``.
        """

        progress = None

        self._session_lock.acquire()
        try:
            if tasking_id in self._progress_table:
                progress = self._progress_table[tasking_id]
        finally:
            self._session_lock.release()

        progress_str = None
        if progress is not None:
            progress_str = pickle.dumps(progress)

        return progress_str

    def get_tasking_result(self, tasking_id: str) -> str:
        """
            Retrieve the final :class:`TaskingResult` for a tasking.
            
            :param tasking_id: Identifier of the tasking whose result is requested.
            
            :returns: Pickled :class:`TaskingResult` data.
        """

        self._session_lock.acquire()
        try:
            if tasking_id in self._results_table:
                result = self._results_table[tasking_id]
            else:
                if tasking_id in self._taskings_table:
                    tstatus = self._status_table[tasking_id]

                    if not (
                        tstatus == ProgressCode.Completed
                        or tstatus == ProgressCode.Errored
                        or tstatus == ProgressCode.Failed
                    ):
                        errmsg = f"The task for tasking_id='{tasking_id}' is not in a completed state. The results are not yet available."
                        raise SemanticError(errmsg)
                else:
                    errmsg = f"The specified tasking tasking_id={tasking_id} is not known to this TaskerService instance."
                    raise ValueError(errmsg)
        finally:
            self._session_lock.release()

        result_str = pickle.dumps(result)

        return result_str

    def get_tasking_status(self, tasking_id: str) -> str:
        """
            Return the current status code for a running tasking.
            
            :param tasking_id: Identifier of the tasking.
            
            :returns: Status string from the progress table.
        """

        self._session_lock.acquire()
        try:
            if tasking_id in self._status_table:
                tstatus = str(self._status_table[tasking_id])
        finally:
            self._session_lock.release()

        return tstatus

    def has_completed_and_result_ready(self, tasking_id) -> bool:
        """
            Check if a tasking has completed and its result is available.
            
            :param tasking_id: Identifier of the tasking.
            
            :returns: ``True`` if the tasking finished and a result exists.
        """

        complete_and_ready = False

        self._session_lock.acquire()
        try:
            if tasking_id in self._status_table:
                tstatus = str(self._status_table[tasking_id])

                if (
                    tstatus == ProgressCode.Completed
                    or tstatus == ProgressCode.Errored
                    or tstatus == ProgressCode.Failed
                ):
                    if tasking_id in self._results_table:
                        complete_and_ready = True

        finally:
            self._session_lock.release()

        return complete_and_ready

    def post_event(self, event: Dict[str, Any]):
        """
            Record an event generated by a running tasking.
            
            :param event: Dictionary describing the event.
        """

        self._session_lock.acquire()
        try:
            tasking_id = event["tasking-id"]

            if tasking_id in self._events_table:
                tasking_events: List[dict] = self._events_table[tasking_id]
                tasking_events.append(event)
            else:
                tasking_events = [event]
                self._events_table[tasking_id] = tasking_events

        finally:
            self._session_lock.release()

        return

    def shutdown(self):
        """
            Shutdown running taskings and stop the event server.
        """
            
        # Go through all of the tasks and if they have not completed, cancel them
        tasking_id: str
        tasking: Tasking
        tstatus: ProgressCode
        
        tasking_table = None
        status_table = None
        events_server = None
        
        self._session_lock.acquire()
        try:
            tasking_table = self._taskings_table
            status_table = self._status_table
            events_server = self._events_server
        finally:
            self._session_lock.release()
        
        try:
            for tasking_id, tasking in tasking_table.items():
                tstatus = status_table[tasking_id]

                if tstatus in [
                    ProgressCode.NotStarted,
                    ProgressCode.Paused,
                    ProgressCode.Running,
                ]:
                    tasking.shutdown()
        finally:
            events_server.shutdown()
        
        return
        
    def start_event_server(self) -> Tuple[str, int]:
        """
        Start the HTTP server used to receive progress events from the tasking
        processes.

        :returns: Tuple of host and port where the server is listening.
        """
            
        sgate = threading.Event()
        sgate.clear()
        
        self._event_thread = threading.Thread(target=self._event_server_thread, name="tasker-session-event-svr", args=(sgate,), daemon=True)
        self._event_thread.start()
        sgate.wait()
        
        return
            
    def _dispatch_task(
            self,
            sgate: threading.Event,
            tasking_manager: TaskingManager,
            tasking: Tasking,
            tasking_name: str,
            tasking_id: str,
            prefix: str,
            parent_id: str,
            log_file: str,
            kwparams: dict,
            aspects: TaskerAspects,
            ):
        """
            Thread entry point used to execute a tasking in a remote process.

            :param sgate: Synchronization gate to signal start.
            :param tasking_manager: Manager controlling the tasking process.
            :param tasking: Tasking instance to run.
            :param tasking_name: Name of the tasking class.
            :param tasking_id: Identifier for the tasking instance.
            :param prefix: Prefix for log files.
            :param parent_id: Parent task identifier.
            :param log_file: Path to the task log file.
            :param kwparams: Keyword parameters for the task execution.
            :param aspects: Task execution aspects.
        """
            
        # Notify the thread starting us that we have started.
        sgate.set()
        
        self._session_lock.acquire()
        try:
            self._status_table[tasking_id] = str(ProgressCode.NotStarted.value)
        finally:
            self._session_lock.release()
        del sgate
        
        self._service_class.log_info(
            f"Dispatching task_type={tasking_name} id={tasking_id}"
        )
        
        progress = None
        
        try:
            inactivity_timeout = None
            if aspects is not None:
                inactivity_timeout = aspects.inactivity_timeout
                
                progress_queue = tasking_manager.Queue()
                
                tasking.execute(progress_queue, kwparams)
                
                while True:
                
                    progress: ProgressInfo = progress_queue.get(
                    block=True, timeout=inactivity_timeout
                    )
                    
                    self._session_lock.acquire()
                    try:
                        self._progress_table[tasking_id] = progress

                        if isinstance(progress, TaskingResult):
                            result: TaskingResult = progress

                            if len(result.errors) > 0:
                                self._status_table[tasking_id] = str(ProgressCode.Errored.value)
                            elif len(result.failures) > 0:
                                self._status_table[tasking_id] = str(ProgressCode.Failed.value)
                            else:
                                self._status_table[tasking_id] = str(ProgressCode.Completed.value)
                                self._results_table[tasking_id] = result
                                break
                        else:
                            prog_status = str(progress.status.value)
                            self._status_table[tasking_id] = prog_status
                
                    finally:
                        self._session_lock.release()
                
        except BaseException as err:
            tbdetail = create_traceback_detail(err)
            
            errmsg_lines = format_traceback_detail(tbdetail)
            errmsg = os.linesep.join(errmsg_lines)
            
            self._service_class.log_error(errmsg)
                    
            with open(log_file, "+a") as tlogf:
                tlogf.write(errmsg)
            
            tresult = TaskingResult(
            tasking_id, tasking_name, parent_id, ResultCode.ERRORED, prefix=prefix
            )
            self._status_table[tasking_id] = str(ProgressCode.Errored.value)
            tresult.add_error(tbdetail)
            self._results_table[tasking_id] = tresult
            
            raise
        
        finally:
            tasking_manager.shutdown()
        
        return
            
    def _event_server_thread(self, sgate: threading.Event):
        """
            Thread responsible for hosting the HTTP server used to receive tasking
            progress events.

            :param sgate: Synchronization gate used to signal when the server is ready.
        """
        handler_type = partial(EventNotificationHandler, self._service_class, self)

        localhost = "127.0.0.1"

        server = HTTPServer((localhost, 0), handler_type)
        server_port = server.server_port

        self._session_lock.acquire()
        try:
            self._events_server = server
            self._events_endpoint = (localhost, server_port)
        finally:
            self._session_lock.release()

        # After we setup the HTTP server and capture the server endpoint information,
        # set the startgate to allow the thread starting the server to proceed.
        sgate.set()

        server.serve_forever()

        return
