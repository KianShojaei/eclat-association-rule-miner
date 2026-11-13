"""UI subpackage for ECLAT Association Rule Miner."""

from src.ui.styles import get_custom_css
from src.ui.components import (
    render_header,
    render_summary_metrics,
    render_horizontal_and_vertical_tables,
    render_frequent_itemsets_section,
    render_association_rules_section,
    render_contingency_inspector,
    render_formulas_reference,
)

__all__ = [
    "get_custom_css",
    "render_header",
    "render_summary_metrics",
    "render_horizontal_and_vertical_tables",
    "render_frequent_itemsets_section",
    "render_association_rules_section",
    "render_contingency_inspector",
    "render_formulas_reference",
]
