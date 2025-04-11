from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Personaje, Mision
from database import get_db, crear_base_datos
from modelos_api import *
from cola import ColaMisiones
from Exceptions import OwnEmpty

app = FastAPI()

crear_base_datos()  # Crear base de datos 

# Cola de misiones en memoria por personaje
colas_personajes = {}

@app.post("/personajes", response_model=PersonajeResponse)
def crear_personaje(personaje: PersonajeCreate, db: Session = Depends(get_db)):
    nuevo = Personaje(nombre=personaje.nombre)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    colas_personajes[nuevo.id] = ColaMisiones()  # Crear cola al registrar un nuevo personaje
    return nuevo

@app.post("/misiones", response_model=MisionResponse)
def crear_mision(mision: MisionCreate, db: Session = Depends(get_db)):
    nueva = Mision(
        nombre=mision.nombre,
        descripcion=mision.descripcion,
        experiencia=mision.experiencia,
        estado="pendiente"
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@app.post("/personajes/{id_personaje}/misiones/{id_mision}")
def aceptar_mision(id_personaje: int, id_mision: int, db: Session = Depends(get_db)):
    personaje = db.query(Personaje).get(id_personaje)
    mision = db.query(Mision).get(id_mision)
    if not personaje or not mision:
        raise HTTPException(status_code=404, detail="Personaje o misión no encontrado")
    
    if id_personaje not in colas_personajes:
        colas_personajes[id_personaje] = ColaMisiones()

    colas_personajes[id_personaje].enqueue(mision) #Añade la mision a la cola del personaje
    return {"msg": "Misión encolada correctamente"}

@app.post("/personajes/{id_personaje}/completar")
def completar_mision(id_personaje: int, db: Session = Depends(get_db)):
    if id_personaje not in colas_personajes:
        raise HTTPException(status_code=404, detail="No hay cola para este personaje")

    cola = colas_personajes[id_personaje]
    if cola.is_empty():
        raise HTTPException(status_code=404, detail="No hay misiones en la cola")

    try:
        mision = cola.dequeue() #Saca la mision de la cola
        personaje = db.query(Personaje).get(id_personaje)
        personaje.experiencia += mision.experiencia
        mision.estado = "completada"
        db.commit()
        return {"msg": f"Misión '{mision.nombre}' completada. XP sumado: {mision.experiencia}"}
    except OwnEmpty:
        raise HTTPException(status_code=404, detail="La cola está vacía")

@app.get("/personajes/{id_personaje}/misiones", response_model=list[MisionResponse])
def listar_misiones(id_personaje: int):
    if id_personaje not in colas_personajes or colas_personajes[id_personaje].is_empty():
        return []

    cola = colas_personajes[id_personaje]
    misiones = []
    for i in range(len(cola)):
        idx = (cola.front + i) % len(cola.data)
        mision = cola.data[idx]
        if mision is not None:
            misiones.append(mision)
    return misiones
