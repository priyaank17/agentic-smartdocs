# prompt

[
  {{
    "role": "system",
    "content": "You are a process control engineer, and your task is to extract relevant instrument information from control_narrative_text_string. The output should be in JSON format with each entry containing the instrument tag, description, and operation_type. Exclude instruments that interact with SIS or alarms. The operation_type should be one of: ['TRANSMITTER', 'DIRECT_ACTING', 'REVERSE_ACTING', 'FAIL_OPEN', 'FAIL_CLOSE']."
  }},
  {{
    "role": "user",
    "content": "narrative_text_string = '''
    Here is the relevant instrument information for the LPG HP Separator, excluding those that interact with SIS or alarms:

1. **Instrument Tag:** PIT-8230-A
   **Description:** Pressure Transmitter
   **Operation Type:** TRANSMITTER

2. **Instrument Tag:** FIT-6000-B1
   **Description:** Flow Transmitter with Temperature Compensation
   **Operation Type:** TRANSMITTER

3. **Instrument Tag:** TIT-6000-B1
   **Description:** Temperature Transmitter
   **Operation Type:** TRANSMITTER

'''
    "
  }},
  {{
    "role": "assistant",
    "content": ```json[
    {{
    "tag": "PIT-8230-A",
    "operation_type": "TRANSMITTER",
    "description": "Pressure Transmitter"
  }},
  {{
    "tag": "FIT-6000-B1",
    "operation_type": "TRANSMITTER",
    "description":"Flow Transmitter with Temperature Compensation"
  }},
  {{
    "tag": "TIT-6000-B1",
    "operation_type": "TRANSMITTER",
    "description": "Temperature Transmitter"
  }}
    ]```
  }},
  {{
    "role": "user",
    "content": "Read the paragraph clearly, identifying control narrative instrument from {narrative_text_string}"
  }},
  {{
    "role": "assistant",
    "content": "",
  }}
]
