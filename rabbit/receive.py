import base64
import datetime
import pika, sys, os, json
#import pdfkit
import io
from spire.xls import *
from spire.xls.common import *


from sqlalchemy import Date, DateTime, ForeignKey, LargeBinary, Text, create_engine, Column, Integer, String, select, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session,relationship

RABBITMQ_URL =os.environ.get('RABBITMQ_URL', 'localhost')
DATABASE_URL = os.environ.get('DATABASE', "postgresql://postgres:1234@localhost:5433/sc_taller1")
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DocumentModel(Base):
    __tablename__ = "Documents"
    id_document = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer,nullable=False)
    source_filename = Column(String,nullable=False)
    source_file = Column(LargeBinary,nullable=False)
    source_file_extension=Column(String,nullable=False)
    pdf_file= Column(LargeBinary,nullable=True)
    status=Column(String,nullable=False)
    upload_datetime=Column(Date, nullable=False)
    converted_datetime=Column(Date, nullable=True)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_URL))
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
                # Decodificar los bytes del archivo fuente en base64 a los bytes originales yconvertirlo en pdf
                datos_bytes = base64.b64decode(book.source_file)
                with open(book.source_filename, "wb") as temp_file:
                    temp_file.write(datos_bytes)
                    ruta_temp=temp_file.name
                workbook = Workbook()
                workbook.LoadFromFile(ruta_temp)
                workbook.SaveToFile("output/ToPdf.pdf", FileFormat.PDF)
                workbook.Dispose()
                ruta_pdf = "output/ToPdf.pdf"
                with open(ruta_pdf, "rb") as archivo_pdf:
                    bytes_pdf = archivo_pdf.read()                
                book.pdf_file=bytes_pdf                
                book.converted_datetime = datetime.datetime.now()
                book.status = "Disponible"
                # Commit the changes to the database
                db.commit()
                db.refresh(book)
                print("Document converted to PDF and saved successfully.")                
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
        print(' [*] Esperando mensajes, oprie CTRL+C para salir')
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