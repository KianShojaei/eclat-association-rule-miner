"""Additional unit tests for dataset formats, Closed/Max patterns, and UI styles."""

from src.data_loader import TransactionLoader
from src.eclat import EclatMiner
from src.ui.styles import get_custom_css


def test_slide13_and_14_closed_and_max_patterns() -> None:
    # Slide 13 & 14 concept test: T1={a1, a2, a3}, T2={a1, a2, a3, a4, a5} with minsup=0.5 (1 transaction)
    csv_data = 'TID,Items\n1,"a1, a2, a3"\n2,"a1, a2, a3, a4, a5"'
    transactions = TransactionLoader.parse_transactions_from_csv(csv_data)
    miner = EclatMiner(use_diffset=False)
    patterns = miner.mine_frequent_itemsets(transactions, min_support=0.5)

    closed_patterns = [p for p in patterns if p.is_closed]
    max_patterns = [p for p in patterns if p.is_maximal]

    # Exactly 2 closed patterns: {a1,a2,a3}:2 and {a1,a2,a3,a4,a5}:1 (Slide 13)
    assert len(closed_patterns) == 2
    # Exactly 1 max-pattern: {a1,a2,a3,a4,a5}:1 (Slide 14)
    assert len(max_patterns) == 1


def test_custom_css_valid() -> None:
    css = get_custom_css()
    assert "<style>" in css
    assert "Vazirmatn" in css
