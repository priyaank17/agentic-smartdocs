"""
This module is used for generating ADM (Asset Data Model) from data sheets.
It includes functions for processing and extracting data from JSON data,
and saving the processed data to an S3 bucket.
"""

import json
import os
import datetime
import tempfile
import ast
from src.utils.log import logger
from src.utils.s3_download_upload import (
    load_into_memory,
    download_storage_file,
    file_exists_in_storage
)
from src.data_sheets.sheet_adm_generation.get_table import (
    nozzles_table,
    table_format_1,
    table_format_2,
    table_format_3,
)
from src.data_sheets.constant import (
    get_standard_property_df,
    get_specific_standard_df,
    standard_property_name_list_path,
    split_alternate_names,
)
from src.data_sheets.get_standard_details.get_standard_data_sheet_data import (
    get_table_name,
)
from src.data_sheets.sheet_adm_generation.postprocessing_adm import (
    convert_to_numerics,
    add_bounding_boxes,
)
from src.utils.storage_utils import (
    fetch_file_via_adapter,
    upload_file_to_storage
)


def _get_correct_context_details(old_data, context_df):
    """Update context details of old data based on context DataFrame."""
    logger.info("INIT: get_correct_context_details function initialized")
    context_df = split_alternate_names(context_df)
    tables = get_table_name()
    columns_name = ["standard_property_name"] + [
        col for col in context_df.columns if col.startswith("alternate_name_")
    ]
    for old_item in old_data:
        if old_item["data_sheet_section"] in tables:
            standard_property_name = old_item["standard_property_name"]
            standard_property_name = old_item["standard_property_name"]
            applicable_to_series = context_df[
                context_df.apply(
                    lambda row, prop=standard_property_name: prop
                    in row[columns_name].values,
                    axis=1,
                )
            ]["applicable to"]
            if not applicable_to_series.empty and standard_property_name:
                old_item_context = old_item["context"]
                applicable_to_value = applicable_to_series.values[0]
                if "meta_data" in applicable_to_value.lower():
                    old_item_context["context_name"] = "META_DATA"
                    old_item_context["subpart_name"] = None
                elif "asset" in applicable_to_value.lower():
                    old_item_context["context_name"] = "EQUIPMENT"
                    old_item_context["connection_type"] = None
                    old_item_context["subpart_name"] = None
                elif (
                    "section" in applicable_to_value.lower()
                    or "side" in applicable_to_value.lower()
                ):
                    old_item_context["context_name"] = "SUB_PART"
                    old_item_context["connection_type"] = None
                    subpart_name = old_item_context["subpart_name"].lower()
                    is_tube = "tube" in applicable_to_value and "tube" in subpart_name
                    is_shell = "shell" in applicable_to_value and "shell" in subpart_name
                    is_air = "air" in applicable_to_value and "air" in subpart_name
                    is_section = (
                        "section" in applicable_to_value and "section" in subpart_name
                    )
                    is_side = ("side" in applicable_to_value and "side" in subpart_name)
                    if not (is_tube or is_shell or is_section or is_air or is_side):
                        old_item["context"]["subpart_name"] = None
            applicable_to_series = None
    logger.info("DONE: get_correct_context_details function executed")


def _process_csv(json_data, csv_file_path, processing_function):
    """Process a CSV file if it exists using the provided processing function."""
    if os.path.exists(csv_file_path):
        processing_function(json_data, csv_file_path)


async def get_properties_from_s3(
    bucket_name, csv_folder_path, json_data, table_details, asset_class
):
    """Retrieve properties from CSV files stored in an S3 bucket."""
    logger.info("INIT: get_properties function initialized")
    with tempfile.TemporaryDirectory() as temp_dir:
        for table_info in table_details:
            table_name = table_info["table_name"]
            column_names = table_info["columns"]
            appearance_number = table_info["appearance_number"]
            file_name = f"{table_name}.csv"
            page_number = table_info["page_number"]
            if appearance_number is not None and appearance_number > 1:
                file_name = f"{table_name}_{appearance_number}.csv"
            storage_path = f"{csv_folder_path}/{file_name}"
            if await file_exists_in_storage(bucket_name, storage_path) :
                local_path = os.path.join(temp_dir, file_name)
                await download_storage_file(
                    bucket_name,
                    storage_path,
                    local_path
                )
                if table_name == "nozzle":
                    nozzles_table(json_data, local_path, page_number)
                else:
                    if column_names:
                        standard_table_list = get_table_name()
                        if table_name in standard_table_list:
                            table_format_2(
                                json_data,
                                local_path,
                                asset_class,
                                appearance_number,
                                page_number,
                            )
                        else:
                            table_format_3(
                                json_data, local_path, appearance_number, page_number
                            )
                    else:
                        table_format_1(
                            json_data, local_path, appearance_number, page_number
                        )


def _get_properties_from_local(csv_folder_path, json_data, table_details, asset_class):
    """Retrieve properties from local CSV files."""
    logger.info("INIT: get_properties from local function initialized")
    for table_info in table_details:
        table_name = table_info["table_name"]
        column_names = table_info["columns"]
        appearance_number = table_info["appearance_number"]
        page_number = table_info["page_number"]
        file_name = f"{table_name}.csv"
        if appearance_number is not None and appearance_number > 1:
            file_name = f"{table_name}_{appearance_number}.csv"
        local_path = os.path.join(csv_folder_path, file_name)
        if os.path.exists(local_path):
            if table_name == "nozzle":
                nozzles_table(json_data, local_path, page_number)
            else:
                if column_names:
                    standard_table_list = get_table_name()
                    if table_name in standard_table_list:
                        table_format_2(
                            json_data,
                            local_path,
                            asset_class,
                            appearance_number,
                            page_number,
                        )
                    else:
                        table_format_3(
                            json_data, local_path, appearance_number, page_number
                        )
                else:
                    table_format_1(
                        json_data, local_path, appearance_number, page_number
                    )
    logger.info("DONE: get_properties from local function executed successfully")
    return json_data


def _get_nozzle_number(data1):
    """Assign unique nozzle numbers to entries without nozzle numbers."""
    n = 1
    for obj in data1:
        if "nozzle_number" not in obj or obj["nozzle_number"] is None:
            nozzle_number = f"DATASHEET_UNNAMED_NOZZLE_{str(n)}"
            n = n + 1
            obj["nozzle_number"] = nozzle_number


def _construct_key(subpart_name, connection_type, nozzle_number=None):
    """Construct a key for the filtered entry based on subpart name,
    connection type, and optional nozzle number."""
    if nozzle_number:
        return f"{subpart_name.upper()}_{connection_type.upper()}_{nozzle_number}"
    return f"{subpart_name.upper()}_{connection_type.upper()}"


def _add_entry_to_filtered(filtered_entry, entry, key):
    """Add an entry to the filtered entries dictionary."""
    if key not in filtered_entry:
        filtered_entry[key] = {
            "subpart_name": entry.get("context", {}).get("subpart_name"),
            "connection_type": entry.get("context", {}).get("connection_type"),
            "nozzle_number": entry.get("context", {}).get("nozzle_number"),
        }
    filtered_entry[key][entry["standard_property_name"]] = entry["property_value"]


def _extract_context_data(entry):
    """Extract context data from an entry."""
    context = entry.get("context", {})
    subpart_name = context.get("subpart_name")
    connection_type = context.get("connection_type")
    context_name = context.get("context_name")
    nozzle_number = context.get("nozzle_number")
    return subpart_name, connection_type, nozzle_number, context_name


def _collect_nozzle_table_entries(property_data, filtered_entry):
    """Collect nozzle table entries from the property data."""
    for entry in property_data:
        subpart_name, connection_type, nozzle_number, context_name = (
            _extract_context_data(entry)
        )
        if (
            subpart_name
            and connection_type
            and context_name == "NOZZLE"
            and entry["data_sheet_section"] == "NOZZLES"
        ):
            key = _construct_key(subpart_name, connection_type, nozzle_number)
            if key not in filtered_entry:
                filtered_entry[key] = {
                    "subpart_name": subpart_name,
                    "connection_type": connection_type,
                    "nozzle_number": nozzle_number,
                }
                filtered_entry[key].update(entry["property_details"])
                if entry["standard_property_name"] != "nozzle_number":
                    _add_entry_to_filtered(filtered_entry, entry, key)


def _merge_or_add_entry(
    filtered_entry, entry, base_key, startswith=False, endswith=False
):
    """Merge or add an entry to the filtered entries."""
    exist = False
    for existing_key in filtered_entry:
        if (startswith and existing_key.startswith(base_key)) or (
            endswith and existing_key.endswith(base_key)
        ):
            exist = True
            _add_entry_to_filtered(filtered_entry, entry, existing_key)
    if not exist:
        _add_entry_to_filtered(filtered_entry, entry, base_key)


def _process_nozzle_entry(property_data, filtered_entry):
    """Process nozzle entries in the property data."""
    # First pass: Collect entries with data_sheet_section == "NOZZLES"
    _collect_nozzle_table_entries(property_data, filtered_entry)
    # Second pass: Collect other entries and merge them appropriately
    for entry in property_data:
        subpart_name, connection_type, nozzle_number, context_name = (
            _extract_context_data(entry)
        )

        if context_name == "NOZZLE" and entry["data_sheet_section"] != "NOZZLES":
            if subpart_name and connection_type:
                if nozzle_number:
                    key = _construct_key(subpart_name, connection_type, nozzle_number)
                    _add_entry_to_filtered(filtered_entry, entry, key)
                else:
                    base_key = _construct_key(subpart_name, connection_type)
                    _merge_or_add_entry(filtered_entry, entry, base_key, startswith=True)
            else:
                if nozzle_number:
                    base_key = nozzle_number
                    _merge_or_add_entry(filtered_entry, entry, base_key, endswith=True)


def _get_nozzle(json_data):
    """Extract all the properties of nozzles from the JSON data."""
    logger.info("INIT: get all the properties of nozzles")
    filtered_entry = {}
    property_data = json_data.get("properties")
    _process_nozzle_entry(property_data, filtered_entry)
    final_output = list(filtered_entry.values())
    json_data["nozzles"] = final_output
    _get_nozzle_number(json_data["nozzles"])
    logger.info("DONE: extracted all the properties of nozzles")
    return final_output


def _get_sub_parts(json_data):
    """Extract all the properties of sub parts from the JSON data."""
    logger.info("INIT: get all the properties of sub_parts")
    filtered_entry = {}
    property_data = json_data.get("properties")
    for entry in property_data:
        context = entry.get(
            "context", {}
        )  # Get the context dictionary, default to empty dictionary if not present
        subpart_name = context.get("subpart_name")
        context_name = context.get("context_name")
        if subpart_name and context_name == "SUB_PART":
            key = subpart_name.upper()

            if key not in filtered_entry:
                filtered_entry[key] = {"subpart_name": subpart_name}

            standard_property_name = entry["standard_property_name"]
            property_value = entry["property_value"]

            filtered_entry[key][standard_property_name] = property_value

    final_output = list(filtered_entry.values())
    json_data["sub_parts"] = final_output
    logger.info("DONE: extracted all the properties of sub_parts")
    return final_output


def _convert_to_list(meta_data_equipment_name_str):
    """Convert a string to a list.
    If the string starts and ends with square brackets,
      it is evaluated as a list. Otherwise,
      it is stripped of leading and trailing single quotes
        and put into a list.
    """
    if meta_data_equipment_name_str.startswith(
        "["
    ) and meta_data_equipment_name_str.endswith("]"):
        meta_data_equipment_name = ast.literal_eval(meta_data_equipment_name_str)
    else:
        meta_data_equipment_name = [meta_data_equipment_name_str.strip("'")]

    return meta_data_equipment_name


def _get_equipments(json_data):
    """Extract all the properties of equipments from the JSON data."""
    logger.info("INIT: get all the properties of equipments")
    filtered_entry = {}
    property_data = json_data.get("properties")
    meta_data = json_data.get("meta_data", {})
    meta_data_equipment_name_str = meta_data.get("equipment_name", "")
    meta_data_equipment_name = _convert_to_list(meta_data_equipment_name_str)
    final_output = []

    if len(meta_data_equipment_name) > 1:
        for equipment_name in meta_data_equipment_name:
            key = equipment_name.upper()
            filtered_entry[key] = {"equipment_name": equipment_name}
        for entry in property_data:
            if entry["context"]["context_name"] == "EQUIPMENT":
                equipment_name = entry["context"]["equipment_name"]
                entry["context"]["subpart_name"] = None
                key = equipment_name.upper()
                filtered_entry[key][entry["standard_property_name"]] = entry[
                    "property_value"
                ]
                final_output = list(filtered_entry.values())
    else:
        for entry in property_data:
            if entry["context"]["context_name"] == "EQUIPMENT":
                entry["context"]["subpart_name"] = None
                filtered_entry[entry["standard_property_name"]] = entry[
                    "property_value"
                ]
        final_output = [filtered_entry]
    json_data["equipments"] = final_output
    logger.info("DONE: extracted all the properties of equipments")
    return final_output


def _get_meta_data(json_data, document_id):
    """Extract the meta data from the JSON data."""
    logger.info("INIT: get meta data function initialized")
    filtered_entry = {
        "uuid": document_id,
        "adm_version": "ADM_DATA_SHEET_" + datetime.datetime.now().strftime("%Y-%m-%d"),
        "adm_generation_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "adm_type": "DATA_SHEET",
    }
    property_data = json_data.get("properties")
    for entry in property_data:
        if entry["context"]["context_name"] == "META_DATA":
            filtered_entry[entry["standard_property_name"]] = entry["property_value"]
    filtered_entry["equipment_tag"] = (
        filtered_entry["equipment_tag"].upper().replace(" ", "")
    )
    filtered_entry["equipment_name"] = filtered_entry["equipment_name"].upper()
    json_data["meta_data"] = filtered_entry
    logger.info("DONE: get meta data function executed")


def _add_equipment_name(json_data):
    """Add the equipment name to the equipment, nozzle, and sub part data in the JSON data."""
    meta_data = json_data.get("meta_data")
    equipment_data = json_data.get("equipments")
    nozzle_data = json_data.get("nozzles")
    sub_parts_data = json_data.get("sub_parts")
    if "equipment_name" not in equipment_data[0]:
        for e in equipment_data:
            e["equipment_name"] = meta_data["equipment_name"]
        for n in nozzle_data:
            n["equipment_name"] = meta_data["equipment_name"]
        for s in sub_parts_data:
            s["equipment_name"] = meta_data["equipment_name"]
    else:
        for n in nozzle_data:
            n["equipment_name"] = n["subpart_name"]
            n["subpart_name"] = n["subpart_name"] + "_SIDE"
        for s in sub_parts_data:
            s["equipment_name"] = s["subpart_name"]
            s["subpart_name"] = s["subpart_name"] + "_SIDE"


def _get_other_node(json_data):
    """Extract the other nodes then subpart, nozzle, equipment of data sheet."""
    logger.info("INIT: get other nodes function initialized")
    property_data = json_data.get("properties")
    for entry in property_data:
        context_name = entry["context"]["context_name"]
        if entry["context"]["context_name"] not in [
            "SUB_PART",
            "NOZZLE",
            "EQUIPMENT",
            "META_DATA",
        ]:
            property_details = entry["property_details"]
            property_details.update(
                {entry["standard_property_name"]: entry["property_value"]}
            )
            json_data.setdefault(context_name.lower(), []).append(property_details)
    logger.info("DONE: get other nodes function executed")


async def get_output_file_name(input_data_path, bucket):
    """Load input data from a specified path,
    extract metadata, and construct an output file name."""
    logger.info("INIT: get_output_file_name function initialized")

    input_data = await fetch_file_via_adapter(bucket, input_data_path)

    asset_tag_number = input_data["meta_data"].get("asset_tag")
    asset_class = input_data["meta_data"].get("asset_class").lower().replace(" ", "_")
    output_file_name = f"{asset_class}.{asset_tag_number}.datasheet"
    document_id = input_data["meta_data"].get("document_id")
    logger.info("Done: get_output_file_name function executed")
    return asset_class, output_file_name, document_id


async def get_table_info(input_data_path, s3_bucket):
    """Get the table information from the input data."""
    logger.info("INIT: get_table_info function initialized")
    input_data = json.loads(
        await load_into_memory(bucket=s3_bucket, path=input_data_path)
    )
    table_details = []
    for table in input_data.get("tables_data", []):
        table_name = table.get("table_name")
        if not table_name:
            continue
        # added to handle table name with spaces
        table_name = table.get("table_name").lower().replace(" ", "_")
        page_number = table.get("page_number")
        columns = table.get("columns", [])
        appearance_number = table.get("appearance_number")
        column_names = [
            column.get("name").lower().replace(" ", "_") for column in columns
        ]
        table_details.append(
            {
                "table_name": table_name,
                "columns": column_names,
                "appearance_number": appearance_number,
                "page_number": page_number,
            }
        )
    logger.info("Done: get_table_info function executed")
    return table_details


async def post_process_json_data(bucket, input_data_path, json_data):
    """Post process the JSON data."""
    logger.info("INIT: post_process_json_data function initialized")
    ocr_json_path = input_data_path.replace("input_data", "ocr_bounding_box")
    ocr_data = await fetch_file_via_adapter(bucket, ocr_json_path)
    json_data = add_bounding_boxes(ocr_data, json_data)
    convert_to_numerics(json_data)
    logger.info("Done: post_process_json_data function executed")
    return json_data


async def generate_adm(
    input_data_path,
    csv_folder_path,
    bucket,
    output_folder_local_path=None,
    is_csv_local_path=False,
):
    """Generate an ADM (Asset Data Model) from input data."""
    logger.info("INIT: generate_adm function initialized")
    asset_class, output_file_name, document_id = await get_output_file_name(
        input_data_path, bucket
    )
    property_name_df = get_standard_property_df(standard_property_name_list_path)
    property_name_df = get_specific_standard_df(property_name_df, asset_class)
    table_details = await get_table_info(input_data_path, bucket)
    json_data = {
        "meta_data": {},
        "equipments": [],
        "nozzles": [],
        "sub_parts": [],
        "properties": [],
    }
    if is_csv_local_path:
        _get_properties_from_local(
            csv_folder_path, json_data, table_details, asset_class
        )
    else:
        await get_properties_from_s3(
            bucket, csv_folder_path, json_data, table_details, asset_class
        )
    _get_meta_data(json_data, document_id)
    _get_correct_context_details(json_data["properties"], property_name_df)
    _get_nozzle(json_data)
    _get_sub_parts(json_data)
    _get_equipments(json_data)
    _add_equipment_name(json_data)
    _get_other_node(json_data)
    json_data = await post_process_json_data(bucket, input_data_path, json_data)
    if output_folder_local_path:
        # local_file_path = f"{output_folder_local_path}/{document_id}.adm.json"
        local_file_path = (
            f"{output_folder_local_path}/{output_file_name.lower()}.adm.json"
        )
        with open(local_file_path, "w", encoding="utf-8") as json_file:
            json.dump(json_data, json_file, indent=2)
        logger.info(f"Data saved to {local_file_path}")
    else:
        file_path = f"{csv_folder_path}/{document_id}.DATA_SHEET.adm.json"
        await upload_file_to_storage(bucket, file_path, json.dumps(json_data))
        logger.info(f"Done: Adm json file is generated in path {file_path}")
