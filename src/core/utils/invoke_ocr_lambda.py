"""This file would be used to extract OCR data from images"""

import os
import json
import botocore
import requests
from dotenv import load_dotenv
from src.utils.log import logger
from src.utils.s3_download_upload import load_into_memory, check_file_in_storage

load_dotenv()


def _invoke_artisan_text_detector_core_lambda(bucket, image_path, ocr_output_json_path):
    """Invoke the lambda function to extract OCR data"""
    logger.info(f"INIT: Invoking lambda function for OCR extraction for {image_path}")
    artisan_text_detector_lambda_url = os.getenv("TEXT_DETECTOR_LAMBDA_URL")
    payload = {
        "action": "google_vision_ocr_raw",
        "bucket": bucket,
        "multiple": False,
        "img_path": image_path,
        "google_vision_raw_ocr_op_path": ocr_output_json_path,
    }

    logger.info(f"Payload for lambda invocation: {payload}")

    headers = {
        "Content-Type": "application/json",
    }
    response = requests.post(
        url=artisan_text_detector_lambda_url, json=payload, headers=headers, timeout=300
    )

    logger.info(f"OCR service response status: {response.status_code}")

    response.raise_for_status()
    response_payload = response.json()

    if response_payload.get("success"):
        logger.info(response_payload)
        return ocr_output_json_path

    logger.error(f"Lambda invocation failed with payload: {response_payload}")
    return None


async def get_ocr_file(bucket, image_path, ocr_output_json_path):
    """Get OCR file from lambda invocation"""
    logger.info(f"INIT: Get OCR file from lambda invocation for {image_path}")

    file_exists = await check_file_in_storage(bucket, ocr_output_json_path)

    if file_exists:
        logger.info("OCR output JSON file already present.")
        json_data = await load_into_memory(bucket, ocr_output_json_path)
        return json.loads(json_data.decode("utf-8"))
    try:
        ocr_output_json_path = _invoke_artisan_text_detector_core_lambda(
            bucket, image_path, ocr_output_json_path
        )

        if ocr_output_json_path:
            logger.info(
                "Lambda invocation succeeded. OCR output JSON path: %s",
                ocr_output_json_path,
            )
            json_data = await load_into_memory(bucket, ocr_output_json_path)
            ocr_output = json.loads(json_data.decode("utf-8"))

            logger.info("Successfully loaded OCR data into memory and parsed JSON.")
            logger.info(
                "Done: OCR extraction completed for image '%s' in bucket '%s'.",
                image_path,
                bucket,
            )
            return ocr_output

        logger.error("Failed to get OCR file due to lambda invocation failure.")
        return None
    except (botocore.exceptions.ClientError, json.JSONDecodeError) as e:
        logger.error("Exception occurred during lambda invocation: %s", str(e))
        return None
