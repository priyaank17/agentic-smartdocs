"""This module consists of functions for generating ADM"""

import json
from src.utils.s3_download_upload import put_object_in_storage, load_json_from_storage


async def generate_adm(bucket_name, data_path, config_data_key, local_path=False):
    """
    Generates an ADM file by reading data from storage,
    converting it to the desired format, and storing the result.
    """
    if local_path:
        with open(data_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
    else:
        json_data = await load_json_from_storage(bucket_name, data_path)

    meta_data = await load_json_from_storage(bucket_name, config_data_key)

    data = {"meta_data": meta_data.get("meta_data"), "data": json_data}
    json_content = json.dumps(data)

    if local_path:
        with open(data_path, "w", encoding="utf-8") as f:
            f.write(json_content)
    else:
        await put_object_in_storage(bucket_name, data_path, json_content.encode("utf-8"))
