import streamlit as st
import tempfile
import os

from rag_utils import (
    SALES_PROMPTS,
    load_documents_into_vectorstore,
    respond,
    clear_chat_history
)

# ----------------------------------------------------
# Streamlit Page Configuration
# ----------------------------------------------------
st.set_page_config(
    page_title="PragyanAI Intelligent Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 PragyanAI Intelligent Assistant")
st.markdown(
    "### AI-Powered Conversational Sales & FAQ Assistant"
)

# ----------------------------------------------------
# Sidebar
# ----------------------------------------------------
st.sidebar.title("Settings")

persona = st.sidebar.selectbox(
    "Choose Persona",
    list(SALES_PROMPTS.keys())
)

uploaded_files = st.sidebar.file_uploader(
    "Upload PDF / Excel Files",
    type=["pdf", "xlsx", "xls"],
    accept_multiple_files=True
)

# ----------------------------------------------------
# Load Uploaded Files
# ----------------------------------------------------
if uploaded_files:

    paths = []

    for uploaded_file in uploaded_files:

        suffix = os.path.splitext(uploaded_file.name)[1]

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as tmp:

            tmp.write(uploaded_file.read())
            paths.append(tmp.name)

    status = load_documents_into_vectorstore(paths)

    st.sidebar.success(status)

# ----------------------------------------------------
# Clear Chat
# ----------------------------------------------------
if st.sidebar.button("🗑 Clear Chat"):

    clear_chat_history(persona)

    st.session_state.messages = []

# ----------------------------------------------------
# Chat History
# ----------------------------------------------------
if "messages" not in st.session_state:

    st.session_state.messages = []

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# ----------------------------------------------------
# Chat Input
# ----------------------------------------------------
question = st.chat_input(
    "Ask anything about PragyanAI..."
)

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)

    with st.spinner("Thinking..."):

        answer = respond(
            question,
            [],
            persona
        )

    with st.chat_message("assistant"):

        st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
