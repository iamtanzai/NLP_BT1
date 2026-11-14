# Bài Tập Lớn NLP: Phân Loại Cảm Xúc Đánh Giá Điện Máy Xanh (Sentiment Analysis)

Dự án được xây dựng theo tiêu chuẩn **Clean Code**, code tay rành mạch từng giai đoạn, dễ hiểu và dễ dàng chạy thực nghiệm từ đầu đến cuối.

---

## 1. Cài đặt Môi Trường (Chạy 1 lần duy nhất)

Mở **PowerShell** hoặc **Terminal** tại thư mục dự án và chạy lần lượt các lệnh sau:

```bash
# Bước 1: Tạo môi trường ảo
python -m venv venv

# Bước 2: Kích hoạt môi trường ảo (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Bước 3: Cài đặt các thư viện cần thiết
python -m pip install -r requirements.txt
```

---

## 2. Quy Trình Chạy Toàn Bộ Dự Án (Chu trình từ đầu đến cuối)

Mở VS Code, chọn **Kernel Python (`venv`)** cho các Notebook và chạy lần lượt theo đúng thứ tự:

| Thứ tự | Notebook | Nhiệm vụ chính | Kết quả đầu ra |
| :---: | :--- | :--- | :--- |
| **1** | **`notebooks/crawl.ipynb`** | Cào dữ liệu theo tỉ lệ thực tế (60% Tích cực, 20% Trung tính, 20% Tiêu cực). Hỗ trợ dừng bất kỳ lúc nào vẫn lưu dữ liệu. | `data/raw/reviews_....csv` |
| **2** | **`notebooks/process.ipynb`** | Làm sạch nhẹ (Unicode NFC, che SĐT/link/email, xóa review rỗng, khử trùng lặp). | `data/processed/reviews_clean.csv` |
| **3** | **`notebooks/label.ipynb`** | Báo cáo thử nghiệm nghiệm thu Prompt gán nhãn với Claude & chia 3 tập Train (70%), Val (15%), Test (15%). | `data/splits/train.csv`<br>`data/splits/validation.csv`<br>`data/splits/test.csv` |
| **4** | **`notebooks/tien_xu_ly.ipynb`** | Phân tích độ lệch từ dừng cảm xúc trên tập Train & thực nghiệm so sánh 3 mức từ dừng trên Validation. | `data/tien_xu_ly/train.csv`<br>`data/tien_xu_ly/validation.csv`<br>`data/tien_xu_ly/test.csv` |
| **5** | **`notebooks/feature.ipynb`** | *(Phần dành cho bạn phụ trách Feature)*: Trích xuất đặc trưng số (TF-IDF, BoW) chỉ fit trên Train. | `models/tfidf_vectorizer.pkl` |
| **6** | **`notebooks/ml.ipynb`** | *(Phần dành cho bạn phụ trách ML)*: Huấn luyện Naive Bayes, SVM, Logistic Regression và đánh giá trên Test. | Báo cáo Classification Report & Confusion Matrix |

---

## 3. Cấu Trúc Thư Mục

```text
code_tay/
│
├── data/
│   ├── product_ids.csv      # Danh sách sản phẩm cào
│   ├── resources/           # Bảng teencode.csv, tu_dung.txt
│   ├── raw/                 # Dữ liệu cào về
│   ├── processed/           # Dữ liệu sau làm sạch nhẹ
│   ├── splits/              # 3 tập train, validation, test
│   └── tien_xu_ly/          # Dữ liệu sau tiền xử lý sâu
│
├── notebooks/
│   ├── crawl.ipynb          # Giai đoạn 1: Thu thập
│   ├── process.ipynb        # Giai đoạn 2: Làm sạch nhẹ
│   ├── label.ipynb          # Giai đoạn 3: Nghiệm thu gán nhãn & Chia tập
│   ├── tien_xu_ly.ipynb     # Giai đoạn 4A: Tiền xử lý sâu & Lọc từ dừng
│   ├── feature.ipynb        # Giai đoạn 4B: Trích chọn đặc trưng (TODO)
│   └── ml.ipynb             # Giai đoạn 5: Huấn luyện mô hình (TODO)
│
├── models/                  # Lưu trữ vectorizer và mô hình học máy
├── requirements.txt         # Thư viện phụ thuộc
└── README.md                # Hướng dẫn dự án
```
