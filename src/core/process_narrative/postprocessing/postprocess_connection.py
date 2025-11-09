"""This module contains functions to synchronize and replicate connections."""
from src.utils.log import logger
from src.utils.s3_download_upload import read_csv_from_storage


def _initialize_replication_flags(data):
    """Initialize replication flags."""
    for connection in data:
        connection["is_replication_present"] = None
    return data


def _clear_replication_flags(data):
    """Clear replication flags."""
    for connection in data:
        del connection["is_replication_present"]
    return data


def _update_replicated_connection_conflicts(data):
    """Update replicated connection conflicts."""
    logger.info(
        "INIT: update if replica of connections with opposite connection type is present"
    )
    for connection_i in data:
        if connection_i["is_replication_present"] is not True:
            for connection_j in data:
                if (
                    (
                        connection_i["destination_asset_name"]
                        == connection_j["destination_asset_name"]
                    )
                    and (
                        connection_i["source_asset_name"]
                        == connection_j["source_asset_name"]
                    )
                    and (
                        connection_i["connection_type"]
                        != connection_j["connection_type"]
                    )
                    and connection_j["is_replication_present"] is not True
                    and connection_i is not connection_j
                ):
                    connection_i["is_replication_present"] = True
                    connection_j["is_replication_present"] = True
                    break
            if connection_i["is_replication_present"] is not True:
                connection_i["is_replication_present"] = False
    logger.info(
        "DONE: updated replication of connections with opposite connection type is present"
    )


async def _get_asset_id_from_asset_name(asset_name, bucket_name, expected_asset_csv_s3):
    """Get asset id from asset name."""
    df = await read_csv_from_storage(bucket=bucket_name, path=expected_asset_csv_s3)
    matching_row = df[df["asset_name"] == asset_name]
    asset_id = "asset_" + str(matching_row["id"].values[0])
    return asset_id


async def _check_asset_name(asset_name, bucket_name, expected_asset_csv_s3):
    """Check asset name."""
    df = await read_csv_from_storage(bucket=bucket_name, path=expected_asset_csv_s3)
    return any(df["asset_name"] == asset_name)


def _is_connection_present_pnid(connection, pnid_connections):
    """Check if connection is present in PNID."""
    source_name = connection["source_asset_name"]
    destination_name = connection["destination_asset_name"]
    connection_type = connection["connection_type"]
    for pnid_conn in pnid_connections:
        if (
            pnid_conn["source_asset_name"] == source_name
            and pnid_conn["destination_asset_name"] == destination_name
            and pnid_conn["connection_type"] == connection_type
        ):
            return True

    return False


async def _replicate_connection(data, bucket_name, expected_asset_csv_s3, pnid_connections):
    """Replicate connection."""
    logger.info("INIT: replicate connection with opposite connection type")
    new_connections = []
    connection_count = 1
    for connection_i in data:
        connection_i["id"] = "connection_" + str(connection_count)
        connection_count = connection_count + 1
        if (
            connection_i["is_replication_present"] is False
            and await _check_asset_name(
                connection_i["destination_asset_name"],
                bucket_name,
                expected_asset_csv_s3,
            )
            and await _check_asset_name(
                connection_i["source_asset_name"], bucket_name, expected_asset_csv_s3
            )
            and _is_connection_present_pnid(connection_i, pnid_connections)
        ):
            connection_i["is_replication_present"] = True
            replicated_connection = connection_i.copy()
            if replicated_connection["connection_type"] == "OUT_LET":
                replicated_connection["connection_type"] = "IN_LET"
                asset_name = replicated_connection["destination_asset_name"]
                replicated_connection["asset_id"] = await _get_asset_id_from_asset_name(
                    asset_name, bucket_name, expected_asset_csv_s3
                )
                replicated_connection["id"] = "connection_" + str(connection_count)
                connection_count = connection_count + 1
            elif replicated_connection["connection_type"] == "IN_LET":
                replicated_connection["connection_type"] = "OUT_LET"
                asset_name = replicated_connection["source_asset_name"]
                replicated_connection["asset_id"] = await _get_asset_id_from_asset_name(
                    asset_name, bucket_name, expected_asset_csv_s3
                )
                replicated_connection["id"] = "connection_" + str(connection_count)
                connection_count = connection_count + 1
            new_connections.append(replicated_connection)
    data.extend(new_connections)
    logger.info("DONE: replicated connection with opposite connection type")
    return data


async def synchronize_and_replicate_connections(
    received_assets_connections,
    bucket_name,
    expected_asset_csv_s3,
    pnid_connections_list,
):
    """Synchronize and replicate connections."""
    logger.info("INIT: Synchronize and replicate connections")
    updated_received_assets_connections = _initialize_replication_flags(
        received_assets_connections
    )
    _update_replicated_connection_conflicts(updated_received_assets_connections)
    await _replicate_connection(
        updated_received_assets_connections,
        bucket_name,
        expected_asset_csv_s3,
        pnid_connections_list,
    )
    _clear_replication_flags(updated_received_assets_connections)
    logger.info("DONE: Synchronized and replicated connections")
