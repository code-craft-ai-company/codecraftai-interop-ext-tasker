"""
    .. module:: taskingprogressmonitor
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: taskingprogressmonitor module.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []

from typing import List, TYPE_CHECKING

import threading
import time
import weakref

from ccai.testbase.results.model.progressdelivery import SummaryProgressDelivery
from ccai.testbase.results.model.progresscode import ProgressCode


if TYPE_CHECKING:
    from ccai.interop.protocols.tasker.taskingresultpromise import (
        TaskingResultPromise,
    )


class TaskingProgressMonitor:
    """
        Monitors remote taskings and collects progress updates.
    """

    def __init__(
        self,
        summary_progress: SummaryProgressDelivery,
        monitored_promises: List["TaskingResultPromise"],
    ):
        """
            Creates a monitor object that polls promises for progress updates.
            
            :param summary_progress: The progress delivery information.
            :param monitored_promises: A list of promises to monitor.
        """

        self._progress_callback = summary_progress.progress_callback
        self._progress_interval = summary_progress.progress_interval

        self._lock = threading.Lock()
        self._monitored_promise_refs = {
            pr.tasking_id: weakref.ref(pr) for pr in monitored_promises
        }
        self._clear_progress_for = [pr.tasking_id for pr in monitored_promises]
        return

    def release(self, tasking_id: str):
        """
            Stops monitoring progress for the specified tasking.
            
            :param tasking_id: The identifier of the tasking to release.
        """

        self._lock.acquire()
        try:
            del self._monitored_promise_refs[tasking_id]
        finally:
            self._lock.release()

        return

    def start(self):
        """
            Starts the monitoring thread that polls promises for progress.
        """

        sgate = threading.Event()
        sgate.clear()

        self._progress_thread = threading.Thread(
            target=self._pull_progress_entry,
            name="progress-pullback",
            args=(sgate,),
            daemon=True,
        )
        self._progress_thread.start()

        sgate.wait()

        return

    def _pull_progress_entry(self, sgate: threading.Event):
        """
            Internal thread entry used to periodically poll task promises for progress.
            
            :param sgate: A startup gate used to signal that the thread has begun execution.
        """

        self._pulling_progress = True

        sgate.set()

        while self._pulling_progress:

            time.sleep(self._progress_interval)

            promises: List["TaskingResultPromise"] = []
            self._lock.acquire()
            try:
                if len(self._monitored_promise_refs) == 0:
                    break

                for pref in self._monitored_promise_refs.values():
                    p = pref()
                    if p is not None:
                        promises.append(p)
            finally:
                self._lock.release()

            completed_list: List["TaskingResultPromise"] = []
            progress_list = []
            for prom_item in promises:
                progress = None
                try:
                    progress = prom_item.get_progress()
                except BaseException:
                    continue

                if (
                    progress.status != ProgressCode.NotStarted
                    and progress.status != ProgressCode.Paused
                    and progress.status != ProgressCode.Running
                ):
                    completed_list.append(progress)

                progress_list.append(progress)

            self._lock.acquire()
            try:
                for prog in completed_list:
                    tasking_id = prog.tasking_id
                    del self._monitored_promise_refs[tasking_id]
            finally:
                self._lock.release()

            self._progress_callback(progress_list)

        return
