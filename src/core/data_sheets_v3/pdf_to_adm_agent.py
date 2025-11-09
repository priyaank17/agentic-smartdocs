"""
Example: extract key metadata from a pump datasheet PDF
using Landing-AI's agentic-doc SDK and Pydantic models.
"""

from __future__ import annotations

# models/heat_exchanger.py
from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from agentic_doc.parse import parse
import pathlib, json
from datetime import datetime
import json, pathlib
from dotenv import load_dotenv

load_dotenv()

class Metadata(BaseModel):
    tag: str
    tank_type: str
    service_description: str
    project_name: str
    client_name: str
    document_number: str

    revision: Optional[str] = None
    project_code: Optional[str] = None
    location: Optional[str] = None
    manufacturer: Optional[str] = None
    date: Optional[str] = None                          # yyyy-mm-dd string


class DesignConditions(BaseModel):
    design_pressure: Optional[float] = None
    design_pressure_unit: Optional[str] = None
    design_temperature: Optional[float] = None
    design_temperature_unit: Optional[str] = None
    test_pressure: Optional[float] = None
    test_pressure_unit: Optional[str] = None
    corrosion_allowance: Optional[float] = None
    corrosion_allowance_unit: Optional[str] = None
    wind_design_speed: Optional[float] = None
    wind_design_speed_unit: Optional[str] = None
    seismic_design_accel: Optional[float] = None
    seismic_design_accel_unit: Optional[str] = None


class OperatingConditions(BaseModel):
    operating_pressure: Optional[float] = None
    operating_pressure_unit: Optional[str] = None
    operating_temperature: Optional[float] = None
    operating_temperature_unit: Optional[str] = None
    normal_capacity: Optional[float] = None
    normal_capacity_unit: Optional[str] = None
    max_capacity: Optional[float] = None
    max_capacity_unit: Optional[str] = None


class MechanicalGeometry(BaseModel):
    tank_diameter: Optional[float] = None
    tank_diameter_unit: Optional[str] = None
    tank_height: Optional[float] = None
    tank_height_unit: Optional[str] = None
    roof_type: Optional[str] = None
    bottom_type: Optional[str] = None
    shell_thickness: Optional[float] = None
    shell_thickness_unit: Optional[str] = None
    roof_thickness: Optional[float] = None
    roof_thickness_unit: Optional[str] = None
    bottom_thickness: Optional[float] = None
    bottom_thickness_unit: Optional[str] = None
    design_code: Optional[str] = None


class Materials(BaseModel):
    shell_material: Optional[str] = None
    roof_material: Optional[str] = None
    bottom_material: Optional[str] = None
    internals_material: Optional[str] = None
    lining_type: Optional[str] = None
    insulation_type: Optional[str] = None


class EnvironmentalConditions(BaseModel):
    ambient_temperature: Optional[float] = None
    ambient_temperature_unit: Optional[str] = None
    humidity_percent: Optional[float] = None
    humidity_percent_unit: Optional[str] = None
    altitude: Optional[float] = None
    altitude_unit: Optional[str] = None
    seismic_zone: Optional[str] = None
    wind_speed: Optional[float] = None
    wind_speed_unit: Optional[str] = None


# ─────────────────────────── array blocks ─────────────────────────── #

class EquipmentItem(BaseModel):
    equipment_role: str
    equipment_name: str
    item_tag_number: str

    description: Optional[str] = None
    quantity: Optional[int] = None
    orientation: Optional[str] = None
    installation_type: Optional[str] = None
    duty_cycle: Optional[str] = None
    criticality_rating: Optional[str] = None
    space_name: Optional[str] = None
    sketch_reference: Optional[str] = None
    notes: Optional[str] = None


class NozzleBase(BaseModel):
    nozzle_id: str
    service: str

    size_nominal: Optional[str] = None
    size_nominal_unit: Optional[str] = None
    rating_class: Optional[str] = None
    orientation: Optional[str] = None
    elevation: Optional[float] = None
    elevation_unit: Optional[str] = None
    remarks: Optional[str] = None


class ProcessNozzle(NozzleBase):
    pass


class InstrumentNozzle(NozzleBase):
    pass


class Manway(BaseModel):
    manway_id: str
    type: str

    size_nominal: Optional[str] = None
    size_nominal_unit: Optional[str] = None
    rating_class: Optional[str] = None
    orientation: Optional[str] = None
    elevation: Optional[float] = None
    elevation_unit: Optional[str] = None
    quantity: Optional[int] = None
    details_reference: Optional[str] = None
    remarks: Optional[str] = None


class FluidData(BaseModel):
    fluid_name: Optional[str] = None
    fluid_density: Optional[float] = None
    fluid_density_unit: Optional[str] = None
    fluid_viscosity: Optional[float] = None
    fluid_viscosity_unit: Optional[str] = None
    flash_point: Optional[float] = None
    flash_point_unit: Optional[str] = None
    ph: Optional[float] = None
    ph_unit: Optional[str] = None
    solids_content_weight_percent: Optional[float] = None
    solids_content_weight_percent_unit: Optional[str] = None


class Accessories(BaseModel):
    manways_count: Optional[int] = None
    manways_count_unit: Optional[str] = None
    nozzles_count: Optional[int] = None
    nozzles_count_unit: Optional[str] = None
    level_gauge_type: Optional[str] = None
    breather_valve: Optional[str] = None
    foam_pourers: Optional[int] = None
    foam_pourers_unit: Optional[str] = None
    fire_water_cooling_rings: Optional[bool] = None


class Instrumentation(BaseModel):
    level_switches: Optional[str] = None
    pressure_gauge: Optional[str] = None
    temperature_elements: Optional[str] = None
    gas_detection: Optional[str] = None


class TestingInspection(BaseModel):
    hydrotest_pressure: Optional[float] = None
    hydrotest_pressure_unit: Optional[str] = None
    vacuum_box_test: Optional[bool] = None
    shell_plate_ultrasonic: Optional[str] = None
    roof_leak_test: Optional[bool] = None
    coating_holiday_test: Optional[bool] = None


class RevisionItem(BaseModel):
    revision: str
    date: str
    description: str
    originator: Optional[str] = None
    reviewed: Optional[str] = None
    approved: Optional[str] = None


class NoteItem(BaseModel):
    note_number: Optional[str] = None
    note_text: Optional[str] = None


# ─────────────────────────── root ADM model ─────────────────────────── #

class WaterTankADM(BaseModel):
    metadata: Metadata
    mechanical_geometry: MechanicalGeometry
    process_fluids: Optional[FluidData] = None

    equipments: Optional[List[EquipmentItem]] = None
    design_conditions: Optional[DesignConditions] = None
    operating_conditions: Optional[OperatingConditions] = None
    construction: Optional[Dict[str, Any]] = None           # complex block – keep flexible
    process_nozzles: Optional[List[ProcessNozzle]] = None
    instrument_nozzles: Optional[List[InstrumentNozzle]] = None
    manways: Optional[List[Manway]] = None
    materials: Optional[Materials] = None
    accessories: Optional[Accessories] = None
    instrumentation: Optional[Instrumentation] = None
    testing_inspection: Optional[TestingInspection] = None
    environmental_conditions: Optional[EnvironmentalConditions] = None
    revisions: Optional[List[RevisionItem]] = None
    notes: Optional[List[NoteItem]] = None

    model_config = {"extra": "allow"}   # let un-modelled blocks pass through

# ────────────────────────────────
# 2.   Parse a PDF (or list of PDFs)
# ────────────────────────────────


pdf = pathlib.Path("data/document_5a847846-368e-4f7a-a107-ec130083d6ce.pdf")
# schema = json.load(open("data/schemas/heat_exchanger_schema.json", encoding="utf-8"))

doc = parse(pdf, extraction_model=WaterTankADM)[0]


if doc.errors:                         # 422 or any server-side error
    print("❌", doc.file_name, "→", doc.error.message)
    # the SDK already dumped full JSON to disk; path is in:
    print("↪ full payload:", doc.error.debug_path)


    adm: WaterTankADM = doc.extraction
    print("Tank tag :", adm.metadata.tag)
    print("Diameter :", adm.mechanical_geometry.tank_diameter,
        adm.mechanical_geometry.tank_diameter_unit)

    # ------------------------------------------------------------------
    # 8.  Persist results
    # ------------------------------------------------------------------

    OUT_DIR = pathlib.Path("outputs")
    OUT_DIR.mkdir(exist_ok=True)

    # (a) the “clean” ADM structure you just typed-checked
    adm_file = OUT_DIR / f"{pdf.stem}_adm.json"
    adm_file.write_text(
        adm.model_dump_json(indent=2, ensure_ascii=False)   # Pydantic v2
    )
    print("✓ ADM JSON saved to:", adm_file.relative_to(pathlib.Path.cwd()))

    # (b) the full raw Landing-AI payload (optional but great for audit/debug)
    raw_file = OUT_DIR / f"{pdf.stem}_{datetime.utcnow():%Y%m%dT%H%M%SZ}_full.json"
    raw_file.write_text(json.dumps(doc.raw_response, indent=2, ensure_ascii=False))
    print("✓ Full extractor payload saved to:", raw_file.relative_to(pathlib.Path.cwd()))
