"""B1 - Cào đánh giá Điện Máy Xanh theo hạn ngạch 20% tiêu cực / 20% trung tính / 60% tích cực.

Chạy:  python crawl_reviews.py --n 1000            (thêm --out file.csv để không ghi đè)
Ra:    data/01.raw_reviews.csv  (review_id, so_sao, noi_dung, product_id, nhom_cam_xuc)
Bấm Ctrl+C lúc nào cũng được, phần đã cào vẫn được lưu.
Gọi thẳng API bằng requests, không cần mở trình duyệt (API chỉ cần User-Agent của trình duyệt).
"""
import argparse
import random
import sys
import time
from pathlib import Path

import pandas as pd
import requests

sys.stdout.reconfigure(encoding="utf-8")  # terminal Windows mặc định cp1252, không in được tiếng Việt
from bs4 import BeautifulSoup

DATA = Path(__file__).resolve().parent / "data"  # chạy từ thư mục nào cũng được
PRODUCTS = DATA / "00.product_ids.csv"
OUTPUT = DATA / "01.raw_reviews.csv"
API = "https://www.dienmayxanh.com/comment/PagingAllRating"
HEADERS = {  # thiếu User-Agent trình duyệt thì API trả 403
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.dienmayxanh.com/",
    "Accept-Language": "vi-VN,vi;q=0.9",
}
RETRIES = 5          # số lần thử lại mỗi request
MAX_FAILS = 3        # bỏ cuộc sau chừng này request hỏng liên tiếp (nghi bị chặn tạm thời)
DELAY = (0.8, 1.8)   # nghỉ ngẫu nhiên giữa 2 request (giây), tránh bị coi là bot


class Blocked(Exception):
    """Trang liên tục từ chối kết nối: dừng lại, lưu phần đã cào."""


def parse(html):
    """Bóc review_id, số sao, nội dung từ HTML của API PagingAllRating."""
    out = []
    for li in BeautifulSoup(html or "", "html.parser").select("li.par"):
        rid = (li.get("id") or "").replace("r-", "").strip()
        tag = li.select_one(".cmt-txt")
        text = " ".join(tag.get_text().split()) if tag else ""  # gộp xuống dòng: mỗi review 1 dòng CSV
        if rid.isdigit() and text:
            out.append({"review_id": rid, "so_sao": len(li.select(".cmt-top-star i.iconcmt-starbuy")),
                        "noi_dung": text})
    return out



def fetch_page(session, pid, page, score):
    """Gọi API, thử lại với backoff. Trả HTML, hoặc None nếu vẫn hỏng sau RETRIES lần."""
    for i in range(RETRIES):
        try:
            r = session.post(API, data={"productid": int(pid), "page": page, "score": score, "pagesize": 20},
                             timeout=30)
            if r.status_code == 200:
                return r.text
            why = f"HTTP {r.status_code}"
        except requests.RequestException as e:
            why = type(e).__name__
        wait = 5 * 2 ** i
        print(f"  Lỗi sp {pid} trang {page} sao {score} (lần {i + 1}/{RETRIES}): {why} -> chờ {wait}s", flush=True)
        time.sleep(wait)
    return None


def crawl(n, rows, save):
    quotas = {"Tiêu cực": (["1", "2"], int(n * 0.2)), "Trung tính": (["3"], int(n * 0.2))}
    quotas["Tích cực"] = (["4", "5"], n - quotas["Tiêu cực"][1] - quotas["Trung tính"][1])
    count, seen, fails = {g: 0 for g in quotas}, set(), 0
    session = requests.Session()
    session.headers.update(HEADERS)
    try:
        for pid in pd.read_csv(PRODUCTS)["product_id"]:
            if all(count[g] >= quotas[g][1] for g in quotas):
                break
            for group, (scores, target) in quotas.items():
                for score in scores:
                    page = 1
                    while count[group] < target:
                        html = fetch_page(session, pid, page, score)
                        if html is None:
                            fails += 1
                            if fails >= MAX_FAILS:
                                raise Blocked(f"{fails} request hỏng liên tiếp")
                            break  # bỏ qua (sản phẩm, số sao) này, sang cái tiếp
                        fails = 0
                        added = 0
                        for item in parse(html):
                            if item["review_id"] not in seen and count[group] < target:
                                seen.add(item["review_id"])
                                rows.append({**item, "product_id": pid, "nhom_cam_xuc": group})
                                count[group] += 1
                                added += 1
                        if added == 0:
                            break
                        page += 1
                        time.sleep(random.uniform(*DELAY))
            save()  # lưu sau mỗi sản phẩm: crash hay mất mạng cũng không mất dữ liệu
            print(f"Sản phẩm (product_id) {pid} xong | Đã có:", " | ".join(f"{g}: {count[g]}/{quotas[g][1]}" for g in quotas), flush=True)
    except Blocked as e:
        print(f"DỪNG: {e}. Có thể trang đang chặn tạm thời IP này (cào quá nhiều/quá nhanh). "
              "Đợi 30-60 phút hoặc đổi mạng (vd. 4G) rồi chạy lại.", flush=True)
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=1000, help="Số review cần cào")
    parser.add_argument("--out", type=Path, default=OUTPUT, help="File CSV đầu ra")
    args = parser.parse_args()
    rows = []

    def save():
        if rows:
            pd.DataFrame(rows).to_csv(args.out, index=False, encoding="utf-8-sig")

    try:
        crawl(args.n, rows, save)
    except KeyboardInterrupt:
        print("Dừng theo yêu cầu, lưu phần đã cào.")
    finally:
        if rows:
            save()
            df = pd.DataFrame(rows)
            print(f"Đã lưu {len(df)}/{args.n} review vào {args.out}")
            print(df["nhom_cam_xuc"].value_counts().to_string())
        else:
            print("Chưa cào được review nào, không ghi file.")


if __name__ == "__main__":
    main()
