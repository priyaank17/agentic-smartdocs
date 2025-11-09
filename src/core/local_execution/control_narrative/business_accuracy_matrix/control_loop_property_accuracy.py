"""This module contains functions for Control Loop Property Accuracy."""

from collections import defaultdict
from src.utils.log import logger


def group_data(ground_truth, output_json):
    """Group data by narrative_id"""
    ground_truth_grouped = defaultdict(list)
    output_grouped = defaultdict(list)

    for gt_entry in ground_truth["data"]:
        ground_truth_grouped[gt_entry["narrative_id"]].append(gt_entry)

    for output_entry in output_json["data"]:
        output_grouped[output_entry["narrative_id"]].append(output_entry)
    return ground_truth_grouped, output_grouped


def overall_accuracy_matrix_info():
    """Overall Accuracy Matrix Info."""
    return {
        "narrative_id": "overall_property_accuracy",
        "precision": 0,
        "recall": 0,
        "true_positive": 0,
        "false_positive": 0,
        "false_negative": 0,
        "total_expected": 0,
        "total_extracted": 0,
        "total_correctly_extracted": 0,
    }


def calculate_precision_recall(ground_truth_grouped, output_grouped):
    """Calculate precision and recall."""
    logger.info("INIT: calculate precision and recall accuracy")
    precision_recall_results = []
    overall_accuracy_matrix = overall_accuracy_matrix_info()
    for narrative_id, ground_truth_list in ground_truth_grouped.items():
        output_list = output_grouped.get(narrative_id, [])
        tp = 0
        fp = 0
        fn = 0
        total_expected = len(ground_truth_list)
        total_extracted = len(output_list)
        if output_list:
            for output_item in output_list:
                for ground_truth_item in ground_truth_list:
                    if (
                        sorted(output_item["process_variable"])
                        == sorted(ground_truth_item["process_variable"])
                        and sorted(output_item["controller"])
                        == sorted(ground_truth_item["controller"])
                        and sorted(output_item["final_control_element"])
                        == sorted(ground_truth_item["final_control_element"])
                    ):
                        best_match = ground_truth_item
                        ground_truth_list.remove(best_match)
                        tp = tp + 1
                        break
                fn = len(ground_truth_list)
            fp = len(output_list) - tp
            precision = tp / (tp + fp) if tp + fp > 0 else 0
            recall = tp / (tp + fn) if tp + fn > 0 else 0
            if total_expected == 0 & total_extracted == 0:
                precision = 1.0
                recall = 1.0
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
    logger.info("DONE: calculated precision and recall accuracy")
    return precision_recall_results


def control_loop_property_accuracy(ground_truth_json, output_json):
    """Overall property accuracy."""
    logger.info("INIT: process_variable_accuracy")
    ground_truth_grouped, output_grouped = group_data(ground_truth_json, output_json)
    precision_recall_results = calculate_precision_recall(
        ground_truth_grouped, output_grouped
    )
    return precision_recall_results
