"""This function invokes ExtractTable Lambda and returns CSV"""
import os
import json
import pandas as pd
from src.utils.log import logger
from src.utils.chatgpt import get_completion
from src.utils.automator_util import invoke_lambda
from src.utils.automator_util import setup_aws_clients

EXTRACT_TABLE_LAMBDA_ARN = os.environ.get("EXTRACT_TABLE_LAMBDA_ARN", "")


def invoke_extract_tables(page_bucket, page_path, document_id):
    """Invoke ExtractTable Lambda for a Page"""
    payload = {
        "action": "extract_table",
        "bucket": page_bucket,
        "img_path": page_path,
        "document_id": document_id,
    }
    logger.info(f"Payload for ExtractTable Lambda: {payload}")
    _, _, lambda_client = setup_aws_clients()
    logger.info("Invoking ExtractTable Lambda...")
    response = invoke_lambda(
        lambda_client=lambda_client,
        function_name=EXTRACT_TABLE_LAMBDA_ARN,
        payload=json.dumps(payload),
    )
    logger.info("Response generated for Lambda.")
    response = json.load(response["Payload"])
    return response


def get_csv(table_dict_data):
    """Convert list of dictionary tables to CSV"""

    if len(table_dict_data) == 1:
        df = pd.DataFrame.from_dict(table_dict_data[0])  # , orient='index')
        # df = df.drop('0', axis=1)
        csv_df = [df.to_csv(header=None, index=False)]

    elif len(table_dict_data) > 1:
        csv_df = []
        for _, table_data in enumerate(table_dict_data):
            df = pd.DataFrame.from_dict(table_data)
            # df = df.drop('0', axis=1)
            csv_df.append(df.to_csv(header=None, index=False))
    else:
        csv_df = []

    return csv_df


def prompt_generator(csv):
    """Generate prompt for ChatGPT"""
    prompt = f"give this data in json format with \
        multiple values wherever it is there: {csv}"
    return prompt


def get_page_csv_data(extract_table_response, document_id):
    """Main function"""
    logger.info("In Main DataSheet data extraction function")
    table_dict_data = extract_table_response["table_data"]
    page_data = {}
    extract_table_page_data = {}
    table_data = []
    table_json_data = []
    if len(table_dict_data) >= 1:
        csvs = get_csv(table_dict_data)
        for i, csv in enumerate(csvs):
            logger.info(f"running for {i + 1} csv")
            temp = {}
            temp["csv"] = csv
            table_data.append(temp)
            prompt = prompt_generator(csv)
            temp["prompt"] = prompt
            logger.info("Generating ChatGPT response...")
            gpt_response = get_completion(prompt)
            gpt_response = gpt_response.replace("\n", "").replace(" ", "")
            try:
                gpt_response = json.loads(gpt_response)
            except ValueError:  # Catching specific exception ValueError
                gpt_response = "[" + gpt_response + "]"
                # gpt_response = json.loads(gpt_response)
            temp["response"] = gpt_response
            table_json_data.append(temp)
            # time.sleep(20)
    else:
        table_json_data = None

    page_data["tables"] = table_json_data
    extract_table_page_data["tables"] = table_data
    page_data["metadata"] = extract_table_response["full_response"]
    logger.info(f"Process Completed for {document_id}")
    return page_data, extract_table_page_data
