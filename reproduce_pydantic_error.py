from typing import Optional

from pydantic.v1 import BaseModel, Field


class OmniBase(BaseModel):
    @property
    def is_ready(self) -> bool:
        return True

    class Config:
        allow_population_by_field_name = True


class MSPBaseModel(OmniBase):
    system_id: Optional[int] = Field(None, alias="System-Id")


print("Attempting to instantiate MSPBaseModel...")
m = MSPBaseModel(system_id=123)
print(f"Success: {m}")
