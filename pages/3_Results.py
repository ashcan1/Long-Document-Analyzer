"""Results page — displays a validated AnalysisResult from session state.

LEARNING: What this page teaches you
======================================
After models.py and processing.py, this page shows the *consumer* side
of Pydantic: once you have a validated AnalysisResult object, how do
you display it, inspect it, and serialise it?

You will also see how to deliberately trigger a ValidationError in the
UI so you can watch Pydantic catch bad data in real time.
"""

import streamlit as st
from pydantic import ValidationError

from src.models import AnalysisResult
from src.processing import analyze, result_to_json

st.title("Results")

# -----------------------------------------------------------------------
# SECTION 1 — Run the analysis and store the result
# -----------------------------------------------------------------------

# LEARNING: Why store results in session_state?
# Streamlit reruns the whole script on every click or widget change.
# session_state persists values across those reruns so the result
# does not disappear the moment the user interacts with anything.

uploaded_file = st.session_state.get("uploaded_file")

if uploaded_file is None:
    st.warning("Upload a document first on the Upload page.")
    st.stop()  # LEARNING: st.stop() halts execution of the rest of the page.

st.subheader("Run Analysis")

if st.button("Analyze document"):
    # LEARNING: We wrap the call in try/except because analyze() calls
    # AnalysisResult.model_validate() internally. If the data coming
    # back from the model is bad, Pydantic raises ValidationError here.
    # Catching it means the app shows a clear message instead of crashing.
    try:
        from src.processing import extract_text, clean_text
        raw_text = extract_text(uploaded_file)
        cleaned = clean_text(raw_text)
        result: AnalysisResult = analyze(cleaned)

        # Store the validated result so it survives reruns.
        st.session_state["analysis_result"] = result
        st.success("Analysis complete — Pydantic validated the result successfully.")

    except ValidationError as error:
        # LEARNING: Show the full ValidationError details in the UI.
        # In production you would log this and show a friendlier message,
        # but during learning it is useful to see exactly what failed.
        st.error("Pydantic ValidationError — the model returned invalid data.")
        for problem in error.errors():
            st.code(
                f"Field : {problem['loc']}\n"
                f"Error : {problem['msg']}\n"
                f"Type  : {problem['type']}",
                language="text",
            )

# -----------------------------------------------------------------------
# SECTION 2 — Display the validated AnalysisResult
# -----------------------------------------------------------------------

result: AnalysisResult = st.session_state.get("analysis_result")

if result is not None:
    st.divider()
    st.subheader("Analysis Result")

    # --- Summary ---
    st.markdown("**Summary**")
    st.write(result.summary)
    # LEARNING: result.summary is a plain Python str. Because it passed
    # validation, you KNOW it is at least 10 characters. No need to
    # defensively check for None or empty string here.

    # --- Key points ---
    st.markdown("**Key Points**")
    for point in result.key_points:
        st.markdown(f"- {point}")
    # LEARNING: result.key_points is a list[str] that Pydantic confirmed
    # has at least one item, so iterating over it is always safe.

    # --- Confidence score ---
    st.markdown("**Confidence Score**")
    st.progress(result.confidence, text=f"{result.confidence:.0%}")
    # LEARNING: result.confidence is a float validated to be 0.0–1.0.
    # st.progress() requires a value in that exact range — Pydantic
    # already guarantees it, so this will never raise a Streamlit error.

    # -----------------------------------------------------------------------
    # SECTION 3 — Inspect the raw model data (learning tool)
    # -----------------------------------------------------------------------
    st.divider()
    st.subheader("Inspect the Pydantic Model (Learning Tools)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**`model_dump()` → Python dict**")
        st.json(result.model_dump())
        # LEARNING: model_dump() converts the Pydantic model back into a
        # plain Python dict. This is what you'd pass to json.dumps(),
        # a database, or any function that doesn't know about Pydantic.

    with col2:
        st.markdown("**`model_dump_json()` → JSON string**")
        st.code(result_to_json(result), language="json")
        # LEARNING: model_dump_json() goes directly to a JSON string.
        # The difference: model_dump() → dict, model_dump_json() → str.
        # Use model_dump_json() when writing to a file or sending over HTTP.

    # -----------------------------------------------------------------------
    # SECTION 4 — Live ValidationError experiment
    # -----------------------------------------------------------------------
    st.divider()
    st.subheader("Try Breaking Validation (Learning Experiment)")
    st.caption(
        "Edit the fields below and click Validate to see Pydantic "
        "accept or reject the data in real time."
    )

    exp_summary = st.text_input("summary", value="Too short")
    exp_points_raw = st.text_area(
        "key_points (one per line)",
        value="First point\nSecond point",
    )
    exp_confidence = st.slider("confidence", min_value=0.0, max_value=2.0, value=0.75, step=0.05)
    # LEARNING: Notice the slider goes up to 2.0 — above the valid range.
    # This lets you intentionally trigger the confidence validator.

    if st.button("Validate"):
        exp_points = [p for p in exp_points_raw.splitlines() if p.strip()]
        try:
            test_result = AnalysisResult(
                summary=exp_summary,
                key_points=exp_points,
                confidence=exp_confidence,
            )
            st.success("Valid! Pydantic accepted this data.")
            st.json(test_result.model_dump())
            # LEARNING: AnalysisResult(...) and AnalysisResult.model_validate({...})
            # both trigger the same validators. Use the constructor when you have
            # keyword arguments; use model_validate() when you have a dict (e.g.
            # a parsed JSON response from an API).

        except ValidationError as error:
            st.error(f"ValidationError: {error.error_count()} problem(s) found.")
            for problem in error.errors():
                st.warning(
                    f"**{list(problem['loc'])[0]}** — {problem['msg']}"
                )
