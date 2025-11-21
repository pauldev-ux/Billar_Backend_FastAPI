from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.turno import Turno
from app.schemas.report_schema import ReporteOut, ReporteTurno, ReporteConsumo
from app.models.mesa import Mesa

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/", response_model=ReporteOut)
def reporte_turnos(
    fecha_inicio: str,
    fecha_fin: str,
    mesa_id: int | None = None,
    db: Session = Depends(get_db)
):
    fecha_inicio_dt = datetime.fromisoformat(fecha_inicio)
    fecha_fin_dt = datetime.fromisoformat(fecha_fin)

    query = db.query(Turno).filter(
        Turno.hora_inicio >= fecha_inicio_dt,
        Turno.hora_fin <= fecha_fin_dt,
        Turno.estado == "cerrado"
    )

    if mesa_id:
        query = query.filter(Turno.mesa_id == mesa_id)

    turnos_db = query.order_by(Turno.hora_inicio.asc()).all()

    turnos_list = []
    tot_tiempo = 0
    tot_prod = 0
    tot_desc = 0
    tot_final = 0

    for t in turnos_db:
        tiempo_total = t.tiempo_estimado_min + t.minutos_extra

        consumos = [
            ReporteConsumo(
                producto_nombre=c.producto.nombre,
                cantidad=c.cantidad,
                subtotal=c.subtotal
            )
            for c in t.consumos
        ]

        turnos_list.append(
            ReporteTurno(
                mesa=t.mesa.nombre,
                hora_inicio=t.hora_inicio,
                hora_fin=t.hora_fin,
                tiempo_total_min=tiempo_total,
                subtotal_tiempo=t.subtotal_tiempo,
                subtotal_productos=t.subtotal_productos,
                descuento=t.descuento,
                total_final=t.total_final,
                consumos=consumos
            )
        )

        tot_tiempo += t.subtotal_tiempo
        tot_prod += t.subtotal_productos
        tot_desc += t.descuento
        tot_final += t.total_final

    return ReporteOut(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        mesa_id=mesa_id,
        turnos=turnos_list,
        total_tiempo=tot_tiempo,
        total_productos=tot_prod,
        total_descuentos=tot_desc,
        total_general=tot_final
    )
