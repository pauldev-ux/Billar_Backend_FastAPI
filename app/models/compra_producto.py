from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from app.database import Base

class CompraProducto(Base):
    __tablename__ = "compras_productos"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String, nullable=False)
    precio_compra = Column(Float, nullable=False)
    cantidad = Column(Integer, nullable=False)

    subtotal = Column(Float, nullable=False)
    fecha_compra = Column(DateTime, default=datetime.utcnow)
