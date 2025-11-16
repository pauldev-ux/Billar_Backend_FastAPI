from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models.factura import Factura
from app.models.consumo import Consumo
from app.models.producto import Producto

router = APIRouter(prefix="/reportes", tags=["Reportes"])


def formatear_factura(factura: Factura, db: Session):
    consumos = (
        db.query(Consumo, Producto)
        .join(Producto, Producto.id == Consumo.producto_id)
        .filter(Consumo.mesa_id == factura.mesa_id)
        .all()
    )

    detalle_consumos = [
        {
            "producto": prod.nombre,
            "cantidad": cons.cantidad,
            "precio_unitario": cons.precio_unitario,
            "subtotal": cons.subtotal
        }
        for cons, prod in consumos
    ]

    return {
        "factura_id": factura.id,
        "fecha": factura.fecha,
        "total_mesa": factura.total_mesa,
        "total_consumos": factura.total_consumos,
        "total_final": factura.total_final,
        "mesa_id": factura.mesa_id,
        "consumos": detalle_consumos
    }


@router.get("/rango")
def reporte_rango(
    desde: str = Query(..., description="YYYY-MM-DD"),
    hasta: str = Query(..., description="YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    inicio = datetime.strptime(desde, "%Y-%m-%d")
    fin = datetime.strptime(hasta, "%Y-%m-%d") + timedelta(days=1)

    facturas = db.query(Factura).filter(
        Factura.fecha >= inicio,
        Factura.fecha < fin
    ).all()

    return [formatear_factura(f, db) for f in facturas]


@router.get("/hoy")
def reporte_hoy(db: Session = Depends(get_db)):
    hoy = datetime.utcnow().date()
    # rango de hoy 00:00 → mañana 00:00
    return reporte_rango(
        desde=str(hoy),
        hasta=str(hoy),
        db=db
    )


@router.get("/mes")
def reporte_mes_actual(db: Session = Depends(get_db)):
    hoy = datetime.utcnow()
    inicio_mes = datetime(hoy.year, hoy.month, 1).date()
    fin_mes = datetime(hoy.year, hoy.month, 28).date()  # flexible

    return reporte_rango(
        desde=str(inicio_mes),
        hasta=str(hoy.date()),
        db=db
    )
