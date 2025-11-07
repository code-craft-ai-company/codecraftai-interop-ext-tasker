"""
    .. module:: taskernode
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: The :class:`TaskerNode` object used to interact with a remote tasker service.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional

import logging
from automojo.xmodules.xlogging.enhancedloggers import getEnhancedLogger
import rpyc
import pickle
import weakref


from automojo.testbase.results.model.taskingresult import TaskingResult
from automojo.testbase.results.model.progressinfo import ProgressInfo
from automojo.testbase.results.model.progressdelivery import SummaryProgressDelivery

from automojo.interop.protocols.tasker.taskingresultpromise import TaskingResultPromise
from automojo.interop.protocols.tasker.taskeraspects import (
    TaskerAspects,
    DEFAULT_TASKER_ASPECTS,
)
from automojo.interop.protocols.tasker.taskingevent import TaskingEvent

TASKER_PROTOCOL_CONFIG = {
    "allow_public_attrs": True,
    "allow_pickle": True,
    "import_custom_exceptions": True,
    "allow_custom_exceptions": True,
    "sync_request_timeout": 120,
    "logger": getEnhancedLogger(),
}


class TaskerNode:
    """
        The :class:`TaskerNode` object represents a remote tasker service endpoint.
    """

    def __init__(
        self,
        ipaddr: str,
        port: int,
        summary_progress: Optional[SummaryProgressDelivery] = None,
        protocol_config: Optional[Dict[str, Any]] = TASKER_PROTOCOL_CONFIG,
        aspect: TaskerAspects = DEFAULT_TASKER_ASPECTS,
    ):
        """
            Initializes a :class:`TaskerNode` that communicates with a tasker service.
            
            :param ipaddr: IP address of the tasker service.
            :param port: Port number of the service.
            :param summary_progress: Optional summary progress delivery settings.
            :param protocol_config: Optional RPyC protocol configuration.
            :param aspect: Default tasker aspects for operations.
        """
        self._ipaddr = ipaddr
        self._port = port
        self._summary_progress = summary_progress
        self._aspects = aspect
        self._session_id = None
        self._protocol_config = protocol_config
        return

    @property
    def ipaddr(self):
        """
            IP address of the tasker service.
        """
        return self._ipaddr

    @property
    def port(self):
        """
            Port number of the tasker service.
        """
        return self._port

    @property
    def session_id(self):
        """
            Current session identifier.
        """
        return self._session_id

    def archive_folder(
        self,
        *,
        folder_to_archive: str,
        dest_folder: str,
        archive_name: str,
        compression_level: int = 7
    ) -> str:
        """
            Creates a compressed archive of a folder on the remote node.
            
            :param folder_to_archive: Folder path to archive.
            :param dest_folder: Destination folder for the archive.
            :param archive_name: Name of the created archive file.
            :param compression_level: Compression level for the archive.
            
            :returns: The full path to the remote archive file.
        """

        client = self._create_connection()

        try:
            rmt_archive_fullpath = client.root.archive_folder(
                folder_to_archive=folder_to_archive,
                dest_folder=dest_folder,
                archive_name=archive_name,
                compression_level=compression_level,
            )
        finally:
            client.close()

        return rmt_archive_fullpath

    def call_tasking_method(
        self,
        *,
        tasking_id: str,
        method_name: str,
        args: List[Any],
        kwargs: Dict[str, Any]
    ) -> Any:
        """
            Calls  the specified method on the remote tasking.
            
            :param tasking_id: The id of the tasking whose method you want to call.
            :param method_name: The name of the method to call on the tasking.
            :param args: A list of positiional arguements to pass to the remote method.
            :param kwargs: A dictionary of keyword arguements to pass to the remote method.
            
            :returns: Returns the response from the remote method.
        """
        client = self._create_connection()

        try:
            pkl_args = pickle.dumps(args)
            pkl_kwargs = pickle.dumps(kwargs)

            pkl_rtnval = client.root.call_tasking_method(
                session_id=self._session_id,
                tasking_id=tasking_id,
                method_name=method_name,
                pkl_args=pkl_args,
                pkl_kwargs=pkl_kwargs,
            )
            rtnval = pickle.loads(pkl_rtnval)

        finally:
            client.close()

        return rtnval

    def cancel_tasking(self, *, tasking_id: str):
        """
            Cancel the specified tasking.
            
            :param tasking_id: The id of the tasking to cancel.
        """
        client = self._create_connection()

        try:
            client.root.cancel_tasking(
                session_id=self._session_id, tasking_id=tasking_id
            )
        finally:
            client.close()

        return

    def file_exists(self, *, filename: str) -> bool:
        """
            Determine if a file exists on the remote node.
            
            :param filename: Path to the remote file.
            
            :returns: ``True`` if the file exists.
        """

        client = self._create_connection()

        try:
            exists = client.root.file_exists(filename=filename)
        finally:
            client.close()

        return exists

    def folder_exists(self, *, folder: str) -> bool:
        """
            Determine if a folder exists on the remote node.
            
            :param folder: Path to the remote directory.
            
            :returns: ``True`` if the folder exists.
        """

        client = self._create_connection()

        try:
            exists = client.root.folder_exists(folder=folder)
        finally:
            client.close()

        return exists

    def get_tasking_events(self, *, tasking_id: str) -> List[dict]:
        """
            Retrieve any events that have been posted for the specified tasking.
            
            :param tasking_id: Identifier of the tasking whose events are requested.
            
            :returns: A list of event dictionaries.
        """

        client = self._create_connection()

        tevents = []
        try:
            tevents_str = client.root.get_tasking_events(
                session_id=self._session_id, tasking_id=tasking_id
            )
            tevents = pickle.loads(tevents_str)

            if tevents is not None and len(tevents) > 0:
                tevents = [TaskingEvent.from_dict(tedata) for tedata in tevents]
        finally:
            client.close()

        return tevents

    def get_tasking_progress(self, *, tasking_id: str) -> ProgressInfo:
        """
            Obtain progress information for a running tasking.
            
            :param tasking_id: Identifier of the tasking to query.
            
            :returns: A :class:`ProgressInfo` instance or ``None`` if not available.
        """

        client = self._create_connection()

        tprog = None
        try:
            tprog_str = client.root.get_tasking_progress(
                session_id=self._session_id, tasking_id=tasking_id
            )
            if tprog_str is not None:
                tprog = pickle.loads(tprog_str)
        finally:
            client.close()

        return tprog

    def get_tasking_status(self, *, tasking_id: str) -> str:
        """
            Retrieve the current status string for the given tasking.
            
            :param tasking_id: Identifier of the tasking to query.
            
            :returns: Status string reported by the tasker service.
        """

        client = self._create_connection()

        tstatus = None
        try:
            tstatus = client.root.get_tasking_status(
                session_id=self._session_id, tasking_id=tasking_id
            )
        finally:
            client.close()

        return tstatus

    def get_tasking_result(self, *, tasking_id: str) -> TaskingResult:
        """
            Fetch the final :class:`TaskingResult` for a completed tasking.
            
            :param tasking_id: Identifier of the tasking whose result is requested.
            
            :returns: The deserialized :class:`TaskingResult` instance.
        """

        client = self._create_connection()

        tresult = None
        try:
            tresult_str = client.root.get_tasking_result(
                session_id=self._session_id, tasking_id=tasking_id
            )
            tresult = pickle.loads(tresult_str)
        finally:
            client.close()

        return tresult

    def has_completed_and_result_ready(self, *, tasking_id: str) -> bool:
        """
            Check if a tasking has completed and the result is available.
            
            :param tasking_id: Identifier of the tasking to check.
            
            :returns: ``True`` if the task finished and the result can be fetched.
        """

        client = self._create_connection()

        try:
            complete_and_ready = client.root.has_completed_and_result_ready(
                session_id=self._session_id, tasking_id=tasking_id
            )
        finally:
            client.close()

        return complete_and_ready

    def execute_tasking(
        self,
        *,
        module_name: str,
        tasking_name: str,
        summary_progress: Optional[SummaryProgressDelivery] = None,
        aspects: Optional[TaskerAspects] = None,
        **kwargs
    ) -> TaskingResultPromise:
        """
            Execute a tasking on the remote node.
            
            :param module_name: Name of the module containing the tasking.
            :param tasking_name: Name of the tasking class to execute.
            :param summary_progress: Optional summary progress delivery instance.
            :param aspects: Optional tasker aspects controlling execution.
            :param kwargs: Additional parameters passed to the tasking.
            
            :returns: A :class:`TaskingResultPromise` tracking the tasking.
        """

        # We are not going to automatically close this as there may be
        client = self._create_connection()

        responder = rpyc.BgServingThread(client)

        if aspects is None:
            aspects = self._aspects

        aspects = pickle.dumps(aspects.as_dict())

        if summary_progress is None:
            summary_progress = self._summary_progress

        taskref_info = client.root.execute_tasking(
            session_id=self._session_id,
            worker=self._ipaddr,
            module_name=module_name,
            tasking_name=tasking_name,
            aspects=aspects,
            **kwargs
        )

        promise = TaskingResultPromise(
            client,
            responder,
            taskref_info["module_name"],
            taskref_info["tasking_id"],
            taskref_info["task_name"],
            taskref_info["log_dir"],
            self._session_id,
            self,
        )

        return promise

    def session_close(self):
        """
            Close the currently open tasking session on the node.
        """

        client = self._create_connection()

        try:
            client.root.session_close(session_id=self._session_id)
            self._session_id = None
        finally:
            client.close()

        return

    def session_open(
        self,
        *,
        worker: str,
        wref: str,
        output_directory: Optional[str] = None,
        log_level: Optional[int] = logging.DEBUG,
        aspects: Optional[TaskerAspects] = None
    ) -> str:
        """
            Open a new tasking session on the node.
            
            :param worker: Worker name for identification.
            :param wref: Worker reference value.
            :param output_directory: Directory for task outputs.
            :param log_level: Logging level for the remote tasker.
            :param aspects: Tasker aspects controlling session defaults.
            
            :returns: The session identifier string.
        """

        if aspects is None:
            aspects = self._aspects

        client = self._create_connection()

        if wref is None:
            wref = self.ipaddr

        try:
            session_id = client.root.session_open(
                worker=worker,
                wref=wref,
                output_directory=output_directory,
                log_level=log_level,
                aspects=aspects,
            )
            self._session_id = session_id
        finally:
            client.close()

        return self._session_id

    def reinitialize_logging(
        self,
        *,
        logging_directory: Optional[str] = None,
        logging_level: Optional[int] = None
    ):
        """
            Request the remote tasker service reinitialize its logging.
            
            :param logging_directory: Directory to place logs.
            :param logging_level: Logging level to set.
        """

        client = self._create_connection()

        try:
            client.root.reinitialize_logging(
                logging_directory=logging_directory, logging_level=logging_level
            )
        finally:
            client.close()

        return

    def resolve_path(self, *, path) -> str:
        """
            Resolve a path on the remote node returning the absolute path.
            
            :param path: Path to resolve.
            
            :returns: The resolved absolute path string.
        """

        client = self._create_connection()

        try:
            full_path = client.root.resolve_path(path=path)
        finally:
            client.close()

        return full_path

    def _create_connection(self):
        """
            Create and return an RPyC connection using the configured aspects.
        """

        if self._aspects is not None:
            self._protocol_config["sync_request_timeout"] = (
                self._aspects.sync_request_timeout
            )

        client = rpyc.connect(
            self._ipaddr, self._port, keepalive=True, config=self._protocol_config
        )

        return client


class TaskerClientNode(TaskerNode):
    """
        Represents a tasker node created from an existing network client.
    """

    def __init__(self, client: Any, ipaddr: str, port: int):
        """
            Create a tasker node backed by an existing client connection.
        """
        self._client_ref = weakref.ref(client)
        super().__init__(ipaddr, port)
        return

    @property
    def client(self) -> Any:
        """
            Return the client object backing this node.

            :returns: The client object used for communication.
        """
        return self._client_ref()
