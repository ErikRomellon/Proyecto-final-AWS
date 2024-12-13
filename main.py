from fastapi import FastAPI, HTTPException, Request, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from database import get_db
from models import Alumno as AlumnoDB, Profesor as ProfesorDB
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import uuid, time, random, string

app = FastAPI()

# Variables de entorno
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = "" # Reemplaza con tus credenciales de AWS
AWS_SESSION_TOKEN = "" # Reemplaza con tus credenciales de AWS
AWS_BUCKET_NAME = "mi-bucket-fastapi" # Reemplaza con tu nombre de bucket
AWS_REGION = "us-east-1" # Reemplaza con tu región de AWS

SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:340185244786:mi-topic-2" # Reemplaza con el ARN de tu tópico de SNS
DYNAMODB_TABLE_NAME = "sesiones-alumnos" # Reemplaza con el nombre de tu tabla de DynamoDB

# Crear clientes de AWS
s3_client = boto3.client(
    "s3",
    aws_access_key_id= AWS_ACCESS_KEY_ID,
    aws_secret_access_key= AWS_SECRET_ACCESS_KEY,
    aws_session_token= AWS_SESSION_TOKEN,
    region_name=AWS_REGION,
)

# Crear cliente de SNS
sns_client = boto3.client(
    "sns",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name=AWS_REGION,
)

# Crear recurso de DynamoDB
dynamodb_resource = boto3.resource(
    "dynamodb",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name=AWS_REGION,
)

# Listar buckets de S3
response = s3_client.list_buckets()
print("buckets")
for bucket in response["Buckets"]:
    print(f"  {bucket['Name']}")


# Entidad Alumno
class Alumno(BaseModel):
    id: Optional[int] = None
    nombres: str = Field(..., min_length=1)
    apellidos: str = Field(..., min_length=1)
    matricula: str = Field(..., min_length=1)
    promedio: Optional[float] = None
    password: str = Field(..., min_length=6)

    class Config:
        orm_mode = True

# Entidad Profesor
class Profesor(BaseModel):
    id: Optional[int] = None
    nombres: str = Field(..., min_length=1)
    apellidos: str = Field(..., min_length=1)
    numeroEmpleado: int = Field(..., ge=1)
    horasClase: int = Field(..., ge=1)

    class Config:
        orm_mode = True


# **Rutas para Alumnos**

# Ruta para obtener todos los alumnos
@app.get("/alumnos", response_model=List[Alumno])
async def obtener_alumnos(db: Session = Depends(get_db)):
    alumnos = db.query(AlumnoDB).all()
    return alumnos

# Ruta para obtener un alumno por su ID
@app.get("/alumnos/{id}", response_model=Alumno)
async def obtener_alumno(id: int, db: Session = Depends(get_db)):
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    return alumno

# Ruta para crear un alumno
@app.post("/alumnos", response_model=Alumno, status_code=201)
async def crear_alumno(alumno: Alumno, db: Session = Depends(get_db)):
    db_alumno = AlumnoDB(**alumno.dict())
    db.add(db_alumno)
    db.commit()
    db.refresh(db_alumno)
    return db_alumno

# Ruta para actualizar un alumno
@app.put("/alumnos/{id}", response_model=Alumno)
async def actualizar_alumno(id: int, alumno: Alumno, db: Session = Depends(get_db)):
    db_alumno = db.query(AlumnoDB).filter(AlumnoDB.id == id).first()
    if not db_alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    for key, value in alumno.dict(exclude_unset=True).items():
        setattr(db_alumno, key, value)
    db.commit()
    db.refresh(db_alumno)
    return db_alumno

# Ruta para eliminar un alumno
@app.delete("/alumnos/{id}", status_code=200)
async def eliminar_alumno(id: int, db: Session = Depends(get_db)):
    db_alumno = db.query(AlumnoDB).filter(AlumnoDB.id == id).first()
    if not db_alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    db.delete(db_alumno)
    db.commit()
    return

# Ruta para enviar un correo al alumno
@app.post("/alumnos/{id}/email")
async def enviar_email(id: int, db: Session = Depends(get_db)):
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    try:
        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=f"Correo para el alumno {alumno.nombres} {alumno.apellidos}",
            Subject="Asunto del correo",
        )
        print("Mensaje publicado:", response)
        return {"message": "Correo enviado", "response": response}
    except NoCredentialsError as e:
        raise HTTPException(status_code=401, detail="Credenciales no válidas")
    except PartialCredentialsError as e:
        raise HTTPException(status_code=401, detail="Credenciales incompletas")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Ruta para subir la foto de perfil de un alumno
@app.post("/alumnos/{id}/fotoPerfil", status_code=200)
async def subir_foto_perfil(id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    object_name = str(uuid.uuid4()) + ".jpg"

    try:
        # Subir archivo a S3
        s3_client.upload_fileobj(
            file.file,
            AWS_BUCKET_NAME,
            object_name,
            ExtraArgs={"ACL": "public-read", "ContentType": "image/jpeg"},
        )
        foto_url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
        alumno.fotoPerfilUrl = foto_url
        db.commit()
        db.refresh(alumno)
        return {"fotoPerfilUrl": foto_url}
    except FileNotFoundError:
        print("The file was not found")
        raise HTTPException(status_code=400, detail="The file was not found")
    except NoCredentialsError:
        print("Credentials not available")
        raise HTTPException(status_code=400, detail="Credentials not available")
    except PartialCredentialsError:
        print("Incomplete credentials provided")
        raise HTTPException(status_code=400, detail="Incomplete credentials provided")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    
#Parte de dinamoDB
@app.post("/alumnos/{id}/session/login")
async def login(id: int, password: str, db: Session = Depends(get_db)):
    # Verificar si el alumno existe
    alumno = db.query(Alumno).filter(Alumno.id == id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    # Comparar la contraseña
    if alumno.password != password:
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")

    # Crear la sesión en DynamoDB
    session_id = str(uuid.uuid4())
    session_string = ''.join(random.choices(string.ascii_letters + string.digits, k=128))
    timestamp = int(time.time())

    try:
        dynamodb_resource.put_item(
            TableName=DYNAMODB_TABLE_NAME,
            Item={
                "id": {"S": session_id},
                "fecha": {"N": str(timestamp)},
                "alumnoId": {"N": str(id)},
                "active": {"BOOL": True},
                "sessionString": {"S": session_string},
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear la sesión: {e}")

    return {"sessionString": session_string}

@app.post("/alumnos/{id}/session/verify")
async def verify_session(id: int, session_string: str):
    try:
        response = dynamodb_resource.scan(
            TableName=DYNAMODB_TABLE_NAME,
            FilterExpression="alumnoId = :id AND sessionString = :sessionString",
            ExpressionAttributeValues={
                ":id": {"N": str(id)},
                ":sessionString": {"S": session_string},
            }
        )

        if not response["Items"]:
            raise HTTPException(status_code=400, detail="Sesión no encontrada o inválida")

        session = response["Items"][0]
        if not session["active"]["BOOL"]:
            raise HTTPException(status_code=400, detail="Sesión inactiva")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al verificar la sesión: {e}")

    return {"message": "Sesión válida"}

@app.post("/alumnos/{id}/session/logout")
async def logout(id: int, session_string: str):
    try:
        response = dynamodb_resource.scan(
            TableName=DYNAMODB_TABLE_NAME,
            FilterExpression="alumnoId = :id AND sessionString = :sessionString",
            ExpressionAttributeValues={
                ":id": {"N": str(id)},
                ":sessionString": {"S": session_string},
            }
        )

        if not response["Items"]:
            raise HTTPException(status_code=400, detail="Sesión no encontrada")

        # Actualizar el estado de la sesión a inactiva
        session_id = response["Items"][0]["id"]["S"]
        dynamodb_resource.update_item(
            TableName=DYNAMODB_TABLE_NAME,
            Key={"id": {"S": session_id}},
            UpdateExpression="SET active = :inactive",
            ExpressionAttributeValues={":inactive": {"BOOL": False}},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cerrar la sesión: {e}")

    return {"message": "Sesión cerrada correctamente"}
# **Rutas para Profesores**

# Ruta para obtener todos los profesores
@app.get("/profesores", response_model=List[Profesor])
async def obtener_profesores(db: Session = Depends(get_db)):
    profesores = db.query(ProfesorDB).all()
    return profesores

# Ruta para obtener un profesor por su ID
@app.get("/profesores/{id}", response_model=Profesor)
async def obtener_profesor(id: int, db: Session = Depends(get_db)):
    profesor = db.query(ProfesorDB).filter(ProfesorDB.id == id).first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return profesor

# Ruta para crear un profesor
@app.post("/profesores", response_model=Profesor, status_code=201)
async def crear_profesor(profesor: Profesor, db: Session = Depends(get_db)):
    db_profesor = ProfesorDB(**profesor.dict())
    db.add(db_profesor)
    db.commit()
    db.refresh(db_profesor)
    return db_profesor

# Ruta para actualizar un profesor
@app.put("/profesores/{id}", response_model=Profesor)
async def actualizar_profesor(id: int, profesor: Profesor, db: Session = Depends(get_db)):
    db_profesor = db.query(ProfesorDB).filter(ProfesorDB.id == id).first()
    if not db_profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    for key, value in profesor.dict(exclude_unset=True).items():
        setattr(db_profesor, key, value)
    db.commit()
    db.refresh(db_profesor)
    return db_profesor

# Ruta para eliminar un profesor
@app.delete("/profesores/{id}", status_code=200)
async def eliminar_profesor(id: int, db: Session = Depends(get_db)):
    db_profesor = db.query(ProfesorDB).filter(ProfesorDB.id == id).first()
    if not db_profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    db.delete(db_profesor)
    db.commit()
    return

# Manejador de excepciones para errores de validación
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [{"loc": err["loc"], "msg": err["msg"]} for err in exc.errors()]
    return JSONResponse(
        status_code=400,
        content={"detail": "Campos incorrectos o inválidos", "errors": errors},
    )
