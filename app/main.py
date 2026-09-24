import os
from dotenv import load_dotenv
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, select
from pydantic import EmailStr
from contextlib import asynccontextmanager

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("La variable de entorno DATABASE_URL no está definida.")

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

class VehiculoBase(SQLModel):
    marca: str
    modelo: str
    anio: int
    placa: str = Field(unique=True, index=True)
    precio_alquiler_dia: float
    disponible: bool = True

class Vehiculo(VehiculoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class VehiculoCreate(VehiculoBase):
    pass

class VehiculoUpdate(SQLModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    placa: Optional[str] = None
    precio_alquiler_dia: Optional[float] = None
    disponible: Optional[bool] = None

class ClienteBase(SQLModel):
    nombre: str
    email: EmailStr = Field(unique=True, index=True)
    licencia_conducir: str = Field(unique=True, index=True)
    telefono: str

class Cliente(ClienteBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(SQLModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    licencia_conducir: Optional[str] = None
    telefono: Optional[str] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(
    title="Sistema de Gestión de Vehículos", 
    lifespan=lifespan
)

@app.post("/vehiculos/", response_model=Vehiculo, status_code=201)
def crear_vehiculo(vehiculo: VehiculoCreate, session: Session = Depends(get_session)):
    db_vehiculo = Vehiculo.model_validate(vehiculo)
    session.add(db_vehiculo)
    session.commit()
    session.refresh(db_vehiculo)
    return db_vehiculo

@app.get("/vehiculos/", response_model=List[Vehiculo])
def listar_vehiculos(session: Session = Depends(get_session)):
    return session.exec(select(Vehiculo)).all()

@app.get("/vehiculos/{vehiculo_id}", response_model=Vehiculo)
def listar_vehiculo(vehiculo_id: int, session: Session = Depends(get_session)):
    vehiculo = session.get(Vehiculo, vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehiculo

@app.put("/vehiculos/{vehiculo_id}", response_model=Vehiculo)
def actualizar_vehiculo(vehiculo_id: int, vehiculo_data: VehiculoUpdate, session: Session = Depends(get_session)):
    db_vehiculo = session.get(Vehiculo, vehiculo_id)
    if not db_vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    update_data = vehiculo_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_vehiculo, key, value)

    session.add(db_vehiculo)
    session.commit()
    session.refresh(db_vehiculo)
    return db_vehiculo

@app.delete("/vehiculos/{vehiculo_id}", status_code=204)
def eliminar_vehiculo(vehiculo_id: int, session: Session = Depends(get_session)):
    vehiculo = session.get(Vehiculo, vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    session.delete(vehiculo)
    session.commit()
    return None

@app.post("/clientes/", response_model=Cliente, status_code=201)
def crear_cliente(cliente: ClienteCreate, session: Session = Depends(get_session)):
    db_cliente = Cliente.model_validate(cliente)
    session.add(db_cliente)
    session.commit()
    session.refresh(db_cliente)
    return db_cliente

@app.get("/clientes/", response_model=List[Cliente])
def listar_clientes(session: Session = Depends(get_session)):
    return session.exec(select(Cliente)).all()

@app.get("/clientes/{cliente_id}", response_model=Cliente)
def listar_cliente(cliente_id: int, session: Session = Depends(get_session)):
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@app.put("/clientes/{cliente_id}", response_model=Cliente)
def actualizar_cliente(cliente_id: int, cliente_data: ClienteUpdate, session: Session = Depends(get_session)):
    db_cliente = session.get(Cliente, cliente_id)
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    update_data = cliente_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_cliente, key, value)

    session.add(db_cliente)
    session.commit()
    session.refresh(db_cliente)
    return db_cliente

@app.delete("/clientes/{cliente_id}", status_code=204)
def eliminar_cliente(cliente_id: int, session: Session = Depends(get_session)):
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    session.delete(cliente)
    session.commit()
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
