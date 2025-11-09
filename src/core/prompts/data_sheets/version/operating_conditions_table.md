# Prompt for Data Sheets table extraction

I am a process engineer, and extracting table from data sheets documents.

```json
{data_sheet_text_string}
```

data_sheet_text_string consist of words with x_coordinate and y_coordinate.
The format of each word is : word (x_coordinate, y_coordinate)

**Use x and y coordinates to create a table.**
**Focus on data for table name : "Operating Conditions"**
**Make a table with this data**

## Table Structure

- The table should include headers such as Property Name, Units, Value
- Property Name should include : Flow normal, Rated, Suction pressure max/rated, discharge pressure, diff.head, NPSHA

## Note

**If a x coordinate of a word falls between two columns, include the word in both column**
**It is possible that the column is empty because of no values**
**give the table in csv format.**
**Note: The coordinates serve solely for computational purposes; avoid incorporating them into the table.**
**Note: Only csv table should be present in the output**
