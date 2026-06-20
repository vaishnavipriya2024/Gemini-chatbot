import os
import streamlit as st
from google import genai
from pypdf import PdfReader
from dotenv import load_dotenv

# Load environment variables if a .env file exists
load_dotenv()

# --- Page Configuration ---
st.set_page_config(page_title="Gemini PDF Chatbot", page_icon="📄", layout="centered")
st.title("📄 Chat with your PDF using Gemini")
st.write("Upload a document, ask a question, and get immediate answers.")

# --- API Key Setup ---
# Check if API key is in environment variables, otherwise ask for it in the sidebar
api_key = os.getenv("GEMINI_API_KEY")

# Initialize the Gemini Client
client = genai.Client(api_key=api_key)

# --- PDF Text Extraction Helper ---
def extract_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

# --- UI Components ---
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    # Extract text once and cache it in the session state
    if "pdf_text" not in st.session_state or st.session_state.get("file_name") != uploaded_file.name:
        with st.spinner("Extracting text from PDF..."):
            st.session_state["pdf_text"] = extract_text(uploaded_file)
            st.session_state["file_name"] = uploaded_file.name
        st.success(f"Successfully loaded: {uploaded_file.name}")

    # User Input
    user_question = st.text_input("Ask a question about your document:")

    if user_question:
        with st.spinner("Gemini is thinking..."):
            try:
                # Construct the prompt context
                prompt = f"""
                You are a helpful document assistant. Answer the user's question based strictly on the provided document context.
                If the answer cannot be found in the text, politely state that the information is not available in the document.
                
                [Document Context]
                {st.session_state['pdf_text']}
                
                [User Question]
                {user_question}
                """
                
                # Query the model
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                
                # Display result
                st.markdown("## 🤖 Answer:")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"An error occurred: {e}")