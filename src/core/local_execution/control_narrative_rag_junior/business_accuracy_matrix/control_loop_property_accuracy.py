"""
This module contains functions to calculate the accuracy of extracted control loop properties.
"""

import json
import pandas as pd


def compare_entries_unordered(extracted, ground_truth):
    """
    Compare extracted and ground truth control loop properties.
    """

    matches = []
    for idx, gt in enumerate(ground_truth["data"], start=1):
        # print(gt)
        match_found = False
        for ext in extracted["data"]:
            if (
                set(sorted(gt["process_variable"]))
                == set(sorted(ext["process_variable"]))
                and set(sorted(gt["controller"])) == set(sorted(ext["controller"]))
                and set(sorted(gt["final_control_element"]))
                == set(sorted(ext["final_control_element"]))
            ):
                match_found = True
                matches.append(("Match", ext.get("id", "N/A"), f"control_loop_{idx}"))
                break
        if not match_found:
            matches.append(("No Match", "N/A", f"control_loop_{idx}"))
    return matches


if __name__ == "__main__":
    # Generate accuracy matrix
    EXTRACTED_JSON_PATH = (
        r"data\local\mafpp\control_narrative\20_nov\5.control_loop_data.json"
    )
    with open(EXTRACTED_JSON_PATH, "r", encoding="utf-8") as file:
        extracted_json = json.load(file)

    GROUND_TRUTH_PATH = (
        r"tests\test_data\mafpp\control_narrative\ground_truth"
        r"\expected_control_loops.json"
    )

    with open(GROUND_TRUTH_PATH, "r", encoding="utf-8") as file:
        GROUND_TRUTH = json.load(file)
    MATCHES = compare_entries_unordered(extracted_json, GROUND_TRUTH)

    # Prepare DataFrame for easy visualization
    accuracy_matrix = pd.DataFrame(
        MATCHES, columns=["Match Status", "Extracted ID", "Ground Truth ID"]
    )

    # Calculate metrics
    true_positives = accuracy_matrix["Match Status"].value_counts().get("Match", 0)
    false_negatives = accuracy_matrix["Match Status"].value_counts().get("No Match", 0)
    false_positives = len(extracted_json["data"]) - true_positives

    # Precision, Recall, and Accuracy
    precision = (
        true_positives / (true_positives + false_positives)
        if (true_positives + false_positives) > 0
        else 0
    )
    recall = (
        true_positives / (true_positives + false_negatives)
        if (true_positives + false_negatives) > 0
        else 0
    )
    accuracy = true_positives / len(GROUND_TRUTH["data"])

    # Display results
    # print("Accuracy Matrix:")
    print(accuracy_matrix)
    print("MATCHED (true_positives)", true_positives)
    print("NOT_MATCHED (false_negatives)", false_negatives)
    print("TOTAL GROUND TRUTH CONTROL LOOPS", len(GROUND_TRUTH["data"]))
    print("TOTAL EXTRACTED", len(extracted_json["data"]))
    print("INCORRECT (false_positives)", false_positives)
    print(f"PRECISION: {precision:.2f}")
    print(f"RECALL: {recall:.2f}")
    # print(f"Accuracy: {accuracy:.2f}")
