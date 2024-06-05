import streamlit as st
from config import Config
from helpers.llm_helper import chat, stream_parser

st.set_page_config(
    page_title=Config.PAGE_TITLE,
    initial_sidebar_state="expanded"
)

st.title(Config.PAGE_TITLE)

st.markdown(" Votre ami d'apprentissage interactif ! Plongez dans l'histoire, testez vos connaissances avec des quiz captivants et découvrez de nouvelles perspectives à chaque question. Transformez vos révisions en une aventure passionnante !")
st.markdown("""\n""")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_prompt := st.chat_input("What would you like to ask?"):
    with st.chat_message("user"):
        st.markdown(user_prompt)

    st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.spinner('Generating response...'):
        llm_stream = chat(user_prompt, model="llama3:latest:", history=st.session_state.messages)

        stream_output = ""
        for output in stream_parser(llm_stream):
            stream_output = output
        
        with st.chat_message("assistant"):
            st.markdown(stream_output)
        
        st.session_state.messages.append({"role": "assistant", "content": stream_output})
