"""Schema for metadata."""

from typing import Optional

from pydantic import BaseModel


class Metadata(BaseModel):
    """Metadata schema."""

    adm_version: Optional[str] = None
    adm_type: Optional[str] = None
    document_name: Optional[str] = None
    document_number: Optional[str] = None
    equipment_name: Optional[str] = None
    equipment_tag: Optional[str] = None
    item_number: Optional[str] = None
    plant_name: Optional[str] = None
    plant_number: Optional[str] = None
    service_name: Optional[str] = None
    manufacture: Optional[str] = None
    client_name: Optional[str] = None
    project_number: Optional[str] = None
    site: Optional[str] = None
    unit: Optional[str] = None
