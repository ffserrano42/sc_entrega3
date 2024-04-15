# Usa la imagen oficial de Python con Streamlit
FROM python:3.10

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de la aplicación al contenedor
COPY ./requirements.txt /app/requirements.txt
COPY . /app

# Instala las dependencias
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Expone el puerto en el que se ejecutará la aplicación Streamlit
EXPOSE 8501

# Comando para ejecutar la aplicación Streamlit
CMD ["streamlit", "run", "Login.py"]