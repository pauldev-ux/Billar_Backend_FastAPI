from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.compra_producto import CompraProducto
from app.schemas.compra_producto_schema import CompraProductoOut

router = APIRouter(prefix="/compras-productos", tags=["Compras Productos"])

# POST — Crear compra
@router.post("/", response_model=CompraProductoOut)
async def crear_compra_producto(
    nombre: str = Form(...),
    precio_compra: float = Form(...),
    cantidad: int = Form(...),
    db: Session = Depends(get_db),
):
    subtotal = precio_compra * cantidad

    compra = CompraProducto(
        nombre=nombre,
        precio_compra=precio_compra,
        cantidad=cantidad,
        subtotal=subtotal,
    )

    db.add(compra)
    db.commit()
    db.refresh(compra)

    return compra


# GET — Listar compras
@router.get("/", response_model=list[CompraProductoOut])
def listar_compras(db: Session = Depends(get_db)):
    return db.query(CompraProducto).order_by(CompraProducto.fecha_compra.desc()).all()


# GET — Obtener compra por ID
@router.get("/{compra_id}", response_model=CompraProductoOut)
def obtener_compra(compra_id: int, db: Session = Depends(get_db)):
    compra = db.query(CompraProducto).filter(CompraProducto.id == compra_id).first()

    if not compra:
        raise HTTPException(404, "Compra no encontrada")

    return compra
