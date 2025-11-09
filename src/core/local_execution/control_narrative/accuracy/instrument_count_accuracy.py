"""This module calculates the accuracy of the instrument count
 for each narrative and the total accuracy of the instrument count
   for all narratives."""

from src.utils.log import logger


def calculate_instrument_count_accuracy(
    expected_instrument_count, received_instrument_count
):
    """Calculates the accuracy of instrument count"""
    logger.info("INIT: calculate_instrument_count_accuracy")
    accuracy_dict = {}
    narrative_ids = set(expected_instrument_count.keys()) | set(
        received_instrument_count.keys()
    )
    # for narrative_id, expected_count in expected_instrument_count.items():
    for narrative_id in narrative_ids:
        expected_count = expected_instrument_count.get(narrative_id, 0)
        received_count = received_instrument_count.get(narrative_id, 0)
        true_positives_instruments = min(expected_count, received_count)

        precision = 0
        recall = 0

        if received_count != 0:
            precision = true_positives_instruments / received_count
            if true_positives_instruments > received_count:
                print("Not valid")

        if expected_count != 0:
            recall = true_positives_instruments / expected_count
        if expected_count == 0 and received_count == 0:
            precision = 1.0
            recall = 1.0
        accuracy_dict[narrative_id] = {
            "instrument_count_precision": precision,
            "instrument_count_recall": recall,
            "instrument_count_true_positives": true_positives_instruments,
            "instrument_count_received_count": received_count,
            "instrument_count_expected_count": expected_count,
        }
    logger.info("DONE: calculate_instrument_count_accuracy")
    return accuracy_dict


def calculate_total_instrument_count_accuracy(
    expected_instrument_count, received_instrument_count
):
    """Calculates the accuracy of total instrument count"""
    logger.info("INIT: calculate total instrument count accuracy")
    precision_total = 0
    recall_total = 0
    true_positives_total = 0
    received_count_total = 0
    expected_count_total = 0

    for narrative_id, expected_count in expected_instrument_count.items():
        received_count = received_instrument_count.get(narrative_id, 0)
        true_positives_instruments = min(expected_count, received_count)

        precision = 0
        recall = 0

        if received_count != 0:
            precision = true_positives_instruments / received_count
            if true_positives_instruments > received_count:
                print("Not valid")

        if expected_count != 0:
            recall = true_positives_instruments / expected_count
        if expected_count == 0 and received_count == 0:
            precision = 1.0
            recall = 1.0
        precision_total += precision
        recall_total += recall
        true_positives_total += true_positives_instruments
        received_count_total += received_count
        expected_count_total += expected_count

    num_assets = len(expected_instrument_count)
    overall_precision_connections = precision_total / num_assets
    overall_recall_connections = recall_total / num_assets

    results = {
        "instrument_count_precision": overall_precision_connections,
        "instrument_count_recall": overall_recall_connections,
        "instrument_count_true_positives": true_positives_total,
        "instrument_count_received_count": received_count_total,
        "instrument_count_expected_count": expected_count_total,
    }
    logger.info(
        f"DONE: calculating total instruments count accuracy for {num_assets} assets."
    )
    return results
