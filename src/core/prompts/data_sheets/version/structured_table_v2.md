# Prompt for Data Sheets table extraction

The task is to construct a csv file.

## For Example

### Given Data

MACHINE SPECIFICATIONS (100, 50)
Engine Model (150, 75)
Marine Grade (825, 75)
Engine Power (HP) (150, 100)
150 (1345, 100)
Fuel Type (150, 125)
Gasoline (1355, 125)
Oil Capacity (L) (150, 150)
3 (835, 150)
Emissions (150, 175)
High (1338, 175)

### Properties to Extract

```json
[
    "engine_model",
    "engine_power_hp",
    "fuel_type",
    "drink_capacity",
    "oil_capacity_l",
    "emissions",
    "maintenance",
    "water_capacity"
]
```

### column names

```json
[
    "marine_grade",
    "industrial_grade"
]
```

### Expected Output Format

The expected output should be in CSV format, showing property names and their corresponding values under each column, based on the defined tolerance for x-coordinates.

Expected Response:

```csv
"property_name","marine_grade","industrial_grade"
"engine_model","Marine Grade",""
"engine_power_hp","",""
"fuel_type","","Gasoline"
"drink_capacity","",""
"oil_capacity_l","3",""
"emissions","","High"
"maintenance","",""
"water_capacity","",""
```

### Explanation

The CSV table is constructed by parsing and structuring data based on text containing x and y coordinates. First, we identify property names [
    "engine_model",
    "engine_power_hp",
    "fuel_type",
    "drink_capacity",
    "oil_capacity_l",
    "emissions",
    "maintenance",
    "water_capacity"
]. column names are also provided : ["marine_grade","industrial_grade"], Corresponding values are then positioned under these headers based on their alignment with the x-coordinates of the property names: Gasoline placed under industrial_grade and "3" is placed under marine_grade. if property name is asked to extract and if it is not there in the give text then make those respective values as empty strings like :  ["drink_capacity","water_capacity"]

## Task

Given a data sheet text string :

```json
{data_sheet_text_string}
```

containing words with x and y coordinates, your goal is to create a table using the provided data. The format of each word is: `word (x_coordinate, y_coordinate)`.

### Table Structure

- The header of the data sheets is defined by: `{columns_name_list}`.
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
