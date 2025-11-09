# Prompt for Data Sheets table extraction

[
  {{
    "role": "system",
    "content":"You are a process engineering lead, your task is to extract table value from data_sheet_text in csv format. The format of each word is : word (x_coordinate, y_coordinate). **Use x and y coordinates to create a table.**
    Use the provided data_sheet_text, map the missing values for each property from the property_name_list and column name given. Do not add any new property_name. Ignore the unit of the property.
  }},
   {{"role": "user", "content": "Narrative Text:
SYSTEM MONITORING PANEL (340, 200)
MODEL DETAILS (1290, 205)
CONFIGURATION SETTINGS (1750, 210)
Model: ABC-123 (330, 250)
Type (854, 250)
Advanced System (1280, 250)
Orientation: Vertical (1720, 255)
Version: 2.5 (340, 300)
Settings: Default (1290, 305)
Security Level: High (1760, 310)

Properties Name Given:
["Model", "Type", "Orientation", "Firmware", "Version", "Settings", "Security Level", "License"]

Column Name Given:
["property_name", "value"]
"}},
    {{"role": "assistant", "content": ```csv
"property_name","value"
"Model","ABC-123"
"Type","Advanced System"
"Orientation","Vertical"
"Firmware",""
"Version","2.5"
"Settings","Default"
"Security Level","High"
"License",""```
}},
{{"role": "user", "content": "tell me the csv table of {data_sheet_text_string}. Having column name {columns_name_list} and property name {properties_name_list}."}}
{{"role": "assistant", "content":}}
]
