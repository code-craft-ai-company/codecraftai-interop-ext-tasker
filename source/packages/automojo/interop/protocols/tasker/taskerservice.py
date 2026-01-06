"""
    .. module:: taskerservice
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`TaskerService` class which is an rypc service
    for running and monitoring remote tasks.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
    
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []



from typing import Dict, Optional

import logging
from automojo.xmodules.xlogging.enhancedloggers import getEnhancedLogger
import os
import pickle
import tempfile
import threading
import traceback

from collections import OrderedDict
from logging.handlers import RotatingFileHandler

import rpyc

from automojo.errors.exceptions import SemanticError

from automojo.testbase.results.model.taskingresult import TaskingResult

from automojo.xmodules.xzipfile import create_archive_of_folder
from automojo.xmodules.fspath import expand_path

from automojo.interop.protocols.tasker.taskeraspects import TaskerAspects, DEFAULT_TASKER_ASPECTS
from automojo.interop.protocols.tasker.taskersession import TaskerSession

class TaskerService(rpyc.Service):
    """
        The :class:`TaskerService` is an rpyc service that handles the spawning of tasks
        on a node.
    """

    service_lock = threading.Lock()

    initialized = False

    logger: logging.Logger = None
    logging_directory = "/opt/tasker/logs"
    logging_level = logging.DEBUG

    active_sessions = OrderedDict()
    max_sessions = 1


    def __init__(self) -> None:
        """
            Initializes the :class:`TaskerService` instance and ensures logging is configured.
        """

        super().__init__()

        this_type = type(self)

        this_type.service_lock.acquire()
        try:
            if this_type.logger is None:
                self._reinitialize_service_logging()
        finally:
            this_type.service_lock.release()

        return


    def exposed_archive_folder(self, *, folder_to_archive: str, dest_folder: str, archive_name: str, compression_level: int = 7) -> str:
        """
            Archive a folder on the server into a zip file.
            
            :param folder_to_archive: Folder to compress.
            :param dest_folder: Destination directory for the archive.
            :param archive_name: Name of the archive file.
            :param compression_level: Compression level for the archive.
            
            :returns: Path to the created archive file.
        """

        this_type = type(self)

        this_type.service_lock.acquire()
        try:

            this_type.logger.info("Method 'exposed_archive_folder' was called.")

            if not archive_name.endswith(".zip"):
                archive_name = f"{archive_name}.zip"

            folder_to_archive = expand_path(folder_to_archive)

            if not os.path.exists(folder_to_archive):
                raise FileNotFoundError(f"The folder to archive folder={folder_to_archive} does not exist")

            dest_folder = expand_path(dest_folder)
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)

            archive_full = os.path.join(dest_folder, archive_name)

            create_archive_of_folder(folder_to_archive, archive_full, compression_level=compression_level)

        finally:
            this_type.service_lock.release()

        return archive_full


    def exposed_cancel_tasking(self, *, session_id: str, tasking_id: str):
        """
            Cancel a running task on behalf of a session.
            
            :param session_id: Identifier of the session requesting cancellation.
            :param tasking_id: Identifier of the tasking to cancel.
        """

        this_type = type(self)

        this_type.service_lock.acquire()
        try:

            this_type.logger.info("Method 'exposed_cancel_tasking' was called.")

            session = self._locked_get_session(session_id)
            
            this_type.service_lock.release()
            try:
                session.cancel_tasking(tasking_id)
            finally:
                this_type.service_lock.acquire()

        finally:
            this_type.service_lock.release()

        return

    def exposed_call_tasking_method(self, *, session_id: str, tasking_id: str, method_name: str, pkl_args: bytes, pkl_kwargs: bytes) -> bytes:
        """
            Invoke a method on a running tasking instance.
            
            :param session_id: Session requesting the call.
            :param tasking_id: Task identifier.
            :param method_name: Method to invoke on the tasking.
            :param pkl_args: Pickled positional arguments.
            :param pkl_kwargs: Pickled keyword arguments.
            
            :returns: Pickled return value from the method call.
        """

        tasking = None

        this_type = type(self)

        this_type.service_lock.acquire()
        try:

            this_type.logger.info("Method 'exposed_call_tasking_method' was called.")

            session = self._locked_get_session(session_id)
            
            this_type.service_lock.release()
            try:
                tasking = session.get_tasking(tasking_id)
            finally:
                this_type.service_lock.acquire()

        finally:
            this_type.service_lock.release()

        this_type.logger.info("Tasking found.")

        # If we didn't find the tasking, an exception should have been raised
        args = pickle.loads(pkl_args)
        kwargs = pickle.loads(pkl_kwargs)

        # We are getting this method off of an instance of a tasking so it should already be bound to 'self'
        method_to_call = getattr(tasking, method_name)
        this_type.logger.info("Got tasking method")

        rtnval = method_to_call(*args, **kwargs)

        this_type.logger.info(f"Tasking method returned={rtnval}")

        pkl_rtnval = pickle.dumps(rtnval)

        return pkl_rtnval

    def exposed_dispose_tasking(self, *, session_id: str, tasking_id: str):
        """
            Dispose of a completed tasking object and free associated resources.
            
            :param session_id: Session owning the tasking.
            :param tasking_id: Identifier of the tasking to dispose.
        """

        this_type = type(self)

        this_type.service_lock.acquire()
        try:

            this_type.logger.info("Method 'exposed_dispose_tasking' was called.")

            session = self._locked_get_session(session_id)
            
            this_type.service_lock.release()
            try:
                session.dispose_tasking(tasking_id)
            finally:
                this_type.service_lock.acquire()

        finally:
            this_type.service_lock.release()

        return
    

    def exposed_execute_tasking(self, *, session_id: str, module_name: str, tasking_name: str, parent_id: Optional[str] = None,
                                aspects: Optional[TaskerAspects]=None, **kwargs) -> dict:
        """
            Execute a tasking on behalf of a session.
            
            :param session_id: Identifier of the owning session.
            :param module_name: Module containing the tasking class.
            :param tasking_name: Name of the tasking class.
            :param parent_id: Optional parent tasking identifier.
            :param aspects: Pickled aspects controlling execution.
            :param kwargs: Additional arguments passed to the tasking.
            
            :returns: Dictionary representation of a :class:`TaskingRef`.
        """

        this_type = type(self)

        this_type.service_lock.acquire()
        try:

            this_type.logger.info("Method 'exposed_execute_tasking' was called.")

            session = self._locked_get_session(session_id)
            
            this_type.service_lock.release()
            try:
                aspects = TaskerAspects.from_dict(pickle.loads(aspects))

                taskref = session.execute_tasking(module_name=module_name, tasking_name=tasking_name, parent_id=parent_id,
                                        aspects=aspects, **kwargs)
            finally:
                this_type.service_lock.acquire()

        except:
            errmsg = traceback.format_exc()
            this_type.logger.error(errmsg)
            raise

        finally:
            this_type.service_lock.release()

        return taskref.as_dict()


    def exposed_file_exists(self, *, filename) -> bool:
        """
            Check if a file exists on the server.

            :returns: ``True`` if the specified file exists.
        """

        this_type = type(self)

        exists = False

        this_type.service_lock.acquire()
        try:

            this_type.logger.info("Method 'exposed_file_exists' was called.")

            filename = expand_path(filename)

            if os.path.exists(filename) and os.path.isfile(filename):
                exists = True

        finally:
            this_type.service_lock.release()

        return exists
    

    def exposed_folder_exists(self, *, folder) -> bool:
        """
            Check if a folder exists on the server.

            :returns: ``True`` if the folder exists.
        """

        this_type = type(self)

        exists = False

        this_type.service_lock.acquire()
        try:

            this_type.logger.info("Method 'exposed_folder_exists' was called.")

            folder = expand_path(folder)

            if os.path.exists(folder) and os.path.isdir(folder):
                exists = True
        finally:
            this_type.service_lock.release()

        return exists


    def exposed_get_tasking_events(self, *, session_id: str, tasking_id: str) -> TaskingResult:
        """
            Retrieve progress events generated by a tasking.
            
            :param session_id: Identifier of the session that owns the tasking.
            :param tasking_id: Identifier of the tasking whose events are requested.
            
            :returns: Serialized events string from the tasking session.
        """

        this_type = type(self)

        events_str = None

        this_type.service_lock.acquire()
        try:

            this_type.logger.info("Method 'exposed_get_tasking_events' was called.")

            session = self._locked_get_session(session_id)
            
            this_type.service_lock.release()
            try:
                events_str = session.get_tasking_events(tasking_id)
            finally:
                this_type.service_lock.acquire()

        except:
            errmsg = traceback.format_exc()
            this_type.logger.error(errmsg)
            raise

        finally:
            this_type.service_lock.release()

        return events_str


    def exposed_get_tasking_progress(self, *, session_id: str, tasking_id: str) -> TaskingResult:
        """
            Obtain progress information for a tasking.
            
            :param session_id: Identifier of the tasking session.
            :param tasking_id: Identifier of the tasking.
            
            :returns: Serialized progress string from the tasking session.
        """

        this_type = type(self)

        progress_str = None

        this_type.service_lock.acquire()
        try:

            this_type.logger.info("Method 'exposed_get_tasking_progress' was called.")

            session = self._locked_get_session(session_id)
            
            this_type.service_lock.release()
            try:
                progress_str = session.get_tasking_progress(tasking_id)
            finally:
                this_type.service_lock.acquire()

        except:
            errmsg = traceback.format_exc()
            this_type.logger.error(errmsg)
            raise

        finally:
            this_type.service_lock.release()

        return progress_str


    def exposed_get_tasking_result(self, *, session_id: str, tasking_id: str) -> TaskingResult:
        """
            Retrieve the final result for a completed tasking.
            
            :param session_id: Identifier of the tasking session.
            :param tasking_id: Identifier of the tasking.
            
            :returns: Serialized :class:`TaskingResult` string.
        """

        this_type = type(self)

        result_str = None

        this_type.service_lock.acquire()
        try:

            this_type.logger.info("Method 'exposed_get_tasking_result' was called.")

            session = self._locked_get_session(session_id)
            
            this_type.service_lock.release()
            try:
                result_str = session.get_tasking_result(tasking_id)
            finally:
                this_type.service_lock.acquire()

        except:
            errmsg = traceback.format_exc()
            this_type.logger.error(errmsg)
            raise

        finally:
            this_type.service_lock.release()

        return result_str
    
    def exposed_get_tasking_status(self, *, session_id: str, tasking_id: str) -> str:
        """
            Query the current status code for a tasking.
            
            :param session_id: Identifier of the tasking session.
            :param tasking_id: Identifier of the tasking.
            
            :returns: Status string describing the tasking state.
        """

        this_type = type(self)

        tstatus = None

        this_type.service_lock.acquire()
        try:

            this_type.logger.info("Method 'exposed_get_tasking_status' was called.")

            session = self._locked_get_session(session_id)
            
            this_type.service_lock.release()
            try:
                tstatus = session.get_tasking_status(tasking_id)
            finally:
                this_type.service_lock.acquire()

        except:
            errmsg = traceback.format_exc()
            this_type.logger.error(errmsg)
            raise

        finally:
            this_type.service_lock.release()

        return tstatus
    
    def exposed_has_completed_and_result_ready(self, *, session_id: str, tasking_id: str) -> bool:
        """
            Determine if a tasking has completed and its result is available.
            
            :param session_id: Identifier of the tasking session.
            :param tasking_id: Identifier of the tasking.
            
            :returns: ``True`` if the tasking result can be fetched.
        """

        complete_and_ready = False

        this_type = type(self)

        this_type.service_lock.acquire()
        try:

            this_type.logger.info("Method 'exposed_has_completed_and_result_ready' was called.")

            session = self._locked_get_session(session_id)
            
            this_type.service_lock.release()
            try:
                complete_and_ready = session.has_completed_and_result_ready(tasking_id)
            finally:
                this_type.service_lock.acquire()

        except:
            errmsg = traceback.format_exc()
            this_type.logger.error(errmsg)
            raise

        finally:
            this_type.service_lock.release()

        return complete_and_ready


    def exposed_make_folder(self, *, folder: str):
        """
            Create a folder on the tasker host.
        """

        this_type = type(self)

        this_type.service_lock.acquire()
        try:

            this_type.logger.info("Method 'exposed_make_folder' was called.")

            folder = expand_path(folder)

            os.makedirs(folder)

        finally:
            this_type.service_lock.release()

        return


    def exposed_session_close(self, *, session_id: str) -> str:
        """
            Close a single tasking session and stop any running taskings.
            
            :param session_id: Identifier of the session to close.
            
            :returns: The closed session identifier.
        """

        this_type = type(self)

        this_type.service_lock.acquire()
        try:
            
            this_type.logger.info("Method 'exposed_close_session' was called.")

            if session_id not in this_type.active_sessions:
                errmsg = f"The specified session '{session_id}' is not an active session."
                raise RuntimeError(errmsg)

            session = this_type.active_sessions[session_id]

            del this_type.active_sessions[session_id]

            session.shutdown()

        finally:
            this_type.service_lock.release()

        return session_id

    def exposed_session_close_all(self) -> Optional[str]:
        """
            Close all active sessions and return the last closed session id.

            :returns: The identifier of the last session closed or ``None`` if no sessions were active.
        """

        this_type = type(self)
        last_session_id = None

        this_type.service_lock.acquire()
        try:
            
            this_type.logger.info("Method 'exposed_close_session_all' was called.")

            closed_sessions = []
            for session_id, session in this_type.active_sessions.items():
                session.shutdown()
                closed_sessions.append(session_id)

            for session_id in closed_sessions:
                del this_type.active_sessions[session_id]
                last_session_id = session_id

        finally:
            this_type.service_lock.release()

        return last_session_id


    def exposed_session_open(self, *, worker: str, wref: str, output_directory: Optional[str] = None,
                             log_level: Optional[int] = logging.DEBUG, notify_url: Optional[str] = None,
                             notify_headers: Optional[Dict[str, str]] = None,
                             aspects: Optional[TaskerAspects] = DEFAULT_TASKER_ASPECTS) -> str:

        """
            Open a new tasking session for a client connection.
            
            :param worker: Name of the worker for logging purposes.
            :param wref: Worker reference value.
            :param output_directory: Directory for task logs.
            :param log_level: Logging level for the session.
            :param notify_url: Optional notification callback URL.
            :param notify_headers: Optional headers for notifications.
            :param aspects: Default aspects for task execution.
            
            :returns: The newly created session identifier.
        """

        this_type = type(self)

        session = None
        session_id = None

        this_type.service_lock.acquire()
        try:
            
            if output_directory is None:
                output_directory = this_type.logging_directory

            this_type.logger.info("Method 'exposed_open_session' was called.")

            if len(this_type.active_sessions) >= this_type.max_sessions:
                errmsg = "Cannot open session. The maximum number of sessions has been reached."
                raise RuntimeError(errmsg)

            session = TaskerSession(this_type, worker, wref, output_directory=output_directory, log_level=log_level,
                                    notify_url=notify_url, notify_headers=notify_headers, aspects=aspects)
            session_id = session.session_id
            session.start_event_server()

            this_type.active_sessions[session_id] = session

        finally:
            this_type.service_lock.release()

        return session_id

    def exposed_reinitialize_logging(self, *, logging_directory: Optional[str] = None, logging_level: Optional[int] = None):
        """
            Called in order to change the location of the service logging.  This is typically not warranted as individual taskings
            derive logging inputs from an established TaskerSession.
        """
        
        this_type = type(self)

        this_type.service_lock.acquire()
        try:

            this_type.logger.info("Method 'exposed_reinitialize_logging' was called.")

            reinitialize_service_logging = False

            if logging_directory is not None:
                this_type.logging_directory = expand_path(logging_directory)
                reinitialize_service_logging = True

            if logging_level is not None:
                this_type.logging_level = logging_level
                reinitialize_service_logging = True

            if reinitialize_service_logging:
                self._reinitialize_service_logging()

        finally:
            this_type.service_lock.release()
        
        return


    def exposed_resolve_path(self, *, path) -> str:
        """
            Resolve an arbitrary path on the tasker host.
            
            :param path: File system path to expand.
            
            :returns: Expanded absolute path string.
        """

        this_type = type(self)

        this_type.service_lock.acquire()
        try:
            this_type.logger.info("Method 'exposed_resolve_path' was called.")

            path = expand_path(path)
        finally:
            this_type.service_lock.release()

        return path

    @classmethod
    def log_debug(cls, message: str):
        """
            Log a debug level message from within the service.
        """

        try:
            cls.logger.debug(message)
        except:
            pass

        return

    @classmethod
    def log_error(cls, message: str):
        """
            Log an error level message from within the service.
        """

        try:
            cls.logger.error(message)
        except:
            pass

        return
    
    @classmethod
    def log_info(cls, message: str):
        """
            Log an info level message from within the service.
        """

        try:
            cls.logger.info(message)
        except:
            pass

        return
    
    @classmethod
    def log_warn(cls, message: str):
        """
            Log a warning level message from within the service.
        """

        try:
            cls.logger.warn(message)
        except:
            pass

        return

    def _locked_get_session(self, session_id: str) -> TaskerSession:
        """
            Retrieve a session object while holding the service lock.
        """

        this_type = type(self)

        if session_id is None:
            raise ValueError(f"The session_id='{session_id}' provided was None.")
    
        if len(self.active_sessions) == 0:
            raise SemanticError("You must first open a tasking session before calling APIs that work with taskings.")

        if session_id not in self.active_sessions:
            raise SemanticError(f"The session_id={session_id} provided was not valid")

        rtnval = self.active_sessions[session_id]

        this_type.logger.info(f"Session found for session_id={session_id}")

        return rtnval


    def _reinitialize_service_logging(self):
        """
            Reset the service logger using current configuration values.
        """

        this_type = type(self)

        if this_type.logger is None:
            this_type.logger = getEnhancedLogger()
        
        handlers_list = [h for h in this_type.logger._logger.handlers]

        for handler in handlers_list:
            this_type.logger.removeHandler(handler)

        logging_dir = this_type.logging_directory
        if not os.path.exists(logging_dir):
            try:
                os.makedirs(logging_dir)
            except BaseException:
                logging_dir = tempfile.mkdtemp()
                this_type.logging_directory = logging_dir

        log_file = os.path.join(logging_dir, "tasker-server.log")

        rotating_handler = RotatingFileHandler(log_file, maxBytes=102400, backupCount=10)
        rotating_handler.setLevel(this_type.logging_level)

        this_type.logger.addHandler(rotating_handler)

        return
