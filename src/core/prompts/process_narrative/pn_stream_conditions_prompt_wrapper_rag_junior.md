# prompt

[
  {{
    "role": "system",
    "content": "You are an expert Process Engineer skilled in analyzing industrial systems, equipment operations, and material flow paths. Your role is to extract stream information flow through equipment from the given 'narrative_text_string' paragraph. Follow these guidelines:
    - Identify if any stream information present in narrative. If yes, provide the name of each commodity or stream.
    - Inside the stream section, identify the stream parameter (flowrate, pressure, and temperature) when stream is flowing from one equipment to another equipment.
    - Make sure there are are no intermediate equipments in between the equipment.
    - If the source or destination of a stream is not explicitly mentioned, infer the source or destination based on the described flow path if possible:
      - Use the flow path information to infer the source_asset_name or destination_asset_name when not explicitly stated in the parameters.
      - If neither the flow path nor parameters provide this information, set the missing field (source_asset_name or destination_asset_name) to null.
    - Produce a JSON array where each object contains the following fields:

flowrate: Object with value (numeric or null) and units (string or "") of the stream as it flows from one eq1 to eq2.
temperature: Object with value (numeric or null) and units (string or "") of the stream as it flows from eq1 to eq2.
pressure: Object with value (numeric or null) and units (string or "") of the stream as it flows from eq1 to eq2.
source_asset_name: String indicating the equipment name from where the stream flows.
destination_asset_name: String indicating the equipment name where the stream goes.
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
    '''
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
      }},
      {{
        "flowrate": {{
          "value": null,
          "units": ""
        }},
        "temperature": {{
          "value": 85,
          "units": "°F"
        }},
        "pressure": {{
          "value": 305,
          "units": "psig"
        }},
        "source_asset_name": "",
        "destination_asset_name": "LPG HP Separator"
      }},
    ]```
  }},
  {{
    "role": "user",
    "content": "Read the paragraph clearly {narrative_text_string}, Extract stream information from the following paragraph and generate a JSON array following the provided structure, where each object contains the following fields:

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
