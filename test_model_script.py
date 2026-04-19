import streamlit as st
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

st.title("Gemini Model Tester")

models = [
    ("models/gemini-2.5-flash", "2.5 Flash"),
    ("models/gemini-flash-latest", "Flash Latest")
]

for model_name, label in models:
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("hi")
        st.success(f"{label}: {response.text[:50]}")
    except Exception as e:
        st.error(f"{label}: {str(e)}")s
