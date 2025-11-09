# prompt to map standard property name with possible property name

[
  {{
    "role" : "system",
    "content" :"Act as a data engineering lead, your task is to map the narrative text with possible property names given in standard property list. The mapping should be one to one mapping only."
  }},
  {{
    "role": "user",
    content: "Narrative Text:
    Performance Case Number 2 :
    Heat Exchanger Section :
    Section " A "
    Section " B "
    Section " C "
    Density :
    IN ( L / V ) / OUT ( L / V )
    - / 0.97
    - / 0.68
    - / 5.00
    25.96 / 6.24
    36.421.03 35.47 / 1.06
    Viscosity :
    IN ( L / V ) / OUT ( L / V )
    cP
    - / 0.01
    - / 0.01
    - / 0.01
    0.07 / 0.01
    0.2 / 0.01
    0.17 / 0.01
    Molecular Weight : IN ( L / V ) / OUT ( LN )
    - / 18.33
    - / 18.33
    - / 21.23
    30.41 / 19.08
    41.19 / 18.50 51.91 / 25.20
    Specific Heat :
    IN ( L / V ) / OUT ( L / V )
    Btu / lb ° F
    - / 0.51
    - / 0.51
    - / 0.69
    0.73 / 0.92
    0.52 0.51
    0.56 / 0.47
    Conductivity :
    IN ( L / V ) / OUT ( L / V ) Btu / ( hr ) ( ft² ) ( ° F / ft )

    Properties Name Given:
    ["fluid_name", "flammable", "explosive", "corrosive", "erosive", "heat_duty", "mass_flowrate", "vapor_flowrate", "liquid_flowrate", "non_condensable_flowrate", "fluid_condensed", "fluid_vaporized", "viscosity", "vapour_viscosity", "liquid_viscosity", "density", "vapour_density", "liquid_density", "specific_heat_capacity", "vapour_specific_heat_capacity", "liquid_specific_heat_capacity", "conductivity", "liquid_conductivity", "liquid_thermal_conductivity", "vapour_conductivity", "vapour_thermal_conductivity", "molecular_weight", "liquid_molecular_weight", "vapour_molecular_weight", "latent_heat", "coeff_of_vol_expansion(liq)", "surface_tension", "liquid_surface_tension", "temperature", "bubble_point", "dew_point", "normal_inlet_pressure", "minimum_velocity", "fouling", "maximum_design_pressure", "minimum_design_pressure", "maximum_design_temperature", "minimum_design_temperature", "heat_transfered", "fluid_description", "total_fluid_flow", "total_vapor_flowrate", "total_liquid_flowrate", "total_non_condensable_flowrate", "vapor_viscosity", "vapor_density", "specific_heat", "vapour_specific_heat", "liquid_specific_heat"]
    "
  }},
  {{"role": "assistant", "content": ```json{{"Density : \n IN ( L / V ) / OUT ( L / V )": ["liquid_density", "vapour_density"], "Viscosity : IN ( L / V ) / OUT ( L / V )": ["liquid_viscosity", "vapour_viscosity"], "Molecular Weight : IN ( L / V ) / OUT ( LN )": ["liquid_molecular_weight", "vapour_molecular_weight"], "Specific Heat : IN ( L / V ) / OUT ( L / V )": ["liquid_specific_heat", "vapour_specific_heat"]", "Conductivity : IN ( L / V ) / OUT ( L / V ": ["liquid_conductivity", "vapour_conductivity"]}}```}},
   {{
    "role": "user",
    content: "Narrative Text:
    Performance Case Number 2 :
    Heat Exchanger Section :
    Section " A "
    Section " B "
    Section " C "
    Latent Heat :
    Btu / lb
    Coeff . Of Vol . Expansion ( Liq . ) :
    Surface Tension ( Liq . ) :
    IN / OUT
    dynes / cm
    Temperature :
    IN / OUT
    ° F / ° F
    Bubble Point / Dew Point :
    Inlet Pressure :
    NORM / MAX
    psig / psig
    Maximum Allowable AP / Calc . AP
    psi / psi
    10 / later
    10 / later
    10 / later
    Maximum Velocity :
    ft / sec
    60 ( Vap )
    15 ( Liq ) / 60 ( Vap ) Note 6
    15 ( Liq ) / 60 ( Vap ) Note 6
    Minimum Velocity :
    ft / sec
    3 ( Liq ) 7 ( Liq + Vap ) Note 6
    3 ( Liq ) 7 ( Liq + Vap ) Note 6
    Fouling Resistance :
    hrft² ° F / Btu

    Properties Name Given:
    ["latent_heat", "inlet_pressure", "coeff_of_vol_expansion(liq)", "surface_tension", "liquid_surface_tension", "temperature", "bubble_point", "dew_point", "normal_inlet_pressure", "maximum_inlet_pressure", "pressure_drop_allowed", "pressure_drop_calculated", "maximum_allowable_pressure_drop", "maximum_calculated_pressure_drop", "friction_pressure_drop_calculated", "maximum_velocity", "minimum_velocity", "fouling", "maximum_design_pressure", "minimum_design_pressure", "maximum_design_temperature", "minimum_design_temperature", "heat_transfered", "fluid_description", "total_fluid_flow", "total_vapor_flowrate", "total_liquid_flowrate", "total_non_condensable_flowrate", "vapor_viscosity", "vapor_density", "specific_heat", "vapour_specific_heat", "liquid_specific_heat", "vapor_conductivity", "vapor_thermal_conductivity", "vapor_molecular_weight", "coefficient_of_volume_expansion", "dp_allowed", "dp_calculated", "maximum_pressure_drop_allowed", "maximum_pressure_drop_calculated", "friction_dp_calculated", "fouling_resistance", "total_fluid", "vapour_flow", "liquid_flow", "non_condensable_flow", "vapor_specific_heat", "delta_pressure_allowed", "delta_pressure_calculated"]
    "
  }},
  {{"role": "assistant", "content": ```json{{"Latent Heat": "latent_heat", "Coeff . Of Vol . Expansion ( Liq . )" : "coefficient_of_volume_expansion", "Surface Tension ( Liq . )": "liquid_surface_tension", "Temperature": "temperature", "Bubble Point / Dew Point": ["bubble_point", "dew_point"], "Inlet Pressure": "inlet_pressure", "Maximum Allowable AP / Calc . AP": ["maximum_pressure_drop_allowed", "maximum_calculated_pressure_drop"], "Maximum Velocity": "maximum_velocity", "Minimum Velocity": "minimum_velocity", "Fouling Resistance": "fouling"}}```}},
  {{
    "role" : "user",
    "content" : "Narrative Text:
    Inlet
    Shell Side
    Outlet Inlet
    Tube Side
    Outlet
    Vapor .
    Lb
    MW
    HC
    Liquid :
    Lb MW
    Steam :
    Lb
    Water :
    Lb
    Noncondensable :
    Lb
    MW
    :
    14 Operating Temperature :
    ° F
    23 Pressure Drop : Allow./Calc .:
    PSI
    4.5 / 3.3
    1 / 1.0
    24 Fouling Resistance :
    Hr FP ° F / BTU
    25 Heat Exchanged :

    Properties Name Given:
    ["liquid_viscosity", "liquid_specific_heat_capacity", "liquid_thermal_conductivity", "liquid_latent_heat", "liquid_surface_tension", "liquid_molecular_weight", "dew_point", "water_density", "water_viscosity", "water_thermal_conductivity", "velocity", "minimum_velocity", "maximum_velocity", "inlet_pressure", "inlet_pressure_maximum", "heat_exchanged", "lmtd_corrected", "lmtd_weighted", "heat_exchanged_mtd", "service_transfer_rate", "clean_transfer_rate", "dirty_transfer_rate", "design_transfer_rate", "design_pressure", "test_pressure", "design_temperature", "test_temperature", "min_design_temperature", "max_design_temperature", "pressure_drop_allowed", "pressure_drop_calculated", "feed_name", "feed_tag", "discharge_name", "discharge_tag", "UA", "heat_transfer_coefficient", "u", "fouling_resistance", "heat_loss", "duty", "fraction", "operating_temperature", "mass_flow_total", "fluid_flow_total", "steam_flow_total", "water_flow_total", "vapour_flow_total", "stream_flow_total", "liquid_flow_total", "non_condensable_flow_total", "log_mean_temp_diff", "fluid", "vapor_specific_heat", "transfer_rate_service", "vapour_molecular_weight", "design_temperature_minimum", "design_temperature_maximum", "delta_pressure_allowed", "delta_pressure_calculated"]
    "
  }},
  {{
    "role": "assistant", "content": ```json{{"Vapor Lb MW": ["vapour_flow_total", "vapour_molecular_weight"], "Liquid : Lb MW": ["liquid_flow_total", "liquid_molecular_weight"], "Steam": "steam_flow_total", "Water": "water_flow_total", "Noncondensable": "non_condensable_flow_total", "Operating Temperature": "operating_temperature", "Pressure Drop : Allow./Calc .": ["pressure_drop_allowed", "pressure_drop_calculated"], "Fouling Resistance": "fouling_resistance", "Heat Exchanged": "heat_exchanged"}}```
  }},
  {{"role": "user", "content": "give the mapped {narrative_text_string} present in {property_name_list}."}}
  {{"role": "assistant", "content":}}
]
