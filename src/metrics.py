"""Pattern Evaluation & Interestingness Measures from Chapter 4 (Slides 38 to 45)."""

import math
from typing import Dict


class PatternEvaluationMetrics:
    """Computes all pattern evaluation measures taught in Chapter 4 (Slides 38-45):
    - Lift (Slide 38)
    - Chi-Square / χ² (Slide 39)
    - AllConfidence (Slide 41)
    - Jaccard (Slide 41)
    - Cosine (Slide 41)
    - Kulczynski / Kulc (Slide 41 & 43)
    - MaxConfidence (Slide 41)
    - Imbalance Ratio / IR (Slide 44)
    """

    @staticmethod
    def compute_all_metrics(
        sup_x_count: int,
        sup_y_count: int,
        sup_xy_count: int,
        total_transactions: int,
    ) -> Dict[str, float]:
        """Compute all interestingness measures for association rule X => Y."""
        if total_transactions <= 0 or sup_x_count <= 0 or sup_y_count <= 0:
            return {
                "support": 0.0,
                "confidence": 0.0,
                "lift": 0.0,
                "kulczynski": 0.0,
                "imbalance_ratio": 0.0,
                "cosine": 0.0,
                "jaccard": 0.0,
                "all_conf": 0.0,
                "max_conf": 0.0,
                "chi_square": 0.0,
            }

        s_x = sup_x_count / total_transactions
        s_y = sup_y_count / total_transactions
        s_xy = sup_xy_count / total_transactions

        # Conditional probabilities p = P(Y|X) = s(X U Y)/s(X) and q = P(X|Y) = s(X U Y)/s(Y) (Slide 41)
        p_y_given_x = s_xy / s_x  # Confidence of X => Y
        p_x_given_y = s_xy / s_y  # Confidence of Y => X

        # 1. Lift(X, Y) = s(X U Y) / (s(X) * s(Y)) (Slide 38)
        lift = s_xy / (s_x * s_y) if (s_x * s_y) > 0 else 0.0

        # 2. AllConf(X, Y) = s(X U Y) / max(s(X), s(Y)) = min(P(Y|X), P(X|Y)) (Slide 41)
        all_conf = s_xy / max(s_x, s_y)

        # 3. MaxConf(X, Y) = max(s(X U Y)/s(X), s(X U Y)/s(Y)) = max(P(Y|X), P(X|Y)) (Slide 41)
        max_conf = max(p_y_given_x, p_x_given_y)

        # 4. Kulczynski: Kulc(X, Y) = 0.5 * (s(X U Y)/s(X) + s(X U Y)/s(Y)) (Slide 41 & 43)
        kulczynski = 0.5 * (p_y_given_x + p_x_given_y)

        # 5. Cosine(X, Y) = s(X U Y) / sqrt(s(X) * s(Y)) = sqrt(P(Y|X) * P(X|Y)) (Slide 41)
        cosine = s_xy / math.sqrt(s_x * s_y)

        # 6. Jaccard(X, Y) = s(X U Y) / (s(X) + s(Y) - s(X U Y)) (Slide 41)
        denom_jaccard = s_x + s_y - s_xy
        jaccard = s_xy / denom_jaccard if denom_jaccard > 0 else 0.0

        # 7. Imbalance Ratio: IR(X, Y) = |s(X) - s(Y)| / (s(X) + s(Y) - s(X U Y)) (Slide 44)
        imbalance_ratio = abs(s_x - s_y) / denom_jaccard if denom_jaccard > 0 else 0.0

        # 8. Chi-Square (χ²) from 2x2 Contingency Table (Slide 39)
        chi_square = PatternEvaluationMetrics.compute_chi_square(
            sup_x_count, sup_y_count, sup_xy_count, total_transactions
        )

        return {
            "support": s_xy,
            "confidence": p_y_given_x,
            "lift": lift,
            "kulczynski": kulczynski,
            "imbalance_ratio": imbalance_ratio,
            "cosine": cosine,
            "jaccard": jaccard,
            "all_conf": all_conf,
            "max_conf": max_conf,
            "chi_square": chi_square,
        }

    @staticmethod
    def compute_chi_square(
        sup_b: int,
        sup_c: int,
        sup_bc: int,
        n: int,
    ) -> float:
        """Compute exact Chi-Square (χ²) statistic on 2x2 contingency table (Slide 39):
        Cells: (B, C), (¬B, C), (B, ¬C), (¬B, ¬C)
        χ² = sum( (Observed - Expected)^2 / Expected )
        """
        if n <= 0:
            return 0.0

        obs_bc = sup_bc
        obs_not_b_c = sup_c - sup_bc
        obs_b_not_c = sup_b - sup_bc
        obs_not_b_not_c = n - sup_b - sup_c + sup_bc

        row_c = sup_c
        row_not_c = n - sup_c
        col_b = sup_b
        col_not_b = n - sup_b

        cells = [
            (obs_bc, (col_b * row_c) / n),
            (obs_not_b_c, (col_not_b * row_c) / n),
            (obs_b_not_c, (col_b * row_not_c) / n),
            (obs_not_b_not_c, (col_not_b * row_not_c) / n),
        ]

        chi_sq = 0.0
        for obs, exp in cells:
            if exp > 0:
                chi_sq += ((obs - exp) ** 2) / exp

        return chi_sq

    @staticmethod
    def interpret_correlation(lift_val: float, kulc_val: float) -> str:
        """Return Persian interpretation of rule correlation based on Slide 38 & 43."""
        if abs(lift_val - 1.0) < 1e-3:
            return "مستقل (Independent)"
        elif lift_val > 1.0:
            if kulc_val >= 0.6:
                return "همبستگی مثبت قوی (Strong Positive)"
            return "همبستگی مثبت (Positive Correlation)"
        else:
            return "همبستگی منفی (Negative Correlation)"
