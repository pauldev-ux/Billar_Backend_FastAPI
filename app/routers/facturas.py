from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.mesa import Mesa
from app.models.consumo import Consumo
from app.models.factura import Factura
from app.schemas.factura_schema import FacturaCreate, FacturaOut

router = APIRouter(prefix="/facturas", tags=["Facturas"])

@router.post("/", response_model=FacturaOut)
def generar_factura(data: FacturaCreate, db: Session = Depends(get_db)):
    mesa = db.query(Mesa).filter(Mesa.id == data.mesa_id).first()
    if not mesa:
        raise HTTPException(404, "Mesa no encontrada")

    if not mesa.hora_inicio:
        raise HTTPException(400, "La mesa no tiene inicio registrado")

    # hora_fin
    mesa.hora_fin = datetime.utcnow()

    # duración en horas
    horas = (mesa.hora_fin - mesa.hora_inicio).total_seconds() / 3600
    total_mesa = horas * mesa.tarifa_por_hora

    # consumos
    consumos = db.query(Consumo).filter(Consumo.mesa_id == data.mesa_id).all()
    total_consumos = sum(c.subtotal for c in consumos)

    total_final = total_mesa + total_consumos

    factura = Factura(
        mesa_id=data.mesa_id,
        total_mesa=total_mesa,
        total_consumos=total_consumos,
        total_final=total_final,
        usuario_id=data.usuario_id,
    )

    # liberar mesa
    mesa.estado = "libre"
    mesa.hora_inicio = None
    mesa.hora_fin = None

    db.add(factura)
    db.commit()
    db.refresh(factura)

    return factura


@router.get("/", response_model=list[FacturaOut])
def listar_facturas(db: Session = Depends(get_db)):
    return db.query(Factura).all()
