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


def calculate_similarity(process_variable_gt, process_variable_output):
    """Calculate similarity between process_variable_gt and process_variable_output"""
    return len(set(process_variable_gt) & set(process_variable_output))


def initialize_metrics():
    """Initialize metrics for precision and recall calculation."""
    return {
        "overall_tp": 0,
        "overall_fp": 0,
        "overall_fn": 0,
        "overall_precision": 0,
        "overall_recall": 0,
        "overall_total_expected": 0,
        "overall_total_best_matched": 0,
        "len_data": 0,
    }


def get_best_match_metrics(ground_truth_item, best_match, property_name):
    """Get metrics for best match."""
    tp = len(set(ground_truth_item[property_name]) & set(best_match[property_name]))
    fp = len(set(best_match[property_name]) - set(ground_truth_item[property_name]))
    fn = len(set(ground_truth_item[property_name]) - set(best_match[property_name]))

    precision = tp / (tp + fp) if tp + fp > 0 else 0
    recall = tp / (tp + fn) if tp + fn > 0 else 0
    if len(ground_truth_item[property_name]) == 0 & len(best_match[property_name]) == 0:
        precision = 1.0
        recall = 1.0

    return tp, fp, fn, precision, recall


def calculate_precision_recall(ground_truth_grouped, output_grouped, property_name):
    """Calculate precision and recall."""
    logger.info("INIT: calculate precision and recall accuracy")
    precision_recall_results = []
    metrics = initialize_metrics()

    for narrative_id, ground_truth_list in ground_truth_grouped.items():
        output_list = output_grouped.get(narrative_id, [])

        if output_list:
            for ground_truth_item in ground_truth_list:
                best_match = None
                best_score = 0
                tp = 0
                fp = 0
                fn = 0
                total_expected = len(ground_truth_item[property_name])
                total_best_matched = 0

                for output_item in output_list:
                    if (len(ground_truth_item[property_name]) == 0) and (
                        len(output_item[property_name]) == 0
                    ):
                        best_match = output_item
                        break
                    score = calculate_similarity(
                        ground_truth_item[property_name], output_item[property_name]
                    )

                    if score > best_score:
                        best_score = score
                        best_match = output_item
                        total_best_matched = len(best_match[property_name])

                if best_match:
                    tp, fp, fn, precision, recall = get_best_match_metrics(
                        ground_truth_item, best_match, property_name
                    )
                    precision_recall_results.append(
                        {
                            "narrative_id": narrative_id,
                            "id": ground_truth_item["control_loop_id"],
                            "precision": precision,
                            "recall": recall,
                            "true_positives": tp,
                            "false_positives": fp,
                            "false_negatives": fn,
                            "total_expected": total_expected,
                            "total_best_matched": total_best_matched,
                        }
                    )
                    output_list.remove(best_match)
                else:
                    precision = 0
                    recall = 0
                    tp = 0
                    fp = 0  # len(output_item[property_name])
                    fn = len(ground_truth_item[property_name])  # 0
                    precision_recall_results.append(
                        {
                            "narrative_id": narrative_id,
                            "id": ground_truth_item["control_loop_id"],
                            "precision": precision,
                            "recall": recall,
                            "true_positives": tp,
                            "false_positives": fp,
                            "false_negatives": fn,
                            "total_expected": total_expected,
                            "total_best_matched": total_best_matched,
                        }
                    )
                metrics["overall_tp"] += tp
                metrics["overall_fp"] += fp
                metrics["overall_fn"] += fn
                metrics["overall_precision"] += precision
                metrics["overall_recall"] += recall
                metrics["overall_total_expected"] += total_expected
                metrics["overall_total_best_matched"] += total_best_matched
                metrics["len_data"] += 1

    overall_recall = metrics["overall_recall"] / metrics["len_data"]
    overall_precision = metrics["overall_precision"] / metrics["len_data"]
    precision_recall_results.append(
        {
            "narrative_id": f"overall_{property_name}_accuracy",
            "id": f"overall_{property_name}_accuracy",
            "precision": overall_precision,
            "recall": overall_recall,
            "true_positives": metrics["overall_tp"],
            "false_positives": metrics["overall_fp"],
            "false_negatives": metrics["overall_fn"],
            "total_expected": metrics["overall_total_expected"],
            "total_best_matched": metrics["overall_total_best_matched"],
        }
    )
    logger.info("DONE: calculated precision and recall accuracy")
    return precision_recall_results


def process_variable_accuracy(ground_truth, output_json):
    """Process variable accuracy."""
    logger.info("INIT: process_variable_accuracy")
    ground_truth_grouped, output_grouped = group_data(ground_truth, output_json)
    precision_recall_results = calculate_precision_recall(
        ground_truth_grouped, output_grouped, "process_variable"
    )
    logger.info("DONE: process_variable_accuracy")
    return precision_recall_results


def controller_accuracy(ground_truth, output_json):
    """Controller accuracy."""
    logger.info("INIT: controller_accuracy")
    ground_truth_grouped, output_grouped = group_data(ground_truth, output_json)
    precision_recall_results = calculate_precision_recall(
        ground_truth_grouped, output_grouped, "controller"
    )
    logger.info("DONE: controller_accuracy")
    return precision_recall_results


def final_control_element_accuracy(ground_truth, output_json):
    """Final control element accuracy."""
    logger.info("INIT: final_control_element_accuracy")
    ground_truth_grouped, output_grouped = group_data(ground_truth, output_json)
    precision_recall_results = calculate_precision_recall(
        ground_truth_grouped, output_grouped, "final_control_element"
    )
    logger.info("DONE: final_control_element_accuracy")
    return precision_recall_results


def overall_property_accuracy(process_variable, controller, final_control_element):
    """Overall property accuracy."""
    logger.info("INIT: process_variable_accuracy")
    overall_process_variable = [
        item for item in process_variable if item["id"].startswith("overall_")
    ]
    overall_controller = [
        item for item in controller if item["id"].startswith("overall_")
    ]
    overall_final_control_element = [
        item for item in final_control_element if item["id"].startswith("overall_")
    ]
    merged_data = (
        overall_process_variable + overall_controller + overall_final_control_element
    )
    selected_fields = [
        {
            "id": item["id"],
            "precision": item["precision"],
            "recall": item["recall"],
            "true_positives": item["true_positives"],
            "false_positives": item["false_positives"],
            "false_negatives": item["false_negatives"],
            "total_expected": item["total_expected"],
            "total_best_matched": item["total_best_matched"],
        }
        for item in merged_data
    ]
    logger.info("DONE: process_variable_accuracy")
    return selected_fields
