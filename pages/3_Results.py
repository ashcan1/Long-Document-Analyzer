import streamlit as st

st.title("Results")

results = st.session_state.get("analysis_results")
if results is None:
    st.warning("No results yet. Run an analysis first.")
else:
    st.write(results)
