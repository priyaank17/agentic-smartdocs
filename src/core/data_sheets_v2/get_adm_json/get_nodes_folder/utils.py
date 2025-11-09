"""Utility functions."""


def get_excluded_keys():
    """Return keys to exclude from property extraction."""
    return {
        "Standard Property",
        "Property",
        "Units",
        "table_name",
        "parent_table_name",
        "asset_type",
        "applicable_categories",
        "node_name",
        "node_category",
        "node_subpart_type",
        "property_name",
    }


def tokenize(text):
    """Tokenize the text into a set of words."""
    return set(text.lower().replace("_", " ").replace("-", " ").split())


def get_base_info(entry):
    """Get base info shared across shell_side and tube_side."""
    return {
        "Standard Property": entry.get("Standard Property"),
        "Property": entry.get("Property"),
        "Units": entry.get("Units"),
        "table_name": entry.get("table_name"),
        "parent_table_name": entry.get("parent_table_name"),
        "node_name": entry.get("node_name"),
        "node_category": entry.get("node_category"),
        "node_subpart_type": entry.get("node_subpart_type"),
    }


def get_nodes_to_extract():
    """Return nodes to extract for datasheet."""
    return {
        "nozzles": {"primary_equipments": ["inlet", "outlet"]},
        "subparts": {"primary_equipments": ["shell_side", "tube_side", "air_side"]},
        "equipments": {
            "primary_equipments": ["asset"],
            "auxiliary_equipments": [
                "agitator",
                "seal_auxiliary_system",
                "seal_specification",
            ],
        },
        "operating_conditions": {
            "primary_equipments": ["asset"],
            "auxiliary_equipments": [
                "agitator",
                "seal_auxiliary_system",
                "seal_specification",
            ],
        },
        "performance": {
            "primary_equipments": ["asset"],
            "auxiliary_equipments": [
                "agitator",
                "seal_auxiliary_system",
                "seal_specification",
            ],
        },
        "mechanical_geometry": {
            "primary_equipments": ["asset"],
            "auxiliary_equipments": [
                "agitator",
                "seal_auxiliary_system",
                "seal_specification",
            ],
        },
        "instrumentation": {
            "primary_equipments": ["asset"],
            "auxiliary_equipments": [
                "agitator",
                "seal_auxiliary_system",
                "seal_specification",
            ],
        },
        "others": {
            "primary_equipments": ["asset"],
            "auxiliary_equipments": [
                "agitator",
                "seal_auxiliary_system",
                "seal_specification",
                "others"
            ],
        },
        "process_fluids": {
            "primary_equipments": ["asset"],
            "auxiliary_equipments": [
                "agitator",
                "seal_auxiliary_system",
                "seal_specification",
            ],
        },
        "testing_inspections": {
            "primary_equipments": ["asset"],
            "auxiliary_equipments": [
                "agitator",
                "seal_auxiliary_system",
                "seal_specification",
            ],
        },
        "construction_accessories": {
            "primary_equipments": ["asset"],
            "auxiliary_equipments": [
                "agitator",
                "seal_auxiliary_system",
                "seal_specification",
            ],
        },
        "materials": {
            "primary_equipments": ["asset"],
            "auxiliary_equipments": [
                "agitator",
                "seal_auxiliary_system",
                "seal_specification",
            ],
        },
        "revisions": {
            "primary_equipments": ["asset"],
            "auxiliary_equipments": ["agitator"],
        },
        "driver_motor": {
            "primary_equipments": ["asset"],
            "auxiliary_equipments": [
                "agitator",
                "seal_auxiliary_system",
                "seal_specification",
            ],
        },
        "design_conditions": {
            "primary_equipments": ["asset"],
            "auxiliary_equipments": [
                "agitator",
                "seal_auxiliary_system",
                "seal_specification",
            ],
        },
        "notes": {
            "primary_equipments": ["asset"],
            "auxiliary_equipments": [
                "agitator",
                "seal_auxiliary_system",
                "seal_specification",
            ],
        },
    }


def node_with_equipment_connect():
    """Return node having equipment UUID."""
    return [
        "nozzles",
        "subparts",
        "materials",
        "process_fluids",
        "construction_accessories",
        "testing_inspections",
        "operating_conditions",
        "performance",
        "others",
        "mechanical_geometry",
        "instrumentation",
        "driver_motor",
        "design_conditions",
        "notes",
    ]
