# Prompt for extracting Property Names from Narrative Text for Data Sheets

Your task is to identify and extract property names from a given narrative text. The property names to look for will be provided in a list. The primary goal is to ensure high recall accuracy, meaning that we aim to identify as many relevant property names as possible from the narrative text. It's acceptable if a few extra property names are extracted due to this approach, but we want to minimize the chances of missing any potential property names.

## For example

### Input Data

#### Narrative Text Given

PERFORMANCE OF ONE UNIT
Fluid Allocation
Shell Side
Tube Side
Fluid Name
Cooling Medium
Gas
Fluid Quantity  Total
lb / hr
Vapor ( In / Out )
Liquid
Steam
Water
Noncondensables
Temperature ( In / Out )
F
Density
lb / ft3
Viscosity
cP
Molecular Weight  Vapor
Molecular Weight  Noncondensables
Heat
Specific
Btu / lb - F
Thermal Conductivity
Btu / hr - ft - F
Latent Heat
Btu / lb
Inlet Pressure
psia
Velocity
ft / sec
Pressure Drop  Allow / Calc
psi
Fouling Resistance ( min )
ft2 - hr - F / Btu
Heat Exchanged Btu / hr
MTD ( Corrected )
31.6 F
Transfer Rate  Service
126.58 Btu / ft2 - hr - F
Clean
156.35 Btu / ft2 - hr - F
Actual
156.35 Btu / ft2 - hr - F

#### Property Name Given

["specified_pressure_drop", "heat_leak", "overall_u", "vapor_fraction", "temperature", "pressure", "molar_flow", "mass_flow", "heat_flow", "steam_flow", "water_flow", "vapor_flow", "stream_flow", "liquid_flow", "non_condensable_flow", "heat_duty", "min.approach", "lmtd", "ua_curvature_error", "hot_pinch_temp", "cold_pinch_temp", "ft_factor", "uncorrected_lmtd", "fluid_name", "fluid_flow", "density", "viscosity", "specific_heat", "latent_heat", "thermal_conductivity", "vapor_density", "vapor_viscosity", "vapor_specific_heat", "vapor_thermal_conductivity", "vapor_latent_heat", "bubble_point", "liquid_density", "liquid_viscosity", "liquid_specific_heat", "liquid_thermal_conductivity", "vapor_molecular_weight", "non_condensables_molecular_weight", "inlet_velocity", "liquid_latent_heat", "dew_point", "velocity", "inlet_pressure", "heat_exchanged", "lmtd_corrected", "lmtd_weighted", "service_transfer_rate", "clean_transfer_rate", "dirty_transfer_rate", "design_transfer_rate", "design_pressure", "test_pressure", "pressure_drop_allowable", "pressure_drop_calculated", "min_design_temperature", "max_design_temperature", "fouling_resistance"]

### Expected Output

["fluid_name", "fluid_flow", "vapor_flow", "liquid_flow", "steam_flow", "water_flow", "non_condensable_flow", "temperature", "density", "viscosity", "vapor_molecular_weight", "non_condensables_molecular_weight", "specific_heat", "thermal_conductivity", "liquid_thermal_conductivity", "latent_heat", "inlet_pressure", "velocity", "pressure_drop_allowable", "pressure_drop_calculated", "fouling_resistance", "heat_exchanged", "service_transfer_rate", "clean_transfer_rate", "dirty_transfer_rate"]

### Explanation

The task involves scanning the narrative text and identifying any terms that match or closely resemble the property names provided in the list.
For Example,
-**"fluid_flow", "vapor_flow", "liquid_flow", "steam_flow", "water_flow", "non_condensable_flow" match with "Fluid Quantity  Total", "Vapor ( In / Out )", "Liquid", "Steam", "Water", "Noncondensables" respectively.**
-**"Temperature ( In / Out )"  and "Fouling Resistance ( min )" in the text corresponds to "temperature"" and "fouling_resistance" in the list.**
-**"Pressure Drop  Allow / Calc" match with "pressure_drop_allowable", "pressure_drop_calculated".**
-**"Transfer Rate  Service", "Clean", "Actual" match with "service_transfer_rate", "clean_transfer_rate", "dirty_transfer_rate".**

Note: Our approach ensures all relevant specifications are captured, adapting to variations in formatting or wording

## Instructions

Given a narrative text string {narrative_text_string} and property names {property_name_list}, your task is to identify and return list of all the property names mentioned in the narrative text string.
Please go though the example and explanation and give the result accordingly.
When identifying property names in the narrative text, consider the following:

- Property names may not always appear in the narrative text exactly as they are in the property name list. They may be worded slightly differently or formatted in a different way. For example, a property name in the list might be "fluid_flow", but in the narrative text, it might appear as "Fluid Quantity Total".
- Be thorough and meticulous in your search for property names. Make sure to check the entire narrative text and do not miss any potential matches.
- Use a flexible and adaptable approach to match property names, considering variations in formatting, wording, and potential synonyms.

## Note

- Provide a list of property names mentioned in the narrative text string given in property_name_list.
- You should double-check that the property name list accurately reflects all possible property names that could appear in the narrative text from the property_name_list.
- Check the property name properly. Please do not miss any property name.
- **The primary goal is to ensure high recall accuracy, so it's acceptable if a few extra property names present in property_name_list also added due to this approach.**
- Only property_name should be given in the output list.
