# Prompt for Data Sheets table extraction

The task is to construct a csv file.

## Example

### Given Data

SYSTEM MONITORING PANEL (340, 200)
MODEL DETAILS (1290, 205)
CONFIGURATION SETTINGS (1750, 210)
Model: ABC-123 (330, 250)
Type: Advanced System (1280, 250)
Orientation: Vertical (1720, 255)
Version: 2.5 (340, 300)
Settings: Default (1290, 305)
Security Level: High (1760, 310)

### Properties to Extract

json
[
    "model",
    "type",
    "orientation",
    "version",
    "settings",
    "security_level",
    "firmware",
    "license"
]

### Expected Output Format

The output should be formatted as CSV, showing property names and their corresponding values under each column, based on the defined tolerance for x-coordinates.

Expected Response:

csv
"property_name","value"
"model","ABC-123"
"type","Advanced System"
"orientation","Vertical"
"version","2.5"
"settings","Default"
"security_level","High"
"firmware",""
"license",""

### Explanation

The CSV table is structured by identifying and extracting values based on their alignment with the property names' x-coordinates. The property names [
    "model",
    "type",
    "orientation",
    "version",
    "settings",
    "security_level",
    "firmware",
    "license"
] are predefined. Each corresponding value is placed under its respective property based on the proximity to the property names in the given text. If a property is specified but not present in the given text, such as "firmware" and "license" in this example, those fields are populated with empty strings in the CSV output.

## Task

Given a data sheet text string :

```json
{data_sheet_text_string}
```

containing words with x and y coordinates, your goal is to create a table using the provided data. The format of each word is: `word (x_coordinate, y_coordinate)`.

### Table Structure

**Extract the values for these properties only: `{properties_name_list}`.**

## Note

**Do not change the property name**
**Do not give information of any other property.**
**Do not write units in value.**
**If a x coordinate of a word falls between two columns, include the word in both column**
**It is possible that the column is empty because of no values for that particular property**
**It is possible that the cell is empty because of no value for that column in that particular property**
**Note: The coordinates serve solely for computational purposes; avoid incorporating them into the table.**

****give only the constructed table in csv format, don't give any explanation.****
