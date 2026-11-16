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

- **Tổng số mẫu cào ban đầu**: **6.952 review** (`01.raw_reviews.csv`).
- **Phân bố theo nhóm số sao**:
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

- **Tổng số mẫu sạch còn lại**: **5.493 review** (`02.clean_reviews.csv`).
  - _Tích cực (theo sao)_: 3.314 dòng
  - _Tiêu cực (theo sao)_: 1.389 dòng
  - _Trung tính (theo sao)_: 790 dòng

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
- **Hệ số Cohen's Kappa**: **0.9565** (mức _Almost Perfect Agreement_ - tương đồng gần như hoàn hảo).
  > Điều này chứng minh bộ luật prompt gán nhãn có độ tin cậy cực cao để làm nhãn huấn luyện cho toàn bộ dataset.

---

## 4. PHÂN CHIA TẬP DỮ LIỆU HUẤN LUYỆN & KIỂM THỬ

Để đảm bảo không bị rò rỉ dữ liệu (Data Leakage):

- **Tập Test (500 câu)**: Sử dụng toàn bộ 500 câu do người gán chuẩn (`04.human_labels.xlsx`).
- **Tập còn lại (4.993 câu)**: Lấy toàn bộ tập AI trừ đi 500 câu của tập Test.
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

- Mô hình được huấn luyện với các thuật toán: **Multinomial Naive Bayes (MNB)** và **Linear Support Vector Classifier (LinearSVC)**.
- Kết quả của mô hình được đánh giá trên chỉ số Val Macro F1 được tính là trung bình của các chỉ số F1 Tiêu cực, F1 Trung tính và F1 Tích cực trên tập Validation nhằm đảm bảo No Data Leakage.

### Bảng xếp hạng chi tiết hiệu năng :

| Xếp hạng | Đặc trưng (Feature) | Mô hình (Model)  | Val Macro F1 | Accuracy (Test) | Macro F1 (Test) | F1 Tiêu cực | F1 Trung tính | F1 Tích cực |
| :------: | ------------------- | ---------------- | :----------: | :-------------: | :-------------: | :---------: | :-----------: | :---------: |
|    1     | TF-IDF              | LinearSVC        |    0.7769    |     86.20%      |     0.7684      |   0.8710    |    0.5000     |   0.9341    |
|    2     | BoW                 | LinearSVC        |    0.7603    |     86.60%      |     0.7768      |   0.8864    |    0.5128     |   0.9310    |
|    3     | BoW                 | MultinomialNB    |    0.7246    |     83.80%      |     0.7398      |   0.8352    |    0.4576     |   0.9266    |
|    4     | Word2Vec            | LinearSVC        |    0.7192    |     83.00%      |     0.7554      |   0.8261    |    0.5312     |   0.9087    |
|    5     | TF-IDF              | MultinomialNB    |    0.7151    |     82.40%      |     0.6908      |   0.8265    |    0.3299     |   0.9159    |
| 6 (Base) | (baseline)          | Nhãn theo số sao |    0.6850    |     76.80%      |     0.6487      |   0.8013    |    0.2639     |   0.8809    |
| 7 (Base) | (baseline)          | Đoán lớp đa số   |    0.2328    |     50.40%      |     0.2234      |   0.0000    |    0.0000     |   0.6702    |

---

## 7. NHẬN XÉT & ĐÁNH GIÁ

### 7.1. Phân tích kết quả xếp hạng

- **Hai nhóm hiệu năng tách biệt rõ rệt**:
  - **Nhóm mô hình học máy (Xếp hạng 1–5)**: Đều vượt trội hoàn toàn so với baseline **Đoán lớp đa số** - Macro F1 chỉ đạt 0.2234 và baseline **Nhãn theo số sao** Macro F1 0.6487. Trong đó, cả 5 mô hình đều đạt Macro F1 trên tập Test từ **0.6908 đến 0.7768** và Accuracy trên 82%.
  - **Mô hình tốt nhất theo Validation**: **TF-IDF + LinearSVC** đạt kết quả tốt nhất với **Val Macro F1 = 0.7769** (Test Accuracy: 86.20%, Test Macro F1: 0.7684). Tiếp theo là **BoW + LinearSVC** với **Val Macro F1 = 0.7603** (Test Macro F1 đạt cao nhất là 0.7768).
  - Khác biệt giữa hai mô hình tốt nhất (TF-IDF + LinearSVC và BoW + LinearSVC) rất nhỏ (~0.016 trên Val và ~0.008 trên Test), cho thấy cả hai đều khai thác rất tốt các tín hiệu từ vựng rời rạc.

- **Độ tin cậy của việc chọn mô hình theo Val Macro F1**:
  - Việc xếp hạng mô hình hoàn toàn dựa trên tập Validation (`Val Macro F1`) tuân thủ nghiêm ngặt nguyên tắc **No Data Leakage**. Kết quả trên tập Test người gán (Test Ground Truth) cho thấy thứ hạng trên Validation phản ánh rất sát năng lực tổng quát hóa thực tế của các mô hình.

---

### 7.2. Phân tích so sánh giữa các mô hình

#### 1. Vì sao Linear SVM (LinearSVC) vượt trội hơn Naive Bayes (MultinomialNB)?

- **Ở cả 2 không gian đặc trưng BoW và TF-IDF, SVM đều vượt trội hơn Naive Bayes**:
  - Với BoW: SVM (0.7603 Val / 0.7768 Test) vượt trội hơn MNB (0.7246 Val / 0.7398 Test).
  - Với TF-IDF: SVM (0.7769 Val / 0.7684 Test) bỏ xa MNB (0.7151 Val / 0.6908 Test), chênh lệch tới **~0.078 điểm F1** trên tập Test.
- **Nguyên nhân toán học và mô hình**:
  - **Giả định độc lập có điều kiện của Naive Bayes bị vi phạm nghiêm trọng**: Đánh giá khách hàng chứa nhiều cụm từ biểu cảm liên kết chặt chẽ (ví dụ: _"dùng rất tốt"_, _"giao hàng chậm"_, _"chất lượng kém"_). Khi tính toán bằng BoW unigram + bigram hoặc TF-IDF, các từ này phụ thuộc mạnh vào nhau. Naive Bayes nhân dồn xác suất độc lập dẫn đến hiện tượng nhân thừa (overcounting) làm xác suất bị lệch và bão hòa.
  - **Cơ chế biên phân loại tối ưu của Linear SVM**: SVM tìm siêu phẳng tối ưu hóa khoảng cách hình học cực đại (maximum margin) giữa các lớp và học trực tiếp trọng số phân biệt cho từng đặc trưng, xử lý tốt không gian đặc trưng thưa (sparse) và nhiều chiều mà không bị ảnh hưởng bởi sự tương quan giữa các từ.

#### 2. Vì sao TF-IDF hiệu quả hơn BoW trên Linear SVM?

- Mặc dù BoW nhỉnh hơn một chút trên Test (0.7768 so với 0.7684), nhưng TF-IDF đạt độ tổng quát hóa ổn định hơn trên Validation (0.7769 so với 0.7603).
- Thành phần **IDF (Inverse Document Frequency)** giúp giảm bớt ảnh hưởng của các từ xuất hiện phổ biến trong toàn bộ review hàng điện máy (như _"sản phẩm"_, _"mua"_, _"dùng"_, _"máy"_), đồng thời khuếch đại trọng số của các từ khóa cảm xúc đặc trưng hiếm hơn (_"xịn"_, _"hài lòng"_, _"ọp ẹp"_, _"thất vọng"_). Điều này giúp siêu phẳng của SVM tập trung vào các đặc trưng có tính phân loại cảm xúc cao thay vì bị ảnh hưởng bởi độ dài hay tần suất thô của câu.

#### 3. Vì sao Word2Vec + LinearSVC có kết quả ổn định nhưng chưa vượt được BoW/TF-IDF?

- Word2Vec biểu diễn câu bằng cách lấy trung bình cộng các vector từ (Average Word Embeddings 100 chiều).
- **Điểm mạnh**: Đạt F1 lớp Trung tính cao nhất bảng (**0.5312**), cho thấy vector ngữ nghĩa có khả năng nắm bắt được những câu bình luận trung lập, chung chung tốt hơn việc chỉ dựa vào từ khóa cứng.
- **Hạn chế **: Khi lấy trung bình cộng toàn câu, tín hiệu cảm xúc cực mạnh từ 1–2 từ khóa then chốt (như _"tệ"_, _"kém"_, _"tuyệt vời"_) dễ bị lẫn và triệt tiêu bởi hàng loạt các từ mô tả trung tính khác trong câu. Ngoài ra, việc huấn luyện Skip-gram trên tập văn bản chỉ khoảng hơn 5.000 dòng là quá nhỏ để vector học được quan hệ ngữ nghĩa tiếng Việt.

---

### 7.3. Phân tích hiệu năng theo từng nhãn cảm xúc

| Nhãn cảm xúc       | Phân bố Test | F1 trung bình các mô hình | Khả năng nhận diện của mô hình                         |
| :----------------- | :----------: | :-----------------------: | :----------------------------------------------------- |
| **Tích cực (1)**   |    50.4%     |     **~0.91 – 0.93**      | Độ chính xác cao, tập từ vựng khen rõ ràng             |
| **Tiêu cực (-1)**  |    35.2%     |     **~0.82 – 0.88**      | Khá tốt, từ vựng chê sản phầm có tính phân biệt mạnh   |
| **Trung tính (0)** |    14.4%     |     **~0.33 – 0.53**      | Độ chính xác thấp, dữ liệu ít, là điểm nghẽn lớn nhất. |

- **Lớp Tích cực (F1 > 0.93)**: Đạt điểm cao nhất vì khách hàng thường khen rất rõ ràng (_"tốt lắm"_, _"rất thích"_, _"giao hàng nhanh 5 sao"_), lượng mẫu nhiều chiếm hơn 50% dataset.
- **Lớp Tiêu cực (F1 ~ 0.87)**: Khách hàng phản ánh lỗi rất cụ thể (_"hỏng"_, _"lỗi"_, _"không chạy"_, _"đổi trả"_) nên các mô hình trích xuất từ khóa nhận diện khá hiệu quả.
- **Lớp Trung tính là "điểm nghẽn" (Bottleneck) lớn nhất**:
  - F1 lớp Trung tính chỉ dao động từ **0.3299 (TF-IDF + MNB)** đến **0.5312 (Word2Vec + SVM)**.
  - **Nguyên nhân 1 (Mất cân bằng dữ liệu - Class Imbalance)**: Mẫu Trung tính chỉ chiếm ~10–14% tổng dataset (chưa tới 600 câu trên toàn bộ tập dữ liệu), khiến mô hình có ít cơ hội học được ranh giới mẫu.
  - **Nguyên nhân 2 (Hiện tượng cảm xúc pha trộn / Ambiguity)**: Các câu trung tính thường vừa khen vừa chê (_"Máy xài ổn nhưng pin hơi tụt nhanh"_, _"Hình thức đẹp mà giao hơi chậm"_), hoặc bình luận hoàn toàn khách quan không sắc thái (_"Đã nhận hàng, chưa thử"_, _"Dùng tạm được"_). Khi thiếu vắng các từ khóa phân cực rõ ràng, mô hình dựa trên từ vựng thường có xu hướng gán nhầm sang Tích cực hoặc Tiêu cực.

---

### 7.4. Vì sao mô hình học máy vượt xa Baseline "Nhãn theo số sao"?

- Baseline **Nhãn theo số sao** chỉ đạt Macro F1 **0.6487** (kém mô hình tốt nhất tới **~0.12 điểm**), đặc biệt F1 lớp Trung tính của số sao chỉ đạt **0.2639**.
- **Nguyên nhân chính**: Có sự khác biệt đáng kể giữa hành vi đánh giá sao và nội dung viết nhận xét của người dùng:
  - Khách hàng chấm **5 sao** vì nhiệt tình của shipper, nhưng nội dung lại chê: _"Đóng gói cẩn thận, shipper dễ thương nhưng máy vừa mở lên đã lỗi nguồn"_ (Nội dung: Tiêu cực, Sao: 5).
  - Khách hàng chấm **1 sao** chỉ để thu hút nhân viên hỗ trợ bảo hành: _"Gọi tổng đài không ai nghe, kiểm tra lại giúp tôi"_ (Nội dung: Trung tính / Yêu cầu hỗ trợ, Sao: 1).
  - Khách chấm **3 sao** nhưng lời khen rất tốt: _"Hàng dùng ngon lành"_ (Nội dung: Tích cực, Sao: 3).
- Mô hình học trực tiếp từ sắc thái ngôn từ đã giải quyết sự "nhiễu" của số sao, đem lại giá trị phân loại cảm xúc thực tế và tin cậy hơn nhiều so với việc chỉ lọc theo số sao thông thường.

---

## 8. HƯỚNG CẢI TIẾN

Dựa trên các kết quả đã làm được, nhóm đề xuất các hướng cải tiến tiếp theo cho bài toán:

1. **Cải thiện dữ liệu và xử lý mất cân bằng lớp (Đặc biệt cho lớp Trung tính)**:
   - **Tăng cường dữ liệu (Data Augmentation)**: Áp dụng các kỹ thuật sinh câu (Back-translation, Paraphrasing bằng LLM) để bổ sung thêm các mẫu đánh giá trung tính, câu vừa khen vừa chê, câu hỏi đáp bảo hành vào tập Train.
   - **Tối ưu hàm mất mát**: Thử nghiệm Class Weights (tăng phạt khi đoán sai lớp Trung tính) hoặc Focal Loss để mô hình tập trung hơn vào các mẫu khó.

2. **Nâng cấp phương pháp biểu diễn đặc trưng và mô hình ngôn ngữ (Transformer)**:
   - Thay thế việc lấy trung bình vector của Word2Vec thô sơ bằng việc tinh chỉnh (Fine-tuning) các mô hình ngôn ngữ ngữ cảnh tiền huấn luyện chuyên sâu cho tiếng Việt như **PhoBERT (base/large)** hoặc **ViBERT**.
   - Các mô hình kiến trúc Transformer dựa trên cơ chế Self-Attention sẽ giải quyết triệt để các câu đánh giá có liên từ tương phản (_"tuy... nhưng..."_, _"tưởng... ai ngờ..."_), tránh việc bắt nhầm cảm xúc do xuất hiện đơn lẻ các từ phân cực.

3. **Mở rộng bài toán sang Phân loại cảm xúc đa khía cạnh (Aspect-Based Sentiment Analysis - ABSA)**:
   - Đánh giá sản phẩm công nghệ/gia dụng thường phản ánh nhiều khía cạnh cùng lúc: _Chất lượng sản phẩm_, _Tốc độ giao hàng_, _Thái độ nhân viên_, _Giá thành_.
   - Thay vì gán một nhãn duy nhất cho toàn bộ đánh giá, hệ thống nên phân tách và chấm điểm cảm xúc riêng biệt cho từng khía cạnh để mang lại giá trị vận hành thực tế cao hơn cho doanh nghiệp.
