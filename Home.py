import streamlit as st
from config import Config
from helpers.llm_helper import chat, stream_parser
from PIL import Image
from streamlit_option_menu import option_menu

im = Image.open("icon.png")

st.set_page_config(
    page_title=Config.PAGE_TITLE,
    initial_sidebar_state="expanded",
    page_icon=im
)
st.image(im, width=100)
st.title(Config.PAGE_TITLE)

st.markdown(" Votre ami d'apprentissage interactif ! Plongez dans l'histoire, testez vos connaissances avec des quiz captivants et découvrez de nouvelles perspectives à chaque question. Transformez vos révisions en une aventure passionnante !")
st.markdown("""\n""")
st.markdown("Découvrez nos différentes pages:")

selected = option_menu(
        menu_title= None,
        options=["Quiz Master", "Quiz Histoire", "Quiz Géo"],
        icons = ["bar-chart-line-fill", "book-half", "map-fill"],
        default_index=0,
        orientation="horizontal",
    )
if selected == 'Quiz Histoire':
    st.info("""
        ❓Quiz d'Histoire

        Prêt à tester vos connaissances en histoire ? 
        Cliquez sur le bouton ci-dessous pour commencer un nouveau quiz et défier vos compétences. \n
        Bonne chance !\n
     """
    )
    if st.button("C'est parti!"):
        st.switch_page("pages\HistoireBot.py")
if selected == 'Quiz Géo':
    st.info("""
        ❓Quiz de Géographie\n
        Envie de tester vos connaissances en géographie ? 
        Cliquez sur le bouton ci-dessous pour commencer un nouveau quiz et explorer le monde à travers nos questions. \n
        Bonne chance !\n
    """)
    if st.button("C'est parti!"):
        st.switch_page("pages\GeographieBot.py")
if selected == 'Quiz Master':
    st.info("""
        ❓Quiz Master

        Prêt à tester vos connaissances ? 
        Cliquez sur le bouton ci-dessous pour commencer un nouveau quiz et défier vos compétences. \n
        Bonne chance !\n
     """
    )
    if st.button("C'est parti!"):
        st.switch_page("pages\QuizMaster.py")  
st.markdown("""\n""")