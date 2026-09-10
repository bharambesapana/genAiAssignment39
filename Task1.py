
import os
import tempfile
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Setup LLM
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=api_key,
    temperature=0.2
)

# Prompt template with context + chat history + question
rag_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful assistant. Answer using ONLY the context below.\n\n"
        "Context:\n{context}"
    ),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])

st.title("PDF Chatbot using ChatGroq")

# Session state to store chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "retriever" not in st.session_state:
    st.session_state.retriever = None


# File uploader (PDF)


uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None and st.session_state.retriever is None:

    try:
        # Save uploaded file to a temp path so PyPDFLoader can read it
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name
        tmp_file.close()

        # Load PDF
        loader = PyPDFLoader(tmp_path)
        documents = loader.load()

        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(documents)

        # Create embeddings + vector store
        embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = FAISS.from_documents(chunks, embedding_model)

        # Save retriever in session state
        st.session_state.retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

        st.success("PDF loaded successfully. You can start asking questions.")

    except Exception as e:
        # Task 10: handle errors gracefully instead of crashing the app
        st.error(f"Could not read this PDF. Please try another file. Error: {e}")

# Display previous chat messages

for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.write(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.write(message.content)


# Chat input box

user_question = st.chat_input("Ask a question about the PDF...")

# Connect RAG chain with UI
if user_question:

    #  if no PDF has been uploaded yet
    if st.session_state.retriever is None:
        st.warning("Please upload a PDF first before asking a question.")

    else:
        with st.chat_message("user"):
            st.write(user_question)

        try:
            # relevant documents
            retrieved_docs = st.session_state.retriever.invoke(user_question)
            context = "\n\n".join([doc.page_content for doc in retrieved_docs])

            # prompt with context + chat history + question
            formatted_prompt = rag_prompt.invoke({
                "context": context,
                "chat_history": st.session_state.chat_history,
                "question": user_question
            })

            # Generating answer using ChatGroq
            response = llm.invoke(formatted_prompt.messages)
            answer = response.content

            # Saving this turn to chat history
            st.session_state.chat_history.append(HumanMessage(content=user_question))
            st.session_state.chat_history.append(AIMessage(content=answer))

            # Displaying response in chat format
            with st.chat_message("assistant"):
                st.write(answer)

        except Exception as e:
            #  handling errors 
            st.error(f"Something went wrong while answering. Please try again. Error: {e}")