# prompt

[
  {{
    "role": "system",
    "content": """You are a process control engineer tasked is to identify the controller and equipment_name in narrative_text_string. Your output must be in JSON format, structured as a list of dictionaries with the following keys:

## Output Structure

  ```json
  [
    {{
      "equipment_name": string,
      "controller": dictionary
    }}
  ]
  ```

"""

  }},
  {{
    "role": "user",
    "content": "narrative_text_string = '''
    LPG HP Separator: In the LPG HP Separator (MBD-8230), the controllers present are:

1. **LIC-8230-A**: A direct acting level controller.
2. **TIC-8230-A**: A reverse acting temperature controller.
'''
    "
  }},
  {{
    "role": "assistant",
    "content": ```json[
      {{'equipment_name': 'LPG HP Separator',
 'controller': {{'LIC-8230-A': 'A direct acting level controller',
  'TIC-8230-A': 'A reverse acting temperature controller'}},
  }}
    ]```
  }},
  {{
    "role": "user",
    "content": "Read the paragraph clearly, identifying controller and equipment_name from {narrative_text_string}. Return the output strictly in the specified JSON structure. All keys — 'equipment_name', 'controller' — must be present in the output, even if their values are empty or not found.""
  }},
  {{
    "role": "assistant",
    "content": "",
  }}
]
