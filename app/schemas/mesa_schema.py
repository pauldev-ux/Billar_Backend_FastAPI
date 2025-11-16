from pydantic import BaseModel
from datetime import datetime

class MesaBase(BaseModel):
    nombre: str
    tarifa_por_hora: float

class MesaCreate(MesaBase):
    pass

class MesaUpdate(BaseModel):
    estado: str | None = None
    hora_inicio: datetime | None = None
    hora_fin: datetime | None = None

class MesaOut(BaseModel):
    id: int
    nombre: str
    tarifa_por_hora: float
    estado: str
    hora_inicio: datetime | None = None
    tiempo_estimado_min: int | None = None
    turno_activo: int | None = None
    minutos_extra: int = 0      # 👈 añadido

    class Config:
        from_attributes = True



