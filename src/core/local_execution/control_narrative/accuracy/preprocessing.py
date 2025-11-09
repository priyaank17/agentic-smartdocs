"""This module contains functions for preprocessing"""

from src.utils.log import logger


def calculate_control_narrative_count(control_loop):
    """Calculate control narrative count"""
    logger.info("INIT: calculate control narrative count")
    control_narrative_count = {}
    for cl in control_loop["data"]:
        narrative_id = cl.get("narrative_id")
        if narrative_id:
            control_narrative_count[narrative_id] = (
                control_narrative_count.get(narrative_id, 0) + 1
            )
    logger.info("DONE: calculated control narrative count")
    return control_narrative_count


def align_connection_counts(
    expected_control_narrative_count, received_control_narrative_count
):
    """This function aligns the connection counts"""
    common_keys = set(expected_control_narrative_count.keys()) & set(
        received_control_narrative_count.keys()
    )
    aligned_expected_count = {
        key: expected_control_narrative_count[key] for key in common_keys
    }
    aligned_received_count = {
        key: received_control_narrative_count[key] for key in common_keys
    }
    return aligned_expected_count, aligned_received_count


def get_control_loops_count(expected_control_loop, received_control_loop):
    """This function returns the control loop count"""
    logger.info("INIT: Get control_loop count")
    expected_control_loop_count = calculate_control_narrative_count(
        expected_control_loop
    )
    received_control_loop_count = calculate_control_narrative_count(
        received_control_loop
    )
    logger.info("DONE: counted control_loop")
    return expected_control_loop_count, received_control_loop_count


def get_instruments_count(expected_instruments, received_instruments):
    """This function returns the instrument count"""
    logger.info("INIT: Get instruments count")
    expected_instrument_count = calculate_control_narrative_count(expected_instruments)
    received_instrument_count = calculate_control_narrative_count(received_instruments)
    logger.info("DONE: counted instruments")
    return expected_instrument_count, received_instrument_count
