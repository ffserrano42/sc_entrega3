import base64
import os
import socket
from fastapi import UploadFile
import requests
import streamlit as st
#Url para probar en el computador
api_url = "http://localhost:5001"
#Url para probar con el dockerCompose
#api_url = "http://172.25.0.3:5001"
st.set_page_config(
    page_title="Taller 1",
    page_icon="🤞",
)

if('url' not in st.session_state):
    st.session_state.url=os.environ.get("API_URL","http://34.102.223.159:5001/")


def obtener_datos_desde_api(username, password, email):
    if(username =="Maestria") and (password=="2024"):
        with st.form(key="Ip_contenedor"):
            st.text_input("Direccion ip del contenedor docker api",os.environ.get("API_URL","localhost"),key="Ip_escrita")
            st.form_submit_button(label="Guardar",on_click=ipContenedor)
    else:
        if('url' in st.session_state):
            if(username !="") and (password !=""):
                try:
                    # Realizar la solicitud GET a la API
                    body = {
                        "name": username,
                        "password": password,
                        "email":email
                    }
                    response = requests.post(st.session_state.url+"/usuarios/iniciar-sesion", json=body)
                    # Verificar si la solicitud fue exitosa (código de respuesta 200)
                    if response.status_code == 200:
                        datos = response.json()
                        print(datos)     
                        token = datos['token']
                        user_id = datos['usuario']['id']
                        user_name = datos['usuario']['name']  
                        st.success(f'Bienvenido **{user_name}**, Selecciona la opcion **documentos** del menu izquierdo para ver tus documentos',icon="👍")            
                        st.session_state.Loged="Loged"
                        st.session_state.name=user_name
                        st.session_state.token=token
                        st.session_state.id=user_id
                    else:
                        if response.status_code==401:
                            datos=response.json()
                            mensaje= datos['detail']
                            st.error(f"revisa los datos suminstrados: {mensaje}",icon="🤷‍♀️")
                        st.session_state.Loged=""
                        return None
                except Exception as e:
                    st.error(f"Error: {e}")
                    return None
            else:
                st.error("Debes colocar tu **usuario** tu **password**",icon="😉")
        else:
            st.error("Debes haber completado la **IP del servidor** donde esta almacenado el API",icon="😉")


def registrar():    
    print(f'Registrando un nuevo usuario')
    if('register_name' in st.session_state and 'register_password' in st.session_state and 'register_email' in st.session_state):
        username=st.session_state.register_name
        password=st.session_state.register_password
        email=st.session_state.register_email                        
        print(f'{username},{password},{email}')
        if(username !="") and (password !="") and (email !=""):
            try:
                # Realizar la solicitud GET a la API
                body = {
                    "name": username,
                    "password": password,
                    "email":email
                }
                response = requests.post(st.session_state.url+"/usuarios", json=body)
                # Verificar si la solicitud fue exitosa (código de respuesta 200)
                if response.status_code == 200:
                    # Convertir la respuesta JSON a un DataFrame de pandas
                    datos = response.json() 
                    print(datos)     
                    st.success("Usuario registrado satifactoriamente")
                else:
                    st.error(f"revisa los datos suministrados: {response.status_code}")
                    st.session_state.Loged=""
                    return None
            except Exception as e:
                st.error(f"Error: {e}")
                return None
    

def ipContenedor():
    #print(f"ingresando a configurar ip {st.session_state.Ip_escrita}")
    st.session_state.url=f"http://{st.session_state.Ip_escrita}:5001"
          

def registrarse():
    if ('url' in st.session_state):
        with st.form(key="Registrarse"):
            # Título del componente
            st.title("Registro")
            # Campo para escribir un nombre
            name = st.text_input("Nombre","",key="register_name")
            email=st.text_input("Correo","",key="register_email")
            password = st.text_input("Contraseña","", type="password",key="register_password")                        
            st.form_submit_button(label="Guardar",on_click=registrar)
            st.form_submit_button(label="Cancelar")
    else:
        st.error("Debes haber completado la **IP del servidor** donde esta almacenado el API",icon="😉")
    
if "Loged" not in st.session_state:
    st.session_state["Loged"] = ""
    st.session_state.name=""
    st.session_state.token=""
    st.session_state.id=""

if st.session_state["Loged"]=="Loged":
     st.title("Ya has realizado Login, favor hacer logout.")

 # Campos de entrada para usuario y contraseña
if st.session_state["Loged"] !="Loged":
    st.title("Login")
    username = st.text_input("Usuario", "")
    email =st.text_input("Correo","")
    password = st.text_input("Contraseña", "", type="password")
    submit = st.button("Login")    
    if submit:
        obtener_datos_desde_api(username, password,email)
    st.button("Registrarse",on_click=registrarse)
    

                     
    
