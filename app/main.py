from typing import List, Optional
import os
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Field, Session, create_engine, select
from pydantic import EmailStr
from dotenv import load_dotenv
import uvicorn

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("La variable de entorno DATABASE_URL no está definida.")

engine = create_engine(DATABASE_URL, echo=True)

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

def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI(title="Sistema de Gestión de Vehículos")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.post("/vehiculos/", response_model=Vehiculo, status_code=201)
def create_vehiculo(vehiculo: VehiculoCreate, session: Session = Depends(get_session)):
    db_vehiculo = Vehiculo.from_orm(vehiculo)
    session.add(db_vehiculo)
    session.commit()
    session.refresh(db_vehiculo)
    return db_vehiculo

@app.get("/vehiculos/", response_model=List[Vehiculo])
def read_vehiculos(session: Session = Depends(get_session)):
    return session.exec(select(Vehiculo)).all()

@app.get("/vehiculos/{vehiculo_id}", response_model=Vehiculo)
def read_vehiculo(vehiculo_id: int, session: Session = Depends(get_session)):
    vehiculo = session.get(Vehiculo, vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehiculo

@app.put("/vehiculos/{vehiculo_id}", response_model=Vehiculo)
def update_vehiculo(vehiculo_id: int, vehiculo_data: VehiculoUpdate, session: Session = Depends(get_session)):
    db_vehiculo = session.get(Vehiculo, vehiculo_id)
    if not db_vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    update_data = vehiculo_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_vehiculo, key, value)

    session.add(db_vehiculo)
    session.commit()
    session.refresh(db_vehiculo)
    return db_vehiculo

@app.delete("/vehiculos/{vehiculo_id}", status_code=204)
def delete_vehiculo(vehiculo_id: int, session: Session = Depends(get_session)):
    vehiculo = session.get(Vehiculo, vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    session.delete(vehiculo)
    session.commit()
    return None

@app.post("/clientes/", response_model=Cliente, status_code=201)
def create_cliente(cliente: ClienteCreate, session: Session = Depends(get_session)):
    db_cliente = Cliente.from_orm(cliente)
    session.add(db_cliente)
    session.commit()
    session.refresh(db_cliente)
    return db_cliente

@app.get("/clientes/", response_model=List[Cliente])
def read_clientes(session: Session = Depends(get_session)):
    return session.exec(select(Cliente)).all()

@app.get("/clientes/{cliente_id}", response_model=Cliente)
def read_cliente(cliente_id: int, session: Session = Depends(get_session)):
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@app.put("/clientes/{cliente_id}", response_model=Cliente)
def update_cliente(cliente_id: int, cliente_data: ClienteUpdate, session: Session = Depends(get_session)):
    db_cliente = session.get(Cliente, cliente_id)
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    update_data = cliente_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_cliente, key, value)

    session.add(db_cliente)
    session.commit()
    session.refresh(db_cliente)
    return db_cliente

@app.delete("/clientes/{cliente_id}", status_code=204)
def delete_cliente(cliente_id: int, session: Session = Depends(get_session)):
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    session.delete(cliente)
    session.commit()
    return None

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
