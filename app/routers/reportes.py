from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.turno import Turno
from app.schemas.report_schema import ReporteOut, ReporteTurno, ReporteConsumo

router = APIRouter(prefix="/reportes", tags=["Reportes"])


def parse_fecha(fecha_str: str):
    # Recibe "2025-11-20" o "20/11/2025" y lo convierte a datetime
    if "/" in fecha_str:
        d, m, y = fecha_str.split("/")
        return datetime(int(y), int(m), int(d))
    else:
        return datetime.fromisoformat(fecha_str)


@router.get("/", response_model=ReporteOut)
def reporte_turnos(
    fecha_inicio: str,
    fecha_fin: str,
    mesa_id: int | None = None,
    db: Session = Depends(get_db)
):
    # Convertimos fechas al inicio y final del día
    fecha_inicio_dt = parse_fecha(fecha_inicio).replace(hour=0, minute=0, second=0)
    fecha_fin_dt = parse_fecha(fecha_fin).replace(hour=23, minute=59, second=59)

    query = db.query(Turno).filter(
        Turno.hora_inicio >= fecha_inicio_dt,
        Turno.hora_fin <= fecha_fin_dt,
        Turno.estado == "cerrado"
    )

    if mesa_id:
        query = query.filter(Turno.mesa_id == mesa_id)

    turnos_db = query.order_by(Turno.hora_inicio.asc()).all()

    turnos = []
    tot_tiempo = tot_prod = tot_desc = tot_serv = tot_final = 0

    for t in turnos_db:

        consumos = [
            ReporteConsumo(
                producto_nombre=c.producto.nombre,
                cantidad=c.cantidad,
                subtotal=c.subtotal
            )
            for c in t.consumos
        ]

        turnos.append(
            ReporteTurno(
                mesa=t.mesa.nombre,
                hora_inicio=t.hora_inicio,
                hora_fin=t.hora_fin,
                tiempo_total_min=int((t.hora_fin - t.hora_inicio).total_seconds() / 60),
                subtotal_tiempo=t.subtotal_tiempo,
                subtotal_productos=t.subtotal_productos,
                descuento=t.descuento,
                servicios_extras=getattr(t, "servicios_extras", 0),
                total_final=t.total_final,
                consumos=consumos
            )
        )

        tot_tiempo += t.subtotal_tiempo
        tot_prod += t.subtotal_productos
        tot_desc += t.descuento
        tot_serv += getattr(t, "servicios_extras", 0)
        tot_final += t.total_final

    return ReporteOut(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        mesa_id=mesa_id,
        turnos=turnos,
        total_tiempo=tot_tiempo,
        total_productos=tot_prod,
        total_descuentos=tot_desc,
        total_servicios_extras=tot_serv,
        total_general=tot_final
    )
