# ============================================================
# app.py
# Part 1 of 3
# ============================================================

import streamlit as st
import tempfile
import os

from rag_utils import (
    SALES_PROMPTS,
    load_documents_into_vectorstore,
    respond,
    clear_chat_history
)

# --------------------------------------------------
# Streamlit Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="PragyanAI Intelligent Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# Custom CSS
# --------------------------------------------------

st.markdown("""
<style>

.main{
    padding-top:1rem;
}

.stChatMessage{
    border-radius:12px;
    padding:10px;
}

h1{
    color:#0F62FE;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("🤖 PragyanAI Intelligent Assistant")

st.markdown("""
AI Powered Conversational Sales & FAQ Assistant

Ask questions regarding:

- AI/GenAI Program
- Fees
- Curriculum
- Placement
- Career Guidance
- Enterprise Partnerships
""")

# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.title("⚙ Settings")

persona = st.sidebar.selectbox(
    "Choose Persona",
    list(SALES_PROMPTS.keys()),
    index=0
)

st.sidebar.markdown("---")

uploaded_files = st.sidebar.file_uploader(
    "Upload PDF / Excel Files",
    type=["pdf","xlsx","xls"],
    accept_multiple_files=True
)

st.sidebar.markdown("---")

clear_chat = st.sidebar.button(
    "🗑 Clear Chat"
)

st.sidebar.markdown("---")

st.sidebar.info(
    "Powered by\n"
    "Groq + LangChain + FAISS + Streamlit"
)
# ============================================================
# app.py
# Part 2 of 3
# ============================================================

# --------------------------------------------------
# Load Uploaded Documents
# --------------------------------------------------

if uploaded_files:

    saved_files = []

    for uploaded_file in uploaded_files:

        suffix = os.path.splitext(uploaded_file.name)[1]

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as tmp:

            tmp.write(uploaded_file.read())
            saved_files.append(tmp.name)

    with st.spinner("Building Knowledge Base..."):

        status = load_documents_into_vectorstore(
            saved_files
        )

    st.sidebar.success(status)

# --------------------------------------------------
# Clear Chat
# --------------------------------------------------

if clear_chat:

    clear_chat_history(persona)

    if "messages" in st.session_state:
        st.session_state.messages = []

# --------------------------------------------------
# Initialize Session State
# --------------------------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []

# --------------------------------------------------
# Display Previous Chat Messages
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"]
        )

# --------------------------------------------------
# Chat Input
# --------------------------------------------------

question = st.chat_input(
    "Ask your question..."
)
# ============================================================
# app.py
# Part 3 of 3
# ============================================================

if question:

    # Display user message
    st.chat_message("user").markdown(question)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    # Generate response
    with st.spinner("Thinking..."):

        try:

            answer = respond(
                message=question,
                history=st.session_state.messages,
                persona_name=persona
            )

        except Exception as e:

            answer = f"❌ Error: {str(e)}"

    # Display assistant response
    st.chat_message("assistant").markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.markdown("---")

st.caption(
    "🚀 Powered by Groq • LangChain • FAISS • HuggingFace • Streamlit"
)
