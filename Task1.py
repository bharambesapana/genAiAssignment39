import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate


st.title("Simple Q&A Chatbot (Ollama)")
st.write("Ask any question and get an answer from a local Ollama model.")


# Let user choose which Ollama model to use

model_choice = st.selectbox(
    "Choose a model:",
    ["llama3", "mistral", "gemma"]
)


# Same prompt template used in earlier tasks

qa_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful assistant. Answer the user's question clearly "
        "and in simple language."
    ),
    ("human", "{question}")
])


# user question
user_question = st.text_input("Enter your question:")


# displaying the answer
if st.button("Get Answer"):

    if user_question.strip() == "":
        st.warning("Please type a question first.")

    else:
        with st.spinner("Thinking..."):

            # Initializing Ollama model
            llm = ChatOllama(model=model_choice)

            # Fill the prompt template
            formatted_prompt = qa_prompt.invoke({"question": user_question})

            response = llm.invoke(formatted_prompt.messages)
            answer = response.content

        # Display the answer clearly
        st.subheader("Answer:")
        st.write(answer)

        # streamlit run A29-streamlitChatbot.py