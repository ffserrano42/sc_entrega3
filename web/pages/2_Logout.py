import streamlit as st
import time
import numpy as np

if st.session_state["Loged"] =="Loged":
    #st.title("Logout")
    #submit = st.button("LogOut")
    #if submit:
        st.session_state["Loged"] = "NotLoged"
        st.session_state.category=""
        st.success("Desconectado satisfactoriamente")
else:
    st.title("Para poder hacer Logout, debes primero hacer Login")