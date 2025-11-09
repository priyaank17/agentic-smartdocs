"""Module contains functions for control loop count accuracy"""

from src.utils.log import logger


def calculate_control_loop_count_accuracy(
    expected_control_loop_count, received_control_loop_count
):
    """Calculates the accuracy of control loop count"""
    logger.info("INIT: calculate_control_loop_count_accuracy")
    accuracy_dict = {}

    for narrative_id, expected_count in expected_control_loop_count.items():
        received_count = received_control_loop_count.get(narrative_id, 0)
        true_positives_control_loops = min(expected_count, received_count)

        precision = 0
        recall = 0

        if received_count != 0:
            precision = true_positives_control_loops / received_count
            if true_positives_control_loops > received_count:
                print("Not valid")

        if expected_count != 0:
            recall = true_positives_control_loops / expected_count
        if expected_count == 0 and received_count == 0:
            precision = 1.0
            recall = 1.0
        accuracy_dict[narrative_id] = {
            "control_loop_count_precision": precision,
            "control_loop_count_recall": recall,
            "control_loop_count_true_positives": true_positives_control_loops,
            "control_loop_count_received_count": received_count,
            "control_loop_count_expected_count": expected_count,
        }
    logger.info("DONE: calculate_control_loop_count_accuracy")
    return accuracy_dict


def calculate_total_control_loop_count_accuracy(
    expected_control_loop_count, received_control_loop_count
):
    """Calculates the accuracy of total control loop count"""
    logger.info("INIT: calculate total control loop count accuracy")
    precision_total = 0
    recall_total = 0
    true_positives_total = 0
    received_count_total = 0
    expected_count_total = 0

    # for narrative_id, expected_count in expected_control_loop_count.items():
    narrative_ids = set(expected_control_loop_count.keys()) | set(
        received_control_loop_count.keys()
    )
    for narrative_id in narrative_ids:
        received_count = received_control_loop_count.get(narrative_id, 0)
        expected_count = expected_control_loop_count.get(narrative_id, 0)
        true_positives_control_loops = min(expected_count, received_count)

        precision = 0
        recall = 0

        if received_count != 0:
            precision = true_positives_control_loops / received_count
            if true_positives_control_loops > received_count:
                print("Not valid")

        if expected_count != 0:
            recall = true_positives_control_loops / expected_count
        if expected_count == 0 and received_count == 0:
            precision = 1.0
            recall = 1.0
        precision_total += precision
        recall_total += recall
        true_positives_total += true_positives_control_loops
        received_count_total += received_count
        expected_count_total += expected_count

    num_assets = len(expected_control_loop_count)
    overall_precision_connections = precision_total / num_assets
    overall_recall_connections = recall_total / num_assets

    results = {
        "control_loop_count_precision": overall_precision_connections,
        "control_loop_count_recall": overall_recall_connections,
        "control_loop_count_true_positives": true_positives_total,
        "control_loop_count_received_count": received_count_total,
        "control_loop_count_expected_count": expected_count_total,
    }
    logger.info(
        f"DONE: calculating total control loop count accuracy for {num_assets} assets."
    )
    return results
