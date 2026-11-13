"""Streamlit UI rendering components for ECLAT & Association Rule Mining (Humanized & Clean)."""

import html
from typing import Dict, List, Set, Tuple
import pandas as pd
import streamlit as st

import config
from src.eclat import FrequentItemset
from src.rules import AssociationRule


def render_header(dataset_title: str, mode_label: str, minsup: float, minconf: float) -> None:
    """Render hero header banner with Material Symbols icons."""
    header_html = (
        '<div class="app-hero-header">'
        '<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">'
        '<div>'
        '<h1 style="display: flex; align-items: center; gap: 10px;">'
        '<span class="ms-icon" style="font-size: 2.1rem;">account_tree</span>'
        '<span>استخراج الگوهای پرتکرار و قواعد انجمنی با الگوریتم ECLAT</span>'
        '</h1>'
        '<p>پیاده‌سازی مبتنی بر ساختار عمودی تراکنش‌ها (TidList & Diffset) به همراه ارزیابی آماری قواعد استخراج‌شده</p>'
        '</div>'
        '<div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">'
        f'<span class="hero-pill"><span class="ms-icon">dataset</span> {html.escape(dataset_title)}</span>'
        f'<span class="hero-pill"><span class="ms-icon">bolt</span> روش: {html.escape(mode_label)}</span>'
        f'<span class="hero-pill" style="direction:ltr;">minsup = {minsup*100:.0f}% | minconf = {minconf*100:.0f}%</span>'
        '</div></div></div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)


def render_summary_metrics(
    num_transactions: int,
    num_unique_items: int,
    frequent_itemsets: List[FrequentItemset],
    rules: List[AssociationRule],
) -> None:
    """Render top 4 KPI summary cards with clean RTL alignment."""
    closed_count = sum(1 for fi in frequent_itemsets if fi.is_closed)
    max_count = sum(1 for fi in frequent_itemsets if fi.is_maximal)
    max_k = max((fi.k for fi in frequent_itemsets), default=0)

    kpi_html = (
        '<div class="kpi-grid">'
        '<div class="kpi-card">'
        '<div class="kpi-header-row"><span class="kpi-title">تعداد کل تراکنش‌ها</span><span class="ms-icon" style="color:#4f46e5;">receipt_long</span></div>'
        f'<div class="kpi-value">{num_transactions}</div>'
        f'<div class="kpi-sub">تعداد آیتم‌های یکتا: {num_unique_items} مورد</div>'
        '</div>'
        '<div class="kpi-card">'
        '<div class="kpi-header-row"><span class="kpi-title">الگوهای پرتکرار کشف‌شده</span><span class="ms-icon" style="color:#4f46e5;">layers</span></div>'
        f'<div class="kpi-value">{len(frequent_itemsets)}</div>'
        f'<div class="kpi-sub">بیشترین طول الگو: {max_k} آیتم</div>'
        '</div>'
        '<div class="kpi-card">'
        '<div class="kpi-header-row"><span class="kpi-title">الگوهای بسته و ماکسیمال</span><span class="ms-icon" style="color:#4f46e5;">compress</span></div>'
        f'<div class="kpi-value">{closed_count} / {max_count}</div>'
        f'<div class="kpi-sub">تعداد Closed / تعداد Maximal</div>'
        '</div>'
        '<div class="kpi-card">'
        '<div class="kpi-header-row"><span class="kpi-title">قواعد انجمنی استخراج‌شده</span><span class="ms-icon" style="color:#4f46e5;">rule</span></div>'
        f'<div class="kpi-value">{len(rules)}</div>'
        '<div class="kpi-sub">بر اساس آستانه Support و Confidence</div>'
        '</div>'
        '</div>'
    )
    st.markdown(kpi_html, unsafe_allow_html=True)


def render_horizontal_and_vertical_tables(
    transactions: List[Tuple[str, List[str]]],
    vertical_db: Dict[str, Set[str]],
    all_tids: Set[str],
) -> None:
    """Render Horizontal Transaction DB vs. Vertical TidList/Diffset tables."""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<h4 style="display:flex; align-items:center; gap:6px;"><span class="ms-icon" style="color:#4f46e5;">table_rows</span> نمایش افقی تراکنش‌ها (Horizontal Format)</h4>',
            unsafe_allow_html=True,
        )
        horiz_rows = [
            {
                "شناسه تراکنش (TID)": tid,
                "آیتم‌های تراکنش (Items)": ", ".join(items),
                "تعداد آیتم": len(items),
            }
            for tid, items in transactions
        ]
        st.dataframe(pd.DataFrame(horiz_rows), width="stretch", hide_index=True)

    with col2:
        st.markdown(
            '<h4 style="display:flex; align-items:center; gap:6px;"><span class="ms-icon" style="color:#0284c7;">view_column</span> نمایش عمودی آیتم‌ها (Vertical TidList & Diffset)</h4>',
            unsafe_allow_html=True,
        )
        vert_rows = []
        for item in sorted(vertical_db.keys()):
            tids = sorted(vertical_db[item], key=lambda x: (len(x), x))
            diff_tids = sorted(all_tids - vertical_db[item], key=lambda x: (len(x), x))
            vert_rows.append(
                {
                    "آیتم (Item)": item,
                    "TidList t(X)": "{" + ", ".join(tids) + "}",
                    "Diffset d(X)": "{" + ", ".join(diff_tids) + "}" if diff_tids else "∅",
                    "تعداد تکرار sup(X)": len(tids),
                    "حمایت نسبی s(X)": f"{(len(tids)/len(transactions))*100:.1f}%",
                }
            )
        st.dataframe(pd.DataFrame(vert_rows), width="stretch", hide_index=True)


def render_frequent_itemsets_section(frequent_itemsets: List[FrequentItemset]) -> None:
    """Render mined frequent k-itemsets along with Closed/Max pattern indicators."""
    if not frequent_itemsets:
        st.warning("هیچ الگوی پرتکراری با آستانه minsup فعلی یافت نشد. لطفاً مقدار minsup را کاهش دهید.")
        return

    col_filter1, _ = st.columns([1, 2])
    with col_filter1:
        pattern_filter = st.radio(
            "فیلتر نمایش الگوها:",
            ["همه الگوهای پرتکرار", "فقط الگوهای بسته (Closed)", "فقط الگوهای ماکسیمال (Maximal)"],
            horizontal=False,
        )

    filtered = frequent_itemsets
    if "Closed" in pattern_filter:
        filtered = [fi for fi in frequent_itemsets if fi.is_closed]
    elif "Maximal" in pattern_filter:
        filtered = [fi for fi in frequent_itemsets if fi.is_maximal]

    rows = []
    for idx, fi in enumerate(filtered, start=1):
        sorted_tids = sorted(fi.tids, key=lambda x: (len(x), x))
        rows.append(
            {
                "#": idx,
                "طول الگو (k)": f"{fi.k}-itemset",
                "مجموعه آیتم (Itemset)": "{" + ", ".join(fi.items) + "}",
                "تعداد تکرار sup(X)": fi.support_count,
                "حمایت نسبی s(X)": f"{fi.relative_support * 100:.1f}%",
                "لیست تراکنش‌ها (TidList)": "{" + ", ".join(sorted_tids) + "}",
                "الگوی بسته (Closed)": "بله" if fi.is_closed else "خیر",
                "الگوی ماکسیمال (Maximal)": "بله" if fi.is_maximal else "خیر",
            }
        )

    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def render_association_rules_section(
    rules: List[AssociationRule],
    selected_metrics: List[str],
) -> None:
    """Render visual rule cards and downloadable rules DataFrame with chosen evaluation metrics."""
    if not rules:
        st.warning("هیچ قاعده انجمنی با آستانه‌های فعلی یافت نشد. لطفاً مقادیر minsup یا minconf را در نوار کناری کاهش دهید.")
        return

    st.markdown(
        f'<h3 style="display:flex; align-items:center; gap:8px;"><span class="ms-icon" style="color:#4f46e5;">auto_awesome</span> قواعد انجمنی استخراج‌شده ({len(rules)} قاعده)</h3>',
        unsafe_allow_html=True,
    )

    for idx, r in enumerate(rules[:12], start=1):
        ant_badges = "".join(f'<span class="item-badge item-ant">{html.escape(it)}</span>' for it in r.antecedent)
        con_badges = "".join(f'<span class="item-badge item-con">{html.escape(it)}</span>' for it in r.consequent)

        if "مثبت" in r.correlation_label:
            corr_cls = "corr-pos"
        elif "منفی" in r.correlation_label:
            corr_cls = "corr-neg"
        else:
            corr_cls = "corr-ind"

        metric_pills_html = (
            f'<span class="metric-pill"><b>Support:</b> {r.support*100:.1f}% ({r.support_count})</span>'
            f'<span class="metric-pill"><b>Confidence:</b> {r.confidence*100:.1f}%</span>'
        )
        for m_key in selected_metrics:
            m_val = r.metrics.get(m_key, 0.0)
            m_short = m_key.upper() if m_key != "imbalance_ratio" else "IR"
            if m_key == "kulczynski":
                m_short = "Kulczynski"
            elif m_key == "chi_square":
                m_short = "Chi-Square"
            elif m_key == "lift":
                m_short = "Lift"
            metric_pills_html += f'<span class="metric-pill" style="border-color:rgba(79,70,229,0.4);"><b>{m_short}:</b> {m_val:.4f}</span>'

        card_html = (
            f'<div class="rule-card">'
            f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:10px;">'
            f'<div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">'
            f'<span style="font-weight:900; color:#4f46e5;">قاعده #{idx}:</span>'
            f'{ant_badges}'
            f'<span class="ms-icon" style="color:#64748b;">arrow_back</span>'
            f'{con_badges}'
            f'</div>'
            f'<span class="{corr_cls}">{html.escape(r.correlation_label)}</span>'
            f'</div>'
            f'<div style="display:flex; flex-wrap:wrap; gap:4px;">{metric_pills_html}</div>'
            f'</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)

    st.markdown(
        '<h4 style="display:flex; align-items:center; gap:6px; margin-top:1.5rem;"><span class="ms-icon" style="color:#4f46e5;">table_chart</span> جدول کامل قواعد انجمنی و معیارهای ارزیابی</h4>',
        unsafe_allow_html=True,
    )
    table_rows = []
    for idx, r in enumerate(rules, start=1):
        row_dict = {
            "#": idx,
            "مقدم (X)": "{" + ", ".join(r.antecedent) + "}",
            "تالی (Y)": "{" + ", ".join(r.consequent) + "}",
            "قاعده (X ⇒ Y)": r.rule_str,
            "Support Count": r.support_count,
            "Support": round(r.support, 4),
            "Confidence": round(r.confidence, 4),
        }
        for m_key in selected_metrics:
            label = config.AVAILABLE_METRICS.get(m_key, m_key).split("(")[0].strip()
            row_dict[label] = round(r.metrics.get(m_key, 0.0), 4)
        row_dict["وضعیت همبستگی"] = r.correlation_label
        table_rows.append(row_dict)

    df_rules = pd.DataFrame(table_rows)
    st.dataframe(df_rules, width="stretch", hide_index=True)

    csv_bytes = df_rules.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="خروجی CSV از جدول قواعد انجمنی",
        data=csv_bytes,
        file_name="eclat_association_rules.csv",
        mime="text/csv",
    )


def render_contingency_inspector(
    rules: List[AssociationRule],
    frequent_itemsets: List[FrequentItemset],
    total_transactions: int,
) -> None:
    """Render 2x2 Contingency Table and all evaluation metrics for a selected rule."""
    if not rules:
        return

    st.markdown("---")
    st.markdown(
        '<h4 style="display:flex; align-items:center; gap:6px;"><span class="ms-icon" style="color:#4f46e5;">troubleshoot</span> بررسی جزئیات آماری و جدول توافقی (Contingency Table)</h4>',
        unsafe_allow_html=True,
    )

    rule_options = [f"قاعده #{i+1}: {r.rule_str} (Confidence = {r.confidence*100:.1f}%)" for i, r in enumerate(rules)]
    selected_idx = st.selectbox("انتخاب قاعده جهت مشاهده جدول توافقی و تمام متریک‌ها:", range(len(rules)), format_func=lambda i: rule_options[i])
    rule = rules[selected_idx]

    sup_map = {fi.itemset_key: fi.support_count for fi in frequent_itemsets}
    sup_x = sup_map.get(frozenset(rule.antecedent), 0)
    sup_y = sup_map.get(frozenset(rule.consequent), 0)
    sup_xy = rule.support_count
    n = total_transactions

    xy = sup_xy
    not_x_y = sup_y - sup_xy
    x_not_y = sup_x - sup_xy
    not_x_not_y = n - sup_x - sup_y + sup_xy

    col_t, col_m = st.columns([1, 1])
    with col_t:
        st.markdown("**جدول توافقی ۲×۲ (2-Way Contingency Table):**")
        cont_df = pd.DataFrame(
            [
                {
                    "تالی / مقدم": f"شامل Y ({', '.join(rule.consequent)})",
                    f"شامل X ({', '.join(rule.antecedent)})": xy,
                    "فاقد X (¬X)": not_x_y,
                    "جمع سطر (Σ row)": sup_y,
                },
                {
                    "تالی / مقدم": "فاقد Y (¬Y)",
                    f"شامل X ({', '.join(rule.antecedent)})": x_not_y,
                    "فاقد X (¬X)": not_x_not_y,
                    "جمع سطر (Σ row)": n - sup_y,
                },
                {
                    "تالی / مقدم": "جمع ستون (Σ col)",
                    f"شامل X ({', '.join(rule.antecedent)})": sup_x,
                    "فاقد X (¬X)": n - sup_x,
                    "جمع سطر (Σ row)": n,
                },
            ]
        )
        st.dataframe(cont_df, width="stretch", hide_index=True)

    with col_m:
        st.markdown("**مقادیر کامل معیارهای ارزیابی برای این قاعده:**")
        m = rule.metrics
        all_m_df = pd.DataFrame(
            [
                {"معیار ارزیابی (Metric)": "Support s(X ∪ Y)", "مقدار محاسباتی": f"{m['support']:.4f} ({m['support']*100:.1f}%)", "Null-Invariant": "—"},
                {"معیار ارزیابی (Metric)": "Confidence c(X ⇒ Y)", "مقدار محاسباتی": f"{m['confidence']:.4f} ({m['confidence']*100:.1f}%)", "Null-Invariant": "—"},
                {"معیار ارزیابی (Metric)": "Lift(X, Y)", "مقدار محاسباتی": f"{m['lift']:.4f}", "Null-Invariant": "No"},
                {"معیار ارزیابی (Metric)": "Chi-Square χ²(X, Y)", "مقدار محاسباتی": f"{m['chi_square']:.4f}", "Null-Invariant": "No"},
                {"معیار ارزیابی (Metric)": "Kulczynski Kulc(X, Y)", "مقدار محاسباتی": f"{m['kulczynski']:.4f}", "Null-Invariant": "Yes"},
                {"معیار ارزیابی (Metric)": "Imbalance Ratio IR(X, Y)", "مقدار محاسباتی": f"{m['imbalance_ratio']:.4f}", "Null-Invariant": "Yes"},
                {"معیار ارزیابی (Metric)": "Cosine(X, Y)", "مقدار محاسباتی": f"{m['cosine']:.4f}", "Null-Invariant": "Yes"},
                {"معیار ارزیابی (Metric)": "Jaccard(X, Y)", "مقدار محاسباتی": f"{m['jaccard']:.4f}", "Null-Invariant": "Yes"},
                {"معیار ارزیابی (Metric)": "AllConf(X, Y)", "مقدار محاسباتی": f"{m['all_conf']:.4f}", "Null-Invariant": "Yes"},
                {"معیار ارزیابی (Metric)": "MaxConf(X, Y)", "مقدار محاسباتی": f"{m['max_conf']:.4f}", "Null-Invariant": "Yes"},
            ]
        )
        st.dataframe(all_m_df, width="stretch", hide_index=True)


def render_formulas_reference() -> None:
    """Render clean, pure-English LTR mathematical formulas so LaTeX never scrambles."""
    st.markdown('<div class="math-ltr-box"><h4>1. ECLAT Vertical TidList Intersection & Diffset</h4></div>', unsafe_allow_html=True)
    st.latex(r"t(X \cup Y) = t(X) \cap t(Y), \qquad \text{sup}(X \cup Y) = |t(X \cup Y)|")
    st.latex(r"\text{Diffset}(XY, X) = d(Y) - d(X), \qquad \text{sup}(XY) = \text{sup}(X) - |\text{Diffset}(XY, X)|")

    st.markdown('<div class="math-ltr-box"><h4>2. Support & Confidence of Association Rule (X ⇒ Y)</h4></div>', unsafe_allow_html=True)
    st.latex(r"\text{Support}(X \Rightarrow Y) = s(X \cup Y) = \frac{\text{sup}(X \cup Y)}{|TDB|}")
    st.latex(r"\text{Confidence}(X \Rightarrow Y) = P(Y \mid X) = \frac{s(X \cup Y)}{s(X)}")

    st.markdown('<div class="math-ltr-box"><h4>3. Correlation & Null-Invariant Evaluation Metrics</h4></div>', unsafe_allow_html=True)
    st.latex(r"\text{Lift}(X, Y) = \frac{s(X \cup Y)}{s(X) \times s(Y)}, \qquad \chi^2 = \sum \frac{(\text{Observed} - \text{Expected})^2}{\text{Expected}}")
    st.latex(r"\text{Kulc}(X, Y) = \frac{1}{2}\left( \frac{s(X \cup Y)}{s(X)} + \frac{s(X \cup Y)}{s(Y)} \right) = \frac{P(Y \mid X) + P(X \mid Y)}{2}")
    st.latex(r"\text{IR}(X, Y) = \frac{|s(X) - s(Y)|}{s(X) + s(Y) - s(X \cup Y)}")
    st.latex(r"\text{Cosine}(X, Y) = \frac{s(X \cup Y)}{\sqrt{s(X) \times s(Y)}}, \qquad \text{Jaccard}(X, Y) = \frac{s(X \cup Y)}{s(X) + s(Y) - s(X \cup Y)}")
    st.latex(r"\text{AllConf}(X, Y) = \frac{s(X \cup Y)}{\max(s(X), s(Y))}, \qquad \text{MaxConf}(X, Y) = \max\left(\frac{s(X \cup Y)}{s(X)}, \frac{s(X \cup Y)}{s(Y)}\right)")
