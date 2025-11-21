from pydantic import BaseModel
from datetime import datetime

class CompraProductoOut(BaseModel):
    id: int
    nombre: str
    precio_compra: float
    cantidad: int
    subtotal: float
    fecha_compra: datetime

    class Config:
        from_attributes = True
