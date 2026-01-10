import sys
from unittest.mock import MagicMock
import logging

# Mocking modules that are not available or not relevant for the bugs
# DO NOT mock automojo or automojo.interop

sys.modules["automojo.errors"] = MagicMock()
sys.modules["automojo.errors.exceptions"] = MagicMock()
sys.modules["automojo.errors.xtraceback"] = MagicMock()
sys.modules["automojo.testbase"] = MagicMock()
sys.modules["automojo.testbase.results"] = MagicMock()
sys.modules["automojo.testbase.results.model"] = MagicMock()
sys.modules["automojo.testbase.results.model.resultcode"] = MagicMock()
sys.modules["automojo.testbase.results.model.resulttype"] = MagicMock()
sys.modules["automojo.testbase.results.model.progressinfo"] = MagicMock()
sys.modules["automojo.testbase.results.model.progresscode"] = MagicMock()
sys.modules["automojo.testbase.results.model.taskingresult"] = MagicMock()
sys.modules["automojo.testbase.results.model.taskinggroup"] = MagicMock()
sys.modules["automojo.testbase.results.recorders"] = MagicMock()
sys.modules["automojo.testbase.results.recorders.resultrecorder"] = MagicMock()

# ProgressDeliveryMethod needs to be a class or object with attributes
class MockProgressDeliveryMethod:
    SUMMARY_PULL_PROGRESS = "SUMMARY_PULL_PROGRESS"

pd_mock = MagicMock()
pd_mock.ProgressDeliveryMethod = MockProgressDeliveryMethod
sys.modules["automojo.testbase.results.model.progressdelivery"] = pd_mock

sys.modules["automojo.xmodules"] = MagicMock()
sys.modules["automojo.xmodules.xdatetime"] = MagicMock()
sys.modules["automojo.xmodules.xformatting"] = MagicMock()
sys.modules["automojo.xmodules.ximport"] = MagicMock()
sys.modules["automojo.xmodules.jsos"] = MagicMock()

# Mocking getEnhancedLogger
logger_mock = MagicMock(spec=logging.Logger)
enhanced_loggers_mock = MagicMock()
enhanced_loggers_mock.getEnhancedLogger = MagicMock(return_value=logger_mock)
sys.modules["automojo.xmodules.xlogging"] = MagicMock()
sys.modules["automojo.xmodules.xlogging.enhancedloggers"] = enhanced_loggers_mock

# Mock interop SUBMODULES that are missing or we want to ignore, BUT NOT interop itself
sys.modules["automojo.interop.interfaces"] = MagicMock()
sys.modules["automojo.interop.interfaces.inetworkclient"] = MagicMock()

sys.modules["automojo.interop.protocols.tasker.taskingevent"] = MagicMock()
sys.modules["automojo.interop.protocols.tasker.taskernode"] = MagicMock()
sys.modules["automojo.interop.protocols.tasker.taskingresultpromise"] = MagicMock()
sys.modules["automojo.interop.protocols.tasker.taskerservice"] = MagicMock()
sys.modules["automojo.interop.protocols.tasker.taskerservermanager"] = MagicMock()

sys.modules["rpyc"] = MagicMock()
sys.modules["rpyc.utils"] = MagicMock()
sys.modules["rpyc.utils.server"] = MagicMock()


# Add source/packages to sys.path
import os
sys.path.insert(0, os.path.abspath("source/packages"))

# Import the modules under test
from automojo.interop.protocols.tasker.taskeraspects import TaskerAspects, DEFAULT_TASKER_ASPECTS
from automojo.interop.protocols.tasker.tasking import Tasking, instantiate_tasking
from automojo.interop.protocols.tasker.taskercontroller import TaskerController
from automojo.interop.protocols.tasker.taskerserver import TaskerServer, TASKER_PROTOCOL_CONFIG

def test_mutable_default_aspects_instantiate_tasking():
    print("Testing mutable default aspects in instantiate_tasking...")
    # Verify default is None now (CORRECT)
    import inspect
    sig = inspect.signature(instantiate_tasking)
    default_aspects = sig.parameters['aspects'].default

    if default_aspects is None:
        print("PASS: default aspects IS None")
    else:
        print(f"FAIL: default aspects IS NOT None, it is {default_aspects}")

    # Modify DEFAULT_TASKER_ASPECTS (should not affect default arg since it is None)
    print(f"Original completion_timeout: {DEFAULT_TASKER_ASPECTS.completion_timeout}")
    DEFAULT_TASKER_ASPECTS.completion_timeout = 99999

    # Re-check default arg
    if default_aspects is None:
        print("PASS: Default argument remains None after modifying global.")

def test_mutable_default_aspects_tasking_init():
    print("\nTesting mutable default aspects in Tasking.__init__...")
    import inspect
    sig = inspect.signature(Tasking.__init__)
    default_aspects = sig.parameters['aspects'].default

    if default_aspects is None:
        print("PASS: default aspects IS None")
    else:
        print(f"FAIL: default aspects IS NOT None, it is {default_aspects}")

def test_mutable_default_aspects_taskercontroller_init():
    print("\nTesting mutable default aspects in TaskerController.__init__...")
    import inspect
    sig = inspect.signature(TaskerController.__init__)
    default_aspects = sig.parameters['aspects'].default

    if default_aspects is None:
        print("PASS: default aspects IS None")
    else:
        print(f"FAIL: default aspects IS NOT None, it is {default_aspects}")

def test_mutable_default_protocol_config_taskerserver_init():
    print("\nTesting mutable default protocol_config in TaskerServer.__init__...")
    import inspect
    sig = inspect.signature(TaskerServer.__init__)
    try:
        default_config = sig.parameters['protocol_config'].default

        if default_config is None:
            print("PASS: default protocol_config IS None")
        else:
            print(f"FAIL: default protocol_config IS NOT None, it is {default_config}")

    except KeyError:
        print("SKIPPING: protocol_config parameter not found in signature.")

def test_logging_handler_accumulation():
    print("\nTesting logging handler accumulation in instantiate_tasking...")
    # Mock import_by_name to return a dummy module
    dummy_module = MagicMock()
    dummy_module.MyTask = MagicMock(spec=Tasking) # Mock Tasking class

    sys.modules["automojo.xmodules.ximport"].import_by_name.return_value = dummy_module

    # Reset logger handlers and getEnhancedLogger mock
    logger_mock.addHandler = MagicMock()
    enhanced_loggers_mock.getEnhancedLogger = MagicMock(return_value=logger_mock)

    # Call instantiate_tasking multiple times
    instantiate_tasking("worker", "wref", "dummy_module", "MyTask", "tid1", "pid", "out", "logdir", "logfile1", 10, ("host", 80), None, None)
    instantiate_tasking("worker", "wref", "dummy_module", "MyTask", "tid2", "pid", "out", "logdir", "logfile2", 10, ("host", 80), None, None)

    # Verify getEnhancedLogger was called with different arguments
    calls = enhanced_loggers_mock.getEnhancedLogger.call_args_list
    print(f"getEnhancedLogger calls: {calls}")

    if len(calls) == 2:
        args1 = calls[0][0][0]
        args2 = calls[1][0][0]
        if args1 == "TASKING.tid1" and args2 == "TASKING.tid2":
            print("PASS: getEnhancedLogger called with unique logger names.")
        else:
            print(f"FAIL: getEnhancedLogger called with unexpected names: {args1}, {args2}")
    else:
        print(f"FAIL: getEnhancedLogger called {len(calls)} times.")

if __name__ == "__main__":
    test_mutable_default_aspects_instantiate_tasking()
    test_mutable_default_aspects_tasking_init()
    test_mutable_default_aspects_taskercontroller_init()
    test_mutable_default_protocol_config_taskerserver_init()
    test_logging_handler_accumulation()
