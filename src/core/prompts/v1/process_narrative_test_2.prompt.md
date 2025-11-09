# Prompt for Process narrative data extraction

I am Process Engineer, working to extract specific information from the process narrative document of an industrial plant.
Extracting an accurate result is very important for my job.
You are given a JSON record containing the details of an asset:
asset_details(id,asset_name,asset_tag,asset_class,process_narrative) =

```json
{asset_json_string}
```

And the list of available assets in the process unit are as follows:

asset_names =

```json
{assets_json_string}
```

Follow the below steps and get the response:
step 1: Each asset contains a bunch of in_lets and out_lets. We call them connections.
Step 2: Collect the process_narrative information from the asset_details.
Step 3 : find the below properties from the process_narrative:

- connection_type: This must be one of ["IN_LET", "OUT_LET"]
- commodity: The substance that flows through the the pipeline to/from the asset
- flow_rate: The flow rate of the commodity. This information is further classified into
    1. value (value should be numerical)
    2. units
- temperature: The temperature of the commodity. This information is further classified into
    1. value (value should be numerical)
    2. units
- pressure: The pressure of the commodity. This information is further classified into
    1. value (value should be numerical)
    2. units

- source_asset_name: Source asset name of the pipeline carrying the commodity. This must be one of the given asset names
- destination_asset_name: Destination asset name of the pipeline carrying the commodity. This must be one of the given asset_names

step 4: source_asset_name and destination_asset_name should be one of the asset_name in the asset_names

Step 5 : Find all the connections in the process narrative related to that asset.The format of the discovered connections should be as below format enclosed between ```json and```.

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

step 6: **response should only the  json object. don't add any comments or code.**
