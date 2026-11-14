# BÁO CÁO CHI TIẾT ĐỒ ÁN XỬ LÝ NGÔN NGỮ TỰ NHIÊN (NLP)
## ĐỀ TÀI: PHÂN LOẠI CẢM XÚC ĐÁNH GIÁ KHÁCH HÀNG ĐIỆN MÁY XANH

---

## 1. TỔNG QUAN DỰ ÁN
- **Mục tiêu**: Xây dựng hệ thống phân loại cảm xúc (Sentiment Analysis) từ các đánh giá của người dùng trên nền tảng Điện Máy Xanh thành 3 mức độ cảm xúc:
  - `-1`: Tiêu cực (Negative)
  - `0`: Trung tính (Neutral)
  - `1`: Tích cực (Positive)
- **Tập danh mục sản phẩm**: 843 mã sản phẩm (`00.product_ids.csv`).

---

## 2. QUY TRÌNH THU THẬP & LÀM SẠCH DỮ LIỆU

### 2.1. Cào dữ liệu thô (Crawling - B1)
Dữ liệu được cào tự động bằng Playwright thông qua API phân trang `PagingAllRating` của Điện Máy Xanh, thu thập theo tỷ lệ hạn ngạch cân đối (20% Tiêu cực - 20% Trung tính - 60% Tích cực).
* **Tổng số mẫu cào ban đầu**: **6.952 review** (`01.raw_reviews.csv`).
* **Phân bố theo nhóm số sao**:
  - Tích cực (4 - 5 sao): **4.714** review (~67.8%)
  - Tiêu cực (1 - 2 sao): **1.393** review (~20.0%)
  - Trung tính (3 sao): **845** review (~12.2%)

### 2.2. Làm sạch dữ liệu nhẹ (Data Cleaning - B2)
Thực hiện qua file `clean_reviews.py` với các bước kiểm duyệt nghiêm ngặt:
1. **Chuẩn hóa Unicode**: Đưa toàn bộ văn bản về chuẩn dựng sẵn **Unicode NFC** (`unicodedata.normalize('NFC', text)`).
2. **Ẩn thông tin nhạy cảm**: Che số điện thoại (`[sđt]`), email (`[email]`), đường dẫn web (`[link]`).
3. **Loại bỏ dữ liệu lỗi & khử trùng lặp**:
   - **Loại bỏ rỗng**: **-2** dòng
   - **Loại bỏ vô nghĩa** (chỉ có ký tự đặc biệt / < 2 ký tự): **-37** dòng
   - **Loại bỏ trùng lặp nội dung**: **-1.420** dòng
* **Tổng số mẫu sạch còn lại**: **5.493 review** (`02.clean_reviews.csv`).
  - *Tích cực (theo sao)*: 3.314 dòng
  - *Tiêu cực (theo sao)*: 1.389 dòng
  - *Trung tính (theo sao)*: 790 dòng

---

## 3. CHIẾN LƯỢC GÁN NHÃN & ĐÁNH GIÁ CHẤT LƯỢNG (B3)

### 3.1. Gán nhãn thủ công (Ground Truth / Test Set)
- Nhóm đã trích xuất mẫu phân tầng gồm **500 câu** (`04.human_labels.xlsx`) để người trực tiếp đọc nội dung chữ và gán nhãn độc lập (không nhìn số sao để tránh thiên kiến).
- **Phân bố 500 câu người gán**:
  - Tích cực (`1`): **252** câu (50.4%)
  - Tiêu cực (`-1`): **176** câu (35.2%)
  - Trung tính (`0`): **72** câu (14.4%)

### 3.2. Gán nhãn tự động bằng AI (Claude Prompt v2)
- Toàn bộ **5.493 câu** được gán nhãn dựa trên sắc thái ngôn từ thực tế (`05.claude_v2.csv`).
- **Phân bố nhãn AI**:
  - Tích cực (`1`): **2.936** câu (53.5%)
  - Tiêu cực (`-1`): **1.979** câu (36.0%)
  - Trung tính (`0`): **578** câu (10.5%)

### 3.3. Độ tin cậy & tương đồng giữa Người và AI (Validation)
Đối soát trên tập 500 câu chuẩn giữa nhãn con người và nhãn AI:
- **Độ trùng khớp (Raw Agreement)**: **487 / 500 câu** (đạt **97.40%**).
- **Hệ số Cohen's Kappa**: **0.9565** (mức *Almost Perfect Agreement* - tương đồng gần như hoàn hảo).
> Điều này chứng minh bộ luật prompt gán nhãn có độ tin cậy cực cao để làm nhãn huấn luyện cho toàn bộ dataset.

---

## 4. PHÂN CHIA TẬP DỮ LIỆU HUẤN LUYỆN & KIỂM THỬ

Để đảm bảo không bị rò rỉ dữ liệu (Data Leakage):
* **Tập Test (500 câu)**: Sử dụng toàn bộ 500 câu do người gán chuẩn (`04.human_labels.xlsx`).
* **Tập còn lại (4.993 câu)**: Lấy toàn bộ tập AI trừ đi 500 câu của tập Test.
  - **Tập Train (4.169 câu)**: Dùng để huấn luyện mô hình.
  - **Tập Validation (824 câu - ~15%)**: Dùng để tinh chỉnh siêu tham số và lựa chọn mô hình.

---

## 5. TIỀN XỬ LÝ & TRÍCH CHỌN ĐẶC TRƯNG (B4 - B5)
1. **Tiền xử lý văn bản**:
   - Chuyển chữ thường, chuẩn hóa Unicode NFC.
   - Chuẩn hóa viết tắt / teencode thông qua từ điển `teencode.csv`.
   - Tách từ tiếng Việt bằng thư viện `underthesea` (`word_tokenize`).
   - Lọc từ dừng chọn lọc theo danh sách `tu_dung.txt` (giữ lại các từ dừng mang sắc thái cảm xúc mạnh).
2. **Các phương pháp trích chọn đặc trưng**:
   - **Bag-of-Words (BoW)**: Đếm tần suất unigram và bigram, loại bỏ từ hiếm (`min_df=2`).
   - **TF-IDF**: Trọng số hóa nghịch đảo tần suất tài liệu, kết hợp làm mượt log.
   - **Word2Vec (Skip-gram)**: Nhúng từ ngữ nghĩa không gian 100 chiều, vector câu là trung bình cộng các vector từ.

---

## 6. KẾT QUẢ THỰC NGHIỆM CÁC MÔ HÌNH HỌC MÁY (B6)

Mô hình được huấn luyện với các thuật toán: **Multinomial Naive Bayes (MNB)**, **Linear Support Vector Classifier (LinearSVC)**, và **Logistic Regression (LogReg)** với trọng số cân bằng lớp (`class_weight='balanced'`).

### Bảng xếp hạng chi tiết hiệu năng trên tập Test:

| Thứ hạng | Đặc trưng (Feature) | Mô hình (Model) | Val Macro F1 | **Accuracy (Test)** | **Macro F1 (Test)** | F1 Tiêu cực | F1 Trung tính | F1 Tích cực |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 🥇 **1** | **TF-IDF** | **LinearSVC** | **0.7760** | **87.20%** | **0.7863** | **0.8883** | 0.5345 | **0.9362** |
| 🥈 **2** | **TF-IDF** | **LogReg** | 0.7712 | 86.80% | **0.8104** | 0.8736 | **0.6277** | 0.9299 |
| 🥉 **3** | **BoW** | **LogReg** | 0.7544 | 86.40% | 0.7963 | 0.8725 | 0.5865 | 0.9300 |
| 4 | BoW | LinearSVC | 0.7310 | 84.40% | 0.7622 | 0.8547 | 0.5116 | 0.9201 |
| 5 | Word2Vec | LinearSVC | 0.7109 | 82.40% | 0.7398 | 0.8248 | 0.4844 | 0.9102 |
| 6 | BoW | MultinomialNB | 0.7074 | 83.40% | 0.6998 | 0.8416 | 0.3404 | 0.9175 |
| 7 | Word2Vec | LogReg | 0.7064 | 82.20% | 0.7726 | 0.8406 | 0.5848 | 0.8926 |
| *8 (Base)* | *(baseline)* | *Nhãn theo số sao* | *0.6850* | *76.80%* | *0.6487* | *0.8013* | *0.2639* | *0.8809* |
| 9 | TF-IDF | MultinomialNB | 0.5973 | 81.80% | 0.5838 | 0.8376 | 0.0000 | 0.9139 |
| *10 (Base)*| *(baseline)* | *Đoán lớp đa số* | *0.2328* | *50.40%* | *0.2234* | *0.0000* | *0.0000* | *0.6702* |

---

## 7. KẾT LUẬN & ĐÁNH GIÁ CHUYÊN MÔN
1. **Mô hình tốt nhất**: Sự kết hợp giữa **TF-IDF + LinearSVC** (hoặc **TF-IDF + Logistic Regression**) đạt kết quả vượt trội với độ chính xác **~87%** và Macro F1 đạt **~0.79 - 0.81**.
2. **Sự vượt trội so với số sao**: Mô hình học máy dựa trên nội dung vượt xa việc chỉ dùng số sao khách hàng bấm (**87.2% vs 76.8% Accuracy**, Macro F1 tăng từ **0.64 lên 0.81**). Điều này phản ánh thực tế nhiều khách hàng đánh giá 5 sao hoặc 3 sao nhưng lời bình luận lại mang tính phàn nàn/chê bai.
3. **Thách thức lớp Trung tính**: Lớp trung tính có số lượng ít nhất và ranh giới sắc thái mỏng, tuy nhiên việc áp dụng `class_weight='balanced'` và đặc trưng n-gram của TF-IDF đã kéo F1 lớp trung tính lên trên **62.7%** (so với baseline số sao chỉ đạt 26.4%).
