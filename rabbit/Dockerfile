# Usa una imagen base de Python
FROM python:3.11

# Establece el directorio de trabajo como root
#WORKDIR /app
WORKDIR /

# Actualiza el índice de los paquetes disponibles e instala las dependencias necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos de la aplicación al contenedor
#COPY ./requirements.txt /app/requirements.txt
#COPY . /app

COPY ./requirements.txt /requirements.txt
COPY . /

# Instala las dependencias
RUN pip install --no-cache-dir --upgrade -r /requirements.txt

# Define el comando predeterminado para ejecutar tu programa cuando se inicie el contenedor
CMD ["python", "converter.py"]