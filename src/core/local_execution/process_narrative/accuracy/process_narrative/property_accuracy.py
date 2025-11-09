"""This module contains functions for property accuracy"""

from src.local_execution.process_narrative.accuracy.process_narrative.constants import (
    expected_property_check,
    received_property_check,
)
from src.utils.log import logger


def map_source_or_destination_property(
    received_data, expected_data, received_asset_id, expected_asset_id, attribute_type
):
    """This function maps source or destination property"""
    logger.info(
        f"INIT: map {attribute_type} of {received_asset_id} and {expected_asset_id}"
    )
    src_properties = {}
    received_connections = received_data.get(received_asset_id, {})
    expected_connections = expected_data.get(expected_asset_id, {})
    used_received_id = set()
    used_expected_id = set()
    for p_connection in received_connections:
        for a_connection in expected_connections:
            if (
                p_connection["connection_type"].lower()
                == a_connection["connection_type"].lower()
                and p_connection.get(attribute_type, "").lower()
                == a_connection.get(attribute_type, "").lower()
                # and a_connection.get("is_connection_type_mentioned_in_narrative") is True
                and p_connection["id"] not in used_received_id
                and a_connection["id"] not in used_expected_id
            ):
                src_properties[p_connection["id"]] = a_connection["id"]
                used_received_id.add(p_connection["id"])
                used_expected_id.add(a_connection["id"])
                break
    logger.info(
        f"DONE: mapped {attribute_type} of {received_asset_id} and {expected_asset_id}"
    )
    return src_properties


def compare_properties(expected, received, expected_name, received_name):
    """This function compares properties"""
    logger.info(f"INIT: compare {expected_name} and {received_name}")
    return expected.get(expected_name, {}).get("value") == received.get(
        received_name, {}
    ).get("value")


def calculate_sensor_property_dict_score(property_dict):
    """This function calculates sensor property dict score"""
    logger.info("INIT: calculate sensor property dict score")
    score = 0
    for key, value in property_dict.items():
        if key[-4:] == value[-4:]:
            score = score + 1
        else:
            score = score + 0.5
    return score


def calculate_total_score(
    expected_property_data,
    received_property_data,
    expected_property_name,
    property_name,
):
    """This function calculates total score"""
    logger.info("INIT: calculate total score")
    property_dict = {}
    property_dict[expected_property_name] = property_name

    for expected_name_check in expected_property_check:
        for received_name_check in received_property_check:
            if (
                received_property_data[received_name_check]["value"]
                == expected_property_data[expected_name_check]["value"]
                and (
                    received_property_data["connection_type"]
                    == expected_property_data["connection_type"]
                )
                and received_name_check not in property_dict.values()
                and expected_name_check not in property_dict
            ):
                if (
                    expected_property_data[expected_name_check]["value"] is None
                    and expected_name_check[-4:] == received_name_check[-4:]
                ):
                    property_dict[expected_name_check] = received_name_check
                    break
                if expected_property_data[expected_name_check]["value"] is not None:
                    property_dict[expected_name_check] = received_name_check
                    break

    score = calculate_sensor_property_dict_score(property_dict)
    return score


def update_mapped_properties(
    mapped_properties, expected_connection, received_connection, score
):
    """This function updates mapped properties"""
    if expected_connection["id"] not in mapped_properties:
        mapped_properties[expected_connection["id"]] = [
            {
                "received_connection_id": received_connection["id"],
                "score": score,
            }
        ]
    else:
        mapped_properties[expected_connection["id"]].append(
            {
                "received_connection_id": received_connection["id"],
                "score": score,
            }
        )


def map_sensor_properties(
    received_data,
    expected_data,
    expected_property_name,
    received_ast_name,
    expected_ast_name,
):
    """This function maps sensor properties"""
    logger.info(
        f"INIT: map {expected_property_name} of {received_ast_name} and {expected_ast_name}"
    )
    mapped_properties = {}
    for property_name in received_property_check:
        expected_connections = expected_data[expected_ast_name]
        received_connections = received_data[received_ast_name]
        for expected_connection in expected_connections:
            for received_connection in received_connections:
                connection_type_matches = expected_connection.get(
                    "connection_type"
                ) == received_connection.get("connection_type")
                value_matches = (
                    expected_connection[expected_property_name]["value"]
                    == received_connection[property_name]["value"]
                )
                value_is_none = (
                    expected_connection[expected_property_name]["value"] is None
                )
                property_name_matches = (
                    expected_property_name[-4:] == property_name[-4:]
                )

                if (
                    connection_type_matches
                    and value_matches
                    and (value_is_none or property_name_matches)
                ):
                    score = calculate_total_score(
                        expected_connection,
                        received_connection,
                        expected_property_name,
                        property_name,
                    )
                    update_mapped_properties(
                        mapped_properties,
                        expected_connection,
                        received_connection,
                        score,
                    )
    logger.info(
        f"DONE: mapped {expected_property_name} of {received_ast_name} and {expected_ast_name}"
    )
    # print(mapped_properties)
    return mapped_properties


def save_highest_scores(data):
    """This function saves highest scores"""
    logger.info("INIT: save highest score")
    flattened_data = []
    for connection, details in data.items():
        for detail in details:
            detail["keys"] = connection
            flattened_data.append(detail)

    flattened_data.sort(key=lambda x: x["score"], reverse=True)
    output_data = {}
    unique_keys = set()

    for detail in flattened_data:
        received_connection_id = detail["received_connection_id"]
        keys = detail["keys"]

        if keys not in unique_keys:
            if received_connection_id not in output_data:
                output_data[received_connection_id] = {
                    "score": detail["score"],
                    "keys": keys,
                }
                unique_keys.add(keys)

    # print(output_data)
    logger.info("DONE: saved highest score")
    return output_data


def compute_accuracy(
    best_connections,
    received_connections_count,
    expected_connections_count,
    ast_name_name,
):
    """This function computes accuracy"""
    logger.info(f"INIT: compute accuracy of {ast_name_name}")
    true_positive = len(best_connections)
    received_total = (
        received_connections_count[ast_name_name]["inlets"]
        + received_connections_count[ast_name_name]["outlets"]
    )
    expected_total = (
        expected_connections_count[ast_name_name]["inlets"]
        + expected_connections_count[ast_name_name]["outlets"]
    )
    accuracy = None
    if expected_total == 0 and received_total == 0:
        accuracy = 1.0
    elif received_total == 0:
        accuracy = 0.0
    else:
        accuracy = true_positive / received_total
    logger.info(f"DONE: accuracy of {ast_name_name},{accuracy} ")
    return accuracy


def calculate_total_asset_sensor_property_accuracy(
    property_name,
    received_data,
    expected_data,
    expected_connections_count,
    received_connections_count,
):
    """This function calculates total asset sensor property accuracy"""
    logger.info(f"INIT: calculate total asset {property_name} property_accuracy")
    total_accuracy = 0
    num_assets = len(expected_connections_count)

    for ast_name in expected_connections_count.keys():
        property_accuracy = compute_accuracy(
            save_highest_scores(
                map_sensor_properties(
                    received_data, expected_data, property_name, ast_name, ast_name
                )
            ),
            received_connections_count,
            expected_connections_count,
            ast_name,
        )
        total_accuracy += property_accuracy
    logger.info(f"DONE: calculated total asset {property_name} property_accuracy")
    return total_accuracy / num_assets if num_assets > 0 else 0


def calculate_total_asset_source_or_destination_name_accuracy(
    property_name,
    received_data,
    expected_data,
    expected_connections_count,
    received_connections_count,
):
    """This function calculates total asset sensor property accuracy"""
    logger.info(f"INIT: calculate total asset {property_name} property_accuracy")
    total_accuracy = 0
    num_assets = len(expected_connections_count)

    for ast_name in expected_connections_count.keys():
        property_accuracy = compute_accuracy(
            map_source_or_destination_property(
                received_data, expected_data, ast_name, ast_name, property_name
            ),
            received_connections_count,
            expected_connections_count,
            ast_name,
        )
        total_accuracy += property_accuracy
    logger.info(f"DONE: calculated total asset {property_name} property_accuracy")
    return total_accuracy / num_assets if num_assets > 0 else 0


def calculate_total_asset_property_accuracy(
    expected_connections_count, received_data, expected_data, received_connections_count
):
    """This function calculates total asset-wise property accuracy"""
    logger.info("INIT: calculate total_asset_property_accuracy")
    asset_accuracy = {
        "flowrate_accuracy": calculate_total_asset_sensor_property_accuracy(
            "flowrate",
            received_data,
            expected_data,
            expected_connections_count,
            received_connections_count,
        ),
        "temperature_accuracy": calculate_total_asset_sensor_property_accuracy(
            "temperature",
            received_data,
            expected_data,
            expected_connections_count,
            received_connections_count,
        ),
        "pressure_accuracy": calculate_total_asset_sensor_property_accuracy(
            "pressure",
            received_data,
            expected_data,
            expected_connections_count,
            received_connections_count,
        ),
        "source_name_accuracy": calculate_total_asset_source_or_destination_name_accuracy(
            "source_asset_name",
            received_data,
            expected_data,
            expected_connections_count,
            received_connections_count,
        ),
        "destination_name_accuracy": calculate_total_asset_source_or_destination_name_accuracy(
            "destination_asset_name",
            received_data,
            expected_data,
            expected_connections_count,
            received_connections_count,
        ),
    }
    logger.info("DONE: calculating total_asset_property_accuracy")
    return asset_accuracy


def calculate_asset_wise_sensor_property_accuracy(
    calculate_asset_wise_sensor_property_accuracy_args,
):
    """This function calculates asset-wise sensor property accuracy"""
    (
        property_name,
        ast_name,
        received_data,
        expected_data,
        expected_connections_count,
        received_connections_count,
    ) = calculate_asset_wise_sensor_property_accuracy_args
    logger.info(f"INIT: calculate {property_name} property accuracy of {ast_name}")
    property_accuracy = compute_accuracy(
        save_highest_scores(
            map_sensor_properties(
                received_data, expected_data, property_name, ast_name, ast_name
            )
        ),
        received_connections_count,
        expected_connections_count,
        ast_name,
    )
    logger.info(f"DONE: calculated {property_name} property accuracy of {ast_name}")
    return property_accuracy


def calculate_asset_wise_source_or_destination_name_accuracy(
    calculate_asset_wise_source_or_destination_name_accuracy_args,
):
    """This function calculates asset-wise sensor property accuracy"""
    (
        property_name,
        ast_name,
        received_data,
        expected_data,
        expected_connections_count,
        received_connections_count,
    ) = calculate_asset_wise_source_or_destination_name_accuracy_args
    logger.info(f"INIT: calculate {property_name} property accuracy of {ast_name}")
    property_accuracy = compute_accuracy(
        map_source_or_destination_property(
            received_data, expected_data, ast_name, ast_name, property_name
        ),
        received_connections_count,
        expected_connections_count,
        ast_name,
    )
    logger.info(f"DONE: calculated {property_name} property accuracy of {ast_name}")
    return property_accuracy


def calculate_asset_wise_property_accuracy(
    expected_connections_count, received_data, expected_data, received_connections_count
):
    """This function calculates asset-wise property accuracy"""
    logger.info("INIT: calculate asset-wise property accuracy")
    property_accuracy = {}

    for ast_name in expected_connections_count.keys():
        property_accuracy[ast_name] = {
            "flowrate_accuracy": calculate_asset_wise_sensor_property_accuracy(
                (
                    "flowrate",
                    ast_name,
                    received_data,
                    expected_data,
                    expected_connections_count,
                    received_connections_count,
                )
            ),
            "temperature_accuracy": calculate_asset_wise_sensor_property_accuracy(
                (
                    "temperature",
                    ast_name,
                    received_data,
                    expected_data,
                    expected_connections_count,
                    received_connections_count,
                )
            ),
            "pressure_accuracy": calculate_asset_wise_sensor_property_accuracy(
                (
                    "pressure",
                    ast_name,
                    received_data,
                    expected_data,
                    expected_connections_count,
                    received_connections_count,
                )
            ),
            "source_name_accuracy": calculate_asset_wise_source_or_destination_name_accuracy(
                (
                    "source_asset_name",
                    ast_name,
                    received_data,
                    expected_data,
                    expected_connections_count,
                    received_connections_count,
                )
            ),
            "destination_name_accuracy": calculate_asset_wise_source_or_destination_name_accuracy(
                (
                    "destination_asset_name",
                    ast_name,
                    received_data,
                    expected_data,
                    expected_connections_count,
                    received_connections_count,
                )
            ),
        }
    logger.info("DONE: calculating asset-wise property accuracy")
    return property_accuracy
