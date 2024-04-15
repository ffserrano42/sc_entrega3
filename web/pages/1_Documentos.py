import base64
from io import StringIO
import requests
import streamlit as st
import pandas as pd
import datetime
import os
import chardet
#Url para probar en el computador con el docker compose
api_url = "http://localhost:5001"
#Url para probar con el dockerCompose
#api_url = "http://localhost:5001"

 # Datos de ejemplo para la primera tabla

df_categorias_usuario=pd.DataFrame()
df_tareas_usuario=pd.DataFrame()
api_url=st.session_state.url


def cargar():       
    if('new_doc' in st.session_state):
        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }          
        doc=st.session_state.new_doc
        if(doc is not None):
            bytes = doc.getvalue()
            #file_extension = os.path.splitext(bytes)[1]
            name=doc.name
            string_doc_base64 = base64.b64encode(bytes).decode('utf-8')
            print(string_doc_base64)            
            print(f'name: {name} type {type(string_doc_base64)}')               
            try:
                # Realizar la solicitud GET a la API
                body = {
                            "id_user": st.session_state.id,
                            "source_filename": name,
                            "source_file": string_doc_base64,
                            "source_file_extension":"any"
                        }
                response = requests.post(st.session_state.url+"/uploadDoc",headers=headers, json=body)
                # Verificar si la solicitud fue exitosa (código de respuesta 200)
                if response.status_code == 200:
                    # Convertir la respuesta JSON a un DataFrame de pandas
                    datos = response.json() 
                    print(datos)     
                    st.success("documento cargado satifactoriamente")
                else:
                    st.error(f"revisa los datos suministrados: {response.status_code}")
                    st.session_state.Loged=""
                    return None
            except Exception as e:
                st.error(f"Error: {e}")
                return None

def descargaroriginal():
    if 'id_doc' in st.session_state:
        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }
        try:
            id_doc=st.session_state.id_doc
            print(id_doc)
            response = requests.get(st.session_state.url+f"/originalDoc/{id_doc}",headers=headers)
            # Verificar si la solicitud fue exitosa (código de respuesta 200)
            if response.status_code == 200:
                # Convertir la respuesta JSON a un DataFrame de pandas
                datos = response.json()
                #print(datos)
                nombre_archivo = datos["source_filename"]                
                datos_base64 = datos["source_file"]
                datos_bytes = base64.b64decode(datos_base64)
                #print (f"{nombre_archivo}, {datos_bytes}")
                with st.spinner("Preparando archivo para descarga..."):
                    # Utilizar file_downloader para permitir al usuario seleccionar la ubicación de descarga
                    st.download_button(label="Descargar archivo original",data=datos_bytes,file_name=nombre_archivo)                                     
            else:
                st.error(f"revisa los datos suministrados: {response.status_code}")
                return None
        except Exception as e:
            st.error(f"Error: {e}")
            return None

def descargarPdf():
    if 'id_docpdf' in st.session_state:
        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }
        try:
            id_docpdf=st.session_state.id_docpdf
            print(id_docpdf)
            response = requests.get(st.session_state.url+f"/convertidoDoc/{id_docpdf}",headers=headers)
            # Verificar si la solicitud fue exitosa (código de respuesta 200)
            if response.status_code == 200:
                # Convertir la respuesta JSON a un DataFrame de pandas
                datos = response.json()
                #print(datos)                
                datos_base64 = datos["pdf_file"]
                datos_bytes = base64.b64decode(datos_base64)
                #print (f"{nombre_archivo}, {datos_bytes}")
                with st.spinner("Preparando archivo para descarga..."):
                    # Utilizar file_downloader para permitir al usuario seleccionar la ubicación de descarga
                    st.download_button(label="Descargar archivo PDF",data=datos_bytes,file_name="convertido.pdf")                                     
            else:
                if response.status_code==404:
                    datos = response.json()
                    st.error(f"{datos['detail']}")
                else:
                    st.error(f"{response.status_code}")                
        except Exception as e:
            st.error(f"Error: {e}")         

def EliminarDocumento():
    if st.session_state.id_docdelete!="":
        headers = {
        "Authorization": f"Bearer {st.session_state.token}"
        }        
        try:
            response=requests.delete(api_url+f"/removeDoc/{st.session_state.id_docdelete}",headers=headers)          
            if response.status_code == 200:                
                datos=response.json()
                st.success("Documento eliminado correctamente")
            else:
                if response.status_code == 404:
                    datos=response.json()
                    st.error(datos['detail'])
        except Exception as e:
            print(f'{e}')
            st.error(f"Error: {e}")
    else:
        print(st.session_state.id)


def documentsbyUser():
    #print("obteniendo categoria por usuarios")
    if st.session_state.id!="":
        headers = {
        "Authorization": f"Bearer {st.session_state.token}"
        }        
        try:
            response=requests.get(api_url+f"/documentos?user_id={st.session_state.id}",headers=headers)          
            if response.status_code == 200:                
                datos=response.json()
                #print(f'datos: {datos}')
                df_categorias_usuario=pd.DataFrame(datos)
                return df_categorias_usuario                
        except Exception as e:
            print(f'{e}')
            st.error(f"Error: {e}")
            return None
    else:
        print(st.session_state.id)

if st.session_state["Loged"] == "Loged": 
    with st.form(key="Cargar Documento"):
            # Título del componente
            st.title("Cargar nuevo documento")
            # Campo para escribir un nombre                        
            uploaded_file = st.file_uploader("Seleccionar un archivo", type=["docx", "pptx", "xlsx", "odt"],key="new_doc")        
            st.form_submit_button(label="Guardar",on_click=cargar)
            st.form_submit_button(label="Cancelar")    
    #with st.form(key="documentos"):
    cols_diplsay=['id_document','source_filename','status','upload_datetime','converted_datetime']
    df=documentsbyUser()
    if(df is not None and len(df)>0):
        st.title("Documentos en tu cuenta")
        st.table(df[cols_diplsay])
    if st.button("Refrescar"):
        st.rerun()
    with st.form(key="Descargar Original"):
        st.text_input("Id del documento",key="id_doc")
        st.form_submit_button(label="Descargar",on_click=descargaroriginal)

    with st.form(key="Descargar pdf"):
        st.text_input("Id del documento",key="id_docpdf")
        st.form_submit_button(label="Descargarpdf",on_click=descargarPdf)

    with st.form(key="Eliminar Documento"):
        st.text_input("Id del documento",key="id_docdelete")
        st.form_submit_button(label="Eliminar",on_click=EliminarDocumento)
else:
     st.error("Debes realizar primer **Login** en la opcion del menu izquierdo",icon="👍")        

