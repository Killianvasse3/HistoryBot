import streamlit as st
from config import Config
from helpers.llm_helper import chat, stream_parser

st.set_page_config(
    page_title="Eliot - statistique",
    initial_sidebar_state="expanded"
)

st.title("Eliot - statistique")

st.markdown(" Votre ami d'apprentissage interactif ! Plongez dans l'histoire, testez vos connaissances avec des quiz captivants et découvrez de nouvelles perspectives à chaque question. Transformez vos révisions en une aventure passionnante !")
st.markdown("""\n""")