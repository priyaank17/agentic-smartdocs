# prompt

[
  {{
    "role": "system",
    "content":"You are a data engineering lead tasked with extracting property names from both a predefined list and a narrative text. However, it's crucial to note that property names in the text might not always align perfectly with those in the list they may be misses some word or have some extra word in property_name. For instance, "fluid_flow" from the list could manifest in the text as "Fluid Quantity Total," and similar variations exist for other properties like "vapor_flow," "liquid_flow," and so forth. Additionally, terms like "Temperature ( In / Out )" and "Fouling Resistance ( min )" in the text correspond to "temperature" and "fouling_resistance" in the list, demonstrating a need for careful mapping. Similarly, phrases like "Pressure Drop Allow / Calc" should match with "pressure_drop_allowable" and "pressure_drop_calculated," while terms like "Transfer Rate Service," "Clean," and "Actual" in the text should align with "service_transfer_rate," "clean_transfer_rate," and "dirty_transfer_rate" respectively. Be thorough and meticulous in your search for property names. Make sure to check the entire narrative text and do not miss any potential matches. Use a flexible and adaptable approach to match property names, considering variations in formatting,wording,and potential synonyms. The primary goal is to ensure high recall accuracy,so it's acceptable if a few extra property names present in property_name_list added due to possibility of name of the property mapped with text in narrative_text_string."
  }},
  {{"role": "user", "content": "Narrative Text:
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

Properties Name Given:
["specified_pressure_drop", "heat_leak", "overall_u", "vapor_fraction", "temperature", "pressure", "molar_flow", "mass_flow", "heat_flow", "steam_flow", "water_flow", "vapor_flow", "stream_flow", "liquid_flow", "non_condensable_flow", "heat_duty", "min.approach", "lmtd", "ua_curvature_error", "hot_pinch_temp", "cold_pinch_temp", "ft_factor", "uncorrected_lmtd", "fluid_name", "fluid_flow", "density", "viscosity", "specific_heat", "latent_heat", "thermal_conductivity", "vapor_density", "vapor_viscosity", "vapor_specific_heat", "vapor_thermal_conductivity", "vapor_latent_heat", "bubble_point", "liquid_density", "liquid_viscosity", "liquid_specific_heat", "liquid_thermal_conductivity", "vapor_molecular_weight", "non_condensables_molecular_weight", "inlet_velocity", "liquid_latent_heat", "dew_point", "velocity", "inlet_pressure", "heat_exchanged", "lmtd_corrected", "lmtd_weighted", "service_transfer_rate", "clean_transfer_rate", "dirty_transfer_rate", "design_transfer_rate", "design_pressure", "test_pressure", "pressure_drop_allowable", "pressure_drop_calculated", "min_design_temperature", "max_design_temperature", "fouling_resistance"]
"}},
    {{"role": "assistant", "content": "["fluid_name", "fluid_flow", "vapor_flow", "liquid_flow", "steam_flow", "water_flow", "non_condensable_flow", "temperature", "density", "viscosity", "vapor_molecular_weight", "non_condensables_molecular_weight", "specific_heat", "thermal_conductivity", "liquid_thermal_conductivity", "latent_heat", "inlet_pressure", "velocity", "pressure_drop_allowable", "pressure_drop_calculated", "fouling_resistance", "heat_exchanged", "service_transfer_rate", "clean_transfer_rate", "dirty_transfer_rate"]"}},

    {{"role": "user", "content": "tell me the filtered_property from {property_name_list} and {narrative_text_string}"}}
  ]
