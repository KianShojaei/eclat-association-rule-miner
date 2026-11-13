"""Association Rule Generation from ECLAT Frequent Itemsets (Slides 9-11)."""

from dataclasses import dataclass
from itertools import combinations
from typing import Dict, FrozenSet, List, Tuple

from src.eclat import FrequentItemset
from src.metrics import PatternEvaluationMetrics


@dataclass
class AssociationRule:
    """Represents a mined Association Rule X => Y along with its evaluation metrics."""

    antecedent: Tuple[str, ...]
    consequent: Tuple[str, ...]
    support_count: int
    support: float
    confidence: float
    metrics: Dict[str, float]
    correlation_label: str

    @property
    def rule_str(self) -> str:
        ant = ", ".join(self.antecedent)
        con = ", ".join(self.consequent)
        return f"{{{ant}}}  ⇒  {{{con}}}"


class AssociationRuleGenerator:
    """Generates strong association rules (s >= minsup, c >= minconf) and computes evaluation metrics."""

    @staticmethod
    def generate_rules(
        frequent_itemsets: List[FrequentItemset],
        total_transactions: int,
        min_confidence: float = 0.5,
    ) -> List[AssociationRule]:
        """Generate all valid association rules X => Y from frequent itemsets.

        Args:
            frequent_itemsets: Output of EclatMiner.mine_frequent_itemsets().
            total_transactions: Total number of transactions |TDB|.
            min_confidence: Minimum confidence threshold in [0.0, 1.0].

        Returns:
            List of AssociationRule objects sorted by Confidence and Support descending.
        """
        if not frequent_itemsets or total_transactions <= 0:
            return []

        # Map frozenset(items) -> support_count for fast O(1) lookup of sup(X) and sup(Y)
        support_map: Dict[FrozenSet[str], int] = {
            fi.itemset_key: fi.support_count for fi in frequent_itemsets
        }

        rules: List[AssociationRule] = []

        for fi in frequent_itemsets:
            if fi.k < 2:
                continue

            items = fi.items
            sup_xy_count = fi.support_count

            # Generate all non-empty proper subsets X of items
            for r in range(1, fi.k):
                for antecedent_tuple in combinations(items, r):
                    ant_key = frozenset(antecedent_tuple)
                    con_tuple = tuple(it for it in items if it not in ant_key)
                    con_key = frozenset(con_tuple)

                    sup_x_count = support_map.get(ant_key, 0)
                    sup_y_count = support_map.get(con_key, 0)
                    if sup_x_count == 0 or sup_y_count == 0:
                        continue

                    confidence = sup_xy_count / sup_x_count
                    if confidence + 1e-9 >= min_confidence:
                        all_metrics = PatternEvaluationMetrics.compute_all_metrics(
                            sup_x_count=sup_x_count,
                            sup_y_count=sup_y_count,
                            sup_xy_count=sup_xy_count,
                            total_transactions=total_transactions,
                        )
                        corr_label = PatternEvaluationMetrics.interpret_correlation(
                            lift_val=all_metrics["lift"],
                            kulc_val=all_metrics["kulczynski"],
                        )
                        rules.append(
                            AssociationRule(
                                antecedent=antecedent_tuple,
                                consequent=con_tuple,
                                support_count=sup_xy_count,
                                support=all_metrics["support"],
                                confidence=all_metrics["confidence"],
                                metrics=all_metrics,
                                correlation_label=corr_label,
                            )
                        )

        rules.sort(key=lambda r: (-r.confidence, -r.support, -r.metrics["kulczynski"]))
        return rules
