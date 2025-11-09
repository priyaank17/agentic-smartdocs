# Prompt for Data Sheets table extraction

[
  {{
    "role": "system",
    "content":"You are a process engineering lead, your task is to extract table value from data_sheet_text in csv format. The format of each word is : word (x_coordinate, y_coordinate). **Use x and y coordinates to create a table.**
    Use the provided data_sheet_text, map the missing values for each property from the property_name_list and column name given. Do not add any new property_name. Do not add the units of the property.
  }},
  {{
    "role": "user",
    "content": "Narrative Text:
    CONSTRUCTION OF (817, 1186)
    27 (167, 1186)
    28 Description (219, 1219)
    Shell Side (622, 1216)
    Tube Side (821, 1216)
    Size  Rating & Type (1030, 1218)
    Shell Side (1238, 1218)
    Tube Side (1448, 1221)
    29 Design / Test Pressure : (260, 1248)
    PSIG (496, 1246)
    400 / BY CODE (622, 1247)
    450 / BY CODE (820, 1246)
    Inlet Connection (996, 1248)
    3 " -300 # RFWN (1238, 1248)
    8 " -3004 RFWN (1448, 1251)
    400/50 (622, 1275)
    Outlet (958, 1276)
    30 Design Temperature : (257, 1279)
    • F (508, 1276)
    400/50 (820, 1276)
    Connection (1028, 1276)
    3 *-300 # RFWN (1236, 1278)
    8 " -300 # RFWN (1448, 1281)
    31 Number of Passes Per Shell : (287, 1308)
    1 (620, 1306)
    2 (820, 1306)
    Intermediate Conn . (1006, 1307)
    1/8 " (819, 1335)
    32 Corrosion Allowance : (256, 1338)
    In (509, 1338)
    1/8 " (622, 1336)
    33 Number Tubes : 52 - U (265, 1368)
    00 : 1.00 In ; Thick : 0.083 ( min . ) In ; Length : 12 FT Pitch : 1.25 In : (718, 1370)
    Tube Pitch Orientation 30 (1194, 1370)

    Properties Name Given:
    ["exchanger_orientation", "design_pressure", "test_pressure","design_temperature", "test_temperature","number_of_passes_per_shell", "tube_type", "corrosion_allowance", "inlet_connection_size_rating_type", "outlet_connection_size_rating_type", "intermediate_connection_size_rating_type", "number_of_tubes", "tube_pitch", "tube_pitch_orientation", "tube_material", "tube_od", "shell_id", "tube_thickness", "tube_length", "shell_cover",]

    Column Name Given:
    ["property_name", "tube_side_inlet", "tube_side_outlet", "shell_side_inlet", "shell_side_outlet"]
    "}},
    {{"role": "assistant", "content": ```csv
    "property_name","tube_side_inlet","tube_side_outlet","shell_side_inlet","shell_side_outlet"
    "exchanger_orientation","","","",""
    "design_pressure","450","450","400","400"
    "test_pressure","BY CODE","BY CODE","BY CODE","BY CODE"
    "design_temperature","400/50","400/50","400/50","400/50"
    "test_temperature","","","",""
    "number_of_passes_per_shell","2","2","1","1"
    "corrosion_allowance","1/8","1/8","1/8","1/8"
    "inlet_connection_size_rating_type","3\"-300# RFWN","3\"-300# RFWN","8\"-300# RFWN","8\"-300# RFWN"
    "outlet_connection_size_rating_type","3\"-300# RFWN","3\"-300# RFWN","8\"-300# RFWN","8\"-300# RFWN"
    "intermediate_connection_size_rating_type","","","",""
    "number_of_tubes","52-U","52-U","",""
    "tube_od","1","1","",""
    "tube_thickness","0.083","0.083","",""
    "tube_length","12","12","",""
    "tube_pitch","1.25","1.25","",""
    "tube_pitch_orientation","30","30","",""
    "tube_type","Bare; Seamless","Bare; Seamless","",""
    "tube_material","SA 179","SA 179","",""
    "shell_id","","","","17 \" SA566-70"
    "shell_cover","","","","SA566-70"```
  }},
  {{
    "role": "user",
    "content": "Narrative Text:
    PERFORMANCE OF ONE UNIT (855, 323)
    5 Fluid Allocation : (182, 354)
    Inlet (588, 354)
    Shell Side (816, 356)
    Outlet Inlet (1068, 358)
    Tube Side (1344, 360)
    Outlet (1556, 363)
    6 Fluid Circulated : (183, 386)
    FEED SEPARATOR VAPOR (816, 388)
    DEETHANIZER TOP STAGE VAPOR (1333, 392)
    7 Total Fluid Flow Rate : (206, 418)
    Lb / Hr (526, 420)
    842273 ( NOTE A  1 ) (816, 424)
    387051 ( NOTE A  1 ) (1331, 426)
    8 (105, 452)
    Vapor . (174, 454)
    Lb (473, 452)
    MW (530, 453)
    842273 (652, 453)
    17.31 (781, 454)
    842273 (910, 455)
    17.31 (1039, 455)
    387051 (1169, 456)
    2352 (1298, 455)
    300084 (1410, 458)
    22 (1538, 458)
    HC (224, 483)
    9 (104, 484)
    Liquid : (173, 484)
    Lb MW (500, 485)
    86967 (1395, 492)
    31.1 (1524, 492)
    10 (98, 516)
    Steam : (174, 517)
    Lb (472, 517)
    11 (96, 550)
    Water : (170, 550)
    Lb (471, 551)
    12 (98, 583)
    Noncondensable : (216, 583)
    Lb (471, 584)
    MW (528, 583)
    13 Description (155, 618)
    : (226, 619)
    14 Operating Temperature : (208, 651)
    ° F (534, 648)
    -116 (749, 650)
    -75 (1006, 652)
    -33 (1264, 654)
    19 Latent Heat : (157, 812)
    BTU / Lb (513, 813)
    SEE HEAT RELEASE DATA (1288, 817)
    21 Velocity : (140, 879)
    Ft / Sec (516, 878)
    23.4 (809, 880)
    2.6 (1259, 882)
    ( NOTE 11 ) (1358, 884)
    22 Inlet Pressure : NOR / MAX (209, 910)
    ☐ PSIG ☑ PSIA (462, 910)
    200/320 (810, 910)
    200/320 (1324, 915)
    23 Pressure Drop : Allow./Calc .: (220, 944)
    PSI (528, 942)
    4.5 / 3.3 (814, 944)
    1 / 1.0 (1330, 948)

    Properties Name Given:
    ['inlet_name', 'inlet_tag', 'outlet_name', 'outlet_tag', 'overall_ua', 'ht_coeff', 'overall_u', 'fouling', 'heat_leak', 'heat_duty', 'vapour_fraction', 'temperature', 'pressure', 'specified_pressure_drop', 'molar_flowrate', 'mass_flowrate', 'heat_flow', 'fluid_flowrate', 'steam_flowrate', 'water_flowrate', 'vapour_flowrate', 'stream_flowrate', 'liquid_flowrate', 'non_condensable_flowrate', 'non_condensable_molecular_weight', 'water_molecular_weight', 'vapor_molecular_weight', 'min.approach', 'lmtd', 'ua_curvature_error', 'hot_pinch_temp', 'cold_pinch_temp', 'ft_factor', 'uncorrected_lmtd', 'fluid_name', 'density', 'viscosity', 'specific_heat_capacity', 'latent_heat', 'thermal_conductivity', 'vapour_density', 'vapour_viscosity', 'vapour_specific_heat_capacity', 'vapour_thermal_conductivity', 'vapour_latent_heat', 'bubble_point', 'liquid_density', 'liquid_viscosity', 'liquid_specific_heat_capacity', 'liquid_thermal_conductivity', 'liquid_latent_heat', 'liquid_surface_tension', 'liquid_molecular_weight', 'dew_point', 'water_density', 'water_viscosity', 'water_thermal_conductivity', 'velocity', 'minimum_velocity', 'maximum_velocity', 'inlet_pressure', 'inlet_pressure_maximum', 'heat_exchanged', 'lmtd_corrected', 'lmtd_weighted', 'heat_exchanged_mtd', 'service_transfer_rate', 'clean_transfer_rate', 'dirty_transfer_rate', 'design_transfer_rate', 'design_pressure', 'test_pressure', 'design_temperature', 'test_temperature', 'min_design_temperature', 'max_design_temperature', 'pressure_drop_allowed', 'pressure_drop_calculated', 'feed_name', 'feed_tag', 'discharge_name', 'discharge_tag', 'UA', 'heat_transfer_coefficient', 'u', 'fouling_resistance', 'heat_loss', 'duty', 'fraction', 'operating_temperature', 'pressure_normal', 'calculated_pressure_drop', 'molar_flow', 'mass_flow', 'heat_flow_total', 'fluid_flow', 'steam_flow', 'water_flow', 'vapour_flow', 'stream_flow', 'liquid_flow', 'non_condensable_flow', 'vapour_molecular_weight', 'minimum_approach', 'log_mean_temperature_difference', 'commodity_name', 'specific_heat', 'vapour_specific_heat', 'vapor_thermal_conductivity', 'liquid_specific_heat', 'mtd_corrected', 'actual_transfer_rate', 'transfer_rate_clean', 'transfer_rate_dirty', 'minimum_design_temperature', 'maximum_design_temperature', 'dp_allowed', 'dp_calculated', 'ht_coefficient', 'pressure_drop', 'molar_flow_total', 'mass_flow_total', 'fluid_flow_total', 'steam_flow_total', 'water_flow_total', 'vapour_flow_total', 'stream_flow_total', 'liquid_flow_total', 'non_condensable_flow_total', 'log_mean_temp_diff', 'fluid', 'vapor_specific_heat', 'transfer_rate_service', 'design_temperature_minimum', 'design_temperature_maximum', 'delta_pressure_allowed', 'delta_pressure_calculated', 'delta_p', 'molar_total_flowrate', 'mass_total_flowrate', 'heat_total_flowrate', 'fluid_total_flowrate', 'steam_total_flowrate', 'water_total_flowrate', 'vapour_total_flowrate', 'stream_total_flowrate', 'liquid_total_flowrate', 'non_condensable_total_flowrate', 'mtd', 'commodity', 'fluid_quantity_total', 'steam_quantity_total', 'fluid_circulated']

    Column Name Given:
    ["property_name", "tube_side_inlet", "tube_side_outlet", "shell_side_inlet", "shell_side_outlet"]
    "
  }},
  {{
    "role": "assistant",
    "content": ```csv
    "standard_property_name","shell_side_inlet","shell_side_outlet","tube_side_inlet","tube_side_outlet"
    "fluid_name","FEED SEPARATOR VAPOR","FEED SEPARATOR VAPOR","DEETHANIZER TOP STAGE VAPOR","DEETHANIZER TOP STAGE VAPOR"
    "fluid_flowrate","842273 (NOTE A 1)","842273 (NOTE A 1)","387051 ( NOTE A  1 )","387051 ( NOTE A  1 )"
    "vapor_flowrate","842273","842273","387051","300084"
    "vapor_molecular_weight","17.31","17.31","23.52","22"
    "liquid_flowrate","","","","86967"
    "liquid_molecular_weight","","","","31.1"
    "steam_flowrate","","","",""
    "water_flowrate","","","",""
    "non_condensable_flowrate","","","",""
    "temperature","-116","-75","-33","-75"
    "non_condensables_molecular_weight","","","",""
    "latent_heat","","","SEE HEAT RELEASE DATA","SEE HEAT RELEASE DATA"
    "inlet_pressure_normal","200","200","200","200"
    "inlet_pressure_maximum","320","320","320","320"
    "velocity","23.4","23.4","2.6","2.6"
    "pressure_drop_allowed","4.5","4.5","1","1"
    "pressure_drop_calculated","3.3","3.3","1","1"```
  }},
  {{
    "role": "user",
    "content": "Narrative Text:
    Inlet (588, 354)
    Shell Side (816, 356)
    Outlet Inlet (1068, 358)
    Tube Side (1344, 360)
    Outlet Inlet(1556, 363)
    24 Fouling Resistance : (186, 976)
    Hr FP ° F / BTU (456, 975)
    0.001 (814, 976)
    0.001 (1330, 980)
    25 Heat Exchanged : (176, 1009)
    18.66 MMBTU / Hr (450, 1009)
    26 Transfer Rate  Service : 23 BTU / Hr Sq Ft* F (312, 1042)
    Clean : 35 BTU / Hr Sq Ft ° F (1000, 1044)

    Properties Name Given:
    ['fouling', 'heat_exchanged', 'lmtd_corrected', 'lmtd_weighted', 'heat_exchanged_mtd', 'service_transfer_rate', 'clean_transfer_rate', 'dirty_transfer_rate', 'design_transfer_rate', 'design_pressure', 'test_pressure', 'design_temperature', 'test_temperature', 'min_design_temperature', 'max_design_temperature', 'pressure_drop_allowed', 'pressure_drop_calculated', 'feed_name', 'feed_tag', 'discharge_name', 'discharge_tag', 'UA', 'heat_transfer_coefficient', 'u', 'fouling_resistance', 'heat_loss', 'duty']

    Column Name Given:
    ["property_name", "tube_side_inlet", "tube_side_outlet", "shell_side_inlet", "shell_side_outlet"]
    "
  }},
  {{
    "role": "assistant",
    "content": ```csv
    "standard_property_name","shell_side_inlet","shell_side_outlet","tube_side_inlet","tube_side_outlet"
    "fouling_resistance","0.001","0.001","0.001","0.001"
    "heat_exchanged","18.86","18.86","18.86","18.86"
    "service_transfer_rate","23","23","23","23"
    "clean_transfer_rate","35","35","35","35"```
  }},
  {{"role": "user", "content": "tell me the csv table of {data_sheet_text_string}. Having column name {columns_name_list} and property name {properties_name_list}."}}
  {{"role": "assistant", "content":}}
]
