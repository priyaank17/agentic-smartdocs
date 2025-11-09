# Prompt for Process narrative data extraction

We are working on to extract certain information from process narrative of an industrial plant.
You are be given a json record containing the details of an asset:

```json
{asset_json_string}
```

And the list of available assets in the process unit are as follows:

```json
{assets_json_string}
```

Each asset contains a bunch of in_lets and out_lets. We call them **connections**. We need to extract the below described information of each connection

- **connection_type**: This must be one of ["IN_LET", "OUT_LET"]
- **commodity**: The substance that flows through the the pipeline to/from the asset
- **flow_rate**: The flow rate of the commodity. This information is further classified into
    1. value (value should be numerical)
    2. units
- **temperature**: The temperature of the commodity. This information is further classified into
    1. value (value should be numerical)
    2. units
- **pressure**: The pressure of the commodity. This information is further classified into
    1. value (value should be numerical)
    2. units

- **source_asset_name**: Source asset name of the pipeline carrying the commodity. This must be one of the given asset names
- **destination_asset_name**: Destination asset name of the pipeline carrying the commodity. This must be one of the given asset names

## Description to resolve Source and Destination

Let us assume there are only two assets. And we are trying to resolve the connections of the first one ({asset})

1. asset_name_one (current asset name) = {asset}
2. asset_name_two

**Case 1**:
While trying to resolve source_asset_name and destination_asset_name of a connection of {asset},
if the connection_type is "IN_LET", this means there is a pipeline that started from the asset_name_two's OUT_LET and reaching this {asset} at this IN_LET.

- The source_asset_name becomes asset_name_two
- The destination_asset_name becomes {asset}

**Case 2**:
While trying to resolve source_asset_name and destination_asset_name of a connection of {asset},
if the connection_type is "OUT_LET", this means there is a pipeline that started from the {asset}'s OUT_LET and reaching asset_name_two's IN_LET.

- The source_asset_name becomes {asset}
- The destination_asset_name becomes asset_name_two

## The format of the discovered connections should be as below

Collect the connections' information and give me a json in the below mentioned format enclosed between ```json and```.

**Instructions for response format**
Give me a response text that can be converted to a json object. Do not send code, or other text containing instructions.

```json
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
            "destination_asset_name": ""

        }}
    ]
}}
```
