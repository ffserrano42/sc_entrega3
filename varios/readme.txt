Decargar las siguientes imagenes
docker pull ffserrano42/api:04202024 --> imagen de fastapi
docker pull ffserrano42/t1_streamlit:02192024--> Imagen del streamlit
docker pull ffserrano42/converter:04202024--> Consumidor de la cola
En este caso NO es necesario descargar la imagen de la base de datos, porque se utiliza el servicio de SQL de GCP
En este caso NO es neceario instalar redes, ya que cada contenedor, estara en una MV diferente, y se conocen solo por la IP privada

Comandos de docker utiles:
docker build -t [tagName] .  -->para construir la imagen de docker y colocarle el nombre de una vez (es recomendable que el nombre sea [accountdocker]/[imagename]:[version])
docker images-->obtiene las imagenes descargadas
docker ps -a -->obtiene los contenedores (corriendo o detenidos)
docker rm [id del contenedor] --> elimina el contenedor
docker rmi [id de la imagen] --> elimina la imagen
docker tag 1234567890ab mi_app:v1.0--Sirve para poner el tag mi_app:v1.0 a la imagen con id 1234567890ab
docker stop [containerid]-->Para un contenedor
docker start [containerid]--> inicia un contenedor.

Comandos linux
1. sudo -->para ejecutar todo con permisos de admin
2. ls -->listar el contenido de un directorio
3. pwd --> obtener la ruta actual donde esta ubicado el usuario.
5. Para instalar libreoffice--> sudo apt install libreoffice
6. para conertir un archivo a PDF utilizando libreoffice--> sudo soffice --headless --convert-to pdf --outdir remote_folder/ remote_folder/nombre_archivo.pptx

Nuevas variables para configurar en los contenedores:
1. PROJECT_ID = El nombre del proyecto en GCP
2. PROJECT_TOPIC = El nombre del topico en PUB/SUB
3. BUCKET_NAME = El nombre del bucket
4. PROJECT_SUSCRIPTION = el nombre del suscriptor asociado al Topico del PUB/SUB
5. DELETE_FILES = Le indica al worker que despues de cargar el archivo, debe borrar los archivos temporales locales.
6. SERVICE_ACCOUNT = Le indica al codigo si utiliza el service account con el que corre la maquina o si utiliza las credenciales en el codigo (True = Utiliza el service account de la vm, False= utiliza las credenciales del codigo)


Pasos para levantar la app por primera vez desde los contenedores
2. docker run --name fast_api  -p 5001:5001 -d --restart unless-stopped -e DATABASE_URL='postgresql://api:Uniandes2025!@10.194.0.14:5433/converter' -e PROJECT_ID=myfirstproject-417702 -e PROJECT_TOPIC=pdfs -e BUCKET_NAME=sc_entrega3_files -e SERVICE_ACCOUNT=True [id_imagen]
    En las variables de DATABASE_URL debe ir el valor entre ' ya que se tiene el caracter de !
5. docker run --name streamlit -p 8501:8501 -d --restart unless-stopped  -e API_URL=http://10.194.0.2:5001 [id_imagen]
6. docker run --name worker -d --restart unless-stopped -e BUCKET_NAME=sc_entrega3_files -e PROJECT_ID=myfirstproject-417702 -e PROJECT_SUSCRIPTION=pdfs-sub -e DATABASE='postgresql://api:Uniandes2025!@34.176.10.10:5433/converter' -e DELETE_FILES=True -e SERVICE_ACCOUNT=True
        En las variables de DATABASE_URL debe ir el valor entre '' ya que se tiene el caracter de !

Pasos para levanta la app despues de haber corrido los contenedores
Antes se deben haber levantado las VMs en el siguiente orden:
    1. darle start al servicio de SQL de GCP
    3. Levantar la VM del frontend
    4. Levantar la VM del API
    5. Levantar la VM del worker


Comando para ejecutar el proyecto de API
1. Abrir consola
2. ubicarse en la carpeta API
3. uvicorn app:app --port 5001 --reload

Paquetes adicionales a instalar
pip install google-cloud-pubsub-->para el pubsub
pip install google-cloud-storage--> para el bucket

Compando para ejecutar el proyecto de WEB
1. Abrir consola
2. ubicarse en la carpeta WEB
3. streamlit run Login.py

Cuando se ejecute el comando y se quieran para variables de entorno se deben crear con MAYUSCULAS.

se debe instalar pika para el manejo de la cola de rabbitmq
    python -m pip install pika
Se debe instalar chardet para el modulo de la app WEB
    pip install chardet


    

