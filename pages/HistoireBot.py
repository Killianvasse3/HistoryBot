import streamlit as st
import re
from streamlit_lottie import st_lottie
import json
import pandas as pd
import altair as alt
from config import Config
from helpers.llm_helper import chat, stream_parser

st.set_page_config(
    page_title=Config.PAGE_TITLE,
    initial_sidebar_state="expanded"
)

def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)
st_lottie(load_lottiefile("images/FloatingBoat.json"), speed=1, reverse=False, loop=True, quality="high", height=300, width=600)

st.title(Config.PAGE_TITLE)

st.markdown("Découvrez l'histoire de manière interactive avec notre bot ! Testez vos connaissances et apprenez grâce à des quiz historiques engageants.")
st.markdown("""\n""")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "scores" not in st.session_state:
    st.session_state.scores = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def send_message(user_input):
    st.session_state.messages.append({"role": "user", "content": user_input})
    reset_scores()  # Reset scores when a new message is sent

    with st.spinner('Generating response...'):
        llm_stream = chat(user_input, model='Histoire', history=st.session_state.messages)

        stream_output = ""
        for output in stream_parser(llm_stream):
            stream_output = output

        with st.chat_message("assistant"):
            st.markdown(stream_output)

        st.session_state.messages.append({"role": "assistant", "content": stream_output})
        detect_scores(stream_output)

def reset_scores():
    st.session_state.scores = []

def detect_scores(content):
    pattern = re.compile(r'(\d+)/(\d+)')
    match = pattern.findall(content)
    for score in match:
        st.session_state.scores.append((int(score[0]), int(score[1])))

# Function to extract quiz options from the assistant's message using regex
def extract_quiz_options(content):
    pattern = re.compile(r'([a-dA-D])\)\s*(.+)')
    matches = pattern.findall(content)
    options = {match[0].upper(): match[1].strip() for match in matches}
    return options

# Always show chat input
if user_prompt := st.chat_input("Que voulez-vous demander ?"):
    with st.chat_message("user"):
        st.markdown(user_prompt)
    send_message(user_prompt)

# Display scores graph
if st.session_state.scores:
    st.markdown("### Vos scores:")
    df = pd.DataFrame(st.session_state.scores, columns=['Score', 'Total'])
    df['Percentage'] = (df['Score'] / df['Total']) * 100
    df['Quiz'] = range(1, len(df) + 1)  # Adding a quiz order index

    line_chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('Quiz:O', title='Quiz Number'),
        y=alt.Y('Score:Q', title='Score (out of 10)'),
        tooltip=['Quiz', 'Score', 'Total', 'Percentage']
    ).interactive()

    st.altair_chart(line_chart, use_container_width=True)

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
