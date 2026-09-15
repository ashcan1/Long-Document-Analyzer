import streamlit as st

st.title("Upload")

# This first version intentionally supports plain text files only.
uploaded_file = st.file_uploader("Upload a text file", type=["txt"])
if uploaded_file is not None:
    # Store the file so the other Streamlit pages can use it.
    st.session_state["uploaded_file"] = uploaded_file
    st.success(f"Loaded: {uploaded_file.name}")
