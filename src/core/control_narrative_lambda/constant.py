"""This file contains the constants used in the control narrative lambda function."""

control_loop_property_name_list = [
    "process_variable",
    "controller",
    "final_control_element",
]

# pylint: disable=invalid-name
prompt_control_loop = """
# Prompt for Control narrative data extraction

```json
{control_narrative_text_string}
```

Understand the above, control_narrative_text_string as process control engineer and Identify the control loops and generate JSON as mentioned below with proper key-value pairs.

**Instructions for response format**
Generate response text that can be converted to a json object. Do not send code, or other text containing instructions.

```json
[
    {{
        "process_variable":[],
        "controller":[],
        "final_control_element":[],
        "description":""
    }}
]
```

- **process_variable**: Instrument which is transmitting the sensed signal to controller. Avoid instruments that are sending signal to the PCS or SIS. Mention only instrument tag
- **controller**: Instrument which is controlling the process variable. Mention only instrument tag
- **final_control_element**: Instrument which is taking action to meet the desired specifications. Mention only instrument tag
- **description**: Briefly describe about the control mechanism by considering the process variable, controller, and final control element and their physical significances

**avoid instruments which are interacting with SIS or alarms in the output JSON**
**A minimum of single value should be present for each key in the above JSON data format to make a control loop. If the response is not meeting this criteria generate the JSON with empty values**
**There is a possibility that there are no control loops in the provided narrative text. In this case generate the JSON with empty values**

## NOTE

***give the response in json format only. don't include any explanation or code.***


"""
prompt_instrument = """
# Prompt for Control narrative data extraction

```json
{control_narrative_text_string}
```

Understand the above, control_narrative_text_string as process control engineer and Generate JSON as mentioned below with proper key-value pairs.

**Instructions for response format**
Generate response text that can be converted to a json object. Do not send code, or other text containing instructions.

```json
[
    {{
        "tag":"",
        "description":"",
        "operation_type":"",
    }}
]
```

- **tag**: ID of an each instrument mentioned in the given text.
- **description**: Explain the significance of the instrument described in the paragraph.
- **operation_type**: Identify the operation type of the instrument. This would be one of ["TRANSMITTER","DIRECT_ACTING", "REVERSE_ACTING", "FAIL_OPEN", "FAIL_CLOSE"].

***avoid instruments which are interacting with SIS or alarms in the output JSON***
"""
