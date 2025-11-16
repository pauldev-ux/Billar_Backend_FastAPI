from pydantic import BaseModel
from datetime import datetime

class FacturaCreate(BaseModel):
    mesa_id: int
    usuario_id: int

class FacturaOut(BaseModel):
    id: int
    mesa_id: int
    fecha: datetime
    total_mesa: float
    total_consumos: float
    total_final: float
    usuario_id: int

    class Config:
        from_attributes = True
