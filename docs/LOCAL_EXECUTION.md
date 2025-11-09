# Local Execution

## Installation

Install the dependencies before  starting the execution.

```sh
    ./scripts/setup.bat
```

## Setup Credentials

Create ``.env```` at the root folder and add the following

```toml
    OPENAI_API_KEY=your_api_key_xxxxxxxxxxx
    SANDBOX_ENV=True

    PYTHONPATH=.
    LOCAL=true
    SANDBOX_ENV = true
    NEO4J_URI = "neo4j://localhost:7687"
    NEO4J_USERNAME = "neo4j"
    NEO4J_PASSWORD = "xxx"
    NEO4J_DATABASE = "<DB Name>"
    SANDBOX_ENV = true
    LOG_FORMAT = "%(levelname)s %(message)s"

    # # ---- DEV ----
    S3_ENV = "dev"
    SECRET_NAME = 'artisan-neo-dev'
    S3_BUCKET = 'artisanbucketoregon133719-dev'
    bucket_name=artisanbucketoregon133719-dev
    SANDBOX_ENV=False
    APPSYNC_ENDPOINT=https://zrrcbkwa4vbhfa4iuspl5ecxgq.appsync-api.us-west-2.amazonaws.com/graphql
    EXTRACT_TABLE_LAMBDA_ARN=arn:aws:lambda:us-west-2:461906100116:function:artisan-table-detection-core
    TEXT_DETECTOR_LAMBDA_ARN = arn:aws:lambda:us-west-2:461906100116:function:artisan-text-detector-core-lambda

    # ---- QA ----
    # S3_ENV = "qa"
    # SECRET_NAME = 'artisan-qa-neo'
    # S3_BUCKET = 'artisanbucketoregon184340-qa'
    # bucket_name=artisanbucketoregon184340-qa
    # # APPSYNC_ENDPOINT=https://abc.appsync-api.us-west-2.amazonaws.com/graphql
    # APPSYNC_ENDPOINT=https://c2irersgazadjbaja2wpjmyxgm.appsync-api.us-west-2.amazonaws.com/graphql
```

1. Create a folder named `data` in the root folder.
2. Create a folder named `mafpp` within the `data` folder.
3. Create a folder named `prompt_responses` within the `mafpp` folder.

**Step 1**: _(Manual Step)_ Create a table of assets and their respective tags and asset classes

- This is a manual effort
- Process engineers will assess the given narrative.pdf and create a table (in CSV format)
- We are interested in creating a table with the below columns
    1. id : This could be a number to identify the record across the process
    2. asset_name: The name of the asset
    3. asset_tag: The tag of the asset
    4. asset_class: The class of the asset. The asset class must be one of the constants defined in ```src/constants/ASSET_CLASSES.json```
        [
            ABSORPTION
            COMPRESSOR,
            DISTILLATION,
            EXPANDER,
            HEAT_EXCHANGER_MULTI_STREAM,
            HEAT_EXCHANGER_SHELL_AND_TUBE,
            PRESSURE_VESSEL,
            PUMP,
            SEPARATOR
        ]

**Step 2**:  Create ```data/configs/config.json```
Fill in the file with the below format. replace plant_name with your current plant name.

```json
{
    "asset_narrative_data_path1": "data/mafpp/received_process_narrative.json",
    "asset_narrative_data_path": "data/mafpp/prompt_responses/connections.json",
    "expected_asset_narrative_data_path": "tests/test_data/mafpp/expected_assets_connections.json",
    "accuracy_path": "data/mafpp",
    "expected_asset_csv": "tests/test_data/mafpp/inputs/assets_table.csv",
    "data_path": "data/mafpp",
    "assets_table_csv_path": "tests/test_data/mafpp/inputs/assets_table.csv",
    "prompt_responses_folder_path": "data/mafpp/prompt_responses",
    "combined_json_output_path": "data/mafpp/prompt_responses/combined_assets.json",
    "validation_schema_path": "src/local_execution/asset_data_extraction/schema.json",
    "connection_data_path": "data/mafpp/prompt_responses/connections.json",
    "assets_data_path": "data/mafpp/prompt_responses/assets.json",
    "expected_assets_path": "tests/test_data/mafpp/expected_assets.json",
    "narrative_text_data_csv_path": "tests/test_data/mafpp/inputs/narrative_paragraphs.csv",
    "plant_id": "44bbbac3-f496-4a6c-800e-808e1dec1fe8",
    "plant_folder_path": "data/sanha_dev",
    "adm_s3_paths_json": "data/sanha_dev/adm_s3_paths.json",
    "adms_folder_path": "data/sanha_dev/adms",
    "adms_db_reeady_folder_path": "data/sanha_dev/adms_db_ready",
    "reports_folder_path": "data/sanha_dev/reports",
    "reports_adm_folder_path": "data/sanha_dev/reports/adms",
    "process_flow_diagrams_folder_path": "data/sanha_dev/process_flow_diagrams",
    "convention_json_path": "data/sanha_dev/convention.json",
    "documents_list_json_path":"data/sanha_dev/documents_list.json",
    "data_sheet_adms_folder_path": "data/sanha_dev/data_sheets",
    "bucket_name": "artisanbucketoregon133719-dev",
    "hmb_adms_folder_path": "data/sanha_dev/hmb_adms",
    "pfd_data_path": "tests/test_data/sanha/D-CAB-SAN-PCP-10-025.pfd.adm.json",
    "pnd_adm_path": "tests/test_data/sanha/pnd_adms/pnd_001.adm.json",
    "process_narratives_folder_path":"data/sanha_dev/process_narratives"
}
```

**Step 4**:

```bash
    pipenv run extract_asset_data
```

```bash
    pipenv accuracy_process_narrative
```
