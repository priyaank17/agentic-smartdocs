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
