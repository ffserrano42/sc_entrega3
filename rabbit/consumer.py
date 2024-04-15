import base64
import datetime
import pika, sys, os, json
import requests
from sqlalchemy import DateTime, LargeBinary, create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

try:
    RABBITMQ_URL =os.environ.get('RABBIT', 'ec2-44-203-110-5.compute-1.amazonaws.com')
    DATABASE_URL = os.environ.get('DATABASE_URL', "postgresql://postgres:123@ec2-44-203-110-5.compute-1.amazonaws.com:5432/sc_taller1")
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()

    class DocumentModel(Base):
        __tablename__ = "Documents"
        id_document = Column(Integer, primary_key=True, index=True)
        id_user = Column(Integer,nullable=False)
        source_filename = Column(String,nullable=False)
        source_file = Column(LargeBinary,nullable=False)
        source_file_extension=Column(String,nullable=False)
        pdf_file= Column(LargeBinary,nullable=True)
        status=Column(String,nullable=False)
        upload_datetime=Column(DateTime, nullable=False)
        converted_datetime=Column(DateTime, nullable=True)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"Error al crear la base de datos: {e}")
    sys.exit(1)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_URL,5672))
    channel = connection.channel()
    def get_db():
        db = SessionLocal()
        try:
            return db
        finally:
            db.close()
  
    def obtain_pdf_convertapi(id_document):
        db=get_db()
        try:
            print(f" deberia ir a procesar el documento con id : {id_document}")
            book = db.query(DocumentModel).filter(DocumentModel.id_document == id_document).first()
            if book:
                # Decodificar los bytes del archivo fuente en base64 a los bytes originales yconvertirlo en pdf
                datos_bytes = base64.b64decode(book.source_file)# haria falta obtener el pdf y guardarlo en base de datos
                if(book.source_filename.endswith(".pptx")):
                    url = "https://v2.convertapi.com/convert/ppt/to/pdf?Secret=GVUuAKrBAROgbUkE"
                    headers = {"Content-Type": "application/json"}
                    data = {
                        "Parameters": [
                            {
                                "Name": "File",
                                "FileValue": {
                                    "Name": book.source_filename,
                                    "Data": base64.b64encode(datos_bytes).decode("utf-8")
                                }
                            },
                            {
                                "Name": "StoreFile",
                                "Value": True
                            }
                        ]
                    }
                    response = requests.post(url, json=data, headers=headers)
                    # Verificar la respuesta
                    if response.status_code == 200:
                        print("La conversión se ha realizado correctamente.")
                        url_converted_pdf=response.json().get("Files")[0].get("Url")
                        response_pdf = requests.get(url_converted_pdf)
                        book.pdf_file=response_pdf.content                
                        book.converted_datetime = datetime.datetime.now()
                        book.status = "Disponible"
                        db.commit()
                        db.refresh(book)
                        print("Document converted to PDF and saved successfully.") 
                    else:
                        print(f"Error al convertir el archivo. Código de estado: {response.status_code}")
                        print(response.text)
                        book.converted_datetime = datetime.datetime.now()
                        book.status = "Error"
                        db.commit()
                        db.refresh(book)
                elif(book.source_filename.endswith(".docx")):
                    url = "https://v2.convertapi.com/convert/docx/to/pdf?Secret=GVUuAKrBAROgbUkE"
                    headers = {"Content-Type": "application/json"}
                    data = {
                        "Parameters": [
                            {
                                "Name": "File",
                                "FileValue": {
                                    "Name": book.source_filename,
                                    "Data": base64.b64encode(datos_bytes).decode("utf-8")
                                }
                            },
                            {
                                "Name": "StoreFile",
                                "Value": True
                            }
                        ]
                    }
                    response = requests.post(url, json=data, headers=headers)
                    # Verificar la respuesta
                     # Verificar la respuesta
                    if response.status_code == 200:
                        print("La conversión se ha realizado correctamente.")
                        url_converted_pdf=response.json().get("Files")[0].get("Url")
                        response_pdf = requests.get(url_converted_pdf)
                        book.pdf_file=response_pdf.content                
                        book.converted_datetime = datetime.datetime.now()
                        book.status = "Disponible"
                        db.commit()
                        db.refresh(book)
                        print("Document converted to PDF and saved successfully.") 
                    else:
                        print(f"Error al convertir el archivo. Código de estado: {response.status_code}")
                        print(response.text)
                        book.converted_datetime = datetime.datetime.now()
                        book.status = "Error"
                        db.commit()
                        db.refresh(book)
                elif(book.source_filename.endswith(".xlsx")):
                    url = "https://v2.convertapi.com/convert/xlsx/to/pdf?Secret=GVUuAKrBAROgbUkE"
                    headers = {"Content-Type": "application/json"}
                    data = {
                        "Parameters": [
                            {
                                "Name": "File",
                                "FileValue": {
                                    "Name": book.source_filename,
                                    "Data": base64.b64encode(datos_bytes).decode("utf-8")
                                }
                            },
                            {
                                "Name": "StoreFile",
                                "Value": True
                            }
                        ]
                    }
                    response = requests.post(url, json=data, headers=headers)
                    # Verificar la respuesta
                     # Verificar la respuesta
                    if response.status_code == 200:
                        print("La conversión se ha realizado correctamente.")
                        url_converted_pdf=response.json().get("Files")[0].get("Url")
                        response_pdf = requests.get(url_converted_pdf)
                        book.pdf_file=response_pdf.content                
                        book.converted_datetime = datetime.datetime.now()
                        book.status = "Disponible"
                        db.commit()
                        db.refresh(book)
                        print("Document converted to PDF and saved successfully.") 
                    else:
                        print(f"Error al convertir el archivo. Código de estado: {response.status_code}")
                        print(response.text)
                        book.converted_datetime = datetime.datetime.now()
                        book.status = "Error"
                        db.commit()
                        db.refresh(book)
                elif(book.source_filename.endswith(".odt")):
                    url = "https://v2.convertapi.com/convert/odt/to/pdf?Secret=GVUuAKrBAROgbUkE"
                    headers = {"Content-Type": "application/json"}
                    data = {
                        "Parameters": [
                            {
                                "Name": "File",
                                "FileValue": {
                                    "Name": book.source_filename,
                                    "Data": base64.b64encode(datos_bytes).decode("utf-8")
                                }
                            },
                            {
                                "Name": "StoreFile",
                                "Value": True
                            }
                        ]
                    }
                    response = requests.post(url, json=data, headers=headers)
                    # Verificar la respuesta
                     # Verificar la respuesta
                    if response.status_code == 200:
                        print("La conversión se ha realizado correctamente.")
                        url_converted_pdf=response.json().get("Files")[0].get("Url")
                        response_pdf = requests.get(url_converted_pdf)
                        book.pdf_file=response_pdf.content                
                        book.converted_datetime = datetime.datetime.now()
                        book.status = "Disponible"
                        db.commit()
                        db.refresh(book)
                        print("Document converted to PDF and saved successfully.") 
                    else:
                        print(f"Error al convertir el archivo. Código de estado: {response.status_code}")
                        print(response.text)
                        book.converted_datetime = datetime.datetime.now()
                        book.status = "Error"
                        db.commit()
                        db.refresh(book)

            else:
                print("No se encontró el libro en la base de datos.")
        finally:
         db.close()

    def callback(ch, method, properties, body):
        data = json.loads(body)
        name = data.get("id_book")      
        obtain_pdf_convertapi(name)
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
        print(' [*] Iniciando el consumidor')
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)