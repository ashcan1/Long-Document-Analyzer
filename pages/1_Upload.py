import streamlit as st

from src.utils import file_fingerprint

st.title("Upload")

def clear_uploaded_file() -> None:
    st.session_state.pop("uploaded_file", None)
    st.session_state.pop("uploaded_file_fingerprint", None)
    st.session_state.pop("analysis_result", None)
    st.session_state.pop("analysis_result_fingerprint", None)
    st.session_state["document_uploader"] = None


uploaded_file = st.file_uploader(
    "Upload a text file",
    type=["txt"],
    key="document_uploader",
)
if uploaded_file is not None:
    fingerprint = file_fingerprint(uploaded_file)
    if fingerprint != st.session_state.get("uploaded_file_fingerprint"):
        st.session_state.pop("analysis_result", None)
        st.session_state.pop("analysis_result_fingerprint", None)
        st.session_state["uploaded_file_fingerprint"] = fingerprint

    st.session_state["uploaded_file"] = uploaded_file
    st.success(f"Loaded: {uploaded_file.name}")

if st.session_state.get("uploaded_file") is not None:
    st.button("Clear uploaded file", on_click=clear_uploaded_file)
