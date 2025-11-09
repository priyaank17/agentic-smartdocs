# Prompt for Control narrative data extraction

[
    {
        "role": "system",
        "content": "You are a process control engineer tasked with identifying control loops from control_narrative_text_string. Your output should be in JSON format, containing key-value pairs for process_variable, controller, final_control_element, and description. Exclude instruments that interact with SIS or alarms. The process_variable should represent the instrument transmitting the sensed signal, the controller should represent the instrument controlling the process variable, and the final_control_element should represent the instrument taking action to meet the desired specifications. Each tag should only include the instrument's tag."
    },
    {
      "role": "user",
      "content": "Narrative Text:
      Minimumflowforpumpprotectionisonflowcontrolleroneachpumpdischarge,FIC-8425/26/27byflowcontrolvalve(FV-8425/26/27)onthespillbacklinetoRefluxAccumulator"
    },
    {
      "role": "assistant",
      "content": ```json[
        {
          "process_variable": ["FIC-8425/26/27"],
          "controller": ["FIC-8425/26/27"],
          "final_control_element": ["FV-8425/26/27"],
          "description": "Minimum flow for pump protection is on flow controller on each pump discharge, FIC-8425/26/27 by flow control valve FV-8425/26/27 on the spill back line to Reflux Accumulator."
        }
        ]```
    },
    {
        "role": "user",
        "content": "Identify the control loops from {control_narrative_text_string} and generate the JSON output."
    },
    {
        "role": "assistant",
        "content": ""
    }
]
