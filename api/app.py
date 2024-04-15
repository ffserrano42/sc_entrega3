import base64
import json
import os
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
import pika
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import Date, DateTime, ForeignKey, LargeBinary, create_engine, Column, Integer, String, select, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session,relationship
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import date, datetime, timedelta
import time
from auth import AuthHandler

#Coneccion para probar con el docker compose
DATABASE_URL = os.environ.get("DATABASE_URL","postgresql://api:Uniandes2025!@34.176.133.163:5432/converter")
  
#Coneccion para probar con el posgress del computador
#DATABASE_URL = "postgresql://postgres:Esposa2021!@localhost:5432/SC_P0"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

auth_handler = AuthHandler()

SECRET_KEY = "tu_clave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 240


#Clases para manejar la conexion a la base de datos
class UsuarioModel(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String,nullable=False)
    password = Column(String,nullable=False)
    email = Column(String, nullable=False)

class DocumentModel(Base):
    __tablename__ = "Documents"
    id_document = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer,nullable=False)
    source_filename = Column(String,nullable=False)
    source_file = Column(String,nullable=False)
    source_file_extension=Column(String,nullable=False)
    pdf_file= Column(String,nullable=True)
    status=Column(String,nullable=False)
    upload_datetime=Column(DateTime, nullable=False)
    converted_datetime=Column(DateTime, nullable=True)

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

tags_metadata = [
    {
        "name": "usuarios",
        "description": "Operacion para crear un usuario, recibe como parametro un JSON que tiene debe ser el usuario password y la imagen",
    },
    {
        "name": "iniciar-sesion",
        "description": "servicio que permite el login de un usuario, con usuario y password, retorna el bearer token a utilizar durante las demas peticiones.",
    },
     {
        "name": "documento",
        "description": "Permite cargar un nuevo documento al usuario",
    },
    {
        "name": "listar documentos",
        "description": "Retorna el listado de **documento** que el usuario tiene almacenados en el sistema",
    },
    {
        "name": "delete_documento" ,
        "description": "Elimina el documento con el **id** y si el documento esta en estado Disponible",
    },
    {
        "name": "listar documentos" ,
        "description": "Obtiene todos los documentos del usuario con **id**",
    },
    {
        "name": "original_documento" ,
        "description": "Obtiene el documento ORIGINAL con el  **id**",
    },
    {
        "name": "convertido_documento" ,
        "description": "Obtiene el documento convertido con el  **id** si esta Disponible y si tiene contenido",
    }    
]

app = FastAPI(openapi_tags=tags_metadata)


# Modelos Pydantic para las operaciones y retorno de datos en las peticiones al API
class Token(BaseModel):
    token: str

class Usuario(BaseModel):
    name: str
    password: str
    email: str = None

class UsuarioResponse(BaseModel):
    id: int
    name: str        

class Documento(BaseModel):    
    id_user: int
    source_filename: str
    source_file: bytes
    source_file_extension:str   


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "https://localhost",
    "http://localhost:4200",
    "http://172.24.99.153:4200",    
    "https://172.24.99.153:4200",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(decoded_token)
        return decoded_token if decoded_token["exp"] >= time.time() else None
    except:
        return {}

#Metodo para generar el token del usuario
def generar_token(data: dict):
    to_encode = data.copy()
    expire = time.time() + ACCESS_TOKEN_EXPIRE_MINUTES
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(encoded_jwt)    
    return encoded_jwt


# Función para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/')
async def heatlh():   
   return {"healthcheck":"ok"}

# Operaciones de Usuario
@app.post("/usuarios",response_model=UsuarioResponse,tags=["usuarios"])
async def crear_usuario(usuario: Usuario, db: Session = Depends(get_db)):
    usuario_existente = db.query(UsuarioModel).filter(UsuarioModel.email == usuario.email).first()    
    # Si usuario_existente no es None, significa que ya existe un usuario con ese correo electrónico
    if usuario_existente:
        raise HTTPException(status_code=404, detail="correo ya registrado")
    else: 
        db_usuario = UsuarioModel(**usuario.dict())
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)
        return UsuarioResponse(id=db_usuario.id,name=db_usuario.name)

#Iniciar sesion, que retorna un usuario y recibe como parametros un name y pass
@app.post("/usuarios/iniciar-sesion", response_model=dict,tags=["iniciar-sesion"])
def iniciar_sesion(usuario_credenciales: Usuario, db: Session = Depends(get_db)):
    db_usuario = (
        db.query(UsuarioModel)
        .filter_by(email=usuario_credenciales.email, password=usuario_credenciales.password)
        .first()
    )
    if db_usuario:
        token = auth_handler.encode_token(db_usuario.email)
        #token = generar_token({"sub": db_usuario.Id})
        return {"token": token,"usuario":UsuarioResponse(id=db_usuario.id,name=db_usuario.name)}
    else:
        # Credenciales incorrectas
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Operaciones de cargar un documento categoria
@app.post("/uploadDoc", response_model=dict,tags=["documento"])
async def crear_documento(doc: Documento , db: Session = Depends(get_db),usermail=Depends(auth_handler.auth_wrapper)):
    try:
        document_data= doc.dict()
        # Decodifica el contenido del archivo de base64 a bytes
        source_file_content = base64.b64decode(document_data["source_file"])
        # Guarda el archivo en disco
        upload_folder = os.environ.get("TOCONVERT","C:/to_convert")
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, document_data["source_filename"])
        with open(file_path, "wb") as file_object:
            file_object.write(source_file_content)
        # Actualiza el campo source_file con la ruta en disco
        document_data["source_file"] = file_path       
        document_db=DocumentModel(**document_data,status ="Pendiente",upload_datetime=datetime.now())    
        db.add(document_db)
        db.commit()
        db.refresh(document_db)
        put_quemessage(document_db.id_document)
        return {"id":document_db.id_document}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=404, detail=f"Error en la base de datos: {str(e)}")
    
#Funcion que coloca en la cola de mensajes el id del documento a procesar.
def put_quemessage(docid):
    try:
        RABBIT = os.environ.get("RABBIT","localhost")
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT))
        channel = connection.channel()
        channel.queue_declare(queue='pdfs')
        data = {
        'id_book': docid    
        }
        # Convert the JSON object to a string
        body = json.dumps(data)
        channel.basic_publish(exchange='',
                            routing_key='pdfs',
                            body=body)
        print(" Mensaje escrito correctamente")
        connection.close()
    except Exception as e:
        print(f"Error en la conexion con el servidor de mensajes: {e}")

#Operacion para eliminar un categoria. Este metodo fallara si la categoria tiene una tarea asignada
@app.delete("/removeDoc/{id}", response_model=dict,tags=["delete_documento"])
async def eliminar_documento(id: int, db: Session = Depends(get_db),username=Depends(auth_handler.auth_wrapper) ):
    documento = db.query(DocumentModel).filter(DocumentModel.id_document == id, DocumentModel.status.in_(['Disponible', 'Error'])).first()      
    # Verificar si se eliminó alguna fila o de lo contrario siempre retornaria que se elimino la categoria
    if documento:
        db.delete(documento)
        db.commit()
        return {"mensaje": "Documento eliminado"}
    else:
        # Si rows_affected no es 1, significa que no se encontró la categoría con ese ID
        raise HTTPException(
            status_code=404,
            detail=f"Documento con ID {id} no encontrado o tiene el estado Pendiente",
        )

#Operacion que permite obtener los documentos pertenecientes al usuario. Si el usuario no documentos, devolvera una lista vacia
@app.get("/documentos",response_model=list, tags=["listar documentos"])
async def obtener_documentos(user_id:int, db: Session = Depends(get_db),username=Depends(auth_handler.auth_wrapper)):
    # Consulta para seleccionar todas las categorías, pero se debe colocar todos los atributos, o de lo contrario no sirve
    documentos_usuario = db.query(DocumentModel).filter(DocumentModel.id_user == user_id).all()         
    if len(documentos_usuario)>0:
        campos_deseados = ['id_document','id_user','source_filename', 'status', 'upload_datetime', 'converted_datetime']
        documentos_dict_list = [] 
        # Iterar sobre los documentos y crear un diccionario con los campos deseados
        for documento in documentos_usuario:
            documento_dict = {campo: getattr(documento, campo) for campo in campos_deseados}
            documentos_dict_list.append(documento_dict)
        return documentos_dict_list
    else:
        print("El usuario no tiene nigun documento")
        tareas_dict_list=[]
        return tareas_dict_list


#Operacion que permite obtener el documento original del usuario.
@app.get("/originalDoc/{doc_id}",response_model=dict,tags=["original_documento"])
async def obtener_original_doc(doc_id: int, db:Session=Depends(get_db),username=Depends(auth_handler.auth_wrapper)):
    documento_usuario = db.query(DocumentModel).filter(DocumentModel.id_document == doc_id).first()    
    if documento_usuario is None:               
        raise HTTPException(status_code=404, detail=f"Documento con ID {id} no encontrado o tiene el estado Pendiente")
    # Obtener la ruta del archivo
    file_path = documento_usuario.source_file    
    # Leer el archivo
    with open(file_path, "rb") as file:
        file_content = file.read()
    # Convertir el contenido del archivo a base64
    file_base64 = base64.b64encode(file_content).decode('utf-8')        
    documento_dict = {
        'id_document': documento_usuario.id_document,
        'source_filename': documento_usuario.source_filename,
        'source_file': file_base64
    }    
    return documento_dict    

#Operacion que permite obtener el documento convertido del usuario.
@app.get("/convertidoDoc/{doc_id}",response_model=dict,tags=["convertido_documento"])
async def obtener_pdf_doc(doc_id: int, db:Session=Depends(get_db),username=Depends(auth_handler.auth_wrapper)):
    documento_usuario = db.query(DocumentModel).filter(DocumentModel.id_document == doc_id,DocumentModel.status == 'Disponible',DocumentModel.pdf_file.isnot(None)).first()    
    if documento_usuario is None:               
        raise HTTPException(status_code=404, detail=f"Revisa que el documento con ID {doc_id} este en estado Disponible")   
    # Obtener la ruta del archivo
    file_path = documento_usuario.pdf_file    
    # Leer el archivo
    with open(file_path, "rb") as file:
        file_content = file.read()
    # Convertir el contenido del archivo a base64
    pdf_base64 = base64.b64encode(file_content).decode('utf-8')
    ###pdf_base64 = base64.b64encode(documento_usuario.pdf_file).decode('utf-8')
    documento_dict = {'pdf_file': pdf_base64}        
    return documento_dict
    