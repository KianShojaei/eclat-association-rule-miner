"""ECLAT Association Rule Mining & Pattern Evaluation Web Application (Streamlit)."""

from pathlib import Path
import sys
from typing import List
import streamlit as st
from streamlit import runtime

if not runtime.exists():
    from streamlit.web import cli as stcli
    sys.argv = ["streamlit", "run", sys.argv[0]] + sys.argv[1:]
    sys.exit(stcli.main())

import config
from src.data_loader import TransactionLoader
from src.eclat import EclatMiner
from src.rules import AssociationRuleGenerator
from src.ui import (
    get_custom_css,
    render_association_rules_section,
    render_contingency_inspector,
    render_formulas_reference,
    render_frequent_itemsets_section,
    render_header,
    render_horizontal_and_vertical_tables,
    render_summary_metrics,
)

st.set_page_config(
    page_title="استخراج قواعد انجمنی با الگوریتم ECLAT",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(get_custom_css(), unsafe_allow_html=True)


def main() -> None:
    with st.sidebar:
        st.markdown(
            '<h3 style="display:flex; align-items:center; gap:8px;"><span class="ms-icon">tune</span> تنظیمات دیتاست و الگوریتم</h3>',
            unsafe_allow_html=True,
        )

        input_source = st.radio(
            "منبع دیتاست ورودی:",
            [
                "دیتاست‌های نمونه آماده",
                "آپلود فایل دیتاست (CSV / TXT)",
                "ورود یا ویرایش دستی تراکنش‌ها",
            ],
        )

        raw_csv_text = ""
        dataset_title = ""

        if input_source == "دیتاست‌های نمونه آماده":
            preset_keys = list(config.PRESET_DATASETS.keys())
            selected_preset = st.selectbox(
                "انتخاب دیتاست:",
                options=preset_keys,
                format_func=lambda k: config.PRESET_DATASETS[k]["name"],
            )
            preset_info = config.PRESET_DATASETS[selected_preset]
            dataset_title = preset_info["name"].split("(")[0].strip()
            st.caption(preset_info["desc"])
            raw_csv_text = Path(preset_info["path"]).read_text(encoding="utf-8")

        elif input_source == "آپلود فایل دیتاست (CSV / TXT)":
            uploaded = st.file_uploader("فایل CSV یا TXT تراکنش‌ها را انتخاب کنید:", type=["csv", "txt"])
            if uploaded is not None:
                raw_csv_text = uploaded.getvalue().decode("utf-8", errors="ignore")
                dataset_title = f"فایل آپلودشده ({uploaded.name})"
            else:
                st.info("لطفاً یک فایل CSV یا TXT آپلود کنید.")
                raw_csv_text = Path(config.PRESET_DATASETS["market_small"]["path"]).read_text(encoding="utf-8")
                dataset_title = "سبد خرید فروشگاهی ۱"

        else:
            default_manual = Path(config.PRESET_DATASETS["market_small"]["path"]).read_text(encoding="utf-8")
            raw_csv_text = st.text_area(
                "ورود تراکنش‌ها (هر سطر یک تراکنش):",
                value=default_manual,
                height=170,
            )
            dataset_title = "دیتاست دستی کاربر"

        st.markdown("---")
        st.markdown(
            '<div style="font-weight:700; display:flex; align-items:center; gap:6px; margin-bottom:6px;"><span class="ms-icon">sliders</span> آستانه‌های Minsup و Minconf:</div>',
            unsafe_allow_html=True,
        )

        minsup_pct = st.slider(
            "حداقل حمایت (Minimum Support %):",
            min_value=5,
            max_value=100,
            value=50,
            step=5,
        )
        minconf_pct = st.slider(
            "حداقل اطمینان (Minimum Confidence %):",
            min_value=10,
            max_value=100,
            value=50,
            step=5,
        )

        minsup = minsup_pct / 100.0
        minconf = minconf_pct / 100.0

        st.markdown("---")
        st.markdown(
            '<div style="font-weight:700; display:flex; align-items:center; gap:6px; margin-bottom:6px;"><span class="ms-icon">memory</span> نحوه محاسبه در الگوریتم ECLAT:</div>',
            unsafe_allow_html=True,
        )
        use_diffset = st.checkbox(
            "استفاده از ساختار Diffset به جای TidList",
            value=False,
            help="در حالت پیش‌فرض از اشتراک مستقیم TidList استفاده می‌شود. با فعال‌سازی این گزینه، تفاضل شناسه‌های تراکنش (Diffset) محاسبه می‌گردد.",
        )

        st.markdown("---")
        st.markdown(
            '<div style="font-weight:700; display:flex; align-items:center; gap:6px; margin-bottom:6px;"><span class="ms-icon">analytics</span> متریک‌های ارزیابی قواعد:</div>',
            unsafe_allow_html=True,
        )
        metric_keys = list(config.AVAILABLE_METRICS.keys())
        selected_metrics: List[str] = st.multiselect(
            "انتخاب متریک‌های ارزیابی (حداقل ۲ متریک):",
            options=metric_keys,
            default=["lift", "kulczynski", "imbalance_ratio"],
            format_func=lambda k: config.AVAILABLE_METRICS[k],
        )
        if len(selected_metrics) < 2:
            st.warning("حداقل ۲ متریک ارزیابی باید انتخاب شود (Lift و Kulczynski به صورت پیش‌فرض انتخاب شدند).")
            selected_metrics = ["lift", "kulczynski"]

    transactions = TransactionLoader.parse_transactions_from_csv(raw_csv_text)
    vertical_db, all_tids = TransactionLoader.to_vertical_format(transactions)

    mode_label = "ECLAT (Diffset)" if use_diffset else "ECLAT (TidList)"
    render_header(dataset_title=dataset_title, mode_label=mode_label, minsup=minsup, minconf=minconf)

    if not transactions:
        st.error("دیتاست ورودی خالی است یا فرمت معتبری ندارد.")
        return

    miner = EclatMiner(use_diffset=use_diffset)
    frequent_itemsets = miner.mine_frequent_itemsets(transactions, min_support=minsup)
    rules = AssociationRuleGenerator.generate_rules(
        frequent_itemsets=frequent_itemsets,
        total_transactions=len(transactions),
        min_confidence=minconf,
    )

    render_summary_metrics(
        num_transactions=len(transactions),
        num_unique_items=len(vertical_db),
        frequent_itemsets=frequent_itemsets,
        rules=rules,
    )

    tab_rules, tab_itemsets, tab_vertical, tab_formulas = st.tabs([
        f"قواعد انجمنی و متریک‌های ارزیابی ({len(rules)})",
        f"الگوهای پرتکرار ECLAT ({len(frequent_itemsets)})",
        "ساختار افقی و عمودی تراکنش‌ها (TidList & Diffset)",
        "مرجع فرمول‌های ریاضی",
    ])

    with tab_rules:
        render_association_rules_section(rules=rules, selected_metrics=selected_metrics)
        render_contingency_inspector(
            rules=rules,
            frequent_itemsets=frequent_itemsets,
            total_transactions=len(transactions),
        )

    with tab_itemsets:
        render_frequent_itemsets_section(frequent_itemsets=frequent_itemsets)

    with tab_vertical:
        render_horizontal_and_vertical_tables(
            transactions=transactions,
            vertical_db=vertical_db,
            all_tids=all_tids,
        )

    with tab_formulas:
        render_formulas_reference()


if __name__ == "__main__":
    main()
