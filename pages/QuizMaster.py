import streamlit as st
from streamlit_lottie import st_lottie
from typing import Literal
from dataclasses import dataclass
import json
import base64
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain, RetrievalQA
from langchain.prompts.prompt import PromptTemplate
from langchain.text_splitter import NLTKTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import nltk
from prompts.prompts import templates
import re
import pandas as pd
import altair as alt
from config import Config
from helpers.llm_helper import chat, stream_parser
# Audio
from audio_recorder_streamlit import audio_recorder
from IPython.display import Audio


def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)
st_lottie(load_lottiefile("images/welcome.json"), speed=1, reverse=False, loop=True, quality="high", height=300)

#st.markdown("""solutions to potential errors:""")
with st.expander("""Why did I encounter errors when I tried to talk to the AI Interviewer?"""):
    st.write("""
    This is because the app failed to record. Make sure that your microphone is connected and that you have given permission to the browser to access your microphone.""")

jd = st.text_area("Bonjour, je suis le quiz Master et suis ici pour vous poser des questions sur votre cours: ")

#st.toast("4097 tokens is roughly equivalent to around 800 to 1000 words or 3 minutes of speech. Please keep your answer within this limit.")

@dataclass
class Message:
    """class for keeping track of interview history."""
    origin: Literal["human", "ai"]
    message: str

def save_vector(text):
    """embeddings"""

    nltk.download('punkt')
    text_splitter = NLTKTextSplitter()
    texts = text_splitter.split_text(text)
     # Create emebeddings
    embeddings = OpenAIEmbeddings()
    docsearch = FAISS.from_texts(texts, embeddings)
    return docsearch

def initialize_session_state_jd():
    """ initialize session states """
    if 'jd_docsearch' not in st.session_state:
        st.session_state.jd_docserch = save_vector(jd)
    if 'jd_retriever' not in st.session_state:
        st.session_state.jd_retriever = st.session_state.jd_docserch.as_retriever(search_type="similarity")
    if 'jd_chain_type_kwargs' not in st.session_state:
        Interview_Prompt = PromptTemplate(input_variables=["context", "question"],
                                          template=templates.jd_template)
        st.session_state.jd_chain_type_kwargs = {"prompt": Interview_Prompt}
    if 'jd_memory' not in st.session_state:
        st.session_state.jd_memory = ConversationBufferMemory()
    # interview history
    if "jd_history" not in st.session_state:
        st.session_state.jd_history = []
        st.session_state.jd_history.append(Message("ai",
                                                   "Bonjour, je suis le quiz Master et suis ici pour vous poser des questions sur votre document que vous avez importé."
                                                   " S'il vous plaît, commencez par vous présenter pour commencer un quiz."))
    # token count
    if "token_count" not in st.session_state:
        st.session_state.token_count = 0
    if "jd_guideline" not in st.session_state:
        llm = ChatOpenAI(
        model_name = "gpt-3.5-turbo",
        temperature = 0.8,)
        st.session_state.jd_guideline = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type_kwargs=st.session_state.jd_chain_type_kwargs, chain_type='stuff',
            retriever=st.session_state.jd_retriever, memory = st.session_state.jd_memory).run("Create an interview guideline and prepare only one questions for each topic. Make sure the questions tests the technical knowledge")
    # llm chain and memory
    if "jd_screen" not in st.session_state:
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.8, )
        PROMPT = PromptTemplate(
            input_variables=["history", "input"],
            template="""Vous êtes le QuizMaster dans un jeu de questions et de réponses. Les règles sont simples :
                        
                        - Posez une question à la fois en vous basant sur le contexte ou le sujet donné.
                         Par exemple :
                            Si le document parle d'un sujet historique ou en lien avec certaines matières, le quiz master posera des questions telles que « Question 1 : ...
                                réponses : 
                                - a) ...
                                - b) ... 
                                - c) ...
                                - d) ...».
                            
                        Ne posez pas la même question.
                        Ne répétez pas la question. 
                        - Attendez la réponse du joueur.
                        - Si la réponse est correcte, félicitez le joueur et posez la question suivante.
                        - Si la réponse est incorrecte, informez le joueur que le jeu est terminé et réinitialisez sa série de victoires.
                        - Gardez une trace de la série de victoires du joueur et encouragez-le au fur et à mesure qu'elle augmente.
                        - Ne fournissez pas d'explications ou d'informations supplémentaires à moins que le joueur ne le demande explicitement.

                        Le jeu se poursuit tant que le joueur continue à répondre correctement. L'objectif du joueur est d'obtenir le plus grand nombre de victoires possible.

                        Série de victoires actuelle :
                        
                        Conversation actuelle :
                        {history}
                        
                        Joueur : {input}
                        QuizMaster :""")

        st.session_state.jd_screen = ConversationChain(prompt=PROMPT, llm=llm,
                                                           memory=st.session_state.jd_memory)
    if 'jd_feedback' not in st.session_state:
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.8, )
        st.session_state.jd_feedback = ConversationChain(
            prompt=PromptTemplate(input_variables=["history", "input"], template=templates.feedback_template),
            llm=llm,
            memory=st.session_state.jd_memory,
        )

def answer_call_back():
    with get_openai_callback() as cb:
        # user input
        human_answer = st.session_state.answer
        # transcribe audio
        input = human_answer

        st.session_state.jd_history.append(
            Message("human", input)
        )
        # OpenAI answer and save to history
        llm_answer = st.session_state.jd_screen.run(input)
        # save audio data to history
        st.session_state.jd_history.append(
            Message("ai", llm_answer)
        )
        st.session_state.token_count += cb.total_tokens
        return llm_answer

if jd:
    # initialize session states
    initialize_session_state_jd()
    #st.write(st.session_state.jd_guideline)
    credit_card_placeholder = st.empty()
    col1, col2 = st.columns(2)
    with col1:
        feedback = st.button("Avoir des retours sur ma session")
    with col2:
        guideline = st.button("Montre moi les règles")
    chat_placeholder = st.container()
    answer_placeholder = st.container()
    audio = None
    # if submit email adress, get interview feedback imediately
    if guideline:
        st.write(st.session_state.jd_guideline)
    if feedback:
        evaluation = st.session_state.jd_feedback.run("Donne les règles du jeu et quelques conseils")
        st.markdown(evaluation)
        st.download_button(label="Télécharger les Feedbacks", data=evaluation, file_name="quiz_feedback.txt")
        st.stop()
    else:
        with answer_placeholder:
            voice: bool = st.checkbox("I would like to speak with AI Interviewer")
            if voice:
                answer = audio_recorder(pause_threshold = 2.5, sample_rate = 44100)
                #st.warning("An UnboundLocalError will occur if the microphone fails to record.")
            else:
                answer = st.chat_input("Your answer")
            if answer:
                st.session_state['answer'] = answer
                audio = answer_call_back()
        with chat_placeholder:
            for answer in st.session_state.jd_history:
                if answer.origin == 'ai':
                    with st.chat_message("assistant"):
                        st.write(answer.message)
                else:
                    with st.chat_message("user"):
                        st.write(answer.message)

        credit_card_placeholder.caption(f"""
        Progression: {int(len(st.session_state.jd_history) / 30 * 100)}% complété.""")
else:
    st.info("Veuillez copier-coller votre cours ou un document.")

