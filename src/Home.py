import os
import openai
import chromadb
import pandas as pd
import streamlit as st

from dotenv import load_dotenv

from chromadb.utils import embedding_functions

from utils import get_documents

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_KEY")
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
OPENAI_ENGINE = os.getenv("OPENAI_ENGINE")
OPENAI_EMBEDDINGS = os.getenv("OPENAI_EMBEDDINGS")
OPENAI_VERSION = os.getenv("OPENAI_VERSION")

COLLECTION_NAME = "csc-ml-collection"

@st.cache_resource
def get_embedding_function(
    api_key,
    api_base,
    api_type,
    api_version,
    deployment_id,
):
    st.session_state["embedding_function"] = embedding_functions.OpenAIEmbeddingFunction(
        api_key=api_key,
        api_base=api_base,
        api_type=api_type,
        api_version=api_version,
        deployment_id=deployment_id,
    )

@st.cache_resource
def get_chat_model(
    azure_deployment,
    azure_endpoint,
    api_key,
    api_version,
):
    st.session_state["openai_client"] = openai.AzureOpenAI(
        azure_endpoint=azure_endpoint,
        azure_deployment=azure_deployment,
        api_version=api_version,
        api_key=api_key,
    )

@st.cache_resource
def get_chroma_client(path):
    st.session_state["client"] = chromadb.PersistentClient(path)

@st.cache_resource
def get_collection(collection_name):
    if "client" not in st.session_state:
        raise Exception("Chroma client not found from session state")

    if "embedding_function" not in st.session_state:
        raise Exception("Embedding function not found from session state")
    
    if len(st.session_state["client"].list_collections()) > 0 and st.session_state["client"].get_collection(name=COLLECTION_NAME):
        st.session_state["client"].delete_collection(name=COLLECTION_NAME)

    st.session_state["collection"] = st.session_state["client"].get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
        embedding_function=st.session_state["embedding_function"],
    )

@st.cache_data
def add_documents(path):
    if "collection" not in st.session_state:
        raise Exception("Collection not found from session state")

    docs, metas, ids = get_documents(path)

    if len(docs) == len(metas) and len(docs) == len(ids) and len(docs) > 0:
        st.session_state["collection"].add(
            documents=docs,
            metadatas=metas,
            ids=ids,
        )

def init():
    try:
        get_embedding_function(
            OPENAI_KEY,
            OPENAI_ENDPOINT,
            "azure",
            OPENAI_VERSION,
            OPENAI_EMBEDDINGS,
        )
        get_chat_model(
            OPENAI_ENGINE,
            OPENAI_ENDPOINT,
            OPENAI_KEY,
            OPENAI_VERSION,
        )
        get_chroma_client("4.225.30.255", 80)
        get_collection(COLLECTION_NAME)
        add_documents("./data/data.parquet.gzip")
    except Exception as ex:
        st.exception(ex)

def app():
    st.title("💬 TuutorBot")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "system", "content": "Olet avulias korkeakoulujen opetuksen ja opiskelijoiden ohjauksen tuutori."},
            {"role": "assistant", "content": "Miten voin auttaa?"}
        ]

    for msg in st.session_state.messages:
        if msg["role"] != "system":
            st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
        query_results = st.session_state["collection"].query(
            query_texts=[prompt],
            n_results=30,
        )
    
        context = ""
        for d in query_results["metadatas"][0]:
            context += d["content"] + "\n"

        st.session_state.messages[0]["content"] = f"""
            Olet avulias korkeakoulujen opetuksen ja opiskelijoiden ohjauksen tuutori.
            Vastaa opiskelijoiden kysymyksiin hyödyntäen seuraavia ajankohtaisia ja
            olennaisia kurssi tietoja hyödyntäen:

                {context}
        """

        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        response = st.session_state["openai_client"].chat.completions.create(
            model=OPENAI_ENGINE,
            messages=st.session_state.messages,
        )
        msg = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)

# init()
# app()