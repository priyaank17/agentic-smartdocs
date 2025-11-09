"""Module contains functions for control loop count accuracy"""

from src.utils.log import logger


def calculate_control_loop_count_accuracy(
    expected_control_loop_count, extracted_control_loop_count
):
    """Calculates the accuracy of control loop count"""
    logger.info("INIT: calculate_control_loop_count_accuracy")
    precision_recall_results = []
    overall_accuracy_matrix = overall_accuracy_matrix_info()

    for narrative_id, expected_count in expected_control_loop_count.items():
        extracted_count = extracted_control_loop_count.get(narrative_id, 0)
        true_positives_control_loops = min(expected_count, extracted_count)

        precision = 0
        recall = 0

        if extracted_count != 0:
            precision = true_positives_control_loops / extracted_count
            if true_positives_control_loops > extracted_count:
                print("Not valid")

        if expected_count != 0:
            recall = true_positives_control_loops / expected_count
        if expected_count == 0 and extracted_count == 0:
            precision = 1.0
            recall = 1.0
        precision_recall_results.append(
            {
                "narrative_id": narrative_id,
                "control_loop_count_precision": precision,
                "control_loop_count_recall": recall,
                "control_loop_count_true_positives": true_positives_control_loops,
                "control_loop_count_extracted_count": extracted_count,
                "control_loop_count_expected_count": expected_count,
            }
        )
        overall_accuracy_matrix["control_loop_count_true_positives"] = (
            overall_accuracy_matrix["control_loop_count_true_positives"]
            + true_positives_control_loops
        )
        overall_accuracy_matrix["control_loop_count_extracted_count"] = (
            overall_accuracy_matrix["control_loop_count_extracted_count"]
            + extracted_count
        )
        overall_accuracy_matrix["control_loop_count_expected_count"] = (
            overall_accuracy_matrix["control_loop_count_expected_count"] + expected_count
        )
        overall_accuracy_matrix["control_loop_count_precision"] = (
            overall_accuracy_matrix["control_loop_count_precision"]
            + precision * extracted_count
        )
        overall_accuracy_matrix["control_loop_count_recall"] = (
            overall_accuracy_matrix["control_loop_count_recall"] + recall * extracted_count
        )

    overall_accuracy_matrix["control_loop_count_precision"] = (
        overall_accuracy_matrix["control_loop_count_precision"]
        / overall_accuracy_matrix["control_loop_count_extracted_count"]
    )
    overall_accuracy_matrix["control_loop_count_recall"] = (
        overall_accuracy_matrix["control_loop_count_recall"]
        / overall_accuracy_matrix["control_loop_count_extracted_count"]
    )
    precision_recall_results.append(overall_accuracy_matrix)
    logger.info("DONE: calculate_control_loop_count_accuracy")
    return precision_recall_results


def overall_accuracy_matrix_info():
    """Overall Accuracy Matrix Info."""
    return {
        "narrative_id": "overall_count_accuracy",
        "control_loop_count_precision": 0,
        "control_loop_count_recall": 0,
        "control_loop_count_true_positives": 0,
        "control_loop_count_extracted_count": 0,
        "control_loop_count_expected_count": 0,
    }
