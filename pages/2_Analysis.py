import streamlit as st

from src.processing import clean_text, extract_text

st.title("Analysis")

# Streamlit reruns this page after interactions, so session state keeps the upload available.
uploaded_file = st.session_state.get("uploaded_file")
if uploaded_file is None:
    st.warning("Upload a document first on the Upload page.")
else:
    st.write(f"Analyzing: {uploaded_file.name}")

    # Keep both versions so the user can check that cleaning did not remove useful text.
    original_text = extract_text(uploaded_file)
    cleaned_text = clean_text(original_text)

    if not cleaned_text:
        st.warning("Your text is empty.")
    else:
        st.subheader("Original text")
        st.text_area("Original document", original_text, height=250)
        st.subheader("Cleaned text")
        st.text_area("Cleaned document", cleaned_text, height=250)
