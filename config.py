"""Global configuration for ECLAT Association Rule Mining Project."""

from pathlib import Path
from typing import Dict

BASE_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = BASE_DIR / "data"

PRESET_DATASETS: Dict[str, Dict[str, str]] = {
    "market_small": {
        "name": "سبد خرید فروشگاهی ۱ (۵ تراکنش - اقلام روزمره)",
        "path": str(DATA_DIR / "slide6_market.csv"),
        "desc": "شامل ۵ تراکنش فروشگاهی (Water, Diaper, Nuts, Coffee, Eggs, Milk)",
    },
    "transactions_abc": {
        "name": "دیتاست تراکنشی ۲ (آیتم‌های a تا e)",
        "path": str(DATA_DIR / "slide26_eclat.csv"),
        "desc": "شامل ۳ تراکنش پایه جهت بررسی نحوه اشتراک مجموعه‌های TidList و Diffset",
    },
    "transactions_classic": {
        "name": "دیتاست تراکنشی ۳ (آیتم‌های A تا E)",
        "path": str(DATA_DIR / "slide21_apriori.csv"),
        "desc": "شامل ۴ تراکنش استاندارد با آیتم‌های نمادین A, B, C, D, E",
    },
    "supermarket": {
        "name": "دیتاست جامع سوپرمارکت (۲۰ تراکنش)",
        "path": str(DATA_DIR / "supermarket_basket.csv"),
        "desc": "شامل ۲۰ تراکنش واقعی فروشگاهی از اقلام لبنی، نان، قهوه و نوشیدنی‌ها",
    },
}

AVAILABLE_METRICS: Dict[str, str] = {
    "lift": "Lift (ضریب همبستگی)",
    "kulczynski": "Kulczynski (معیار کولچینسکی)",
    "imbalance_ratio": "Imbalance Ratio (نسبت عدم تعادل)",
    "cosine": "Cosine (تشابه کسینوسی)",
    "jaccard": "Jaccard (ضریب ژاکارد)",
    "all_conf": "AllConfidence (حداقل اطمینان)",
    "max_conf": "MaxConfidence (حداکثر اطمینان)",
    "chi_square": "Chi-Square (آماره کای‌دو)",
}
