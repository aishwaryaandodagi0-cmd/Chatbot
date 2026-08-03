# ============================================================
# rag_utils.py
# Part 1 of 3
# ============================================================

import os
import pandas as pd
import streamlit as st

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_groq import ChatGroq

# ------------------------------------------------------------
# Groq API Key
# ------------------------------------------------------------

groq_api_key = st.secrets["GROQ_API_KEY"]

# ------------------------------------------------------------
# Create FAQ Excel if not exists
# ------------------------------------------------------------

if not os.path.exists("pragyan_faq_prices.xlsx"):

    faq_data = {
        "Category":[
            "Program Overview",
            "Program Structure",
            "Program Structure",
            "Pricing & Fees",
            "Pricing & Fees",
            "Curriculum & Skills",
            "Curriculum & Skills",
            "Evaluation & Projects",
            "Career & Placement",
            "Leadership & Contact"
        ],

        "Question":[
            "What is the total duration and structure of the PragyanAI program?",
            "What happens in Phase 1 (First 6 Months)?",
            "What happens in Phase 2 (12 Months)?",
            "What is the fee structure for the Founding Batch?",
            "What is the salary potential after completing the program?",
            "What modules are covered in Months 1-3 (Foundational Core)?",
            "What modules are covered in Months 4-6 (Advanced Frontier)?",
            "How are students evaluated during the 6-month offline training?",
            "What career tracks or roles are unlocked?",
            "Who leads PragyanAI and how can I contact them?"
        ],

        "Answer":[
            "The PragyanAI AI GenAI program is an 18-month journey comprising 6 Months of Fully Offline Training followed by a 12-Month Internship & Placement Drive.",

            "Phase 1 consists of intensive offline training with classroom sessions, labs, projects, hackathons and seminars.",

            "Phase 2 consists of internship, placement preparation, resume building and startup exposure.",

            "Initial fee ₹50,000 + ₹50,000 success fee after placement.",

            "Expected salary ranges from ₹6 LPA to ₹25 LPA depending upon role.",

            "Months 1-3 cover Python, Analytics, Data Science, BI and Machine Learning.",

            "Months 4-6 cover Deep Learning, Computer Vision, NLP, GenAI, RAG, LangChain and Agentic AI.",

            "Technical seminars and 48-hour hackathons are conducted for evaluation.",

            "Career paths include Data Scientist, AI Engineer, GenAI Engineer, Agentic AI Engineer and Software Engineer.",

            "Led by Sateesh Ambesange."
        ]
    }

    pd.DataFrame(faq_data).to_excel(
        "pragyan_faq_prices.xlsx",
        index=False
    )

# ------------------------------------------------------------
# System Prompts
# ------------------------------------------------------------

SALES_PROMPTS = {

    "PragyanAI Student Counselor":
"""
You are Aarav, Academic & Career Advisor.

Use ONLY the retrieved context.

Context:
{context}

Help students regarding:

• Program
• Curriculum
• Fees
• Placements
• Projects

Never make up information.
""",

    "PragyanAI Institutional / CoE Advisor":
"""
You are Dr. Kavita.

Use ONLY retrieved context.

Context:

{context}

Answer questions related to colleges,
partnerships,
curriculum,
evaluation,
and placements.
""",

    "PragyanAI Enterprise AI & Placement Lead":
"""
You are Rohan.

Use ONLY retrieved context.

Context:

{context}

Answer enterprise hiring,
placements,
skills,
AI talent
and recruitment queries.
"""

}
# ============================================================
# rag_utils.py
# Part 2 of 3
# ============================================================

# ------------------------------------------------------------
# Embeddings & Vector Store
# ------------------------------------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

vectorstore = None

# ------------------------------------------------------------
# Load Documents into Vector Store
# ------------------------------------------------------------

def load_documents_into_vectorstore(file_paths=None):

    global vectorstore

    docs = []

    # Load uploaded files
    if file_paths:

        for path in file_paths:

            if path.endswith(".pdf"):

                loader = PyPDFLoader(path)
                docs.extend(loader.load())

            elif path.endswith(".xlsx") or path.endswith(".xls"):

                df = pd.read_excel(path)

                for _, row in df.iterrows():

                    content = " | ".join(
                        f"{col}: {val}"
                        for col, val in row.items()
                    )

                    docs.append(
                        Document(
                            page_content=content,
                            metadata={"source": path}
                        )
                    )

    # Load default FAQ
    if os.path.exists("pragyan_faq_prices.xlsx"):

        df = pd.read_excel("pragyan_faq_prices.xlsx")

        for _, row in df.iterrows():

            content = " | ".join(
                f"{col}: {val}"
                for col, val in row.items()
            )

            docs.append(
                Document(
                    page_content=content,
                    metadata={
                        "source":
                        "pragyan_faq_prices.xlsx"
                    }
                )
            )

    # Fallback knowledge
    if len(docs) == 0:

        docs = [

            Document(
                page_content="PragyanAI provides a 6-month offline AI training followed by a 12-month internship and placement program."
            ),

            Document(
                page_content="The founding batch fee consists of ₹50,000 training fee and ₹50,000 success fee after placement."
            )
        ]

    vectorstore = FAISS.from_documents(
        docs,
        embeddings
    )

    return (
        f"✅ Knowledge Base Loaded "
        f"({len(docs)} document chunks)"
    )

# Build initial vector database
load_documents_into_vectorstore()

# ------------------------------------------------------------
# Groq LLM
# ------------------------------------------------------------

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama-3.3-70b-versatile",
    temperature=0.3
)

# ------------------------------------------------------------
# Chat Memory
# ------------------------------------------------------------

store = {}

def get_session_history(session_id: str):

    if session_id not in store:

        store[session_id] = ChatMessageHistory()

    return store[session_id]

# ------------------------------------------------------------
# Create RAG Chain
# ------------------------------------------------------------

def create_rag_chain(
    persona_name: str,
    retrieved_context: str
):

    system_prompt = SALES_PROMPTS.get(
        persona_name,
        SALES_PROMPTS[
            "PragyanAI Student Counselor"
        ]
    ).format(
        context=retrieved_context
    )

    prompt = ChatPromptTemplate.from_messages(

        [
            ("system", system_prompt),
            MessagesPlaceholder(
                variable_name="history"
            ),
            ("human", "{input}")
        ]

    )

    return (
        prompt
        | llm
        | StrOutputParser()
    )
  # ============================================================
# rag_utils.py
# Part 3 of 3
# ============================================================

# ------------------------------------------------------------
# Respond Function
# ------------------------------------------------------------

def respond(
    message,
    history,
    persona_name
):

    if not message.strip():
        return ""

    # If vector store is not available
    if vectorstore is None:
        return "Knowledge base is not loaded."

    # Retrieve relevant documents
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 4}
    )

    relevant_docs = retriever.invoke(message)

    context = "\n".join(
        [
            f"- {doc.page_content}"
            for doc in relevant_docs
        ]
    )

    # Session ID
    session_id = (
        "pragyan_"
        + persona_name.replace(" ", "_")
    )

    # Create chain
    base_chain = create_rag_chain(
        persona_name,
        context
    )

    conversational_chain = RunnableWithMessageHistory(

        base_chain,

        get_session_history,

        input_messages_key="input",

        history_messages_key="history"

    )

    try:

        answer = conversational_chain.invoke(

            {
                "input": message
            },

            config={
                "configurable": {
                    "session_id": session_id
                }
            }

        )

        return answer

    except Exception as e:

        return f"Error : {str(e)}"


# ------------------------------------------------------------
# Clear Memory
# ------------------------------------------------------------

def clear_chat_history(persona_name):

    session_id = (
        "pragyan_"
        + persona_name.replace(" ", "_")
    )

    if session_id in store:

        store[session_id].clear()


# ------------------------------------------------------------
# Test
# ------------------------------------------------------------

if __name__ == "__main__":

    print(
        load_documents_into_vectorstore()
    )

    print(
        respond(
            "Tell me about the PragyanAI program.",
            [],
            "PragyanAI Student Counselor"
        )
    )
