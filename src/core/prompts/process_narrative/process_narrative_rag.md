
# prompt

[
  {{
    "role": "system",
    "content": "You are a process engineer yor task is to extract value of flowrate, pressure, and temperature of the commodity between the source_asset and destination_asset using 'narrative_text_string' input. The output should be in JSON format with each entry containing the flowrate, pressure, temperature, source_asset_name and destination_asset_name."
  }},
  {{
    "role": "user",
    "content": "narrative_text_string = '''The LPG Feed Chiller is an aluminum multi-stream exchanger cold box that
cools the incoming feed stream to around -11 °F using recycle streams from the De-ethanizer Overhead Condenser and the liquid outlet from the LPG HP Separator. Liquids condense out of the feed stream, which is fed to the LPG
HP Separator that operates around -11 °F and 915 psig. The gas from the separator is fed to the Turbo-Expanders, and the liquids are recycled under level control, back to the LPG Feed Chiller. The conditions of the liquid recycle stream at the inlet and outlet to the feed chiller are around 310 psig at -45 °F and 305 psig at 85 °F, respectively. The stream coming to the LPG Feed Chiller from the De-ethanizer Overhead Condenser originates at the Absorption Tower Overheads, and is heated in the feed chiller from -68 °F to 82 °F and is then fed to the Recompressors.'''

    query = '''
    source_asset_name: 'LPG HP SEPARATOR TO FLARE'
    destination_asset_name: 'FEED CHILLER'
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
            "value": -11,
            "units": "°F"
            }},
          "pressure": {{
            "value": 915,
            "units": "psig"
            }},
          "source_asset_name": "LPG HP SEPARATOR TO FLARE",
          "destination_asset_name": "FEED CHILLER"
        }}
        ]```
  }},
  {{
    "role": "user",
    "content": "narrative_text_string = '''The chilled gas from the turbo-expanders is fed to the base of the Absorption Tower where it flows upwards countercurrent to the partially-condensed overheads from the De-ethanizer tower. The liquid flowing down the Absorption Tower absorbs any of the remaining heavier components in the gas that were not removed as liquids in the LPG HP Separator. The gas leaving the top of the Absorption Tower is at 273 psig and -115°F, with a very lean composition, consisting principally of methane and ethane. This cold, lean gas is fed to the De-Ethanizer Overhead Condenser (another aluminum multi-stream exchanger) where it is used to partially condense the De-ethanizer overheads whilst being heated to around -69 °F. The lean gas then flows to the LPG Feed Chiller where it is heated further before reaching the recompressors.'''

    query = '''
    source_asset_name: 'DEETHANIZER OVERHEAD CONDENSER'
    destination_asset_name: 'FEED CHILLER'
    '''
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
            "value": -69,
            "units": "°F"
            }},
          "pressure": {{
            "value": null,
            "units": ""
            }},
          "source_asset_name": "DEETHANIZER OVERHEAD CONDENSER",
          "destination_asset_name": "FEED CHILLER"
        }}
        ]```
  }},
  {{
    "role": "user",
    "content": "narrative_text_string = '''The De-ethanizer operates between 198 °F in its bottoms stream and -40 °F in its overheads. Heat input to the De-ethanizer is supplied by the De-ethanizer Reboiler, which is a thermosyphon type exchanger that uses heat medium on the tube side. The operating pressure of this column is between 294 and 297 psig. The overhead streams contain principally methane and ethane, and is partially condensed by the De-ethanizer Overhead Condenser. This two-phase stream is fed to the Absorption Tower, from which the De-ethanizer Reflux Pumps return the liquids under level control back to the De-ethanizer.'''

    query = '''
    source_asset_name: 'DEETHANIZER INTERNAL REFLUX CONDENSER'
    destination_asset_name: 'GAS/GAS EXCHANGER'
    '''
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
            "units": "°F"
            }},
          "pressure": {{
            "value": null,
            "units": ""
            }},
          "source_asset_name": "DEETHANIZER INTERNAL REFLUX CONDENSER",
          "destination_asset_name": "GAS/GAS EXCHANGER"
        }}
        ]```
  }},
  {{
    "role": "user",
    "content": "Read the text clearly {narrative_text_string} and Please provide the values of flowrate, pressure, and temperature for the commodity between the {query}, source asset name and destination asset name in JSON format."
  }},
  {{
    "role": "assistant",
    "content": "",
  }}
]
