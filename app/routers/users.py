from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserOut
from passlib.context import CryptContext
from app.deps import get_current_user

router = APIRouter(prefix="/users", tags=["Usuarios"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/", response_model=UserOut)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    hashed = pwd_context.hash(data.password)
    new_user = User(username=data.username, password_hash=hashed, rol=data.rol)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get("/me", response_model=UserOut)
def obtener_usuario_logeado(user = Depends(get_current_user)):
    return user