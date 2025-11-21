from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.mesa import Mesa
from app.models.turno import Turno
from app.schemas.mesa_schema import MesaCreate, MesaUpdate, MesaOut
from datetime import datetime

router = APIRouter(prefix="/mesas", tags=["Mesas"])
@router.post("/", response_model=MesaOut)
def create_mesa(data: MesaCreate, db: Session = Depends(get_db)):
    mesa = Mesa(
        nombre=data.nombre,
        tarifa_por_hora=data.tarifa_por_hora,
        estado="libre"
    )
    db.add(mesa)
    db.commit()
    db.refresh(mesa)
    return mesa


@router.get("/", response_model=list[MesaOut])
def listar_mesas(db: Session = Depends(get_db)):
    mesas = db.query(Mesa).all()
    resultado = []

    for mesa in mesas:
        turno_activo = db.query(Turno)\
            .filter(Turno.mesa_id == mesa.id, Turno.estado == "abierto")\
            .first()

        resultado.append({
            "id": mesa.id,
            "nombre": mesa.nombre,
            "estado": mesa.estado,
            "tarifa_por_hora": mesa.tarifa_por_hora,
            "hora_inicio": turno_activo.hora_inicio if turno_activo else None,
            "turno_activo": turno_activo.id if turno_activo else None,
        })

    return resultado






@router.put("/{mesa_id}", response_model=MesaOut)
def actualizar_mesa(mesa_id: int, data: MesaUpdate, db: Session = Depends(get_db)):
    mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
    if not mesa:
        raise HTTPException(404, "Mesa no encontrada")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(mesa, field, value)

    db.commit()
    db.refresh(mesa)
    return mesa


@router.delete("/{mesa_id}")
def eliminar_mesa(mesa_id: int, db: Session = Depends(get_db)):
    mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
    if not mesa:
        raise HTTPException(404, "Mesa no encontrada")

    db.delete(mesa)
    db.commit()
    return {"mensaje": "Mesa eliminada"}
