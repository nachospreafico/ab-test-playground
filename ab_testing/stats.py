from dataclasses import dataclass
from typing import Optional
from scipy.stats import norm

@dataclass
class ABTestResult:
    """Stores the main metrics and statistical results for an A/B test."""
    n_a: int
    c_a: int
    n_b: int
    c_b: int
    cr_a: float
    cr_b: float
    lift_abs: float
    lift_rel: float
    z_score: float
    p_value: float
    alpha: float
    is_significant: bool

class InvalidABTestInput(Exception):
    """Raised when A/B test input values are invalid."""
    pass

def conversion_rate(conversions: int, total: int) -> float:
    """
    Computes conversion rate as conversions / total.

    Args:
        conversions: Number of converted users.
        total: Total users in the group.

    Returns:
        Conversion rate as a float between 0 and 1.
    """
    if total == 0:
        return 0.0
    return conversions / total

def compute_lift(cr_a: float, cr_b: float) -> tuple[float, float]:
    """
    Computes absolute and relative lift of variant B vs control A.

    Args:
        cr_a: Conversion rate of control (A).
        cr_b: Conversion rate of variant (B).

    Returns:
        (lift_abs, lift_rel) where:
            lift_abs = cr_b - cr_a
            lift_rel = lift_abs / cr_a  (if cr_a > 0 else 0.0)
    """
    lift_abs = cr_b - cr_a

    if cr_a == 0:
        lift_rel = 0.0
    else:
        lift_rel = lift_abs / cr_a

    return lift_abs, lift_rel

def validate_inputs(n_a: int, c_a: int, n_b: int, c_b: int) -> None:
    '''
    Validates user input and raises appropriate Exceptions if a validation fails:

    Args:
        n_a: Sample size of control (A).
        c_a: Conversions of control (A).
        n_b: Sample size of treatment (B).
        c_b: Conversions of treatment (B)

    Returns:
        None
    '''
    def _raise_if_invalid_group(n: int, c: int, label: str) -> None:
        if n < 0:
            raise InvalidABTestInput(f"Group {label} sample size is negative")
        if c < 0:
            raise InvalidABTestInput(f"Group {label} conversions are negative")
        if n == 0:
            raise InvalidABTestInput(f"Group {label} sample size cannot be 0")
        if c > n:
            raise InvalidABTestInput(f"Group {label} conversions are greater than sample size")
    _raise_if_invalid_group(n_a, c_a, "A")
    _raise_if_invalid_group(n_b, c_b, "B")

def z_test_proportions(n_a: int, c_a: int, n_b: int, c_b: int, alternative: str = "two-sided") -> tuple[float, float]:
    '''
    Computes the z-score and p-value for the difference between two proportions.

    Args:
        n_a: Sample size of control (A).
        c_a: Conversions of control (A).
        n_b: Sample size of treatment (B).
        c_b: Conversions of treatment (B).
        alternative: Alternative hypothesis to test 
            ('two-sided', 'larger', or 'smaller'). Defaults to 'two-sided'.

    Returns:
        A tuple (z_score, p_value)
    '''
    cr_a, cr_b = conversion_rate(c_a, n_a), conversion_rate(c_b, n_b)
    pooled = (c_a + c_b) / (n_a + n_b)
    standard_error = (pooled * (1 - pooled) * (1/n_a + 1/n_b))**0.5
    if standard_error == 0:
        return 0.0, 1.0
    z_score = (cr_b - cr_a) / standard_error
    if alternative == "two-sided":
        p_value = 2 * (1 - norm.cdf(abs(z_score)))
    elif alternative == "larger":
        p_value = 1 - norm.cdf(z_score)
    elif alternative == "smaller":
        p_value = norm.cdf(z_score)
    else:
        raise ValueError("alternative must be 'two-sided', 'larger', or 'smaller'")
    return (z_score, p_value)

def run_ab_test(n_a: int, c_a: int, n_b: int, c_b: int, alpha: float = 0.05, alternative: str = "two-sided") -> ABTestResult:
    """
    Runs a full A/B test analysis:
    - validates inputs
    - computes conversion rates
    - computes absolute and relative lift
    - performs a z-test
    - determines statistical significance

    Args:
        n_a: Sample size of control (A).
        c_a: Conversions of control (A).
        n_b: Sample size of treatment (B).
        c_b: Conversions of treatment (B).
        alpha: Significance level. Defaults to 0.05.
        alternative: Hypothesis alternative ('two-sided', 'larger', 'smaller').

    Returns:
        ABTestResult object containing all computed metrics.
    """
    validate_inputs(n_a, c_a, n_b, c_b)
    cr_a, cr_b = conversion_rate(c_a, n_a), conversion_rate(c_b, n_b)
    lift_abs, lift_rel = compute_lift(cr_a, cr_b)
    z_score, p_value = z_test_proportions(n_a, c_a, n_b, c_b, alternative)
    is_significant = p_value < alpha

    return ABTestResult(
        n_a=n_a,
        c_a=c_a,
        n_b=n_b,
        c_b=c_b,
        cr_a=cr_a,
        cr_b=cr_b,
        lift_abs=lift_abs,
        lift_rel=lift_rel,
        z_score=z_score,
        p_value=p_value,
        alpha=alpha,
        is_significant=is_significant,
    )

