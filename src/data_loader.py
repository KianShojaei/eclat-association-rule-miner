"""Transactional database loader and Horizontal-to-Vertical converter."""

import csv
import io
from typing import Dict, List, Set, Tuple


class TransactionLoader:
    """Loads transactional datasets from CSV/TXT/Raw strings and converts to Vertical TidList format."""

    @staticmethod
    def parse_transactions_from_csv(csv_content: str) -> List[Tuple[str, List[str]]]:
        """Parse transactions from CSV string.

        Supports two formats:
        1. Two-column format: TID, Items (comma-separated inside quotes)
        2. Multi-column basket format: each row is a list of items
        """
        lines = [line.strip() for line in csv_content.strip().splitlines() if line.strip()]
        if not lines:
            return []

        reader = list(csv.reader(io.StringIO("\n".join(lines))))
        if not reader:
            return []

        # Check if first row is a header
        first_row_lower = [c.strip().lower() for c in reader[0]]
        start_idx = 1 if ("tid" in first_row_lower or "items" in first_row_lower or "id" in first_row_lower) else 0

        transactions: List[Tuple[str, List[str]]] = []
        for idx, row in enumerate(reader[start_idx:], start=1):
            clean_cols = [c.strip() for c in row if c.strip()]
            if not clean_cols:
                continue

            if len(clean_cols) == 2 and ("," in clean_cols[1] or ";" in clean_cols[1] or " " in clean_cols[1]):
                tid = clean_cols[0]
                raw_items = clean_cols[1].replace(";", ",")
                items = [it.strip() for it in raw_items.split(",") if it.strip()]
            elif len(clean_cols) >= 2 and start_idx == 1 and "tid" in first_row_lower[0]:
                tid = clean_cols[0]
                items = []
                for col in clean_cols[1:]:
                    items.extend([it.strip() for it in col.split(",") if it.strip()])
            else:
                tid = f"T{idx}"
                items = []
                for col in clean_cols:
                    items.extend([it.strip() for it in col.split(",") if it.strip()])

            # Deduplicate preserving order
            unique_items = list(dict.fromkeys(items))
            if unique_items:
                transactions.append((str(tid), unique_items))

        return transactions

    @staticmethod
    def to_vertical_format(
        transactions: List[Tuple[str, List[str]]]
    ) -> Tuple[Dict[str, Set[str]], Set[str]]:
        """Convert Horizontal Transaction DB to Vertical Data Format (Item -> TidList).

        Matches Slide 26:
            Horizontal: T10 -> {a, c, d, e}
            Vertical:   a -> {T10, T20}, e -> {T10, T20, T30}, ...
        """
        vertical_db: Dict[str, Set[str]] = {}
        all_tids: Set[str] = set()

        for tid, items in transactions:
            all_tids.add(tid)
            for item in items:
                if item not in vertical_db:
                    vertical_db[item] = set()
                vertical_db[item].add(tid)

        return vertical_db, all_tids
