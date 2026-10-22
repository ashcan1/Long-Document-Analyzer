import streamlit as st

st.title("Upload")

uploaded_file = st.file_uploader("Upload a text file", type=["txt"])
if uploaded_file is not None:
    st.session_state["uploaded_file"] = uploaded_file
    st.success(f"Loaded: {uploaded_file.name}")
