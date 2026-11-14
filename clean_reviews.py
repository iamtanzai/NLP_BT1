"""B2 - Làm sạch nhẹ: chuẩn Unicode NFC, che SĐT/email/link, bỏ câu rỗng/vô nghĩa, khử trùng lặp.

Chạy:  python clean_reviews.py
Vào:   data/01.raw_reviews.csv
Ra:    data/02.clean_reviews.csv  (không đổi ngữ pháp hay sắc thái câu)
"""
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")  # terminal Windows mặc định cp1252, không in được tiếng Việt

DATA = Path(__file__).resolve().parent / "data"  # chạy từ thư mục nào cũng được
INPUT = DATA / "01.raw_reviews.csv"
OUTPUT = DATA / "02.clean_reviews.csv"
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
URL = re.compile(r"https?://\S+|www\.\S+")
PHONE = re.compile(r"(?<!\d)(?:\+?84|0)[1-9](?:[\s.\-]?\d){7,9}(?!\d)")


def clean(text):
    if not isinstance(text, str) or not text.strip():
        return ""
    text = unicodedata.normalize("NFC", text)
    text = PHONE.sub("[sđt]", URL.sub("[link]", EMAIL.sub("[email]", text)))
    return re.sub(r"\s+", " ", text).strip()


def is_valid(text):
    """Phải có ít nhất 1 chữ cái; bỏ câu chỉ có 1 ký tự như 'a', '.'."""
    words = text.split()
    return bool(re.search(r"[a-zA-ZÀ-ỹ]", text)) and not (len(words) == 1 and len(words[0]) < 2)


def match_key(text):
    """Khóa so trùng: viết thường, bỏ dấu câu."""
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", text.lower())).strip()


def main():
    df = pd.read_csv(INPUT)
    n0 = len(df)
    df["noi_dung"] = df["noi_dung"].apply(clean)
    df = df[df["noi_dung"] != ""]
    n1 = len(df)
    df = df[df["noi_dung"].apply(is_valid)]
    n2 = len(df)
    df = df[~df["noi_dung"].apply(match_key).duplicated()]
    df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    print(f"Ban đầu {n0} | rỗng -{n0 - n1} | vô nghĩa -{n1 - n2} | trùng -{n2 - len(df)} | còn {len(df)}")
    print(df["nhom_cam_xuc"].value_counts().to_string())


if __name__ == "__main__":
    main()
