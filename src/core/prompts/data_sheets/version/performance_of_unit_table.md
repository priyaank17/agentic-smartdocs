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

- The header of the datasheets is : 'property_name', 'shell_side_inlet', 'shell_side_outlet', 'tube_side_inlet', 'tube_side_outlet'.
- Using the provided dataset, fill in the missing values for each property. The keys are the name of the property
[
    "fluid_name",
    "fluid_quantity_total",
    "vapor_quantity_total",
    "liquid_quantity_total",
    "steam_quantity_total",
    "water_quantity_total",
    "non_condensables",
    "temperature",
    "dew_point",
    "bubble_point",
    "vapor_density",
    "liquid_density",
    "vapor_viscosity",
    "liquid_viscosity",
    "vapor_molecular_weight",
    "non_condensables_molecular_weight",
    "vapor_specific_heat_capacity",
    "liquid_specific_heat_capacity",
    "vapor_thermal_conductivity",
    "liquid_thermal_conductivity",
    "latent_heat",
    "pressure",
    "inlet_velocity",
    "pressure_drop_allowed",
    "pressure_drop_calculated",
    "fouling_resistance",
    "heat_exchanged",
    "transfer_rate_dirty",
    "transfer_rate_clean"
]

## Note

**Do not give information of any other property.**
**Do not write units in value.**
**If a x coordinate of a word falls between two columns, include the word in both column**
**It is possible that the column is empty because of no values**
**give the table in csv format.**
**Note: The coordinates serve solely for computational purposes; avoid incorporating them into the table.**
**Note: Only csv table should be present in the output**
