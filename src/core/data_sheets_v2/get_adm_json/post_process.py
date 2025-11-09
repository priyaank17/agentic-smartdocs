"""Convert JSON keys from snake_case to camelCase."""


def to_camel_case(snake_str):
    """Convert snake_case string to camelCase."""
    parts = snake_str.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


def convert_keys_to_camel_case(obj):
    """Recursively convert dictionary keys to camelCase."""
    if isinstance(obj, dict):
        return {to_camel_case(k): convert_keys_to_camel_case(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_keys_to_camel_case(elem) for elem in obj]
    return obj


def generate_relationships(adm_data):  # NOQA
    """Generate entity-to-entity relationships from ADM data."""
    relationships = []

    data_sheet_uuid = adm_data.get("metaData", {}).get("uuid")
    equipment_tag_to_uuid = {}

    # Step 1: DESCRIBES_<NODE_NAME> from DATA_SHEET
    top_level_keys = [
        "revisions",
        "equipments",
        "processFluids",
        "testingInspections",
        "materials",
        "constructionAccessories",
        "nozzles",
        "subparts",
        "designConditions",
        "driverMotor",
        "instrumentation",
        "mechanicalGeometry",
        "operatingConditions",
        "others",
        "performance",
        "notes",
    ]

    for key in top_level_keys:
        for entry in adm_data.get(key, []):
            relationships.append(
                {
                    "sourceUuid": data_sheet_uuid,
                    "destinationUuid": entry["uuid"],
                    "relationshipType": f"DESCRIBES_{key.upper()}",
                }
            )

    # Step 2: Build tag to UUID mapping for equipments and subparts
    for eq in adm_data.get("equipments", []):
        equipment_tag_to_uuid[eq["uuid"]] = {
            "type": "Equipment",
            "tag": eq["equipmentTag"],
        }

    for sub in adm_data.get("subparts", []):
        equipment_tag_to_uuid[sub["uuid"]] = {
            "type": "Subpart",
            "tag": sub["equipmentTag"],
        }

    # Step 3: Equipment relationships
    part_keys = [
        "processFluids",
        "testingInspections",
        "materials",
        "constructionAccessories",
        "nozzles",
        "subparts",
        "designConditions",
        "driverMotor",
        "instrumentation",
        "mechanicalGeometry",
        "operatingConditions",
        "others",
        "performance",
    ]

    for key in part_keys:
        for entry in adm_data.get(key, []):
            equipment_uuid = entry.get("equipmentUuid")
            if equipment_uuid:
                # Forward
                relationships.append(
                    {
                        "sourceUuid": equipment_uuid,
                        "destinationUuid": entry["uuid"],
                        "relationshipType": f"HAS_{key.upper()}",
                    }
                )
                # Reverse
                relationships.append(
                    {
                        "sourceUuid": entry["uuid"],
                        "destinationUuid": equipment_uuid,
                        "relationshipType": "PART_OF_EQUIPMENT",
                    }
                )

    # Step 4: Nozzle relationships with Subpart
    for nozzle in adm_data.get("nozzles", []):
        equipment_uuid = nozzle.get("equipmentUuid")
        subpart_uuid = nozzle.get("subpartUuid")
        if subpart_uuid:
            relationships.append(
                {
                    "sourceUuid": subpart_uuid,
                    "destinationUuid": nozzle["uuid"],
                    "relationshipType": "HAS_NOZZLE",
                }
            )
            relationships.append(
                {
                    "sourceUuid": nozzle["uuid"],
                    "destinationUuid": subpart_uuid,
                    "relationshipType": "PART_OF_SUBPART",
                }
            )

    return relationships


def ensure_all_entities_present(adm: dict) -> dict:
    """
    Ensure that all required entities are present in the ADM data.
    """
    required_keys = [
        "revisions",
        "equipments",
        "processFluids",
        "testingInspections",
        "materials",
        "constructionAccessories",
        "nozzles",
        "subparts",
        "designConditions",
        "driverMotor",
        "instrumentation",
        "mechanicalGeometry",
        "operatingConditions",
        "others",
        "performance",
        "notes",
    ]

    for key in required_keys:
        if key not in adm:
            adm[key] = []

    return adm


def _remove_uuid_fields(item):
    """Helper to remove specific UUID fields from a dict."""
    for field in ["dataSheetUuid", "equipmentUuid", "subpartUuid"]:
        if field in item:
            del item[field]


def clean_uuid(adm_data):
    """
    Clean up the ADM data by removing specific UUID fields.
    """
    for _, node_value in adm_data.items():
        if isinstance(node_value, list):
            for item in node_value:
                if isinstance(item, dict):
                    _remove_uuid_fields(item)
        elif isinstance(node_value, dict):
            _remove_uuid_fields(node_value)
