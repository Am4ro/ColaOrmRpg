from pydantic import BaseModel
from typing import Optional

class MisionCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    experiencia: int

class PersonajeCreate(BaseModel):
    nombre: str

class MisionResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    experiencia: int
    estado: str

    class Config:
        orm_mode = True

class PersonajeResponse(BaseModel):
    id: int
    nombre: str
    experiencia: int

    class Config:
        orm_mode = True
