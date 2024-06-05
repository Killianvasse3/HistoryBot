import streamlit as st
import re
from config import Config
from helpers.llm_helper import chat, stream_parser

st.set_page_config(
    page_title=Config.PAGE_TITLE,
    initial_sidebar_state="expanded"
)

st.title(Config.PAGE_TITLE)

st.markdown("Découvrez l'histoire de manière interactive avec notre bot ! Testez vos connaissances et apprenez grâce à des quiz historiques engageants.")
st.markdown("""\n""")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def send_message(user_input):
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner('Generating response...'):
        llm_stream = chat(user_input, model='Histoire', history=st.session_state.messages)

        stream_output = ""
        for output in stream_parser(llm_stream):
            stream_output = output

        with st.chat_message("assistant"):
            st.markdown(stream_output)

        st.session_state.messages.append({"role": "assistant", "content": stream_output})

# Function to extract quiz options from the assistant's message using regex
def extract_quiz_options(content):
    pattern = re.compile(r'([a-dA-D])\)\s*(.+)')
    matches = pattern.findall(content)
    options = {match[0].upper(): match[1].strip() for match in matches}
    return options

# Function to extract list options from the assistant's message using regex
def extract_list_options(content):
    pattern = re.compile(r'-\s*(.+)')
    matches = pattern.findall(content)
    return matches

# Always show chat input
if user_prompt := st.chat_input("Que voulez-vous demander ?"):
    with st.chat_message("user"):
        st.markdown(user_prompt)
    send_message(user_prompt)

# Add buttons for multiple choice options if they are present in the assistant's response
quiz_options = {}
if st.session_state.messages:
    last_message = st.session_state.messages[-1]
    if last_message["role"] == "assistant":
        content = last_message["content"]
        quiz_options = extract_quiz_options(content)
        if quiz_options:
            st.markdown("### Sélectionnez votre réponse :")
            columns = st.columns(len(quiz_options))
            for i, (option_letter, option_text) in enumerate(quiz_options.items()):
                if columns[i].button(f"{option_letter}) {option_text}"):
                    with st.chat_message("user"):
                        st.markdown(option_letter)
                    send_message(option_letter)
                    st.experimental_rerun()

# Initial welcome message
if not st.session_state.messages:
    initial_message = "Bienvenue à notre quiz d'histoire ! Testez vos connaissances et découvrez des faits fascinants. Prêt à relever le défi ?"
    st.session_state.messages.append({"role": "assistant", "content": initial_message})
    with st.chat_message("assistant"):
        st.markdown(initial_message)
