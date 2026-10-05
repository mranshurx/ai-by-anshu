import streamlit as st
from google import genai

# Page Configuration
st.set_page_config(
    page_title="Free AI Web UI",
    page_icon="🤖",
    layout="centered"
)

# App Title & Description
st.title("💬 Unrestricted Free AI Chat UI")
st.markdown("Powered by Google Gemini & hosted on Render for free.")

# --- SIDEBAR FOR API KEY ---
st.sidebar.header("🔑 Authentication")
user_api_key = st.sidebar.text_input(
    "Enter your Gemini API Key:",
    type="password",
    help="Get your free key from Google AI Studio. It is only stored in your current session."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.markdown("This web UI connects directly to the Google Gemini API using your own key.")

# Check if the user has entered an API key
if not user_api_key:
    st.warning("⚠️ Please enter your Gemini API Key in the sidebar to start chatting!")
    st.stop()

# Initialize the official Google GenAI client with the user-provided key
try:
    client = genai.Client(api_key=user_api_key)
except Exception as e:
    st.error(f"Failed to initialize client: {e}")
    st.stop()

# Model selection (using Gemini 2.5 Flash as a fast, powerful default)
model_name = "gemini-2.5-flash"

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages when the app reruns
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input from the bottom chat box
if prompt := st.chat_input("Type your message here..."):
    # Add user message to session state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate the response using Gemini
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            # Format chat history for the API call
            formatted_history = []
            for msg in st.session_state.messages[:-1]:
                role_val = "user" if msg["role"] == "user" else "model"
                formatted_history.append({
                    "role": role_val,
                    "parts": [{"text": msg["content"]}]
                })

            # Create a chat session with history
            chat = client.chats.create(
                model=model_name,
                history=formatted_history
            )
            
            # Send the new message
            response = chat.send_message(prompt)
            ai_response = response.text

            message_placeholder.markdown(ai_response)
            
            # Save assistant response to session state
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except Exception as e:
            error_message = f"An error occurred: {e}"
            message_placeholder.markdown(error_message)
