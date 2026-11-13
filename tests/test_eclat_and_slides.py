"""Comprehensive unit tests verifying exact mathematical numbers from Chapter 4 Slides."""

import pytest
from src.data_loader import TransactionLoader
from src.eclat import EclatMiner
from src.metrics import PatternEvaluationMetrics
from src.rules import AssociationRuleGenerator


SLIDE_6_CSV = """TID,Items
1,"Water, Nuts, Diaper"
2,"Water, Coffee, Diaper"
3,"Water, Diaper, Eggs"
4,"Nuts, Eggs, Milk"
5,"Nuts, Coffee, Diaper, Eggs, Milk"
"""

SLIDE_26_CSV = """TID,Items
10,"a, c, d, e"
20,"a, b, e"
30,"b, c, e"
"""


class TestSlide6To11Examples:
    """Verify that our implementation reproduces the exact numbers on Slides 6, 7, 8, 10, and 11."""

    def test_slide7_and_8_frequent_itemsets(self) -> None:
        transactions = TransactionLoader.parse_transactions_from_csv(SLIDE_6_CSV)
        assert len(transactions) == 5

        miner = EclatMiner(use_diffset=False)
        freq_itemsets = miner.mine_frequent_itemsets(transactions, min_support=0.5)

        sup_map = {fi.items: (fi.support_count, fi.relative_support) for fi in freq_itemsets}

        # Slide 8: Frequent 1-itemsets with minsup = 50%:
        # Water: 3/5 (60%), Nuts: 3/5 (60%), Diaper: 4/5 (80%), Eggs: 3/5 (60%)
        assert sup_map[("Water",)] == (3, 0.6)
        assert sup_map[("Nuts",)] == (3, 0.6)
        assert sup_map[("Diaper",)] == (4, 0.8)
        assert sup_map[("Eggs",)] == (3, 0.6)
        assert ("Coffee",) not in sup_map
        assert ("Milk",) not in sup_map

        # Slide 8: Frequent 2-itemsets: {Diaper, Water}: 3/5 (60%)
        assert sup_map[("Diaper", "Water")] == (3, 0.6)
        # Total frequent itemsets = 4 (1-itemsets) + 1 (2-itemset) = 5
        assert len(freq_itemsets) == 5

    def test_slide10_and_11_association_rules(self) -> None:
        transactions = TransactionLoader.parse_transactions_from_csv(SLIDE_6_CSV)
        miner = EclatMiner(use_diffset=False)
        freq_itemsets = miner.mine_frequent_itemsets(transactions, min_support=0.5)

        rules = AssociationRuleGenerator.generate_rules(
            frequent_itemsets=freq_itemsets,
            total_transactions=len(transactions),
            min_confidence=0.5,
        )
        assert len(rules) == 2

        rule_dict = {(r.antecedent, r.consequent): r for r in rules}
        # Slide 11: Water -> Diaper (s=60%, c=100%)
        r_wd = rule_dict[(("Water",), ("Diaper",))]
        assert pytest.approx(r_wd.support) == 0.60
        assert pytest.approx(r_wd.confidence) == 1.00

        # Slide 10 & 11: Diaper -> Water (s=60%, c=75%)
        r_dw = rule_dict[(("Diaper",), ("Water",))]
        assert pytest.approx(r_dw.support) == 0.60
        assert pytest.approx(r_dw.confidence) == 0.75


class TestSlide26EclatAndDiffset:
    """Verify Vertical Format, TidList Intersection, and Diffset equivalence on Slide 26."""

    def test_vertical_format_slide26(self) -> None:
        transactions = TransactionLoader.parse_transactions_from_csv(SLIDE_26_CSV)
        v_db, all_tids = TransactionLoader.to_vertical_format(transactions)
        assert all_tids == {"10", "20", "30"}
        assert v_db["a"] == {"10", "20"}
        assert v_db["b"] == {"20", "30"}
        assert v_db["c"] == {"10", "30"}
        assert v_db["d"] == {"10"}
        assert v_db["e"] == {"10", "20", "30"}

    def test_tidlist_and_diffset_produce_identical_results(self) -> None:
        transactions = TransactionLoader.parse_transactions_from_csv(SLIDE_6_CSV)
        miner_tid = EclatMiner(use_diffset=False)
        miner_diff = EclatMiner(use_diffset=True)

        res_tid = miner_tid.mine_frequent_itemsets(transactions, min_support=0.4)
        res_diff = miner_diff.mine_frequent_itemsets(transactions, min_support=0.4)

        assert len(res_tid) == len(res_diff)
        for a, b in zip(res_tid, res_diff):
            assert a.items == b.items
            assert a.support_count == b.support_count
            assert a.tids == b.tids
            assert a.is_closed == b.is_closed
            assert a.is_maximal == b.is_maximal


class TestSlide38To44InterestingnessMetrics:
    """Verify exact mathematical formulas for Lift, Chi-Square, Kulczynski, Cosine, Jaccard, and IR."""

    def test_slide38_lift_basketball_cereal(self) -> None:
        # Slide 37-38: Total=1000, B (basketball)=600, C (cereal)=750, BC=400
        metrics = PatternEvaluationMetrics.compute_all_metrics(
            sup_x_count=600, sup_y_count=750, sup_xy_count=400, total_transactions=1000
        )
        # lift(B, C) = (400/1000) / ((600/1000)*(750/1000)) = 0.4 / 0.45 = 0.8889 (Slide 38 shows 0.89)
        assert pytest.approx(metrics["lift"], rel=1e-2) == 0.89

    def test_slide39_chi_square_basketball_cereal(self) -> None:
        # Slide 39: chi^2 = (400-450)^2/450 + (350-300)^2/300 + (200-150)^2/150 + (50-100)^2/100 = 55.56
        chi2 = PatternEvaluationMetrics.compute_chi_square(
            sup_b=600, sup_c=750, sup_bc=400, n=1000
        )
        assert pytest.approx(chi2, rel=1e-2) == 55.56

    def test_slide43_and_44_null_invariant_measures_d1_to_d6(self) -> None:
        # Slide 43 & 44 Table: D1 has mc=10000, ~mc=1000, m~c=1000, ~m~c=100000
        # Therefore: sup(m) = 11000, sup(c) = 11000, sup(mc) = 10000, total = 122000
        m_d1 = PatternEvaluationMetrics.compute_all_metrics(
            sup_x_count=11000, sup_y_count=11000, sup_xy_count=10000, total_transactions=122000
        )
        # Slide 43 & 44 row D1: Jaccard=0.83, Cosine=0.91, Kulc=0.91, AllConf=0.91, MaxConf=0.91, IR=0
        assert pytest.approx(m_d1["jaccard"], abs=0.01) == 0.83
        assert pytest.approx(m_d1["cosine"], abs=0.01) == 0.91
        assert pytest.approx(m_d1["kulczynski"], abs=0.01) == 0.91
        assert pytest.approx(m_d1["all_conf"], abs=0.01) == 0.91
        assert pytest.approx(m_d1["max_conf"], abs=0.01) == 0.91
        assert pytest.approx(m_d1["imbalance_ratio"], abs=0.01) == 0.0

        # Slide 44 row D5: mc=1000, ~mc=100, m~c=10000, ~m~c=100000
        # sup(m) = 11000, sup(c) = 1100, sup(mc) = 1000, total = 111100
        m_d5 = PatternEvaluationMetrics.compute_all_metrics(
            sup_x_count=11000, sup_y_count=1100, sup_xy_count=1000, total_transactions=111100
        )
        # Slide 44 row D5: Jaccard=0.09, Cosine=0.29, Kulc=0.50, IR=0.89
        assert pytest.approx(m_d5["jaccard"], abs=0.01) == 0.09
        assert pytest.approx(m_d5["cosine"], abs=0.01) == 0.29
        assert pytest.approx(m_d5["kulczynski"], abs=0.01) == 0.50
        assert pytest.approx(m_d5["imbalance_ratio"], abs=0.01) == 0.89
