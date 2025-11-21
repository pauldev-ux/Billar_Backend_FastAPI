from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, mesas, productos, consumos, facturas, reportes, users, turnos, compras_productos
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Billar API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción ajustamos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(mesas.router)
app.include_router(productos.router)
app.include_router(consumos.router)
app.include_router(facturas.router)
app.include_router(reportes.router)
app.include_router(users.router)
app.include_router(turnos.router)
app.include_router(compras_productos.router)