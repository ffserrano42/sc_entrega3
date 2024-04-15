import base64
import datetime
import subprocess
import pika, sys, os, json,traceback
import io
import re
from subprocess import Popen, PIPE
import requests
from sqlalchemy import Date, DateTime, ForeignKey, LargeBinary, Text, create_engine, Column, Integer, String, select, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session,relationship

RABBITMQ_URL =os.environ.get('RABBITMQ_URL', '34.176.60.161')# colocar la ip privada de la maquina donde esta el rabbit
DATABASE_URL = os.environ.get('DATABASE', "postgresql://api:Uniandes2025!@34.176.133.163:5432/converter")# colocar la ip privada del servidor de postgress
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

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_URL,5672))
    channel = connection.channel()
    def get_db():
        db = SessionLocal()
        try:
            return db
        finally:
            db.close()

   
    def obtain_pdf(id_document):
        db=get_db()
        try:
            print(f" deberia ir a procesar el documento con id : {id_document}")
            book = db.query(DocumentModel).filter(DocumentModel.id_document == id_document).first()
            if book:                           
                try:
                    upload_folder = os.environ.get("TOCONVERT","remote_folder/")
                    name_output = re.sub(r'\.(xlsx|pptx|docx|odt)$', '.pdf', book.source_filename)
                    #Opcion que funciona si no se ejecuta desde un contenedor
                        #source_file_without_first_slash = book.source_file.replace('/', '', 1)# se elimina el primer slash de la base de datos, ya que el comando no sirve sin este                    
                    #Opcion que funciona si no se ejecuta desde un contenedor
                        #subprocess.call(['sudo','soffice', '--headless', '--convert-to', 'pdf', '--outdir', upload_folder, source_file_without_first_slash])                                        
                    #Opcion que funciona si se ejecuta desde un contenedor
                    source_file_without_first_slash=book.source_file
                    print(f"soffice --headless --convert-to pdf --outdir {upload_folder} {source_file_without_first_slash}")
                    subprocess.call(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', upload_folder, source_file_without_first_slash])
                    print(f"El archivo {book.source_file} ha sido convertido a PDF correctamente.")
                    book.converted_datetime = datetime.datetime.now()
                    book.status = "Disponible"
                    book.pdf_file = f"/{upload_folder}{name_output}"# se debe colocar el '/' al inicio para que el api pueda leerlo
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
   
    def callback(ch, method, properties, body):
        data = json.loads(body)
        name = data.get("id_book")      
        obtain_pdf(name)
    try:
        channel.basic_consume(queue='pdfs',
                            auto_ack=True,
                            on_message_callback=callback)
        print(' [*] Esperando mensajes, oprime CTRL+C para salir')
        channel.start_consuming()
    except pika.exceptions.ChannelClosedByBroker:
        print("La cola 'pdfs' no existe. Esperando...")        

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)