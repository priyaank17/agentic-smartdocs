# Prompt for Data Sheets table extraction

I am a process engineer, and extracting table from data sheets documents.

```json
{data_sheet_text_string}
```

data_sheet_text_string consist of words with x_coordinate and y_coordinate.
The format of each word is : word (x_coordinate, y_coordinate)

**Use x and y coordinates to create a table.**
**Make a table with this data**

## Table Structure

- Using the provided dataset, fill in the missing values for each property. The keys are the name of the property
[
    "duty": {{"value": ""}},
    "ua": {{"value": ""}},
    "ua_curve_error": {{"value": ""}},
    "ft_factor": {{"value": ""}},
    "heat_leak": {{"value": ""}},
    "minimum_approach": {{"value": ""}},
    "hot_pinch_temperature": {{"value": ""}},
    "uncorrected_lmtd": {{"value": ""}},
    "heat_loss": {{"value": ""}},
    "lmtd": {{"value": ""}},
    "cold_pinch_temperature": {{"value": ""}},
]
- where 'value' defines the value of the property.
- Do not give information of any other property.

## Note

**Do not give information of any other property.**
**Do not write units in value.**
**If a x coordinate of a word falls between two columns, include the word in both column**
**It is possible that the column is empty because of no values**
**give the table in csv format.**
**Note: The coordinates serve solely for computational purposes; avoid incorporating them into the table.**
**Note: Only csv table should be present in the output**
