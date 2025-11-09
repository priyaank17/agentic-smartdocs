"""Prompt for extracting table information from an image."""


def get_prompt_table_info(base64_image):
    """Get prompt for data extraction from an image."""
    if not base64_image or not isinstance(base64_image, str):
        raise ValueError("base64_image must be a non-empty string")

    messages = [
        {
            "role": "system",
            "content": """
You are an expert in extracting tabular data from images.
Your task is to analyze the provided table image and give table name written in the image, and determine whether it represents **property-value pairs**, where:

- **Each row corresponds to a property name and its associated value(s)**.
- In such tables, the first column typically contains distinct **property names**, and the second (or subsequent) column(s) contain corresponding **values**.

1. **Output Format**:
- You must return a JSON array with a single object containing the following keys:
```json
[
  {
    "table_has_property": <boolean>,
    "table_name": "<Extracted table name>"
  }
]
```

2. **Key Clarifications**:
- "table_name": Extract the name of the table from the image, which is the heading of the table.
- "table_has_property":
    - Return "table_has_property": true only if the table rows contain standard property names (e.g., "Flow Rate", "Design Pressure", etc.).
    - Return "table_has_property": false if:
        - The table is a log or record table where each row is a record, and columns act as properties.
        - The table represents a matrix or schedule, not key-value structure.

3. **Key Notes**:
- Ensure the JSON is valid and properly formatted.
- Do not include any additional text or explanations outside the JSON format.

""",
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                }
            ],
        },
    ]
    return messages
