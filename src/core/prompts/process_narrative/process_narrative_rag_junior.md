# prompt

[
  {{
    "role": "system",
    "content": "Your task is to give me only the directly mentioned values of flowrate, pressure, and temperature of the commodity between the source_asset and destination_asset from the given 'narrative_text_string' paragraph. If a value is inferred or not directly present in the text, do not include it in the output. The output should be in JSON format with each entry containing only the directly present flowrate, pressure, temperature, along with the source_asset_name and destination_asset_name."
  }},
  {{
    "role": "user",
    "content": "narrative_text_string = '''The flow rate of the dry gas from the Gas Dehydration System to the LPG Feed Chiller is approximately 340 MMSCFD. The conditions are approximately 923 psig and 92 °F.'''

    query = '''
    source_asset_name: 'GAS DEHYDRATION SYSTEM'
    destination_asset_name: 'FEED CHILLER'
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
        "source_asset_name": "GAS DEHYDRATION SYSTEM",
        "destination_asset_name": "FEED CHILLER"
      }}
    ]```
  }},
  {{
    "role": "user",
    "content": "narrative_text_string = '''The specific flow rate between the Debutanizer Reflux Accumulator and the Debutanizer Reflux Pump is not directly mentioned in the provided context. However, the discharge conditions for the Debutanizer Reflux Pumps are stated to be around 478 psig at 128 °F. Therefore, the conditions at the inlet to the Debutanizer Reflux Pumps (from the Debutanizer Reflux Accumulator) would be similar or slightly lower than these discharge conditions.'''

    query = '''
    source_asset_name: 'DEBUTANIZER REFLUX ACCUMULATOR'
    destination_asset_name: 'DEBUTANIZER REFLUX PUMP'
    '''
    "
  }},
  {{
    "role": "assistant",
    "content": ```json[
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
        "source_asset_name": "DEBUTANIZER REFLUX ACCUMULATOR",
        "destination_asset_name": "DEBUTANIZER REFLUX PUMP"
      }}
    ]```
  }},
  {{
    "role": "user",
    "content": "Read the paragraph clearly {narrative_text_string} and provide only the correct value of flowrate, pressure, and temperature between the {query}, source asset name and destination asset name in JSON format."
  }},
  {{
    "role": "assistant",
    "content": "",
  }}
]
