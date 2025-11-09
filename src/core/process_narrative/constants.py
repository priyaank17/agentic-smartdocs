"""This consists of the prompt and schema for the process narrative data extraction task."""
PID_PROMPT = """
# Prompt for Process narrative data extraction

I am a process engineer, extracting the details of assets from process narrative document.

assume source_destination_data = "```json {source_destination_connection_json}```"

This means we have **asset_name**, **asset_tag**, **asset_class**, **asset_id**, **connections**, **source_asset_name**, **destination_asset_name**, **commodity_type** from source_destination_data and asset. Ensure that each connection's details are correctly associated with the corresponding connection type as specified in the source_destination_data.

Extract the below described information of each connection from this paragraph only : {assets_json_string}.
**In single paragraph you should collect the connection details of all the assets which are there in both the paragraph and{asset_json_string}**

- **commodity**: The substance flowing through the pipeline to/from the asset.
- **flow_rate**: The flow rate of the commodity. This information is further classified into
    1. value (value should be numerical)
    2. units
- **temperature**: The temperature of the commodity. The unit of temperature is **°F**. This information is further classified into
    1. value (value should be numerical)
    2. units
- **pressure**: The pressure of the commodity. The unit of pressure is **psig**.This information is further classified into
    1. value (value should be numerical)
    2. units

- **narrative_id**: {narrative_id}

## About the paragraph

**Each paragraph may contain more than one asset**. Do not generate any new connections which is not present in source_destination data.
The source_asset_name and destination_asset_name of a each connections should present in source_destination_data only. Do not generate any new source_asset_name and destination_asset_name of a connection.

## The format of the discovered connections should be as below

Collect the connections' information and give me a json in the below mentioned format enclosed between ```json and```.

**Instructions for response format**
Give me a response text that can be converted to a json object. Do not send code, or other text containing instructions.

```json
[
{{
    "asset_name": "",
    "asset_tag": "",
    "asset_class": "",
    "asset_id":"",
    "connections": [
        {{
            "connection_type": "",
            "commodity": "",
            "flow_rate": {{"value": , "units": ""}},
            "temperature": {{"value": , "units": ""}},
            "pressure": {{"value": , "units": ""}},
            "source_asset_name": "",
            "destination_asset_name": "",
            "narrative_id: "",
        }}
    ]
}}]
```

**Ensure that the information is correctly associated with the corresponding source and destination assets, as well as the connection type specified in source_destination_data.**
**Give the response in json format only. don't include any explanation or code.**
"""

SCHEMA = """{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "meta_data": {
      "type": "object",
      "properties": {
        "id": { "type": "string", "format": "uuid" },
        "adm_type": { "type": "string" },
        "plant_name": { "type": "string" },
        "document_name": { "type": "string" },
        "document_number": { "type": ["string", "null"] }
      }
    },
    "connections": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "connection_type": { "type": "string", "enum": ["IN_LET", "OUT_LET"] },
          "commodity": { "type": "string" },
          "flow_rate": {
            "type": "object",
            "properties": {
              "value": { "type": ["number", "string", "null"] },
              "units": { "type": ["string", "null"] }
            },
            "required": ["value", "units"]
          },
          "temperature": {
            "type": "object",
            "properties": {
              "value": { "type": ["number", "string", "null"] },
              "units": { "type": ["string", "null"] }
            },
            "required": ["value", "units"]
          },
          "pressure": {
            "type": "object",
            "properties": {
              "value": { "type": ["number", "string", "null"] },
              "units": { "type": ["string", "null"] }
            },
            "required": ["value", "units"]
          },
          "source_asset_name": { "type": "string" },
          "destination_asset_name": { "type": "string" },
          "narrative_id": { "type": "string" },
          "id": { "type": "string" },
          "asset_id": { "type": ["string", "null"] }
        }
      }
    }
  }}
"""
