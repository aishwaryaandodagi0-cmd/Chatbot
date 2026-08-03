import streamlit as st
import os
from groq import Groq


# ----------------------------
# PAGE CONFIG
# ----------------------------

st.set_page_config(
    page_title="PragyanAI Assistant",
    page_icon="🤖",
    layout="wide"
)


# ----------------------------
# CUSTOM CSS
# ----------------------------

st.markdown(
"""
<style>

body{
    background-color:#0e1117;
}

.stApp{
    background-color:#0e1117;
}


h1{
    color:white;
}


.chat-box{
    height:500px;
    border:1px solid #444;
    border-radius:8px;
    padding:20px;
    background:#161b22;
}


.sidebar-box{
    border:1px solid #444;
    padding:15px;
    border-radius:8px;
    background:#161b22;
}

</style>

""",
unsafe_allow_html=True
)



# ----------------------------
# TITLE
# ----------------------------


st.title("PragyanAI Conversational Sales & FAQ Assistant")

st.write(
"Answers program questions based on the **PragyanAI Presentation & FAQ Sheet**."
)



# ----------------------------
# SIDEBAR
# ----------------------------


with st.sidebar:


    st.subheader("Select PragyanAI Persona")


    persona = st.selectbox(
        "",
        [
            "PragyanAI Student Counselor",
            "PragyanAI Sales Assistant",
            "PragyanAI Technical Expert"
        ]
    )


    st.divider()


    st.subheader("Upload Additional PDFs or Excel Sheets")


    uploaded_file = st.file_uploader(
        "",
        type=[
            "pdf",
            "xlsx",
            "xls"
        ]
    )


    if uploaded_file:

        st.success(
            f"{uploaded_file.name} uploaded"
        )



    st.divider()


    st.subheader("Knowledge Base Status")


    st.info(
        "PragyanAI presentation FAQ pre-loaded."
    )



# ----------------------------
# SESSION MEMORY
# ----------------------------


if "messages" not in st.session_state:

    st.session_state.messages=[]



# ----------------------------
# CHAT AREA
# ----------------------------


st.subheader("💬 Chatbot")


chat_container = st.container()



with chat_container:


    for msg in st.session_state.messages:


        if msg["role"]=="user":

            st.chat_message("user").write(
                msg["content"]
            )

        else:

            st.chat_message("assistant").write(
                msg["content"]
            )



# ----------------------------
# GROQ MODEL
# ----------------------------


def get_response(question):


    try:


        client = Groq(
            api_key=st.secrets["GROQ_API_KEY"]
        )


        prompt=f"""

You are {persona}.

Answer user questions related to PragyanAI programs.

Question:
{question}

"""


        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                "role":"system",
                "content":prompt
                }
            ]

        )


        return response.choices[0].message.content



    except Exception as e:


        return "Please configure GROQ_API_KEY"



# ----------------------------
# INPUT BOX
# ----------------------------


user_input = st.chat_input(
    "Type a message..."
)



if user_input:


    st.session_state.messages.append(
        {
        "role":"user",
        "content":user_input
        }
    )


    answer=get_response(
        user_input
    )


    st.session_state.messages.append(
        {
        "role":"assistant",
        "content":answer
        }
    )


    st.rerun()



# ----------------------------
# CLEAR MEMORY
# ----------------------------


if st.button(
    "Clear Memory for Selected Persona",
    use_container_width=True
):

    st.session_state.messages=[]

    st.success(
        "Memory cleared"
    )
