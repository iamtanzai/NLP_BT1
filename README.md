# Phân loại cảm xúc đánh giá Điện Máy Xanh

Phân loại review thành 3 nhãn: `-1` tiêu cực, `0` trung tính, `1` tích cực.

```
crawl_reviews.py       B1  cào review                 -> data/01.raw_reviews.csv
clean_reviews.py       B2  làm sạch nhẹ               -> data/02.clean_reviews.csv
prompt_ai_label1.md    B3  prompt gán nhãn (luật rút từ 500 câu nhóm gán tay)
sentiment_dmx.ipynb    B3–B7 đọc nhãn, EDA, chia tập, tiền xử lý, đặc trưng, huấn luyện, đánh giá
data/
  00.product_ids.csv       danh sách sản phẩm để cào
  01.raw_reviews.csv       review thô
  02.clean_reviews.csv     review sau làm sạch
  03.human_labels.csv      mẫu 500 câu người gán (cột label để trống)
  04.human_labels.xlsx     500 câu nhóm đã gán tay, dùng làm tập test
  ai_label1.xlsx           nhãn AI cho 500 câu trên, kèm các câu lệch với người
  05.claude_v2.csv         nhãn AI cho toàn bộ 02 (review_id, noi_dung, label), dùng để huấn luyện
  teencode.csv, tu_dung.txt
out/model_scores.csv       bảng kết quả các mô hình
```

## Cài đặt

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Chạy

1. `python crawl_reviews.py --n 1000` (đã có sẵn dữ liệu thì bỏ qua)
2. `python clean_reviews.py`
3. Gán nhãn theo `prompt_ai_label1.md` (đã có sẵn `04.human_labels.xlsx` và `05.claude_v2.csv`)
4. Mở `sentiment_dmx.ipynb`, chọn kernel `venv`, rồi Run All

Notebook cần cả hai file nhãn 04 và 05. Nếu cào lại dữ liệu thì phải gán lại 05 cho khớp `02.clean_reviews.csv`.
