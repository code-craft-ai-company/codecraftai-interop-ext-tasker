"""
    .. module:: taskerservermanager
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`TaskerServerManager` class which is used to create
    a remote :class:`TaskerServer` process.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
    
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []



from typing import Optional, Tuple

import multiprocessing
import multiprocessing.managers

from ccai.interop.protocols.tasker.taskerserver import TaskerServer


class TaskerServerManager(multiprocessing.managers.SyncManager):
    """
        This is a process manager used for creating a :class:`TaskerServerManager`
        in a remote process that can be communicated with via a proxy.
    """


TaskerServerManager.register("TaskerServer", TaskerServer)


def spawn_tasking_server_process(svc_endpoint: Tuple[str, int], logging_directory: Optional[str] = None) -> Tuple[TaskerServerManager, TaskerServer]:
    """
        Spawns a new :class:`TaskerServer` in a separate process.

        :param svc_endpoint: Tuple of IP address and port to bind the server.
        :param logging_directory: Optional directory for log files.

        :returns: A tuple containing the manager and the server proxy.
    """

    ipaddr, port = svc_endpoint

    svr_manager = TaskerServerManager()
    svr_manager.start()

    tasking_svr_proxy = svr_manager.TaskerServer(hostname=ipaddr, port=port, logging_directory=logging_directory)

    return svr_manager, tasking_svr_proxy

