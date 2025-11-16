from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.turno import Turno
from app.models.consumo import Consumo
from app.models.mesa import Mesa
from app.models.producto import Producto
from app.schemas.turno_schema import (
    TurnoCreate, TurnoOut, AgregarProducto, AgregarTiempo, CerrarTurno
)

router = APIRouter(prefix="/turnos", tags=["Turnos"])


# ============================================================
# 🔄 FUNCION QUE TRANSFORMA EL TURNO EN UN DICT LISTO PARA EL FRONT
# ============================================================
def turno_to_dict(turno: Turno):
    consumos = []
    for c in turno.consumos:
        consumos.append({
            "id": c.id,
            "producto_id": c.producto_id,
            "producto_nombre": c.producto.nombre,  # 👈 NOMBRE DEL PRODUCTO
            "cantidad": c.cantidad,
            "subtotal": c.subtotal
        })

    return {
        "id": turno.id,
        "mesa_id": turno.mesa_id,
        "hora_inicio": turno.hora_inicio,
        "hora_fin": turno.hora_fin,
        "tarifa_hora": turno.tarifa_hora,
        "tiempo_estimado_min": turno.tiempo_estimado_min,
        "minutos_extra": turno.minutos_extra,
        "tiempo_total_min": turno.tiempo_estimado_min + turno.minutos_extra,
        "subtotal_tiempo": turno.subtotal_tiempo,
        "subtotal_productos": turno.subtotal_productos,
        "descuento": turno.descuento,
        "total_final": turno.total_final,
        "estado": turno.estado,
        "consumos": consumos
    }


# ============================================================
# 🚀 INICIAR TURNO
# ============================================================
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
        tiempo_estimado_min=data.tiempo_estimado_min,
        hora_inicio=datetime.now(),
        estado="abierto"
    )

    db.add(turno)
    mesa.estado = "ocupada"
    db.commit()
    db.refresh(turno)

    return turno_to_dict(turno)


# ============================================================
# 🟩 AGREGAR PRODUCTO
# ============================================================
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


# ============================================================
# ➕ AGREGAR TIEMPO
# ============================================================
@router.patch("/{turno_id}/agregar-tiempo", response_model=TurnoOut)
def agregar_tiempo(turno_id: int, data: AgregarTiempo, db: Session = Depends(get_db)):
    turno = db.query(Turno).filter(Turno.id == turno_id, Turno.estado == "abierto").first()
    if not turno:
        raise HTTPException(404, "Turno no encontrado o ya cerrado")

    turno.minutos_extra += data.minutos
    db.commit()
    db.refresh(turno)

    return turno_to_dict(turno)


# ============================================================
# 🔍 PREVIEW DEL CIERRE
# ============================================================
@router.get("/{turno_id}/preview", response_model=TurnoOut)
def preview(turno_id: int, db: Session = Depends(get_db)):
    turno = db.query(Turno).filter(Turno.id == turno_id).first()
    if not turno:
        raise HTTPException(404, "Turno no encontrado")

    minutos_totales = turno.tiempo_estimado_min + turno.minutos_extra
    horas = minutos_totales / 60
    subtotal_tiempo = horas * turno.tarifa_hora

    turno.subtotal_tiempo = subtotal_tiempo
    turno.total_final = subtotal_tiempo + turno.subtotal_productos - turno.descuento

    return turno_to_dict(turno)


# ============================================================
# 🔴 CERRAR TURNO
# ============================================================
@router.patch("/{turno_id}/cerrar", response_model=TurnoOut)
def cerrar_turno(turno_id: int, data: CerrarTurno, db: Session = Depends(get_db)):
    turno = db.query(Turno).filter(Turno.id == turno_id, Turno.estado == "abierto").first()
    if not turno:
        raise HTTPException(404, "Turno no encontrado o ya cerrado")

    turno.hora_fin = datetime.now()

    minutos_totales = turno.tiempo_estimado_min + turno.minutos_extra
    horas = minutos_totales / 60

    turno.subtotal_tiempo = horas * turno.tarifa_hora
    turno.descuento = data.descuento
    turno.total_final = turno.subtotal_tiempo + turno.subtotal_productos - turno.descuento
    turno.estado = "cerrado"

    mesa = db.query(Mesa).filter(Mesa.id == turno.mesa_id).first()
    mesa.estado = "libre"

    db.commit()
    db.refresh(turno)

    return turno_to_dict(turno)
