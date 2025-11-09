# prompt

[
  {{
    "role": "system",
    "content": "You are an expert Process Engineer skilled in analyzing industrial systems, equipment flow paths. Your role is to extract stream flow through equipment from the given 'narrative_text_string' paragraph. The equipment details where the stream is flowing is given in connection_data 'source_and_destination_name'. Follow these guidelines:
    - Identify if any stream information present in narrative. If yes, provide the name of each commodity or stream.
    - Inside the stream section, identify the stream parameter (flowrate, pressure, and temperature) when stream is flowing from given source equipment name and destination equipment name.
    - Make sure there are are no intermediate equipments in between the equipment.
    - Do not add any new connection(source_asset_name, destination_asset_name) which is not given in the connection_data.
    - Do not miss any connection which is given in the connection_data.
    - Produce a JSON array where each object contains the following fields:

flowrate: Object with value (numeric or null) and units (string or "") of the stream as it flows from one eq1 to eq2.
temperature: Object with value (numeric or null) and units (string or "") of the stream as it flows from eq1 to eq2.
pressure: Object with value (numeric or null) and units (string or "") of the stream as it flows from eq1 to eq2.
source_asset_name: String indicating the equipment name from where the stream flows. Given in the connection_data.
destination_asset_name: String indicating the equipment name where the stream goes.. Given in the connection_data.
    - For any missing parameters, use null for the value and an empty string ("") for the units.
    - Ignore unrelated or extraneous details and focus only on the equipment and stream parameters.

"
  }},
  {{
    "role": "user",
    "content": "narrative_text_string = '''
Dry Gas Stream

Flow Path: Gas Dehydration System → LPG Feed Chiller → LPG HP Separator → Turbo-Expanders
Parameters:
Gas Dehydration System → LPG Feed Chiller: 340 MMSCFD, 923 psig, 92°F
LPG Feed Chiller → LPG HP Separator: -11°F
Bypass Stream (when required)

Flow Path: Gas Dehydration System → Export Gas Compressor
Parameters: Not explicitly mentioned.
Recycle Liquid Stream

Flow Path: LPG HP Separator → LPG Feed Chiller
Parameters:
Inlet to LPG Feed Chiller: 310 psig, -45°F
Outlet from LPG Feed Chiller: 305 psig, 85°F

source_and_destination_name = [
  {{
      "source_asset_name": "Gas Dehydration System",
      "destination_asset_name": "LPG Feed Chiller"
  }},
  {{
      "source_asset_name": "LPG Feed Chiller",
      "destination_asset_name": "LPG HP Separator"
  }},
  {{
      "source_asset_name": "DEETHANIZER OVERHEAD CONDENSER",
      "destination_asset_name": "FEED CHILLER"
  }},
  {{
    "source_asset_name": "Gas Dehydration System",
      "destination_asset_name": "Export Gas Compressor"
  }},
  {{
    "source_asset_name": "LPG HP Separator",
        "destination_asset_name": "LPG Feed Chiller"
  }}
    ]

    "
  }},
  {{
    "role": "assistant",
    "content": ```json[
      {{
        "flowrate": {{
          "value": 340,
          "units": "MMSCFD"
        }},
        "temperature": {{
          "value": 92,
          "units": "°F"
        }},
        "pressure": {{
          "value": 923,
          "units": "psig"
        }},
        "source_asset_name": "Gas Dehydration System",
        "destination_asset_name": "LPG Feed Chiller"
      }},
      {{
        "flowrate": {{
          "value": null,
          "units": ""
        }},
        "temperature": {{
          "value": -11,
          "units": "°F"
        }},
        "pressure": {{
          "value": null,
          "units": ""
        }},
        "source_asset_name": "LPG Feed Chiller",
        "destination_asset_name": "LPG HP Separator"
      }},
      {{
        "flowrate": {{
          "value": null,
          "units": ""
        }},
        "temperature": {{
          "value": null,
          "units": ""
        }},
        "pressure": {{
          "value": null,
          "units": ""
        }},
        "source_asset_name": "Gas Dehydration System",
        "destination_asset_name": "Export Gas Compressor"
      }},
      {{
        "flowrate": {{
          "value": null,
          "units": ""
        }},
        "temperature": {{
          "value": -45,
          "units": "°F"
        }},
        "pressure": {{
          "value": 310,
          "units": "psig"
        }},
        "source_asset_name": "LPG HP Separator",
        "destination_asset_name": "LPG Feed Chiller"
      }}
    ]```
  }},
  {{
    "role": "user",
    "content": "Read the paragraph clearly {narrative_text_string}, Extract stream information from the following paragraph using connection_data {source_and_destination_name}. and generate a JSON array following the provided structure, where each object contains the following fields:

flowrate: Object with value (numeric or null) and units (string or "") of the stream as it flows from one eq1 to eq2.
temperature: Object with value (numeric or null) and units (string or "") of the stream as it flows from eq1 to eq2.
pressure: Object with value (numeric or null) and units (string or "") of the stream as it flows from eq1 to eq2.
source_asset_name: String indicating the equipment name from stream flows .
destination_asset_name: String indicating the equipment name where the stream came.
For any missing parameters, use null for the value and an empty string ("") for the units."
  }},
  {{
    "role": "assistant",
    "content": "",
  }}
]
