"""This module calculates the accuracy of the control loop properties"""

from src.control_narrative_lambda.constant import control_loop_property_name_list


def calculate_score(ground_truth, output):
    """This function calculates score"""
    score = 0
    for key in control_loop_property_name_list:
        if (
            key in ground_truth
            and key in output
            and set(ground_truth[key]) == set(output[key])
        ):
            score += 1

    return score


def find_best_match(output_list, ground_truth_list, used_control_loop_ids):
    """This function finds best match"""
    best_match = {}
    best_score = 0
    for output in output_list["data"]:
        if output["narrative_id"] == ground_truth_list[0]["narrative_id"]:
            current_score = sum(
                calculate_score(ground_truth, output)
                for ground_truth in ground_truth_list
            )
            if (
                current_score > best_score
                and output["control_loop_id"] not in used_control_loop_ids
            ):
                best_score = current_score
                best_match = output

    return best_match


def generate_control_loop_mapping(output_data, ground_truth_data):
    """This function generates control loop mapping"""
    control_loop_mapping = {}
    used_control_loop_ot_ids = set()

    for ground_truth in ground_truth_data["data"]:
        matching_output = find_best_match(
            output_data, [ground_truth], used_control_loop_ot_ids
        )
        matched_control_loop_id = matching_output.get("control_loop_id", None)

        if matched_control_loop_id is not None:
            control_loop_mapping[ground_truth["control_loop_id"]] = (
                matched_control_loop_id
            )
            used_control_loop_ot_ids.add(matched_control_loop_id)
    return control_loop_mapping


def calculate_accuracy_per_property(ground_truth_data, output_data):
    """This function calculates accuracy per property"""
    mapping = generate_control_loop_mapping(output_data, ground_truth_data)
    results = {}

    for ground_truth_entry in ground_truth_data["data"]:
        control_loop_id_ground_truth = ground_truth_entry.get("control_loop_id")
        control_loop_id_output = mapping.get(control_loop_id_ground_truth)

        output_entry = next(
            (
                ot
                for ot in output_data["data"]
                if ot["control_loop_id"] == control_loop_id_output
            ),
            None,
        )
        if output_entry:
            for prop in control_loop_property_name_list:
                ground_truth_prop = set(ground_truth_entry.get(prop, []))
                output_prop = set(output_entry.get(prop, []))
                tp = len(ground_truth_prop & output_prop)
                fp = len(output_prop - ground_truth_prop)
                fn = len(ground_truth_prop - output_prop)
                total_expected = len(ground_truth_prop)
                total_best_matched = len(output_prop)

                recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                precision = tp / (tp + fp) if (tp + fp) > 0 else 0

                if len(ground_truth_prop) == 0 and len(output_prop) == 0:
                    recall = precision = 1
                    tp = fp = fn = 0

                results.setdefault(control_loop_id_ground_truth, {}).setdefault(
                    prop, {}
                )["recall"] = recall
                results[control_loop_id_ground_truth][prop]["precision"] = precision
                results[control_loop_id_ground_truth][prop]["true_positive"] = tp
                results[control_loop_id_ground_truth][prop]["false_positive"] = fp
                results[control_loop_id_ground_truth][prop]["false_negative"] = fn
                results[control_loop_id_ground_truth][prop][
                    "total_expected"
                ] = total_expected
                results[control_loop_id_ground_truth][prop][
                    "total_best_matched"
                ] = total_best_matched

        else:
            for prop in control_loop_property_name_list:
                ground_truth_prop = set(ground_truth_entry.get(prop, []))
                fn = len(ground_truth_prop)
                results.setdefault(control_loop_id_ground_truth, {}).setdefault(
                    prop, {}
                )["recall"] = 0
                results[control_loop_id_ground_truth][prop]["precision"] = 0
                results[control_loop_id_ground_truth][prop]["true_positive"] = 0
                results[control_loop_id_ground_truth][prop]["false_positives"] = 0
                results[control_loop_id_ground_truth][prop]["false_negatives"] = fn
                results[control_loop_id_ground_truth][prop][
                    "total_expected"
                ] = total_expected
                results[control_loop_id_ground_truth][prop][
                    "total_best_matched"
                ] = total_best_matched

    return results
