"""This module contains functions for Instrument Property Accuracy."""

from collections import defaultdict


def group_data(ground_truth_json, output_json):
    """Group data by narrative_id"""
    grouped_ground_truth_json = defaultdict(list)
    grouped_output_json = defaultdict(list)

    for ground_truth in ground_truth_json["data"]:
        grouped_ground_truth_json[ground_truth["narrative_id"]].append(
            {
                "tag": ground_truth["tag"],
                "operation_type": ground_truth["operation_type"],
            }
        )

    for output in output_json["data"]:
        grouped_output_json[output["narrative_id"]].append(
            {
                "tag": output["tag"],
                "operation_type": output["operation_type"],
            }
        )
    return grouped_ground_truth_json, grouped_output_json


def instrument_property_accuracy(ground_truth_json, output_json):
    """Instrument Property Accuracy."""
    grouped_ground_truth_json, grouped_output_json = group_data(
        ground_truth_json, output_json
    )
    # precision_recall_by_narrative = {}
    precision_recall_results = []
    overall_accuracy_matrix = overall_accuracy_matrix_info()
    for narrative_id in sorted(
        set(grouped_ground_truth_json.keys()),
        key=lambda x: int(x.split("_")[1]),
    ):
        ground_truth_json_for_narrative = grouped_ground_truth_json.get(
            narrative_id, []
        )
        output_json_for_narrative = grouped_output_json.get(narrative_id, [])

        tp = sum(
            1
            for ground_truth in ground_truth_json_for_narrative
            if ground_truth in output_json_for_narrative
        )
        fn = len(ground_truth_json_for_narrative) - tp
        fp = len(output_json_for_narrative) - tp
        total_expected = len(ground_truth_json_for_narrative)
        total_extracted = len(output_json_for_narrative)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        precision_recall_results.append(
            {
                "narrative_id": narrative_id,
                "precision": precision,
                "recall": recall,
                "true_positive": tp,
                "false_positive": fp,
                "false_negative": fn,
                "total_expected": total_expected,
                "total_extracted": total_extracted,
                "total_correctly_extracted": tp,
            }
        )
        overall_accuracy_matrix["true_positive"] = (
            overall_accuracy_matrix["true_positive"] + tp
        )
        overall_accuracy_matrix["false_positive"] = (
            overall_accuracy_matrix["false_positive"] + fp
        )
        overall_accuracy_matrix["false_negative"] = (
            overall_accuracy_matrix["false_negative"] + fn
        )
        overall_accuracy_matrix["total_expected"] = (
            overall_accuracy_matrix["total_expected"] + total_expected
        )
        overall_accuracy_matrix["total_extracted"] = (
            overall_accuracy_matrix["total_extracted"] + total_extracted
        )
        overall_accuracy_matrix["total_correctly_extracted"] = (
            overall_accuracy_matrix["total_correctly_extracted"] + tp
        )
        overall_accuracy_matrix["precision"] = (
            overall_accuracy_matrix["precision"] + precision * total_extracted
        )
        overall_accuracy_matrix["recall"] = (
            overall_accuracy_matrix["recall"] + recall * total_extracted
        )
    overall_accuracy_matrix["precision"] = (
        overall_accuracy_matrix["precision"]
        / overall_accuracy_matrix["total_extracted"]
    )
    overall_accuracy_matrix["recall"] = (
        overall_accuracy_matrix["recall"] / overall_accuracy_matrix["total_extracted"]
    )
    precision_recall_results.append(overall_accuracy_matrix)
    return precision_recall_results


def overall_accuracy_matrix_info():
    """Overall Accuracy Matrix Info."""
    return {
        "narrative_id": "overall_count_accuracy",
        "precision": 0,
        "recall": 0,
        "true_positive": 0,
        "false_positive": 0,
        "false_negative": 0,
        "total_expected": 0,
        "total_extracted": 0,
        "total_correctly_extracted": 0,
    }
