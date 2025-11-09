# Prompt for Data Sheets table extraction

[
  {{
    "role": "system",
    "content":"You are a process engineering lead, your task is to extract table value from data_sheet_text in csv format. The format of each word is : word (x_coordinate, y_coordinate). **Use x and y coordinates to create a table.**
    Use the provided data_sheet_text, map the missing values for each of the column name given. Column name should be in columns_name_list."
  }},
{{
    "role": "user", "content": TAG (426, 1124)\nNOZZLE SERVICE (658, 1124)\nSIZE (828, 1126)\nRATING (946, 1128)\nA (428, 1152)\n. REFL . COND . INLET (646, 1153)\n30 " (838, 1154)\n300 # RFWN (974, 1154)\nB (426, 1178)\nREFL . COND . OUTLET (671, 1179)\n30 " (834, 1180)\n300 # RFWN (972, 1182)\nC (428, 1204)\nVENT (649, 1206)\n2 " (837, 1207)\n300 # RFWN (974, 1210)\nD (432, 1237)\nDRAIN (660, 1240)\n2 " (838, 1237)\n300 # RFWN (979, 1242)\n

   Column Name Given:
   ["nozzle_number","subpart_name","connection_type"]
  }},
    {{"role": "assistant", "content": ```csv
"nozzle_number","subpart_name","connection_type"
"A","REFL_COND","INLET"
"B","REFL_COND","OUTLET"
"C","VENT","OUTLET"
"D","DRAIN","OUTLET"```
}},
{{
    "role": "user", "content": "TAG : (232, 750)\nMANIFOLD SERVICE (424, 750)\nSIZE : (736, 750)\nQUANTITY (870, 750)\nRATING / FACING (1138, 750)\nA1 & A2 (191, 814)\nFEED GAS INLET (383, 814)\n18 " (736, 814)\n( 2 ) (870, 816)\n600 # RF (1086, 814)\nB1 & B2 (191, 846)\nFEED GAS OUTLET (395, 846)\n16 " (736, 844)\n( 2 ) (870, 846)\n600 # RF (1088, 846)\n( see note (1231, 875)\nC (190, 875)\nRESIDUE GAS INLET (401, 877)\n36 " (736, 876)\n( 1 ) (870, 878)\n300 # RF (1086, 876)\n17  page 12 ) (1364, 876)\n( see note (1232, 904)\nD (191, 908)\nRESIDUE GAS OUTLET (412, 908)\n36 " (734, 906)\n( 1 ) (870, 908)\n300 # RF (1086, 907)\n17  page 12 ) (1366, 906)\nE1 & E2 (191, 938)\nHP SEP . FLASH LIQ . INLET (430, 938)\n6 " (736, 938)\n( 2 ) (870, 940)\n600 # RF (1087, 938)\n( With internal (1256, 936)\nF1 & F2 (192, 969)\nHP SEP . FLASH VAP . INLET (434, 970)\n10 " (736, 968)\n( 2 ) (870, 970)\n600 # RF (1086, 968)\nsparger pipe ) (1254, 969)\nG1 & G2 (190, 999)\nDEETHANIZER FEED OUTLET (444, 1000)\n16 " (736, 1000)\n( 2 ) (870, 1002)\n600 # RF (1087, 1000)\n'

    Column Name Given:
   ["nozzle_number","subpart_name","connection_type","manifold_service","size","quantity","rating/facing"]
   "
}},
{{"role": "assistant", "content": ```csv
"nozzle_number","subpart_name","connection_type","manifold_service","size","quantity","rating/facing"
"A1","FEED_GAS","INLET","FEED GAS INLET","18","(2)","600 # RF"
"A2","FEED_GAS","INLET","FEED GAS INLET","18","(2)","600 # RF"
"B1","FEED_GAS","OUTLET","FEED GAS OUTLET","16","(2)","600 # RF"
"B2","FEED_GAS","OUTLET","FEED GAS OUTLET","16","(2)","600 # RF"
"C","RESIDUE_GAS","INLET","RESIDUE GAS OUTLET","36","(1)","300 # RF"
"D","RESIDUE_GAS","OUTLET","RESIDUE GAS OUTLET","36","(1)","300 # RF"
"E1","HP_SEP","INLET","HP SEP . FLASH LIQ . INLET","6","(2)","600 # RF"
"E2","HP_SEP","INLET","HP SEP . FLASH LIQ . INLET","6","(2)","600 # RF"
"F1","HP_SEP","INLET","HP SEP . FLASH VAP . INLET","10","(2)","600 # RF"
"F2","HP_SEP","INLET","HP SEP . FLASH VAP . INLET","10","(2)","600 # RF"
"G1","DEETHANIZER_FEED","OUTLET","DEETHANIZER FEED OUTLET","16","(2)","600 # RF"
"G2","DEETHANIZER_FEED","OUTLET","DEETHANIZER FEED OUTLET","16","(2)","600 # RF"```
}},
{{
    "role": "user", "content": TAG (517, 1172)\nNOZZLE SERVICE (725, 1172)\nSIZE (1070, 1172)\nRATING (1183, 1174)\nAl (526, 1196)\nDEBUTANIZER FEED LIQ . INLET (754, 1198)\n8 " (1083, 1196)\n300 # RFWN (1215, 1200)\nBJ (524, 1221)\nDEBUTANIZER FEED LIQ . OUTLET (765, 1223)\n8 " (1084, 1222)\n300 # RFWN (1214, 1224)\nDEBUTANIZER BTMS (700, 1246)\nC1 (522, 1246)\n. LIQ . INLET (865, 1247)\n300 # RFWN (1224, 1250)\nDI (522, 1270)\nDEBUTANIZER BTMS . LIQ . OUTLET (770, 1272)\n300 # RFWN (1224, 1274)\nFI (522, 1296)\nSHELL PSV (722, 1296)\n2 " (1080, 1296)\n300 # RFWN (1222, 1299)\nNI (522, 1320)\n..SHELL (694, 1322)\nDRAIN (774, 1322)\n2 " (1080, 1322)\n300 # RFWN (1221, 1325)\nV ] (522, 1346)\nSHELL VENT (734, 1346)\n2 " (1080, 1347)\n300 # RFWN (1224, 1350)\n

   Column Name Given:
   ["nozzle_number","subpart_name","connection_type"]
  }},
    {{"role": "assistant", "content": ```csv
"nozzle_number","subpart_name","connection_type"
"A1","DEBUTANIZER FEED","INLET"
"B1","DEBUTANIZER FEED","OUTLET"
"C1","DEBUTANIZER BTMS","INLET"
"D1","DEBUTANIZER BTMS","OUTLET"
"F1","SHELL_PSV","OUTLET"
"N1","SHELL_DRAIN","OUTLET"
"V","SHELL_VENT","OUTLET"```
}},
{{"role": "user", "content": "tell me the csv table of {data_sheet_text_string}. Having column name {columns_name_list}. Ignore {properties_name_list}"}}
{{"role": "assistant", "content":}}
]
