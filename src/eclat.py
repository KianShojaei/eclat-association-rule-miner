"""ECLAT Algorithm Implementation (Vertical TidList Intersection & Diffset Acceleration)."""

import math
from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Set, Tuple


@dataclass
class FrequentItemset:
    """Represents a discovered frequent pattern (k-itemset)."""

    items: Tuple[str, ...]
    support_count: int
    relative_support: float
    tids: Set[str]
    is_closed: bool = False
    is_maximal: bool = False

    @property
    def k(self) -> int:
        return len(self.items)

    @property
    def itemset_key(self) -> FrozenSet[str]:
        return frozenset(self.items)


class EclatMiner:
    """Implements the ECLAT (Equivalence Class Transformation) depth-first search algorithm.

    Supports both:
    1. Standard Vertical TidList Intersection: t(XY) = t(X) intersect t(Y) (Slide 26)
    2. Diffset Acceleration: d(XY) = d(Y) - d(X) (Slide 26)
    Also identifies Closed Patterns (Slide 13) and Max-Patterns (Slide 14).
    """

    def __init__(self, use_diffset: bool = False) -> None:
        self.use_diffset = use_diffset

    def mine_frequent_itemsets(
        self,
        transactions: List[Tuple[str, List[str]]],
        min_support: float = 0.5,
    ) -> List[FrequentItemset]:
        """Mine all frequent itemsets from a transactional dataset using ECLAT.

        Args:
            transactions: List of (TID, [item1, item2, ...]) tuples.
            min_support: Relative minimum support threshold in (0.0, 1.0].

        Returns:
            List of FrequentItemset objects sorted by support and length.
        """
        num_trans = len(transactions)
        if num_trans == 0 or min_support <= 0.0:
            return []

        # Minimum absolute support count (sigma): e.g., ceil(0.5 * 5) = 3 (or exact >= min_support)
        min_sup_count = max(1, math.ceil(round(min_support * num_trans, 9)))

        # Step 1: Transform Horizontal DB to Vertical Data Format (Item -> TidList)
        vertical_db: Dict[str, Set[str]] = {}
        all_tids: Set[str] = set()
        for tid, items in transactions:
            all_tids.add(tid)
            for item in set(items):
                vertical_db.setdefault(item, set()).add(tid)

        # Step 2: Filter frequent 1-itemsets
        freq_1_items: List[Tuple[str, Set[str]]] = []
        for item in sorted(vertical_db.keys()):
            tids = vertical_db[item]
            if len(tids) >= min_sup_count:
                freq_1_items.append((item, tids))

        discovered: Dict[FrozenSet[str], Tuple[Tuple[str, ...], int, Set[str]]] = {}

        # Step 3: Recursive Depth-First Search (DFS) equivalence class mining
        if not self.use_diffset:
            self._eclat_tidlist_dfs(
                prefix=(),
                items_tidlists=freq_1_items,
                min_sup_count=min_sup_count,
                discovered=discovered,
            )
        else:
            # In Diffset mode, for 1-itemsets we store diffset with respect to all_tids: d(X) = T_all - t(X)
            items_diffsets: List[Tuple[str, int, Set[str], Set[str]]] = [
                (item, len(tids), all_tids - tids, tids) for item, tids in freq_1_items
            ]
            self._eclat_diffset_dfs(
                prefix=(),
                items_data=items_diffsets,
                min_sup_count=min_sup_count,
                discovered=discovered,
            )

        # Step 4: Construct result objects and mark Closed (Slide 13) & Maximal (Slide 14) patterns
        results: List[FrequentItemset] = []
        all_keys = list(discovered.keys())

        for key, (items_tuple, sup_cnt, tids_set) in discovered.items():
            # Closed pattern (Slide 13): no proper super-pattern Y > X has the SAME support as X
            is_closed = True
            # Max-pattern (Slide 14): no proper super-pattern Y > X is frequent
            is_maximal = True

            for other_key in all_keys:
                if other_key != key and key.issubset(other_key):
                    is_maximal = False
                    other_sup = discovered[other_key][1]
                    if other_sup == sup_cnt:
                        is_closed = False
                        break

            results.append(
                FrequentItemset(
                    items=items_tuple,
                    support_count=sup_cnt,
                    relative_support=sup_cnt / num_trans,
                    tids=tids_set,
                    is_closed=is_closed,
                    is_maximal=is_maximal,
                )
            )

        results.sort(key=lambda x: (x.k, -x.support_count, x.items))
        return results

    def _eclat_tidlist_dfs(
        self,
        prefix: Tuple[str, ...],
        items_tidlists: List[Tuple[str, Set[str]]],
        min_sup_count: int,
        discovered: Dict[FrozenSet[str], Tuple[Tuple[str, ...], int, Set[str]]],
    ) -> None:
        """Recursive DFS using vertical TidList set intersections: t(P U {x, y}) = t(Px) intersect t(Py)."""
        n = len(items_tidlists)
        for i in range(n):
            item_i, tids_i = items_tidlists[i]
            new_prefix = prefix + (item_i,)
            sup_i = len(tids_i)
            discovered[frozenset(new_prefix)] = (new_prefix, sup_i, tids_i)

            # Build equivalence class suffix extensions
            suffix_extensions: List[Tuple[str, Set[str]]] = []
            for j in range(i + 1, n):
                item_j, tids_j = items_tidlists[j]
                intersected_tids = tids_i.intersection(tids_j)
                if len(intersected_tids) >= min_sup_count:
                    suffix_extensions.append((item_j, intersected_tids))

            if suffix_extensions:
                self._eclat_tidlist_dfs(
                    prefix=new_prefix,
                    items_tidlists=suffix_extensions,
                    min_sup_count=min_sup_count,
                    discovered=discovered,
                )

    def _eclat_diffset_dfs(
        self,
        prefix: Tuple[str, ...],
        items_data: List[Tuple[str, int, Set[str], Set[str]]],
        min_sup_count: int,
        discovered: Dict[FrozenSet[str], Tuple[Tuple[str, ...], int, Set[str]]],
    ) -> None:
        """Recursive DFS using Diffsets (Slide 26):
        Diffset(Px, Py) = d(Py) - d(Px), and sup(Pxy) = sup(Px) - |Diffset(Px, Py)|.
        """
        n = len(items_data)
        for i in range(n):
            item_i, sup_i, diff_i, tids_i = items_data[i]
            new_prefix = prefix + (item_i,)
            discovered[frozenset(new_prefix)] = (new_prefix, sup_i, tids_i)

            suffix_extensions: List[Tuple[str, int, Set[str], Set[str]]] = []
            for j in range(i + 1, n):
                item_j, _, diff_j, tids_j = items_data[j]
                # Slide 26 formula: Diffset(Pxy) = d(Py) - d(Px)
                new_diff = diff_j - diff_i
                new_sup = sup_i - len(new_diff)
                if new_sup >= min_sup_count:
                    new_tids = tids_i.intersection(tids_j)
                    suffix_extensions.append((item_j, new_sup, new_diff, new_tids))

            if suffix_extensions:
                self._eclat_diffset_dfs(
                    prefix=new_prefix,
                    items_data=suffix_extensions,
                    min_sup_count=min_sup_count,
                    discovered=discovered,
                )
