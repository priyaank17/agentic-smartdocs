# prompt

[
  {{
    "role": "system",
    "content": "Your are a process engineer. Your task is to check if operating conditions of an equipment present in 'narrative_text_string' paragraph. If present provide the names and values of operating conditions in json format. The output should be in JSON format."
  }},
  {{
    "role": "user",
    "content": "narrative_text_string = '''The operating conditions for the LPG HP Separator (MBD-8230) are as follows:

- Temperature: Approximately -11 °F
- Pressure: Approximately 915 psig

These conditions are part of the processing environment for the LPG HP Separator in the LPG system.'''

    query = '''
    equipment_name: 'LPG HP Separator'
    '''
    "
  }},
  {{
    "role": "assistant",
    "content": ```json[
      {{
        "temperature": {{
          "value": -11,
          "units": "°F"
        }},
        "pressure": {{
          "value": 915,
          "units": "psig"
        }},
        "equipment_name": "LPG HP Separator"
      }}
    ]```
  }},
  {{
    "role": "user",
    "content": "narrative_text_string = '''Not explicitly mentioned'''

    query = '''
    equipment_name: 'Turbo Expander'
    '''
    "
  }},
  {{
    "role": "assistant",
    "content": ```json[
      {{
        "equipment_name": "Turbo Expander"
      }}
    ]```
  }},
  {{
    "role": "user",
    "content": "From the paragraph {narrative_text_string} provide the operating parameters of equipment {query} in JSON format."
  }},
  {{
    "role": "assistant",
    "content": "",
  }}
]
