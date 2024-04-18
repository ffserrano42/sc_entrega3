Decargar las siguientes imagenes
docker pull ffserrano42/api:04172024 --> imagen de fastapi
docker pull ffserrano42/t1_streamlit:02192024--> Imagen del streamlit
docker pull ffserrano42/consumer:24032024--> Consumidor de la cola
En este caso NO es necesario descargar la imagen de la base de datos, porque se utiliza el servicio de SQL de GCP
En este caso NO es neceario instalar redes, ya que cada contenedor, estara en una MV diferente, y se conocen solo por la IP privada

Comandos de docker utiles
docker inspect network [Nombre red]-->obtiene los contenedores conectados a esa red, y asi obtener las ips
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' [ID del contenedor] -->obtiene la IP que Docker le asigno al contenedor
docker images-->obtiene las imagenes descargadas
docker ps -a -->obtiene los contenedores (corriendo o detenidos)
docker rm [id del contenedor] --> elimina el contenedor
docker rmi [id de la imagen] --> elimina la imagen
docker tag 1234567890ab mi_app:v1.0--Sirve para poner el tag mi_app:v1.0 a la imagen con id 1234567890ab
-v c:/to_convert:/input sirve para montar una ruta local a uno en la maquina virtual en docker

Comandos linux
1. sudo -->para ejecutar todo con permisos de admin
2. ls -->listar el contenido de un directorio
3. pwd --> obtener la ruta actual donde esta ubicado el usuario.
5. Para instalar libreoffice--> sudo apt install libreoffice
6. para conertir un archivo a PDF utilizando libreoffice--> sudo soffice --headless --convert-to pdf --outdir remote_folder/ remote_folder/nombre_archivo.pptx


Nuevas variables para configurar en los contenedores:
1. TOCONVERT -->Ruta local donde se deben escribir los archivos. debe tener el mismo nombre del folder que esta en el servidor del worker y se debe llamar remote_folder/ y debe ser el mismo que se monto el nfs
En el API el valor TOCONVERT debe iniciar con el / por ejemplo {/remote_folder} en el consumer debe finalizar {remote_folder/}


ips privadas de GCP fs:
1. API: 10.194.0.2
2. worker/rabbitmq: 10.194.0.5
3. nfs: 10.194.0.4
4. DB_dev: 10.66.192.9

Pasos para levantar la app por primera vez
2. docker run --name fast_api  -p 5001:5001 -d --restart unless-stopped -e DATABASE_URL='postgresql://api:Uniandes2025!@10.194.0.14:5433/converter' -e PROJECT_ID=myfirstproject-417702 -e PROJECT_TOPIC=pdfs -e BUCKET_NAME=sc_entrega3_files [id_imagen]
    En las variables de DATABASE_URL debe ir el valor entre ' ya que se tiene el caracter de !
5. docker run --name streamlit -p 8501:8501 -d --restart unless-stopped  -e API_URL=http://10.194.0.2:5001 [id_imagen]
6. docker run --name consumer --privileged -e RABBITMQ_URL=10.194.0.5 -e DATABASE='postgresql://api:Uniandes2025!@10.66.192.9:5432/converter' -e TOCONVERT=remote_folder/ -v /home/zedano/remote_folder:/remote_folder [id_imagen]
        En las variables de DATABASE_URL debe ir el valor entre '' ya que se tiene el caracter de !



Pasos para levanta la app despues de haber corrido los contenedores
Antes se deben haber levantado las VMs en el siguiente orden:
    1. darle start al servicio de SQL de GCP
    2. Levantar la VM del servidor nfs
    3. Levantar la VM del frontend
    4. Levantar la VM del API
    5. Levantar la VM del worker

En cada VM se debe:
    1. Obtener el listado de todos los contenedores con docker ps -a
    2. Utilizar el comando docker start [id contenedor] para iniciar el contenedor    
    3.1 en la maquina worker se debe iniciar el programa en python (Plan B):
    3.1.1 source venv/bin/activate-->ambiente virtual
    23.1.2 python converter/converter.py-->archivo a ejecutar

Recomendacion!!!
1. Antes de levantar el contenedor del Consumer, haber levantado todos los otros contenedores, logerase en la app y dejar un archivo, esto hara que la cola tenga algun mensaje  y asi el consumer quede "activo".


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


    

