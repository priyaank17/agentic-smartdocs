# prompt to extract operating information from junior

For the equipment {equipment_name}, check if any operating condition of the equipment are provided. If such operating conditions are present, list the names and values of the operating parameters that describe the equipment's normal operation, excluding stream-specific details.

- Only provide the conditions at which the equipment operates.
- Do not include any stream details.
- Do not include any inlet or outlet condition.
- If no operating condition of the equipment are provided, include: **'Not explicitly mentioned.'**
For example, for LPG Feed Chiller, extract the parameter specifically related to the equipment's operation, not the streams.
