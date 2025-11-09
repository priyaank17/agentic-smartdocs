# prompt to map standard property name with possible property name

[
  {{
    "role" : "system",
    "content" :"Act as a data engineering lead, your task is to map the narrative text with possible property names given in standard property list. The mapping should be one to one mapping only."
  }},
  {{
    "role" : "user",
    "content" : "Narrative Text:
    PERFORMANCE OF ONE UNIT
    Fluid Allocation
    Shell Side
    Tube Side
    Fluid Name
    Cooling Medium
    Gas
    Fluid Quantity  Total
    lb / hr
    Vapor .
    Lb
    MW
    Liquid :
    Lb MW
    Steam
    Water
    Noncondensables
    Temperature ( In / Out )
    F
    Density
    (L / V)
    lb / ft3
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
    Bubble Point / Dew Point
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
    ["specified_pressure_drop", "heat_leak", "overall_u", "vapor_fraction", "temperature", "pressure", "molar_flow", "mass_flow", "heat_flow", "steam_flow", "water_flow", "vapor_flow", "stream_flow", "liquid_flow", "non_condensable_flow", "heat_duty", "min.approach", "lmtd", "ua_curvature_error", "hot_pinch_temp", "cold_pinch_temp", "ft_factor", "uncorrected_lmtd", "fluid_name", "fluid_flow", "density", "viscosity", "specific_heat", "latent_heat", "thermal_conductivity", "vapor_density", "vapor_viscosity", "vapor_specific_heat", "vapor_thermal_conductivity", "vapor_latent_heat", "bubble_point", "liquid_density", "liquid_viscosity", "liquid_specific_heat", "liquid_thermal_conductivity", "vapor_molecular_weight", "non_condensables_molecular_weight", "inlet_velocity", "liquid_latent_heat", "dew_point", "velocity", "inlet_pressure", "heat_exchanged", "lmtd_corrected", "lmtd_weighted", "service_transfer_rate", "clean_transfer_rate", "actual_transfer_rate", "design_transfer_rate", "design_pressure", "test_pressure", "pressure_drop_allowable", "pressure_drop_calculated", "min_design_temperature", "max_design_temperature", "fouling_resistance"]
    "
  }},
  {{
    "role": "assistant", "content": ```{{"Fluid Name": "fluid_name", "Fluid Quantity Total": "fluid_flow", "Vapor Lb MW": ["vapor_flow", "vapor_molecular_weight"], "Liquid : Lb MW": ["liquid_flow", "liquid_molecular_weight"], "Steam": "steam_flow", "Water": "water_flow", "Noncondensables": "non_condensable_flow", "Temperature ( In / Out )": "temperature", "Density (L / V)": ["liquid_density", "vapor_density"], "Molecular Weight  Noncondensables": "non_condensables_molecular_weight", "Heat  Specific": "specific_heat", "Thermal Conductivity": "thermal_conductivity", "Latent Heat": "latent_heat", "Inlet Pressure": "inlet_pressure", "Bubble Point / Dew Point": ["bubble_point", "dew_point"], "Velocity": "velocity", "Pressure Drop  Allow / Calc": ["pressure_drop_allowable", "pressure_drop_calculated"], "Fouling Resistance ( min )": "fouling_resistance", "Heat Exchanged": "heat_exchanged", "Transfer Rate  Service": "service_transfer_rate", "Clean": "clean_transfer_rate", "Actual": "actual_transfer_rate"}}```
  }},
  {{
    "role": "user",
    content: "Narrative Text:
    Performance Case Number 2 :
    " Early Case "
    Heat Exchanger Section :
    Section " A "
    Section " B "
    Section " C "
    Fluid Name :
    Residue Gas
    Feed Gas
    HP Separator Flash
    Vessel Liq / Vap
    Flammable / Explosive :
    Yes / Yes
    Yes / Yes
    Yes / Yes
    Corrosive / Erosive Due to :
    Yes / No
    Yes / No
    Yes / No
    Heat duty :
    ( Notes 2 & 3 P11 )
    mmBtu / hr
    Total Fluid Flow :
    lb / hr
    Total Vapor Flow :
    IN / OUT
    lb / hr
    Total Liquid Flow :
    IN / OUT
    lb / hr
    Total Non - condensable :
    IN / OUT
    lb / hr
    Fluid Condensed Vaporized
    /
    :
    lb / hr
    0 / 0
    /
    -
    lb / ft³

    Properties Name Given:
    ["fluid_name", "flammable", "explosive", "corrosive", "erosive", "heat_duty", "mass_flowrate", "vapor_flowrate", "liquid_flowrate", "non_condensable_flowrate", "fluid_condensed", "fluid_vaporized", "viscosity", "vapour_viscosity", "liquid_viscosity", "density", "vapour_density", "liquid_density", "specific_heat_capacity", "vapour_specific_heat_capacity", "liquid_specific_heat_capacity", "conductivity", "liquid_conductivity", "liquid_thermal_conductivity", "vapour_conductivity", "vapour_thermal_conductivity", "molecular_weight", "liquid_molecular_weight", "vapour_molecular_weight", "latent_heat", "coeff_of_vol_expansion(liq)", "surface_tension", "liquid_surface_tension", "temperature", "bubble_point", "dew_point", "normal_inlet_pressure", "maximum_inlet_pressure", "pressure_drop_allowed", "pressure_drop_calculated", "maximum_allowable_pressure_drop", "maximum_calculated_pressure_drop", "friction_pressure_drop_calculated", "maximum_velocity", "minimum_velocity", "fouling", "maximum_design_pressure", "minimum_design_pressure", "maximum_design_temperature", "minimum_design_temperature", "heat_transfered", "fluid_description", "total_fluid_flow", "total_vapor_flowrate", "total_liquid_flowrate", "total_non_condensable_flowrate", "vapor_viscosity", "vapor_density", "specific_heat", "vapour_specific_heat", "liquid_specific_heat", "vapor_conductivity", "vapor_thermal_conductivity", "vapor_molecular_weight", "coefficient_of_volume_expansion", "dp_allowed", "dp_calculated", "maximum_pressure_drop_allowed", "maximum_pressure_drop_calculated", "friction_dp_calculated", "fouling_resistance", "total_fluid", "vapour_flow", "liquid_flow", "non_condensable_flow", "vapor_specific_heat", "delta_pressure_allowed", "delta_pressure_calculated", "maximum_dp_allowed", "maximum_dp_calculate", "friction_delta_pressure_calculated", "total_fluid_entering", "vapour_flow_total", "liquid_flow_total", "non_condensable_flow_total", "vapor_specific_heat_capacity", "allowable_pressure_drop", "maximum_delta_pressure_allowed", "maximum_delta_pressure_calculate", "fluid_quantity_total", "vapour_total_flowrate", "liquid_total_flowrate", "non_condensable_total_flowrate", "vapor_quantity_total", "liquid_quantity_total", "non_condensables_total"]
    "
  }},
  {{"role": "assistant", "content": ```{{"Fluid Name": "fluid_name", "Flammable / Explosive ": ["flammable", "explosive"], "Corrosive / Erosive" : ["corrosive", "erosive"], "Heat duty": "heat_duty", "Total Fluid Flow": "total_fluid_flow", "Total Vapor Flow": "total_vapor_flowrate", "Total Liquid Flow": "total_liquid_flowrate", "Total Non - condensable": "total_non_condensable_flowrate", "Fluid Condensed Vaporized": ["fluid_condensed", "fluid_vaporized"]```}},
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
    ["fluid_name", "flammable", "explosive", "corrosive", "erosive", "heat_duty", "mass_flowrate", "vapor_flowrate", "liquid_flowrate", "non_condensable_flowrate", "fluid_condensed", "fluid_vaporized", "viscosity", "vapour_viscosity", "liquid_viscosity", "density", "vapour_density", "liquid_density", "specific_heat_capacity", "vapour_specific_heat_capacity", "liquid_specific_heat_capacity", "conductivity", "liquid_conductivity", "liquid_thermal_conductivity", "vapour_conductivity", "vapour_thermal_conductivity", "molecular_weight", "liquid_molecular_weight", "vapour_molecular_weight", "latent_heat", "coeff_of_vol_expansion(liq)", "surface_tension", "liquid_surface_tension", "temperature", "bubble_point", "dew_point", "normal_inlet_pressure", "maximum_inlet_pressure", "pressure_drop_allowed", "pressure_drop_calculated", "maximum_allowable_pressure_drop", "maximum_calculated_pressure_drop", "friction_pressure_drop_calculated", "maximum_velocity", "minimum_velocity", "fouling", "maximum_design_pressure", "minimum_design_pressure", "maximum_design_temperature", "minimum_design_temperature", "heat_transfered", "fluid_description", "total_fluid_flow", "total_vapor_flowrate", "total_liquid_flowrate", "total_non_condensable_flowrate", "vapor_viscosity", "vapor_density", "specific_heat", "vapour_specific_heat", "liquid_specific_heat", "vapor_conductivity", "vapor_thermal_conductivity", "vapor_molecular_weight", "coefficient_of_volume_expansion", "dp_allowed", "dp_calculated", "maximum_pressure_drop_allowed", "maximum_pressure_drop_calculated", "friction_dp_calculated", "fouling_resistance", "total_fluid", "vapour_flow", "liquid_flow", "non_condensable_flow", "vapor_specific_heat", "delta_pressure_allowed", "delta_pressure_calculated", "maximum_dp_allowed", "maximum_dp_calculate", "friction_delta_pressure_calculated", "total_fluid_entering", "vapour_flow_total", "liquid_flow_total", "non_condensable_flow_total", "vapor_specific_heat_capacity", "allowable_pressure_drop", "maximum_delta_pressure_allowed", "maximum_delta_pressure_calculate", "fluid_quantity_total", "vapour_total_flowrate", "liquid_total_flowrate", "non_condensable_total_flowrate", "vapor_quantity_total", "liquid_quantity_total", "non_condensables_total"]
    "
  }},
  {{"role": "assistant", "content": ```{{"Density : \n IN ( L / V ) / OUT ( L / V )": ["liquid_density", "vapour_density"], "Viscosity : IN ( L / V ) / OUT ( L / V )": ["liquid_viscosity", "vapour_viscosity"], "Molecular Weight : IN ( L / V ) / OUT ( LN )": ["liquid_molecular_weight", "vapour_molecular_weight"], "Specific Heat : IN ( L / V ) / OUT ( L / V )": ["liquid_specific_heat", "vapour_specific_heat"]", "Conductivity : IN ( L / V ) / OUT ( L / V ": ["liquid_conductivity", "vapour_conductivity"]}}```}},
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
    ["fluid_name", "flammable", "explosive", "corrosive", "erosive", "heat_duty", "mass_flowrate", "vapor_flowrate", "liquid_flowrate", "non_condensable_flowrate", "fluid_condensed", "fluid_vaporized", "viscosity", "vapour_viscosity", "liquid_viscosity", "density", "vapour_density", "liquid_density", "specific_heat_capacity", "vapour_specific_heat_capacity", "liquid_specific_heat_capacity", "conductivity", "liquid_conductivity", "liquid_thermal_conductivity", "vapour_conductivity", "vapour_thermal_conductivity", "molecular_weight", "liquid_molecular_weight", "vapour_molecular_weight", "latent_heat", "coeff_of_vol_expansion(liq)", "surface_tension", "liquid_surface_tension", "temperature", "bubble_point", "dew_point", "normal_inlet_pressure", "maximum_inlet_pressure", "pressure_drop_allowed", "pressure_drop_calculated", "maximum_allowable_pressure_drop", "maximum_calculated_pressure_drop", "friction_pressure_drop_calculated", "maximum_velocity", "minimum_velocity", "fouling", "maximum_design_pressure", "minimum_design_pressure", "maximum_design_temperature", "minimum_design_temperature", "heat_transfered", "fluid_description", "total_fluid_flow", "total_vapor_flowrate", "total_liquid_flowrate", "total_non_condensable_flowrate", "vapor_viscosity", "vapor_density", "specific_heat", "vapour_specific_heat", "liquid_specific_heat", "vapor_conductivity", "vapor_thermal_conductivity", "vapor_molecular_weight", "coefficient_of_volume_expansion", "dp_allowed", "dp_calculated", "maximum_pressure_drop_allowed", "maximum_pressure_drop_calculated", "friction_dp_calculated", "fouling_resistance", "total_fluid", "vapour_flow", "liquid_flow", "non_condensable_flow", "vapor_specific_heat", "delta_pressure_allowed", "delta_pressure_calculated", "maximum_dp_allowed", "maximum_dp_calculate", "friction_delta_pressure_calculated", "total_fluid_entering", "vapour_flow_total", "liquid_flow_total", "non_condensable_flow_total", "vapor_specific_heat_capacity", "allowable_pressure_drop", "maximum_delta_pressure_allowed", "maximum_delta_pressure_calculate", "fluid_quantity_total", "vapour_total_flowrate", "liquid_total_flowrate", "non_condensable_total_flowrate", "vapor_quantity_total", "liquid_quantity_total", "non_condensables_total"]
    "
  }},
  {{"role": "assistant", "content": ```{{"Latent Heat": "latent_heat", "Coeff . Of Vol . Expansion ( Liq . )" : "coefficient_of_volume_expansion", "Surface Tension ( Liq . )": "liquid_surface_tension", "Temperature": "temperature", "Bubble Point / Dew Point": ["bubble_point", "dew_point"], "Inlet Pressure": "inlet_pressure", "Maximum Allowable AP / Calc . AP": ["maximum_pressure_drop_allowed", "maximum_calculated_pressure_drop"], "Maximum Velocity": "maximum_velocity", "Minimum Velocity": "minimum_velocity", "Fouling Resistance": "fouling"}}```}},
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
    ["fouling", "heat_leak", "heat_duty", "vapour_fraction", "temperature", "pressure", "specified_pressure_drop", "molar_flowrate", "mass_flowrate", "heat_flow", "fluid_flowrate", "steam_flowrate", "water_flowrate", "vapour_flowrate", "stream_flowrate", "liquid_flowrate", "non_condensable_flowrate", "non_condensable_molecular_weight", "water_molecular_weight", "vapor_molecular_weight", "min.approach", "lmtd", "ua_curvature_error", "hot_pinch_temp", "cold_pinch_temp", "ft_factor", "uncorrected_lmtd", "fluid_name", "density", "viscosity", "specific_heat_capacity", "latent_heat", "thermal_conductivity", "vapour_density", "vapour_viscosity", "vapour_specific_heat_capacity", "vapour_thermal_conductivity", "vapour_latent_heat", "bubble_point", "liquid_density", "liquid_viscosity", "liquid_specific_heat_capacity", "liquid_thermal_conductivity", "liquid_latent_heat", "liquid_surface_tension", "liquid_molecular_weight", "dew_point", "water_density", "water_viscosity", "water_thermal_conductivity", "velocity", "minimum_velocity", "maximum_velocity", "inlet_pressure", "inlet_pressure_maximum", "heat_exchanged", "lmtd_corrected", "lmtd_weighted", "heat_exchanged_mtd", "service_transfer_rate", "clean_transfer_rate", "dirty_transfer_rate", "design_transfer_rate", "design_pressure", "test_pressure", "design_temperature", "test_temperature", "min_design_temperature", "max_design_temperature", "pressure_drop_allowed", "pressure_drop_calculated", "feed_name", "feed_tag", "discharge_name", "discharge_tag", "UA", "heat_transfer_coefficient", "u", "fouling_resistance", "heat_loss", "duty", "fraction", "operating_temperature", "pressure_normal", "calculated_pressure_drop", "molar_flow", "mass_flow", "heat_flow_total", "fluid_flow", "steam_flow", "water_flow", "vapor_flow"", "vapour_flow", "stream_flow", "liquid_flow", "non_condensable_flow", "vapour_molecular_weight", "minimum_approach", "log_mean_temperature_difference", "commodity_name", "specific_heat", "vapour_specific_heat", "vapor_thermal_conductivity", "liquid_specific_heat", "mtd_corrected", "actual_transfer_rate", "transfer_rate_clean", "transfer_rate_dirty", "minimum_design_temperature", "maximum_design_temperature", "dp_allowed", "dp_calculated", "ht_coefficient", "pressure_drop", "molar_flow_total", "mass_flow_total", "fluid_flow_total", "steam_flow_total", "water_flow_total", "vapour_flow_total", "stream_flow_total", "liquid_flow_total", "non_condensable_flow_total", "log_mean_temp_diff", "fluid", "vapor_specific_heat", "transfer_rate_service", "design_temperature_minimum", "design_temperature_maximum", "delta_pressure_allowed", "delta_pressure_calculated", "delta_p", "molar_total_flowrate", "mass_total_flowrate", "heat_total_flowrate", "fluid_total_flowrate", "steam_total_flowrate", "water_total_flowrate", "vapour_total_flowrate", "stream_total_flowrate", "liquid_total_flowrate", "non_condensable_total_flowrate", "mtd", "commodity", "fluid_quantity_total", "steam_quantity_total", "fluid_circulated"]
    "
  }},
  {{
    "role": "assistant", "content": ```{{"Vapor Lb MW": ["vapour_flow_total", "vapour_molecular_weight"], "Liquid : Lb MW": ["liquid_flow_total", "liquid_molecular_weight"], "Steam": "steam_flow_total", "Water": "water_flow_total", "Noncondensable": "non_condensable_flow_total", "Operating Temperature": "operating_temperature", "Pressure Drop : Allow./Calc .": ["pressure_drop_allowed", "pressure_drop_calculated"], "Fouling Resistance": "fouling_resistance", "Heat Exchanged": "heat_exchanged"}}```
  }},
  {{"role": "user", "content": "give the mapped {narrative_text_string} present in {property_name_list}."}}
  {{"role": "assistant", "content":}}
]
