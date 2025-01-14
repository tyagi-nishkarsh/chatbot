import streamlit as st
import requests
from langchain_groq import ChatGroq
import os

# Initialize the chatbot
llm = ChatGroq(
    temperature=0, 
    groq_api_key='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', 
    model_name="llama-3.1-70b-versatile"
)

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# File to log user questions
log_file = "user_questions.log"

def log_question(question):
    """Log user questions to a file."""
    with open(log_file, "a") as f:
        f.write(question + "\n")

# Function to search the web using Google Custom Search API
def search_web(query):
    api_key = "AIzaSyAHRg3xoX-_j-duSPQSSfzLnghFODdQMhw"
    cx = "80102c50a86d74d76"
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json()
        return results.get("items", [])[:3]  # Return top 3 results or empty if no results
    else:
        return []

# Function to extract and clean the answer from search results
def extract_answer_from_search(results):
    if results:
        best_result = results[0]
        snippet = best_result.get("snippet", "No summary available.")
        return snippet
    return "I couldn't find an answer to that question."

# Function to handle user input and get a response
def handle_input():
    user_input = st.session_state.user_input  # Get user input from session state
    if user_input:
        # Log the user question
        log_question(user_input)
        
        # Append user input to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Construct conversation history to send to the model
        conversation_history = "\n".join(
            f"{msg['role'].capitalize()}: {msg['content']}" 
            for msg in st.session_state.chat_history
        )
        
        # Check if the query is time-sensitive (Virat Kohli and 2024)
        if "virat kohli" in user_input.lower() and "century" in user_input.lower() and "2024" in user_input.lower():
            st.session_state.chat_history.append(
                {"role": "bot", "content": "Searching for the latest information..."}
            )
            search_results = search_web(user_input)
            chatbot_response = extract_answer_from_search(search_results)
        else:
            # Process the query with the chatbot model
            response = llm.invoke(conversation_history)
            chatbot_response = response.content
        
        # Add the bot's response to the chat history
        st.session_state.chat_history.append({"role": "bot", "content": chatbot_response})

        # Clear the input box by resetting session state (but not the chat history)
        st.session_state.user_input = ""

# Streamlit UI setup
st.title("ChatBot")
st.write("Heyyy guys!")

# Multi-line input field with a submit button
st.text_area(
    "Enter your question:",
    key="user_input",
    placeholder="Type your message here...",
    on_change=handle_input,
    height=100
)

# Display the chat history (latest message at the bottom)
if st.session_state.chat_history:
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(
                f"""
                <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
                    <div style="background-color: black; color: white; padding: 10px; border-radius: 10px; max-width: 70%; text-align: right;">
                        <strong>You:</strong> {chat['content']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif chat["role"] == "bot":
            st.markdown(
                f"""
                <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;">
                    <div style="background-color: black; color: white; padding: 10px; border-radius: 10px; max-width: 70%;">
                        <strong>Bot:</strong> {chat['content']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# Add CSS to fix the input box at the bottom
st.markdown(
    """
    <style>
    textarea.stTextArea {
        position: fixed;
        bottom: 20px;
        left: 10%;
        width: 80%;
        z-index: 10;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
