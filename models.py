from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Alumno(Base):
    __tablename__ = "alumnos"

    id = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(100), index=True)
    apellidos = Column(String(100), index=True)
    matricula = Column(String(20), unique=True, index=True)
    promedio = Column(Float, nullable=True)
    password = Column(String(100))
    fotoPerfilUrl = Column(String(255), nullable=True)  # Especifica la longitud máxima

class Profesor(Base):
    __tablename__ = "profesores"

    id = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(100), index=True)  # Especifica la longitud máxima
    apellidos = Column(String(100), index=True)  # Especifica la longitud máxima
    numeroEmpleado = Column(Integer, unique=True, index=True)
    horasClase = Column(Integer)