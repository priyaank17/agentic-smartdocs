"""
Postprocess the JSON data.
"""


def sync_item_number_and_equipment_tag(data: dict) -> dict:
    """
    Sync 'item_number' and 'equipment_tag' in the meta data.
    """
    if not data.get("item_number") and data.get("equipment_tag"):
        data["item_number"] = data["equipment_tag"]
    elif not data.get("equipment_tag") and data.get("item_number"):
        data["equipment_tag"] = data["item_number"]
    return data


def process_meta_data(meta_data):
    """
    Process the JSON data.
    """
    meta_data = sync_item_number_and_equipment_tag(meta_data)
    return meta_data
