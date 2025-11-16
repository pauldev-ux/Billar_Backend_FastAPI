from pydantic import BaseModel
from datetime import datetime
from typing import List

class ConsumoDetalle(BaseModel):
    id: int
    producto_id: int
    producto_nombre: str  # 👈 nuevo campo
    cantidad: int
    subtotal: float

    class Config:
        from_attributes = True


class TurnoBase(BaseModel):
    mesa_id: int
    tarifa_hora: float
    tiempo_estimado_min: int


class TurnoCreate(TurnoBase):
    pass


class AgregarProducto(BaseModel):
    producto_id: int
    cantidad: int


class AgregarTiempo(BaseModel):
    minutos: int


class CerrarTurno(BaseModel):
    descuento: float = 0


class TurnoOut(BaseModel):
    id: int
    mesa_id: int
    hora_inicio: datetime
    hora_fin: datetime | None
    tarifa_hora: float
    tiempo_estimado_min: int
    minutos_extra: int
    subtotal_tiempo: float
    subtotal_productos: float
    descuento: float
    total_final: float
    estado: str

    consumos: List[ConsumoDetalle] = []

    class Config:
        from_attributes = True
