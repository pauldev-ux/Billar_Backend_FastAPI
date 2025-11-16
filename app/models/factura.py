from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from datetime import datetime
from app.database import Base

class Factura(Base):
    __tablename__ = "facturas"

    id = Column(Integer, primary_key=True)
    mesa_id = Column(Integer, ForeignKey("mesas.id"))
    fecha = Column(DateTime, default=datetime.utcnow)
    total_mesa = Column(Float)
    total_consumos = Column(Float)
    total_final = Column(Float)
    usuario_id = Column(Integer, ForeignKey("users.id"))
