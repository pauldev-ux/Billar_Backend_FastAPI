from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.turno import Turno
from app.models.consumo import Consumo
from app.models.mesa import Mesa
from app.models.producto import Producto
from app.schemas.turno_schema import (
    TurnoCreate, TurnoOut, AgregarProducto, CerrarTurno
)

router = APIRouter(prefix="/turnos", tags=["Turnos"])


def turno_to_dict(turno: Turno):
    consumos = [{
        "id": c.id,
        "producto_id": c.producto_id,
        "producto_nombre": c.producto.nombre,
        "cantidad": c.cantidad,
        "subtotal": c.subtotal
    } for c in turno.consumos]

    return {
        "id": turno.id,
        "mesa_id": turno.mesa_id,
        "hora_inicio": turno.hora_inicio,
        "hora_fin": turno.hora_fin,
        "tarifa_hora": turno.tarifa_hora,
        "subtotal_tiempo": turno.subtotal_tiempo,
        "subtotal_productos": turno.subtotal_productos,
        "servicios_extras": turno.servicios_extras,
        "descuento": turno.descuento,
        "total_final": turno.total_final,
        "estado": turno.estado,
        "consumos": consumos,
    }


# INICIAR TURNO
@router.post("/iniciar", response_model=TurnoOut)
def iniciar_turno(data: TurnoCreate, db: Session = Depends(get_db)):
    mesa = db.query(Mesa).filter(Mesa.id == data.mesa_id).first()
    if not mesa:
        raise HTTPException(404, "Mesa no encontrada")

    if mesa.estado == "ocupada":
        raise HTTPException(400, "La mesa ya tiene un turno activo")

    turno = Turno(
        mesa_id=data.mesa_id,
        tarifa_hora=data.tarifa_hora,
        hora_inicio=datetime.now(),
        estado="abierto"
    )

    db.add(turno)
    mesa.estado = "ocupada"
    mesa.hora_inicio = turno.hora_inicio
    db.commit()
    db.refresh(turno)

    return turno_to_dict(turno)


# AGREGAR PRODUCTO
@router.post("/{turno_id}/agregar-producto", response_model=TurnoOut)
def agregar_producto(turno_id: int, data: AgregarProducto, db: Session = Depends(get_db)):
    turno = db.query(Turno).filter(Turno.id == turno_id, Turno.estado == "abierto").first()
    if not turno:
        raise HTTPException(404, "Turno no encontrado o ya cerrado")

    producto = db.query(Producto).filter(Producto.id == data.producto_id).first()
    if not producto:
        raise HTTPException(404, "Producto no encontrado")

    if producto.stock < data.cantidad:
        raise HTTPException(400, "Stock insuficiente")

    subtotal = producto.precio * data.cantidad

    consumo = Consumo(
        turno_id=turno.id,
        producto_id=producto.id,
        cantidad=data.cantidad,
        subtotal=subtotal
    )

    producto.stock -= data.cantidad
    turno.subtotal_productos += subtotal

    db.add(consumo)
    db.commit()
    db.refresh(turno)

    return turno_to_dict(turno)


# PREVIEW ANTES DE CERRAR TURNO
@router.get("/{turno_id}/preview", response_model=TurnoOut)
def preview(turno_id: int, db: Session = Depends(get_db)):
    turno = db.query(Turno).filter(Turno.id == turno_id).first()
    if not turno:
        raise HTTPException(404, "Turno no encontrado")

    # calcular tiempo real
    minutos = (datetime.now() - turno.hora_inicio).total_seconds() / 60

    # Reglas:
    # <= 30 minutos → media hora
    # >= 31 minutos → hora completa
    if minutos <= 30:
        subtotal = (turno.tarifa_hora / 2)
    else:
        horas_completas = int(minutos // 60)
        resto = minutos % 60

        subtotal = horas_completas * turno.tarifa_hora
        subtotal += turno.tarifa_hora if resto >= 31 else turno.tarifa_hora / 2

    turno.subtotal_tiempo = subtotal
    turno.total_final = subtotal + turno.subtotal_productos + turno.servicios_extras - turno.descuento

    return turno_to_dict(turno)


# CERRAR TURNO
@router.patch("/{turno_id}/cerrar", response_model=TurnoOut)
def cerrar_turno(turno_id: int, data: CerrarTurno, db: Session = Depends(get_db)):
    turno = db.query(Turno).filter(Turno.id == turno_id, Turno.estado == "abierto").first()
    if not turno:
        raise HTTPException(404, "Turno no encontrado o ya cerrado")

    turno.hora_fin = datetime.now()

    minutos = (turno.hora_fin - turno.hora_inicio).total_seconds() / 60

    if minutos <= 30:
        subtotal = (turno.tarifa_hora / 2)
    else:
        horas_completas = int(minutos // 60)
        resto = minutos % 60

        subtotal = horas_completas * turno.tarifa_hora
        subtotal += turno.tarifa_hora if resto >= 31 else turno.tarifa_hora / 2

    turno.subtotal_tiempo = subtotal
    turno.descuento = data.descuento
    turno.servicios_extras = data.servicios_extras

    turno.total_final = subtotal + turno.subtotal_productos + turno.servicios_extras - turno.descuento
    turno.estado = "cerrado"

    mesa = db.query(Mesa).filter(Mesa.id == turno.mesa_id).first()
    mesa.estado = "libre"
    mesa.hora_inicio = None

    db.commit()
    db.refresh(turno)

    return turno_to_dict(turno)
