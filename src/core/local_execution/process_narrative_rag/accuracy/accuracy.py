""""
This module contains functions for Accuracy."""

from collections import defaultdict
import os
import json


def compare_assets(gt, ext):
    """Check if the source and destination assets match (case-insensitive)."""
    return (
        gt["source_asset_name"].lower() == ext["source_asset_name"].lower()
        and gt["destination_asset_name"].lower()
        == ext["destination_asset_name"].lower()
    )


def compare_values(gt, ext, field):
    """Compare the values of a specific field (ignoring units)."""
    return gt[field]["value"] == ext[field]["value"]


def update_accuracy_matrix(accuracy_matrix, field, is_correct):
    """Update the accuracy matrix for a specific field."""
    accuracy_matrix[field]["total"] += 1
    if is_correct:
        accuracy_matrix[field]["correct"] += 1


def process_fields(gt, ext, accuracy_matrix, value_fields):
    """Process fields."""
    for field in value_fields:
        if field in gt and field in ext:
            update_accuracy_matrix(
                accuracy_matrix, f"{field}", compare_values(gt, ext, field)
            )


def all_values_match(gt, ext, value_fields):
    """Check if all value fields (flowrate, temperature, pressure) match."""
    return all(compare_values(gt, ext, field) for field in value_fields)


def compute_metrics(ground_truth, extracted_data):
    """Calculate accuracy, recall, and precision based on the values and asset names."""
    accuracy_matrix = defaultdict(lambda: {"correct": 0, "total": 0})
    recall_data = {"correct": 0, "total": 0}
    precision_data = {"correct": 0, "total": 0}
    value_fields = ["flowrate", "temperature", "pressure"]
    recall_json = []
    not_recall_json = []
    precision_json = []
    not_precision_json = []
    for gt in ground_truth:
        in_recall = False
        recall_data["total"] += 1

        for ext in extracted_data:
            if compare_assets(gt, ext):
                recall_data["correct"] += 1
                recall_json.append(gt)
                in_recall = True
                precision_data["total"] += 1
                if all_values_match(gt, ext, value_fields):
                    precision_data["correct"] += 1
                    precision_json.append(gt)
                else:
                    not_precision_json.append(gt)
                process_fields(gt, ext, accuracy_matrix, value_fields)
                update_accuracy_matrix(
                    accuracy_matrix,
                    "source_asset_name",
                    gt["source_asset_name"].lower() == ext["source_asset_name"].lower(),
                )
                update_accuracy_matrix(
                    accuracy_matrix,
                    "destination_asset_name",
                    gt["destination_asset_name"].lower()
                    == ext["destination_asset_name"].lower(),
                )
                break
        if not in_recall:
            not_recall_json.append(gt)

    # save_precision_recall_local(recall_json, precision_json, not_precision_json, not_recall_json)
    return accuracy_matrix, recall_data, precision_data


def save_precision_recall_local(recall_json, precision_json, not_precision_json, not_recall_json):
    """Save precision and recall data to local file."""
    precision_recall_path = "data/local/mafpp/process_narrative/accuracy/6_nov/2/"
    recall_path = precision_recall_path + "recall.json"
    os.makedirs(os.path.dirname(recall_path), exist_ok=True)
    save_json_to_local(
        recall_json, recall_path
    )

    precision_path = precision_recall_path + "precision.json"
    os.makedirs(os.path.dirname(precision_path), exist_ok=True)

    save_json_to_local(
        precision_json, precision_path
    )

    not_precision_path = precision_recall_path + "not_precision.json"
    os.makedirs(os.path.dirname(not_precision_path), exist_ok=True)

    save_json_to_local(
        not_precision_json, not_precision_path
    )

    not_recall_path = precision_recall_path + "not_recall.json"
    os.makedirs(os.path.dirname(not_recall_path), exist_ok=True)

    save_json_to_local(
        not_recall_json, not_recall_path
    )


def save_json_to_local(data, file_path):
    """Save JSON data to a local file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def calculate_recall(recall_data):
    """Calculate recall."""
    recall = (
        recall_data["correct"] / recall_data["total"] if recall_data["total"] > 0 else 0
    )
    return recall


def calculate_precision(precision_data):
    """Calculate precision."""
    precision = (
        precision_data["correct"] / precision_data["total"]
        if precision_data["total"] > 0
        else 0
    )
    return precision


def calculate_accuracy(accuracy_matrix):
    """Calculate accuracy from accuracy matrix."""
    accuracy_results = {}
    for field, counts in accuracy_matrix.items():
        correct = counts["correct"]
        total = counts["total"]
        accuracy_results[field] = (correct / total) * 100 if total > 0 else 0
    return accuracy_results


if __name__ == "__main__":

    GROUND_TRUTH_PATH = "tests/test_data/mafpp/gt_process_narrative.json"

    with open(GROUND_TRUTH_PATH, "r", encoding="utf-8") as file:
        GROUND_TRUTH_DATA = json.load(file)

    EXTRACTED_DATA_PATH = (
        "data/local/mafpp/process_narrative/"
        "test_output/6_nov/7.PROCESS_NARRATIVE.adm.json"
    )

    with open(EXTRACTED_DATA_PATH, "r", encoding="utf-8") as file:
        EXTRACTED_DATA = json.load(file)
    EXTRACTED_DATA = EXTRACTED_DATA["connections"]
    ACCURACY_MATRIX, RECALL_DATA, PRECISION_DATA = compute_metrics(
        GROUND_TRUTH_DATA, EXTRACTED_DATA
    )
    ACCURACY_RESULTS = calculate_accuracy(ACCURACY_MATRIX)
    RECALL = calculate_recall(RECALL_DATA)
    PRECISION = calculate_precision(PRECISION_DATA)

    print("Accuracy Matrix (Based on Values Only):")
    for FIELD, ACC in ACCURACY_RESULTS.items():
        print(f"{FIELD}: {ACC:.2f}%")

    print(f"Recall: {RECALL * 100:.2f}%")
    print(f"Precision: {PRECISION * 100:.2f}%")
    print("accuracy_matrix", ACCURACY_MATRIX)
    print("recall_data", RECALL_DATA)
    print("precision_data", PRECISION_DATA)
