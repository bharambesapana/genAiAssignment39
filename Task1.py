import streamlit as st
from groq import Groq

# 1. Setup page layout and title
st.set_page_config(page_title="Groq Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 Groq AI Chatbot")

# 2. Initialize the Groq client using Streamlit secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. Model selection sidebar
model_options = [
    "llama-3.3-70b-versatile",
    "llama3-8b-8192",
    "mixtral-8x7b-32768"
]
selected_model = st.sidebar.selectbox("Choose a model:", model_options)

# 4. Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Display existing chat history from session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 6. Accept user input
if user_prompt := st.chat_input("What is on your mind?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.write(user_prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # Display assistant response container
    with st.chat_message("assistant"):
        # Create a placeholder to update the text streaming in real time
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Request streaming response from Groq API
            completion = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            
            # Iterate through the stream and stitch chunks together
            for chunk in completion:
                chunk_text = chunk.choices[0].delta.content
                if chunk_text is not None:
                    full_response += chunk_text
                    # Dynamically update the placeholder UI with the cumulative response
                    response_placeholder.write(full_response)
                    
        except Exception as e:
            st.error(f"An error occurred: {e}")
            full_response = "Sorry, I couldn't process that request."
            response_placeholder.write(full_response)

    # Add complete assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})