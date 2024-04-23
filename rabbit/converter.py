import base64
import datetime
from pathlib import Path
import subprocess
import pika, sys, os, json,traceback
import io
import re
from subprocess import Popen, PIPE
import requests
from sqlalchemy import Date, DateTime, ForeignKey, LargeBinary, Text, create_engine, Column, Integer, String, select, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session,relationship
from google.cloud import pubsub_v1
from google.cloud import storage
from google.oauth2 import service_account
from google.cloud import pubsub_v1

DATABASE_URL = os.environ.get('DATABASE', "postgresql://api:Uniandes2025!@104.197.133.154:5432/converter")# colocar la ip privada del servidor de postgress
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
    
def get_google_credentials(credentials_file_path):
    credentials = service_account.Credentials.from_service_account_file(credentials_file_path)
    return credentials

def callback(message):
        data = json.loads(message.data.decode("utf-8"))
        name = data.get("id_book")
        print(f"{name} ha sido recibido")
        message.ack() # Se debe acusar primero, ya que si se levanta una nueva VM, este mensaje se vuelve a tomar y satura otra maquina
        obtain_pdf(name)        

def obtain_pdf(id_document):
        db=get_db()
        try:
            print(f" deberia ir a procesar el documento con id : {id_document}")
            book = db.query(DocumentModel).filter(DocumentModel.id_document == id_document).first()
            if book:                           
                try:
                    service_account_acces=os.environ.get("SERVICE_ACCOUNT","False")
                    if(service_account_acces=="False"):#Se valida si se debe acceder con una cuenta de servicio o con las cuentas del json
                        credentials = get_google_credentials("prime-bridge-418615-bb8381a0df5a.json")
                        client = storage.Client(credentials=credentials)
                    else:
                        client = storage.Client()
                    bucket_name = os.environ.get("BUCKET_NAME", "sc-entrega3_2")
                    bucket = client.bucket(bucket_name)
                    blob = bucket.blob(book.source_filename)
                    base_folder="downloads"
                    path_folder = f'./{base_folder}'
                    # Create this folder locally if it does not exist
                    # parents=True will create intermediate directories if they do not exist
                    Path(path_folder).mkdir(parents=True, exist_ok=True)
                    blob.download_to_filename(f'{path_folder}/{blob.name}')
                    print(blob.path)
                    #upload_folder = os.environ.get("TOCONVERT","remote_folder/")
                    #name_output = re.sub(r'\.(xlsx|pptx|docx|odt)$', '.pdf', book.source_filename)                    
                    #source_file_without_first_slash=book.source_file
                    print(f"soffice --headless --convert-to pdf --outdir {base_folder}/ {base_folder}/{blob.name}")
                    subprocess.call(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', base_folder+"/", base_folder+'/'+blob.name])
                    print(f"El archivo {book.source_file} ha sido convertido a PDF correctamente.")
                    pdf_filename = re.sub(r'\.(pptx|docx|xlsx|odt)$', '.pdf', blob.name)
                    pdf_blob = bucket.blob(pdf_filename)
                    pdf_blob.upload_from_filename(f"{path_folder}/{pdf_filename}")                    
                    print(f"El archivo {pdf_filename} ha sido subido a Google Cloud Storage correctamente.")
                    book.converted_datetime = datetime.datetime.now()
                    book.status = "Disponible"
                    book.pdf_file = f"https://storage.cloud.google.com/{bucket.name}/{pdf_blob.name}"# se debe colocar el '/' al inicio para que el api pueda leerlo
                    db.commit()
                    db.refresh(book)
                    print("Document converted to PDF and saved successfully.")
                    delete_files=os.environ.get("DELETE_FILES","False")
                    if(delete_files=="True"):
                        print(f"Eliminando archivos {path_folder}/{blob.name} y {path_folder}/{pdf_filename}")
                        os.remove(f"{path_folder}/{blob.name}")
                        os.remove(f"{path_folder}/{pdf_filename}")
                except Exception as e:
                    excepcion_completa = traceback.format_exc()
                    print(f"Error al convertir el archivo {book.source_file} a PDF:", e)
                    book.converted_datetime = datetime.datetime.now()
                    book.status = f"Error: {excepcion_completa}"                    
                    db.commit()
                    db.refresh(book)                                                   
            else:
                print("No se encontró el libro en la base de datos.")
        finally:
         db.close()

def get_db():
        db = SessionLocal()
        try:
            return db
        finally:
            db.close()

def main():
    # Crea un suscriptor para el tópico en GCP    
    service_account_acces=os.environ.get("SERVICE_ACCOUNT","False")
    if(service_account_acces=="False"):#Se valida si se debe acceder con una cuenta de servicio o con las cuentas del json
        credentials = get_google_credentials("prime-bridge-418615-bb8381a0df5a.json")
        subscriber = pubsub_v1.SubscriberClient(credentials=credentials)
    else:
        subscriber = pubsub_v1.SubscriberClient()    
    subscription_path = subscriber.subscription_path(os.environ.get("PROJECT_ID","prime-bridge-418615"), os.environ.get("PROJECT_SUSCRIPTION","pdf_entrega3-sub"))      
    # Inicia la escucha de mensajes
    subscriber.subscribe(subscription_path, callback=callback)
    print('Esperando mensajes, presiona Ctrl+C para salir')
    import time
    while True:
        time.sleep(60)
    


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)