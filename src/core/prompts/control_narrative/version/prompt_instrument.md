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
