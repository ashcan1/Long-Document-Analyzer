import streamlit as st

from src.processing import extract_text

st.title("Analysis")

uploaded_file = st.session_state.get("uploaded_file")
if uploaded_file is None:
    st.warning("Upload a document first on the Upload page.")
else:
    st.write(f"Analyzing: {uploaded_file.name}")
    text = extract_text(uploaded_file)
    st.subheader("Document preview")
    st.text_area("Extracted text", text, height=400)
