import streamlit as st
from pydantic import ValidationError

from src.models import AnalysisResult
from src.processing import analyze, extract_text, clean_text, result_to_json

st.title("Results")

uploaded_file = st.session_state.get("uploaded_file")
if uploaded_file is None:
    st.warning("Upload a document first on the Upload page.")
    st.stop()

# --- Run analysis ---
if st.button("Analyze document"):
    try:
        raw_text = extract_text(uploaded_file)
        cleaned = clean_text(raw_text)
        result: AnalysisResult = analyze(cleaned)
        st.session_state["analysis_result"] = result
        st.success("Analysis complete.")
    except ValidationError as e:
        st.error("Pydantic ValidationError — invalid data returned.")
        for p in e.errors():
            st.code(f"Field: {p['loc']}\nError: {p['msg']}", language="text")

# --- Display result ---
result: AnalysisResult = st.session_state.get("analysis_result")

if result is not None:
    st.divider()

    st.markdown("**Summary**")
    st.write(result.summary)

    st.markdown("**Key Points**")
    for point in result.key_points:
        st.markdown(f"- {point}")

    st.markdown("**Confidence**")
    st.progress(result.confidence, text=f"{result.confidence:.0%}")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**model_dump() → dict**")
        st.json(result.model_dump())
    with col2:
        st.markdown("**model_dump_json() → JSON string**")
        st.code(result_to_json(result), language="json")

    # --- Live validation experiment ---
    st.divider()
    st.subheader("Try Breaking Validation")

    exp_summary = st.text_input("summary", value="Too short")
    exp_points_raw = st.text_area("key_points (one per line)", value="First point\nSecond point")
    exp_confidence = st.slider("confidence", min_value=0.0, max_value=2.0, value=0.75, step=0.05)

    if st.button("Validate"):
        exp_points = [p for p in exp_points_raw.splitlines() if p.strip()]
        try:
            test_result = AnalysisResult(
                summary=exp_summary,
                key_points=exp_points,
                confidence=exp_confidence,
            )
            st.success("Valid!")
            st.json(test_result.model_dump())
        except ValidationError as e:
            st.error(f"{e.error_count()} problem(s) found.")
            for p in e.errors():
                st.warning(f"**{list(p['loc'])[0]}** — {p['msg']}")
