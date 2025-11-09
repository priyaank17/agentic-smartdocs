"""This module calculates the accuracy of the instrument count
 for each narrative and the total accuracy of the instrument count
   for all narratives."""

from src.utils.log import logger


def calculate_instrument_count_accuracy(
    expected_instrument_count, extracted_instrument_count
):
    """Calculates the accuracy of instrument count"""
    logger.info("INIT: calculate_instrument_count_accuracy")
    precision_recall_results = []
    overall_accuracy_matrix = overall_accuracy_matrix_info()
    narrative_ids = set(expected_instrument_count.keys()) | set(
        extracted_instrument_count.keys()
    )
    for narrative_id in narrative_ids:
        expected_count = expected_instrument_count.get(narrative_id, 0)
        extracted_count = extracted_instrument_count.get(narrative_id, 0)
        true_positives_instruments = min(expected_count, extracted_count)
        precision = 0
        recall = 0

        if extracted_count != 0:
            precision = true_positives_instruments / extracted_count
            if true_positives_instruments > extracted_count:
                print("Not valid")

        if expected_count != 0:
            recall = true_positives_instruments / expected_count
        if expected_count == 0 and extracted_count == 0:
            precision = 1.0
            recall = 1.0
        precision_recall_results.append(
            {
                "narrative_id": narrative_id,
                "instrument_count_precision": precision,
                "instrument_count_recall": recall,
                "instrument_count_true_positives": true_positives_instruments,
                "instrument_count_extracted_count": extracted_count,
                "instrument_count_expected_count": expected_count,
            }
        )
        overall_accuracy_matrix["instrument_count_true_positives"] = (
            overall_accuracy_matrix["instrument_count_true_positives"]
            + true_positives_instruments
        )
        overall_accuracy_matrix["instrument_count_extracted_count"] = (
            overall_accuracy_matrix["instrument_count_extracted_count"]
            + extracted_count
        )
        overall_accuracy_matrix["instrument_count_expected_count"] = (
            overall_accuracy_matrix["instrument_count_expected_count"] + expected_count
        )
        overall_accuracy_matrix["instrument_count_precision"] = (
            overall_accuracy_matrix["instrument_count_precision"]
            + precision * extracted_count
        )
        overall_accuracy_matrix["instrument_count_recall"] = (
            overall_accuracy_matrix["instrument_count_recall"] + recall * extracted_count
        )

    overall_accuracy_matrix["instrument_count_precision"] = (
        overall_accuracy_matrix["instrument_count_precision"]
        / overall_accuracy_matrix["instrument_count_extracted_count"]
    )
    overall_accuracy_matrix["instrument_count_recall"] = (
        overall_accuracy_matrix["instrument_count_recall"]
        / overall_accuracy_matrix["instrument_count_extracted_count"]
    )
    precision_recall_results.append(overall_accuracy_matrix)
    logger.info("DONE: calculate_instrument_count_accuracy")
    return precision_recall_results


def overall_accuracy_matrix_info():
    """Overall Accuracy Matrix Info."""
    return {
        "narrative_id": "overall_count_accuracy",
        "instrument_count_precision": 0,
        "instrument_count_recall": 0,
        "instrument_count_true_positives": 0,
        "instrument_count_extracted_count": 0,
        "instrument_count_expected_count": 0,
    }
