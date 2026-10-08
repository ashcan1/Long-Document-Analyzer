import streamlit as st

from src.processing import clean_text, extract_text, count_tokens, fits_in_context, MAX_TOKENS

st.title("Analysis")

uploaded_file = st.session_state.get("uploaded_file")
if uploaded_file is None:
    st.warning("Upload a document first on the Upload page.")
else:
    st.write(f"Analyzing: {uploaded_file.name}")

    original_text = extract_text(uploaded_file)
    cleaned_text = clean_text(original_text)

    if not cleaned_text:
        st.warning("Your text is empty.")
    else:
        # Token count metrics
        token_count = count_tokens(cleaned_text)
        word_count  = len(cleaned_text.split())

        col1, col2, col3 = st.columns(3)
        col1.metric("Words",       word_count)
        col2.metric("Tokens",      token_count)
        col3.metric("Model Limit", f"{MAX_TOKENS:,}")

        if fits_in_context(cleaned_text):
            st.success("Document fits in one request.")
        else:
            st.error(f"Too long — {token_count:,} tokens exceeds the {MAX_TOKENS:,} limit. Needs chunking.")

        st.divider()
        st.subheader("Original text")
        st.text_area("Original document", original_text, height=250)
        st.subheader("Cleaned text")
        st.text_area("Cleaned document", cleaned_text, height=250)
