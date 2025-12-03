import streamlit as st

from ab_testing.stats import run_ab_test, InvalidABTestInput
from ab_testing.copydeck import (
    WHAT_IS_AB_TEST,
    CONTROL_VS_VARIANT,
    WHAT_IS_CONVERSION_RATE,
    WHAT_IS_PVALUE,
    build_result_summary,
)

st.set_page_config(
    page_title="A/B Test Playground",
    layout="wide",
)

st.title("🧪 A/B Test Playground")
st.write(
    "Simulate a simple A/B test, see the key metrics, "
    "and understand the statistics behind product experiments."
)

left_col, right_col = st.columns(2)

with left_col:
    st.header("Inputs")

    st.write("##### Enter the sample size and conversions for each group.")
    n_a = st.number_input("Sample size (A)", min_value=0, value=1000)
    c_a = st.number_input("Conversions (A)", min_value=0, value=100)
    n_b = st.number_input("Sample size (B)", min_value=0, value=1000)
    c_b = st.number_input("Conversions (B)", min_value=0, value=100)

    alternatives = ["two-sided", "larger", "smaller"]
    alternative = st.selectbox("##### Select the alternative to test", options=alternatives, index=0)

    alpha = st.slider("##### Enter your desired alpha", min_value=0.01, max_value=0.1, value=0.05)

    run_clicked = st.button("Run A/B Test")

with right_col:
    st.header("Results")
    st.write("Results will appear here after running the test.")

    if run_clicked:
        try:
            result = run_ab_test(n_a, c_a, n_b, c_b, alpha, alternative)
        except InvalidABTestInput as e:
            st.error(str(e))
        else:
            st.success(result)


st.markdown("---")

st.subheader("Learn the concepts")

with st.expander("📘 What is an A/B test?"):
    st.markdown(WHAT_IS_AB_TEST)

with st.expander("🧪 Control vs Variant"):
    st.markdown(CONTROL_VS_VARIANT)

with st.expander("📊 What is conversion rate?"):
    st.markdown(WHAT_IS_CONVERSION_RATE)

with st.expander("🎲 What is a p-value?"):
    st.markdown(WHAT_IS_PVALUE)
