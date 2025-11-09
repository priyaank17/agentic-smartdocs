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
    precision_recall_by_narrative = {}
    overall_tp = 0
    overall_fp = 0
    overall_fn = 0
    overall_precision = 0
    overall_recall = 0
    len_data = 0
    overall_total_expected = 0
    overall_total_output = 0
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
        total_output = len(output_json_for_narrative)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        precision_recall_by_narrative[narrative_id] = {
            "precision": precision,
            "recall": recall,
            "true_positive": tp,
            "false_positive": fp,
            "false_negative": fn,
            "total_expected": total_expected,
            "total_output": total_output,
        }
        overall_tp += tp
        overall_fp += fp
        overall_fn += fn
        overall_precision += precision
        overall_recall += recall
        overall_total_expected += total_expected
        overall_total_output += total_output
        len_data += 1

    # overall_precision = (
    #     overall_tp / (overall_tp + overall_fp) if overall_tp + overall_fp > 0 else 0
    # )
    # overall_recall = (
    #     overall_tp / (overall_tp + overall_fn) if overall_tp + overall_fn > 0 else 0
    # )
    overall_recall = overall_recall / len_data
    overall_precision = overall_precision / len_data
    precision_recall_by_narrative["overall_property_accuracy"] = {
        "precision": overall_precision,
        "recall": overall_recall,
        "true_positive": overall_tp,
        "false_positive": overall_fp,
        "false_negative": overall_fn,
        "total_expected": overall_total_expected,
        "total_output": overall_total_output,
    }
    return precision_recall_by_narrative
