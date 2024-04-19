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

RABBITMQ_URL =os.environ.get('RABBITMQ_URL', '34.176.60.161')# colocar la ip privada de la maquina donde esta el rabbit
DATABASE_URL = os.environ.get('DATABASE', "postgresql://api:Uniandes2025!@34.176.96.127:5433/converter")# colocar la ip privada del servidor de postgress
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

def callback2(message):
        data = json.loads(message.data.decode("utf-8"))
        name = data.get("id_book")
        print(f"{name} ha sido recibido")
        obtain_pdf(name)
        message.ack()

def obtain_pdf(id_document):
        db=get_db()
        try:
            print(f" deberia ir a procesar el documento con id : {id_document}")
            book = db.query(DocumentModel).filter(DocumentModel.id_document == id_document).first()
            if book:                           
                try:
                    credentials = get_google_credentials("myfirstproject-417702-6a6d72abcd7b.json")
                    client = storage.Client(credentials=credentials)
                    bucket_name = os.environ.get("BUCKET_NAME", "sc_entrega3_files")
                    bucket = client.bucket(bucket_name)
                    blob = bucket.blob(book.source_filename)
                    path_folder = f'./downloads'
                    # Create this folder locally if it does not exist
                    # parents=True will create intermediate directories if they do not exist
                    Path(path_folder).mkdir(parents=True, exist_ok=True)
                    blob.download_to_filename(f'{path_folder}/{blob.name}')                    
                    upload_folder = os.environ.get("TOCONVERT","remote_folder/")
                    name_output = re.sub(r'\.(xlsx|pptx|docx|odt)$', '.pdf', book.source_filename)                    
                    source_file_without_first_slash=book.source_file
                    print(f"soffice --headless --convert-to pdf --outdir {upload_folder} {path_folder}/{blob.name}")
                    #subprocess.call(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', upload_folder, source_file_without_first_slash])
                    print(f"El archivo {book.source_file} ha sido convertido a PDF correctamente.")
                    pdf_blob = bucket.blob(f"uploaded_example.pdf")
                    pdf_blob.upload_from_filename(f"{path_folder}/uploaded_example.pdf")
                    book.converted_datetime = datetime.datetime.now()
                    book.status = "Disponible"
                    book.pdf_file = f"https://storage.cloud.google.com/{bucket.name}/{pdf_blob.name}"# se debe colocar el '/' al inicio para que el api pueda leerlo
                    db.commit()
                    db.refresh(book)
                    print("Document converted to PDF and saved successfully.")
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
def callback(ch, method, properties, body):
        data = json.loads(body)
        name = data.get("id_book")      
        obtain_pdf(name)
    #try:
    #    channel.basic_consume(queue='pdfs',
    #                        auto_ack=True,
    #                        on_message_callback=callback)
    #    print(' [*] Esperando mensajes, oprime CTRL+C para salir')
    #    channel.start_consuming()
    #except pika.exceptions.ChannelClosedByBroker:
    #    print("La cola 'pdfs' no existe. Esperando...")    

def main():
    #connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_URL,5672))
    #channel = connection.channel()
    # Crea un suscriptor para el tópico en GCP
    credentials = get_google_credentials("myfirstproject-417702-6a6d72abcd7b.json")
    subscriber = pubsub_v1.SubscriberClient(credentials=credentials)
    subscription_path = subscriber.subscription_path(os.environ.get("PROJECT_ID","myfirstproject-417702"), os.environ.get("PROJECT_SUSCRIPTION","pdfs-sub"))      
    # Inicia la escucha de mensajes
    subscriber.subscribe(subscription_path, callback=callback2)
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