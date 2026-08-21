"""
    ======================================= CODE GENERATED - DO NOT EDIT =======================================
    This is a code generated execution sequence document, do not manually edit this document.  The 'testbase'
    test framework generates this document in order to layout the test run scopes, parameter creations, and
    test calls in a user ledgible way which is easy to read and also to debug.
"""

__traceback_format_policy__ = "Brief"

import logging

from ccai.xmodules.xlogging.enhancedloggers import getEnhancedLogger

from ccai.testbase.constraints import ConstraintsCatalog

logger = getEnhancedLogger()

constraints_catalog = ConstraintsCatalog()



def session(sequencer):
    """
    This is the entry point for the test run sequence document.
    """

    with sequencer.enter_session_scope_context() as ssc:


        scope_automojo(sequencer)

    return

def scope_automojo(sequencer):
    """
    This is the entry point for the 'automojo' test scope.
    """

    with sequencer.enter_module_scope_context("automojo") as msc:
        scope_automojo_tests(sequencer)

    return

def scope_automojo_tests(sequencer):
    """
    This is the entry point for the 'automojo_tests' test scope.
    """

    with sequencer.enter_module_scope_context("automojo.tests") as msc:
        scope_automojo_tests_singlehost(sequencer)

    return

def scope_automojo_tests_singlehost(sequencer):
    """
    This is the entry point for the 'automojo_tests_singlehost' test scope.
    """

    with sequencer.enter_module_scope_context("automojo.tests.singlehost") as msc:
        scope_automojo_tests_singlehost_interop(sequencer)

    return

def scope_automojo_tests_singlehost_interop(sequencer):
    """
    This is the entry point for the 'automojo_tests_singlehost_interop' test scope.
    """

    with sequencer.enter_module_scope_context("automojo.tests.singlehost.interop") as msc:
        scope_automojo_tests_singlehost_interop_protocols(sequencer)

    return

def scope_automojo_tests_singlehost_interop_protocols(sequencer):
    """
    This is the entry point for the 'automojo_tests_singlehost_interop_protocols' test scope.
    """

    with sequencer.enter_module_scope_context("automojo.tests.singlehost.interop.protocols") as msc:
        scope_automojo_tests_singlehost_interop_protocols_tasker(sequencer)

    return

def scope_automojo_tests_singlehost_interop_protocols_tasker(sequencer):
    """
    This is the entry point for the 'automojo_tests_singlehost_interop_protocols_tasker' test scope.
    """

    with sequencer.enter_module_scope_context("automojo.tests.singlehost.interop.protocols.tasker") as msc:
        scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskercontroller(sequencer)
        scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskerdaemon(sequencer)
        scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskernode(sequencer)
        scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskerserver(sequencer)
        scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskerservermanager(sequencer)
        scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskerservice(sequencer)
        scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskersession(sequencer)
        scope_automojo_tests_singlehost_interop_protocols_tasker_test_tasking(sequencer)
        scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskingadapter(sequencer)
        scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskingevent(sequencer)
        scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskinggroupscope(sequencer)
        scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskingprogressmonitor(sequencer)
        scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskingresultpromise(sequencer)

    return

def scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskercontroller(sequencer):
    """
    This is the entry point for the 'automojo_tests_singlehost_interop_protocols_tasker_test_taskercontroller' test scope.
    """

    with sequencer.enter_module_scope_context("automojo.tests.singlehost.interop.protocols.tasker.test_taskercontroller") as msc:
        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskercontroller#test_execute_tasking_variants ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskercontroller#test_execute_tasking_variants"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskercontroller import test_execute_tasking_variants

            test_execute_tasking_variants()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskercontroller#test_wait_for_any_to_event_error_when_task_complete_without_event ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskercontroller#test_wait_for_any_to_event_error_when_task_complete_without_event"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskercontroller import test_wait_for_any_to_event_error_when_task_complete_without_event

            test_wait_for_any_to_event_error_when_task_complete_without_event()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskercontroller#test_wait_for_any_to_event_success ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskercontroller#test_wait_for_any_to_event_success"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskercontroller import test_wait_for_any_to_event_success

            test_wait_for_any_to_event_success()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskercontroller#test_wait_for_tasking_results_returns_results ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskercontroller#test_wait_for_tasking_results_returns_results"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskercontroller import test_wait_for_tasking_results_returns_results

            test_wait_for_tasking_results_returns_results()


    return

def scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskerdaemon(sequencer):
    """
    This is the entry point for the 'automojo_tests_singlehost_interop_protocols_tasker_test_taskerdaemon' test scope.
    """

    with sequencer.enter_module_scope_context("automojo.tests.singlehost.interop.protocols.tasker.test_taskerdaemon") as msc:
        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskerdaemon#test_daemon_main_debug_flag_forces_start ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskerdaemon#test_daemon_main_debug_flag_forces_start"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskerdaemon import test_daemon_main_debug_flag_forces_start

            test_daemon_main_debug_flag_forces_start()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskerdaemon#test_daemon_main_start_action_invokes_start ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskerdaemon#test_daemon_main_start_action_invokes_start"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskerdaemon import test_daemon_main_start_action_invokes_start

            test_daemon_main_start_action_invokes_start()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskerdaemon#test_process_exists_true_and_false ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskerdaemon#test_process_exists_true_and_false"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskerdaemon import test_process_exists_true_and_false

            test_process_exists_true_and_false()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskerdaemon#test_remove_pidfile_deletes_existing_file ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskerdaemon#test_remove_pidfile_deletes_existing_file"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskerdaemon import test_remove_pidfile_deletes_existing_file

            test_remove_pidfile_deletes_existing_file()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskerdaemon#test_write_trace_appends_lines ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskerdaemon#test_write_trace_appends_lines"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskerdaemon import test_write_trace_appends_lines

            test_write_trace_appends_lines()


    return

def scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskernode(sequencer):
    """
    This is the entry point for the 'automojo_tests_singlehost_interop_protocols_tasker_test_taskernode' test scope.
    """

    with sequencer.enter_module_scope_context("automojo.tests.singlehost.interop.protocols.tasker.test_taskernode") as msc:
        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskernode#test_call_tasking_method_pickles_arguments ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskernode#test_call_tasking_method_pickles_arguments"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskernode import test_call_tasking_method_pickles_arguments

            test_call_tasking_method_pickles_arguments()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskernode#test_create_connection_uses_timeout_and_connects ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskernode#test_create_connection_uses_timeout_and_connects"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskernode import test_create_connection_uses_timeout_and_connects

            test_create_connection_uses_timeout_and_connects()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskernode#test_execute_tasking_returns_promise ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskernode#test_execute_tasking_returns_promise"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskernode import test_execute_tasking_returns_promise

            test_execute_tasking_returns_promise()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskernode#test_session_close_resets_session_id_and_calls_remote ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskernode#test_session_close_resets_session_id_and_calls_remote"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskernode import test_session_close_resets_session_id_and_calls_remote

            test_session_close_resets_session_id_and_calls_remote()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskernode#test_session_open_sets_session_id_and_closes_client ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskernode#test_session_open_sets_session_id_and_closes_client"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskernode import test_session_open_sets_session_id_and_closes_client

            test_session_open_sets_session_id_and_closes_client()


    return

def scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskerserver(sequencer):
    """
    This is the entry point for the 'automojo_tests_singlehost_interop_protocols_tasker_test_taskerserver' test scope.
    """

    with sequencer.enter_module_scope_context("automojo.tests.singlehost.interop.protocols.tasker.test_taskerserver") as msc:
        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskerserver#test_get_service_endpoint_matches_listener ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskerserver#test_get_service_endpoint_matches_listener"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskerserver import test_get_service_endpoint_matches_listener

            test_get_service_endpoint_matches_listener()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskerserver#test_serve_forever_runs_in_current_thread ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskerserver#test_serve_forever_runs_in_current_thread"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskerserver import test_serve_forever_runs_in_current_thread

            test_serve_forever_runs_in_current_thread()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskerserver#test_start_runs_service_thread ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskerserver#test_start_runs_service_thread"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskerserver import test_start_runs_service_thread

            test_start_runs_service_thread()


    return

def scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskerservermanager(sequencer):
    """
    This is the entry point for the 'automojo_tests_singlehost_interop_protocols_tasker_test_taskerservermanager' test scope.
    """

    with sequencer.enter_module_scope_context("automojo.tests.singlehost.interop.protocols.tasker.test_taskerservermanager") as msc:
        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskerservermanager#test_spawn_returns_running_server ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskerservermanager#test_spawn_returns_running_server"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskerservermanager import test_spawn_returns_running_server

            test_spawn_returns_running_server()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskerservermanager#test_spawn_uses_logging_directory ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskerservermanager#test_spawn_uses_logging_directory"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskerservermanager import test_spawn_uses_logging_directory

            test_spawn_uses_logging_directory()


    return

def scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskerservice(sequencer):
    """
    This is the entry point for the 'automojo_tests_singlehost_interop_protocols_tasker_test_taskerservice' test scope.
    """

    with sequencer.enter_module_scope_context("automojo.tests.singlehost.interop.protocols.tasker.test_taskerservice") as msc:
        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskerservice#test_archive_folder_creates_zip ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskerservice#test_archive_folder_creates_zip"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskerservice import test_archive_folder_creates_zip

            test_archive_folder_creates_zip()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskerservice#test_file_and_folder_exists ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskerservice#test_file_and_folder_exists"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskerservice import test_file_and_folder_exists

            test_file_and_folder_exists()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskerservice#test_locked_get_session_validations ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskerservice#test_locked_get_session_validations"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskerservice import test_locked_get_session_validations

            test_locked_get_session_validations()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskerservice#test_session_close_all_returns_last_closed_session ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskerservice#test_session_close_all_returns_last_closed_session"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskerservice import test_session_close_all_returns_last_closed_session

            test_session_close_all_returns_last_closed_session()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskerservice#test_session_close_all_returns_none_when_no_sessions ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskerservice#test_session_close_all_returns_none_when_no_sessions"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskerservice import test_session_close_all_returns_none_when_no_sessions

            test_session_close_all_returns_none_when_no_sessions()


    return

def scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskersession(sequencer):
    """
    This is the entry point for the 'automojo_tests_singlehost_interop_protocols_tasker_test_taskersession' test scope.
    """

    with sequencer.enter_module_scope_context("automojo.tests.singlehost.interop.protocols.tasker.test_taskersession") as msc:
        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskersession#test_cancel_tasking_invokes_shutdown_when_running ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskersession#test_cancel_tasking_invokes_shutdown_when_running"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskersession import test_cancel_tasking_invokes_shutdown_when_running

            test_cancel_tasking_invokes_shutdown_when_running()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskersession#test_cancel_tasking_raises_unknown_tasking ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskersession#test_cancel_tasking_raises_unknown_tasking"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskersession import test_cancel_tasking_raises_unknown_tasking

            test_cancel_tasking_raises_unknown_tasking()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskersession#test_dispose_tasking_removes_and_shutdown ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskersession#test_dispose_tasking_removes_and_shutdown"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskersession import test_dispose_tasking_removes_and_shutdown

            test_dispose_tasking_removes_and_shutdown()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskersession#test_get_tasking_progress_returns_progress ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskersession#test_get_tasking_progress_returns_progress"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskersession import test_get_tasking_progress_returns_progress

            test_get_tasking_progress_returns_progress()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskersession#test_get_tasking_result_raises_when_not_complete ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskersession#test_get_tasking_result_raises_when_not_complete"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskersession import test_get_tasking_result_raises_when_not_complete

            test_get_tasking_result_raises_when_not_complete()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskersession#test_has_completed_and_result_ready_checks ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskersession#test_has_completed_and_result_ready_checks"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskersession import test_has_completed_and_result_ready_checks

            test_has_completed_and_result_ready_checks()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskersession#test_post_and_get_tasking_events ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskersession#test_post_and_get_tasking_events"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskersession import test_post_and_get_tasking_events

            test_post_and_get_tasking_events()


    return

def scope_automojo_tests_singlehost_interop_protocols_tasker_test_tasking(sequencer):
    """
    This is the entry point for the 'automojo_tests_singlehost_interop_protocols_tasker_test_tasking' test scope.
    """

    with sequencer.enter_module_scope_context("automojo.tests.singlehost.interop.protocols.tasker.test_tasking") as msc:
        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_tasking#test_get_identity_and_full_name ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_tasking#test_get_identity_and_full_name"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_tasking import test_get_identity_and_full_name

            test_get_identity_and_full_name()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_tasking#test_instantiate_tasking_missing_returns_none ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_tasking#test_instantiate_tasking_missing_returns_none"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_tasking import test_instantiate_tasking_missing_returns_none

            test_instantiate_tasking_missing_returns_none()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_tasking#test_instantiate_tasking_returns_instance ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_tasking#test_instantiate_tasking_returns_instance"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_tasking import test_instantiate_tasking_returns_instance

            test_instantiate_tasking_returns_instance()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_tasking#test_mark_progress_state_transitions ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_tasking#test_mark_progress_state_transitions"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_tasking import test_mark_progress_state_transitions

            test_mark_progress_state_transitions()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_tasking#test_taskingidentity_as_tuple ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_tasking#test_taskingidentity_as_tuple"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_tasking import test_taskingidentity_as_tuple

            test_taskingidentity_as_tuple()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_tasking#test_write_metrics_creates_file ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_tasking#test_write_metrics_creates_file"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_tasking import test_write_metrics_creates_file

            test_write_metrics_creates_file()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_tasking#test_write_metrics_unknown_stream_raises ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_tasking#test_write_metrics_unknown_stream_raises"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_tasking import test_write_metrics_unknown_stream_raises

            test_write_metrics_unknown_stream_raises()


    return

def scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskingadapter(sequencer):
    """
    This is the entry point for the 'automojo_tests_singlehost_interop_protocols_tasker_test_taskingadapter' test scope.
    """

    with sequencer.enter_module_scope_context("automojo.tests.singlehost.interop.protocols.tasker.test_taskingadapter") as msc:
        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskingadapter#test_available_nodes_after_init ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskingadapter#test_available_nodes_after_init"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskingadapter import test_available_nodes_after_init

            test_available_nodes_after_init()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskingadapter#test_checkout_and_checkin_nodes ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskingadapter#test_checkout_and_checkin_nodes"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskingadapter import test_checkout_and_checkin_nodes

            test_checkout_and_checkin_nodes()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskingadapter#test_checkout_nodes_overflow_raises ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskingadapter#test_checkout_nodes_overflow_raises"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskingadapter import test_checkout_nodes_overflow_raises

            test_checkout_nodes_overflow_raises()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskingadapter#test_create_tasking_group_scope_uses_nodes_and_sequencer ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskingadapter#test_create_tasking_group_scope_uses_nodes_and_sequencer"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskingadapter import test_create_tasking_group_scope_uses_nodes_and_sequencer

            test_create_tasking_group_scope_uses_nodes_and_sequencer()


    return

def scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskingevent(sequencer):
    """
    This is the entry point for the 'automojo_tests_singlehost_interop_protocols_tasker_test_taskingevent' test scope.
    """

    with sequencer.enter_module_scope_context("automojo.tests.singlehost.interop.protocols.tasker.test_taskingevent") as msc:
        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskingevent#test_as_dict_serialization ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskingevent#test_as_dict_serialization"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskingevent import test_as_dict_serialization

            test_as_dict_serialization()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskingevent#test_from_dict_creates_equivalent_event ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskingevent#test_from_dict_creates_equivalent_event"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskingevent import test_from_dict_creates_equivalent_event

            test_from_dict_creates_equivalent_event()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskingevent#test_properties_return_values ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskingevent#test_properties_return_values"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskingevent import test_properties_return_values

            test_properties_return_values()


    return

def scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskinggroupscope(sequencer):
    """
    This is the entry point for the 'automojo_tests_singlehost_interop_protocols_tasker_test_taskinggroupscope' test scope.
    """

    with sequencer.enter_module_scope_context("automojo.tests.singlehost.interop.protocols.tasker.test_taskinggroupscope") as msc:
        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskinggroupscope#test_cancel_tasks_collects_errors ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskinggroupscope#test_cancel_tasks_collects_errors"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskinggroupscope import test_cancel_tasks_collects_errors

            test_cancel_tasks_collects_errors()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskinggroupscope#test_clear_summary_progress_calls_recorder ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskinggroupscope#test_clear_summary_progress_calls_recorder"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskinggroupscope import test_clear_summary_progress_calls_recorder

            test_clear_summary_progress_calls_recorder()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskinggroupscope#test_finalize_sync_checks_in_nodes ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskinggroupscope#test_finalize_sync_checks_in_nodes"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskinggroupscope import test_finalize_sync_checks_in_nodes

            test_finalize_sync_checks_in_nodes()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskinggroupscope#test_notify_summary_progress_updates_recorder ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskinggroupscope#test_notify_summary_progress_updates_recorder"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskinggroupscope import test_notify_summary_progress_updates_recorder

            test_notify_summary_progress_updates_recorder()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskinggroupscope#test_update_group_records_results_once ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskinggroupscope#test_update_group_records_results_once"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskinggroupscope import test_update_group_records_results_once

            test_update_group_records_results_once()


    return

def scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskingprogressmonitor(sequencer):
    """
    This is the entry point for the 'automojo_tests_singlehost_interop_protocols_tasker_test_taskingprogressmonitor' test scope.
    """

    with sequencer.enter_module_scope_context("automojo.tests.singlehost.interop.protocols.tasker.test_taskingprogressmonitor") as msc:
        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskingprogressmonitor#test_pull_progress_entry_collects_completed_progress ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskingprogressmonitor#test_pull_progress_entry_collects_completed_progress"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskingprogressmonitor import test_pull_progress_entry_collects_completed_progress

            test_pull_progress_entry_collects_completed_progress()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskingprogressmonitor#test_pull_progress_entry_handles_missing_progress ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskingprogressmonitor#test_pull_progress_entry_handles_missing_progress"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskingprogressmonitor import test_pull_progress_entry_handles_missing_progress

            test_pull_progress_entry_handles_missing_progress()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskingprogressmonitor#test_release_removes_promise ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskingprogressmonitor#test_release_removes_promise"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskingprogressmonitor import test_release_removes_promise

            test_release_removes_promise()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskingprogressmonitor#test_start_runs_monitor_thread ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskingprogressmonitor#test_start_runs_monitor_thread"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskingprogressmonitor import test_start_runs_monitor_thread

            test_start_runs_monitor_thread()


    return

def scope_automojo_tests_singlehost_interop_protocols_tasker_test_taskingresultpromise(sequencer):
    """
    This is the entry point for the 'automojo_tests_singlehost_interop_protocols_tasker_test_taskingresultpromise' test scope.
    """

    with sequencer.enter_module_scope_context("automojo.tests.singlehost.interop.protocols.tasker.test_taskingresultpromise") as msc:
        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskingresultpromise#test_call_tasking_method_forwards_args ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskingresultpromise#test_call_tasking_method_forwards_args"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskingresultpromise import test_call_tasking_method_forwards_args

            test_call_tasking_method_forwards_args()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskingresultpromise#test_cancel_invokes_node ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskingresultpromise#test_cancel_invokes_node"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskingresultpromise import test_cancel_invokes_node

            test_cancel_invokes_node()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskingresultpromise#test_getters_return_node_values ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskingresultpromise#test_getters_return_node_values"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskingresultpromise import test_getters_return_node_values

            test_getters_return_node_values()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskingresultpromise#test_is_task_complete_relays_node ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskingresultpromise#test_is_task_complete_relays_node"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskingresultpromise import test_is_task_complete_relays_node

            test_is_task_complete_relays_node()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskingresultpromise#test_taskingref_as_dict ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskingresultpromise#test_taskingref_as_dict"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskingresultpromise import test_taskingref_as_dict

            test_taskingref_as_dict()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskingresultpromise#test_wait_completes_when_done ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskingresultpromise#test_wait_completes_when_done"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskingresultpromise import test_wait_completes_when_done

            test_wait_completes_when_done()

        # ================ Test Scope: automojo.tests.singlehost.interop.protocols.tasker.test_taskingresultpromise#test_wait_timeout_raises_error ================

        test_scope_name = "automojo.tests.singlehost.interop.protocols.tasker.test_taskingresultpromise#test_wait_timeout_raises_error"

        with sequencer.enter_test_scope_context(test_scope_name) as tscope:
            from automojo.tests.singlehost.interop.protocols.tasker.test_taskingresultpromise import test_wait_timeout_raises_error

            test_wait_timeout_raises_error()


    return
