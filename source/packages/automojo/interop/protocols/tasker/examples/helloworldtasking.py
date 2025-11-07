
"""
    .. module:: helloworldtasking
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: helloworldtasking module.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

import os
import time

from datetime import datetime

from automojo.testbase.results.model.progressinfo import ProgressInfo, ProgressType, ProgressCode

from automojo.interop.protocols.tasker.tasking import Tasking

class HelloWorldTasking(Tasking):
    """
        Simple example tasking that writes a message a number of times.
    """

    PREFIX = "helloworld"

    def begin(self, kwparams: dict):
        """
            Called when the task is beginning execution.
            
            :param kwparams: Parameters describing the task execution.
        """

        self._message = kwparams["message"]
        self._iterations = kwparams["iterations"]

        self._data = {
            "pid": os.getpid(),
            "message": self._message,
            "iterations": self._iterations
        }
        
        time.sleep(5)

        return

    def mark_progress_start(self):
        """
            Marks the start of progress for the tasking.

            :returns: ``None``
        """
        now = datetime.now()
        self._current_progress = ProgressInfo(
            self._tasking_id,
            "hello",
            self.full_name,
            ProgressType.NumericRange,
            0,
            self._iterations,
            0,
            ProgressCode.Running,
            now,
            self._data,
        )
        return

    def log_message(self, message) -> bool:
        """
            Logs a message to the tasking logger.

            :param message: Text to log.

            :returns: ``True`` if the message was logged.
        """
        self._logger.info(message)
        return True

    def perform(self):
        """
            Performs one iteration of work.

            :returns: ``True`` if additional iterations remain.
        """
        position = self._current_progress.position

        time.sleep(1)

        morework = False
        if position < self._current_progress.range_max:
            morework = True
            self._current_progress.position = position + 1

        return morework
