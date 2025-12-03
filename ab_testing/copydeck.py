from ab_testing.stats import ABTestResult

# --- Concept texts for expanders --- #

WHAT_IS_AB_TEST = """
An A/B test compares **two versions** (A and B) of something,
such as a screen, an email, or a button. Traffic is randomly
split between A and B, and we measure a **metric** like
conversion rate to see which performs better.
"""

CONTROL_VS_VARIANT = """
- **Control (A):** the current or baseline version.
- **Variant (B):** the new version with a change we want to test.

We compare the metrics of A and B to decide whether to adopt
the new version or keep the control.
"""

WHAT_IS_CONVERSION_RATE = """
Conversion rate is defined as:

> **conversion rate = conversions / users**

If 100 users convert out of 1,000, the conversion rate is 10%.
It's one of the most common metrics in A/B testing.
"""

WHAT_IS_PVALUE = """
The **p-value** is the probability of observing a difference
at least as large as the one we see if there is actually
**no real effect** (no difference between A and B).

We usually compare it to a **significance level** (alpha),
often 0.05.
- If p-value < alpha → we say the result is *statistically significant*.
- If p-value ≥ alpha → the data is consistent with “no real effect”.
"""

def build_result_summary(result: ABTestResult) -> str:
    """
    Builds a human-readable summary of the A/B test result,
    including lift, statistical significance, and a product-oriented recommendation.

    Args:
        result: ABTestResult containing all computed metrics.

    Returns:
        A string summarizing the outcome and recommended action.
    """
    lift_abs = result.lift_abs
    lift_rel = result.lift_rel
    lift_rel_pct = lift_rel * 100
    p_value = result.p_value
    alpha = result.alpha
    is_significant = result.is_significant
    if abs(lift_abs) < 1e-6:
        direction_text = "No observable difference between variant B and control A"
    elif lift_abs > 0:
        direction_text = "Variant B performs better than control A"
    else:  # lift_abs < 0
        direction_text = "Variant B performs worse than control A"
    lift_rel_formatted = f"{lift_rel_pct:+.2f}%"
    p_value_text = "p < 0.001" if p_value < 0.001 else f"p = {p_value:.3f}"
    if is_significant:
        significance_text = f"The result is statistically significant at α = {alpha:.2f}"
    else:
        significance_text = f"The result is not statistically significant at α = {alpha:.2f}"
    if lift_abs > 0 and is_significant:
        reco_text = "Recommendation: ship variant B; it shows a statistically significant improvement over control A."
    elif lift_abs > 0 and not is_significant:
        reco_text = "Recommendation: continue the test and collect more data before making a decision."
    elif lift_abs < 0 and is_significant:
        reco_text = "Recommendation: keep control A; variant B appears to hurt performance."
    elif lift_abs < 0 and not is_significant:
        reco_text = "Recommendation: keep control A for now; there is no strong evidence that variant B improves performance."
    else:
        reco_text = "Recommendation: no clear evidence of a difference between A and B; you may keep control A or redesign the experiment."
    line1 = f"{direction_text} ({lift_rel_formatted})"
    line2 = f"{significance_text} ({p_value_text})"
    line3 = reco_text

    return line1 + "\n\n" + line2 + "\n\n" + line3
