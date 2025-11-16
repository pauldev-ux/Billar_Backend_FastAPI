from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.consumo import Consumo
from app.models.turno import Turno
from app.models.producto import Producto
from app.schemas.consumo_schema import ConsumoCreate, ConsumoOut

router = APIRouter(prefix="/consumos", tags=["Consumos"])


# REGISTRAR CONSUMO
@router.post("/", response_model=ConsumoOut)
def registrar_consumo(data: ConsumoCreate, db: Session = Depends(get_db)):
    turno = db.query(Turno).filter(Turno.id == data.turno_id).first()
    if not turno:
        raise HTTPException(404, "Turno no encontrado")

    producto = db.query(Producto).filter(Producto.id == data.producto_id).first()
    if not producto:
        raise HTTPException(404, "Producto no encontrado")

    if producto.stock < data.cantidad:
        raise HTTPException(400, "Stock insuficiente")

    subtotal = producto.precio * data.cantidad

    consumo = Consumo(
        turno_id=data.turno_id,
        producto_id=data.producto_id,
        cantidad=data.cantidad,
        subtotal=subtotal
    )

    producto.stock -= data.cantidad
    turno.subtotal_productos += subtotal

    db.add(consumo)
    db.commit()
    db.refresh(consumo)

    return consumo


# LISTAR CONSUMOS POR TURNO
@router.get("/turno/{turno_id}", response_model=list[ConsumoOut])
def obtener_consumos(turno_id: int, db: Session = Depends(get_db)):
    return db.query(Consumo).filter(Consumo.turno_id == turno_id).all()


# ELIMINAR CONSUMO
@router.delete("/{consumo_id}")
def eliminar_consumo(consumo_id: int, db: Session = Depends(get_db)):
    consumo = db.query(Consumo).filter(Consumo.id == consumo_id).first()
    if not consumo:
        raise HTTPException(404, "Consumo no encontrado")

    db.delete(consumo)
    db.commit()
    return {"mensaje": "Consumo eliminado"}
