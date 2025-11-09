@REM First download the Asset_Class_Standard_Properties.xlsx from drive and save in data folder
CALL python -m src.local_execution.data_sheets.update_standard_property_table.get_standard_name_csv
