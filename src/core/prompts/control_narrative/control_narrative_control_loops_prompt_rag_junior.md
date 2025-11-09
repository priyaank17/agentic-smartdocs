# prompt

[
  {{
    "role": "system",
  "content": """You are a process control engineer. Your task is to extract and identify the following elements from the provided narrative_text_string: controller, transmitter, control valve, and equipment name.

  Your output must be in JSON format, structured as a list of dictionaries with the following keys:

## Output Structure

  ```json
  [
    {{
      "equipment_name": string,
      "equipment_tag": string,
      "controller": dictionary,
      "transmitter": dictionary,
      "control_valve": dictionary
    }}
  ]
  ```

  """
  }},
  {{
    "role": "user",
    "content": "narrative_text_string = '''
    LPG HP Separator MBD-8230 (controller LIC-8230-A): In the LPG HP Separator (MBD-8230), the controller LIC-8230-A is a direct acting controller that manages the liquid level in the separator.

- **Transmitter Tags:**
  - **LIT-8230-A:** This is the level transmitter that senses the process variable, which is the liquid level in the LPG HP Separator, and provides level indication to the PCS.

- **Control Valve Tags:**
  - **LV-8230-A1:** This is a fail-closed valve that opens from 0% to 50% as the controller output increases, allowing more liquid to flow to the De-ethanizer and reducing the level in the separator.
  - **LV-8030-A2:** This is another fail-closed valve that opens from 50% to 100% as the controller output increases further, allowing even more liquid to flow to the De-ethanizer to manage the separator level.

The controller LIC-8230-A is configured as a split range direct acting controller. As the level rises above the setpoint, the controller output increases, first opening LV-8230-A1 and then LV-8030-A2 if the level continues to rise, thereby reducing the level in the separator. If the level falls below the setpoint, the controller output decreases, reversing the procedure.
  '''
    "
  }},
  {{
    "role": "assistant",
    "content": ```json[
      {{'equipment_name': 'LPG HP Separator',
      'equipment_tag': 'MBD-8230',
      'controller': {{'LIC-8230-A': 'The controller LIC-8230-A is configured as a split range direct acting controller. As the level rises above the setpoint, the controller output increases, first opening LV-8230-A1 and then LV-8030-A2 if the level continues to rise, thereby reducing the level in the separator. If the level falls below the setpoint, the controller output decreases, reversing the procedure.'}},
      'transmitter': {{ 'LIT-8230-A': 'This is the level transmitter that senses the process variable, which is the liquid level in the LPG HP Separator, and provides level indication to the PCS.' }}
      'control_valve': {{ 'LV-8230-A1': 'This is a fail-closed valve that opens from 0% to 50% as the controller output increases, allowing more liquid to flow to the De-ethanizer and reducing the level in the separator',
      'LV-8030-A2': 'This is another fail-closed valve that opens from 50% to 100% as the controller output increases further, allowing even more liquid to flow to the De-ethanizer to manage the separator level.'}}
      }}
    ]```
  }},
  {{
    "role": "user",
    "content": "narrative_text_string = '''
    Recompressor CBA-2350 (controller LIC-8120-A): The provided context does not contain specific information about the controller LIC-8120-A, the transmitter tags that sense its process variable, or the control valve tags associated with it. Therefore, I am unable to provide the requested details. If you have access to additional documentation or context that includes this information, I would be able to assist you further.",

  '''
    "
  }},
  {{
    "role": "assistant",
    "content": ```json[
      {{'equipment_name': 'Recompressor',
      'equipment_tag': 'CBA-2350',
      'controller': {{}},
      'transmitter': {{}}
      'control_valve': {{}}
      }}
    ]```
  }},
  {{
  "role": "user",
  "content": "Carefully read the provided {narrative_text_string}. Extract and identify the controller, transmitter, control valve, and equipment name. Return the output strictly in the specified JSON structure. All keys — 'equipment_name', 'equipment_tag', 'controller', 'transmitter', and 'control_valve' — must be present in the output, even if their values are empty or not found."
}}
,
  {{
    "role": "assistant",
    "content": "",
  }}
]
