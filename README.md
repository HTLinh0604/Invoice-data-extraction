# 🧾 HỆ THỐNG NHẬN DIỆN VÀ TỰ ĐỘNG HÓA LƯU TRỮ THÔNG TIN HÓA ĐƠN
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web%20App-black?logo=flask)
![OpenCV](https://img.shields.io/badge/OpenCV-Image%20Processing-blue?logo=opencv)
![Tesseract](https://img.shields.io/badge/Tesseract-OCR-lightgrey?logo=tesseract)

Đồ án này xây dựng một hệ thống tự động trích xuất thông tin từ hóa đơn bán lẻ bằng công nghệ OCR và lưu trữ dữ liệu có cấu trúc, giúp doanh nghiệp tối ưu hóa quy trình tài chính và kế toán.

## 📋 Mục lục
* [🎯 Mục tiêu & Ý nghĩa](#-mục-tiêu--ý-nghĩa)
* [🛠️ Công nghệ sử dụng](#-công-nghệ-sử-dụng)
* [📊 Dữ liệu](#-dữ-liệu)
* [⚙️ Quy trình hoạt động của hệ thống](#-quy-trình-hoạt-động-của-hệ-thống)
    * [1. Tiền xử lý ảnh (OpenCV)](#1-tiền-xử-lý-ảnh-opencv)
    * [2. Chiến lược OCR (Tesseract)](#2-chiến-lược-ocr-tesseract)
    * [3. Trích xuất thông tin (Regex)](#3-trích-xuất-thông-tin-regex)
* [📈 Kết quả thực nghiệm](#-kết-quả-thực-nghiệm)
* [🖥️ Giao diện hệ thống](#-giao-diện-hệ-thống)
* [🚀 Kết luận & Hướng phát triển](#-kết-luận--hướng-phát-triển)
* [👥 Thông tin Đồ án](#-thông-tin-đồ-án)

---

## 🎯 Mục tiêu & Ý nghĩa

### Mục tiêu
* **Tổng quan:** Xây dựng một hệ thống hoàn chỉnh giúp doanh nghiệp trích xuất, phân tích và quản lý dữ liệu hóa đơn hiệu quả bằng OCR và học máy.
* **Cụ thể:** Áp dụng OCR (Tesseract) kết hợp các kỹ thuật xử lý ảnh (OpenCV) để trích xuất dữ liệu từ ảnh hóa đơn với độ chính xác và tốc độ xử lý được tối ưu.

### Ý nghĩa thực tiễn
Hệ thống hoạt động như một công cụ thông minh, giúp doanh nghiệp:
* Tiết kiệm thời gian và nhân lực nhập liệu thủ công.
* Giảm thiểu sai sót trong quá trình xử lý dữ liệu tài chính.
* Tối ưu hóa quy trình lưu trữ và tra cứu hóa đơn.
* Cung cấp dữ liệu "sạch" cho các tác vụ phân tích và ra quyết định chiến lược.

---

## 🛠️ Công nghệ sử dụng
* **Ngôn ngữ lập trình:** Python 3.9
* **Xử lý ảnh (Image Processing):** `OpenCV`
* **Nhận diện ký tự quang học (OCR):** `Tesseract` (với ngôn ngữ `vie`)
* **Trích xuất thông tin:** `Regex` (Biểu thức chính quy)
* **Web Framework:** `Flask` (Xây dựng giao diện demo)
* **Thư viện hỗ trợ:** `Pandas`, `NumPy`

---

## 📊 Dữ liệu

* **Nguồn:** Bộ dữ liệu được thu thập từ nền tảng **Roboflow**.
* **Đối tượng:** 28 tấm ảnh hóa đơn từ cửa hàng **Bách Hóa Xanh**.
* **Đặc điểm:**
    * Định dạng: JPG, PNG.
    * Ngôn ngữ: Tiếng Việt.
    * Chất lượng: Đa dạng, bao gồm ảnh rõ nét, ảnh chụp trong điều kiện ánh sáng yếu, góc chụp lệch, và có nhiễu nền.
* **Các trường thông tin trích xuất (10 trường):**
    1.  `Store Name` (Tên cửa hàng)
    2.  `Address` (Địa chỉ)
    3.  `Date` (Ngày giao dịch)
    4.  `Employee` (Nhân viên)
    5.  `Bill no` (Số hóa đơn)
    6.  `Products` (Danh sách sản phẩm)
    7.  `Total_products` (Tổng tiền sản phẩm)
    8.  `Paid` (Số tiền thanh toán)
    9.  `Change` (Tiền thối)
    10. `Discount` (Giảm giá)

---

## ⚙️ Quy trình hoạt động của hệ thống
Hệ thống xử lý ảnh hóa đơn qua 3 giai đoạn chính:

### 1. Tiền xử lý ảnh (OpenCV)
Ảnh đầu vào được xử lý qua pipeline (`preprocess_pipeline`) để tối ưu hóa cho OCR:
1.  **Chuyển đổi ảnh xám (Grayscale):** Đơn giản hóa dữ liệu ảnh.
2.  **Điều chỉnh góc nghiêng (Deskewing):** Tự động xác định và xoay ảnh để văn bản nằm ngang.
3.  **Loại bỏ nhiễu nền:** Sử dụng Gaussian Blur và phép chia ảnh (`cv2.divide`) để cân bằng độ sáng và làm nổi bật văn bản.
4.  **Ngưỡng hóa (Thresholding):** Dùng phương pháp Otsu để chuyển ảnh sang dạng nhị phân (trắng/đen).
5.  **Xử lý hình thái học (Morphology):** Tự động giãn nở (Dilation) và co ngót (Erosion) để loại bỏ nhiễu nhỏ và kết nối các vùng văn bản bị đứt gãy.
6.  **Phóng to ảnh (Resize):** Tăng kích thước ảnh lên gấp đôi (`fx=2, fy=2`) để Tesseract nhận diện ký tự nhỏ tốt hơn.



### 2. Chiến lược OCR (Tesseract)
Hệ thống áp dụng chiến lược "fall-back" (dự phòng) linh hoạt để tối đa hóa khả năng trích xuất:
1.  **Nhận diện toàn bộ (Full Image):**
    * Chạy Tesseract (`--oem 3 --psm 6`, ngôn ngữ `vie`) trên toàn bộ ảnh đã tiền xử lý.
    * Trích xuất văn bản thô.
2.  **Đánh giá chất lượng:**
    * Kiểm tra số lượng trường thông tin quan trọng bị thiếu (`None`).
3.  **Chiến lược dự phòng (Fall-back):**
    * Nếu số trường bị thiếu **> 3**, hệ thống nhận định OCR toàn ảnh thất bại.
    * Kích hoạt chế độ xử lý từng đoạn ảnh (`extract_from_crops`): Ảnh được cắt thành các đoạn nhỏ (cao 100px, chồng lấn 50px), sau đó chạy OCR trên từng đoạn và ghép kết quả lại.

### 3. Trích xuất thông tin (Regex)
Văn bản thô từ Tesseract được đưa vào hàm `extract_structured_receipt_fields`. Hàm này sử dụng các mẫu **Biểu thức chính quy (Regex)** được thiết kế riêng cho hóa đơn Bách Hóa Xanh để "bóc tách" và định dạng lại 10 trường thông tin mục tiêu.

---

## 📈 Kết quả thực nghiệm

Hiệu suất của hệ thống được đánh giá trên 28 ảnh hóa đơn thực tế:

| Kết quả đánh giá | Số lượng ảnh | Tỷ lệ | Chi tiết |
| :--- | :---: | :---: | :--- |
| **Tốt / Khá tốt** | 13 / 28 | 46.5% | Nhận diện chính xác 70-85%. |
| **Trung bình / Kém** | 10 / 28 | 35.7% | Nhận diện được một số trường cơ bản, sai lệch nhiều. |
| **Thất bại hoàn toàn** | 5 / 28 | 17.9% | Không nhận diện được thông tin nào (do ảnh quá mờ, nhiễu). |

> ⚠️ **LỖI NGHIÊM TRỌNG:** Trường **Tổng tiền sản phẩm (`Total_products`)** **thất bại 100%** (không nhận diện được ở bất kỳ ảnh nào). Các trường tài chính khác như `Paid` và `Change` có tỷ lệ nhận diện thấp (28-35%) và thường xuyên mắc lỗi định dạng số.

**Phân tích lỗi:**
* Chất lượng ảnh gốc thấp (mờ, sáng tối không đều) là nguyên nhân chính gây thất bại.
* Bố cục phức tạp và font chữ nhỏ ở các trường tài chính khiến Tesseract gặp khó khăn.

---

## 🖥️ Giao diện hệ thống
Hệ thống được triển khai thành một ứng dụng web đơn giản bằng **Flask**.

* **Chức năng Upload:** Người dùng có thể tải ảnh hóa đơn trực tiếp lên giao diện.
![Giao diện Upload ảnh hóa đơn](code_project/static/img/upload.png)
* **Hiển thị kết quả:** Trang kết quả trình bày thông tin trích xuất một cách có tổ chức.
![Giao diện hiển thị kết quả trích xuất](code_project/static/img/result1.png)
![Giao diện hiển thị kết quả trích xuất](code_project/static/img/result2.png)
* **Cảnh báo lỗi:** Các trường thông tin không tìm thấy (`None`) sẽ được **highlight màu đỏ** để người dùng dễ dàng phát hiện và kiểm tra lại.

* **Lưu trữ tự động:** Kết quả trích xuất được tự động lưu vào file `results.csv`, giúp chuẩn hóa đầu ra và phục vụ cho các phân tích sau này.

---

## 🚀 Kết luận & Hướng phát triển

### Kết luận
Hệ thống đã tự động hóa thành công quy trình xử lý hóa đơn, đạt độ chính xác tương đối (75-85%) trên các ảnh chất lượng tốt. Giao diện Flask thân thiện và tính năng cảnh báo lỗi giúp tăng cường trải nghiệm người dùng. Tuy nhiên, hệ thống còn yếu kém nghiêm trọng trong việc nhận diện các trường tài chính quan trọng và các ảnh chất lượng thấp.

### Hướng phát triển
1.  **Mở rộng Dataset:** Thu thập thêm nhiều mẫu hóa đơn đa dạng (từ nhiều cửa hàng, nhiều điều kiện chụp) để huấn luyện.
2.  **Áp dụng Deep Learning:** Thay thế Tesseract/Regex bằng các mô hình học sâu tiên tiến (như CRNN, CTPN, hoặc các mô hình Vision-Language) để cải thiện độ chính xác, đặc biệt với bố cục phức tạp.
3.  **Cải thiện tiền xử lý:** Tăng cường các thuật toán xử lý ảnh nâng cao.
4.  **Nâng cấp giao diện:** Tích hợp **tính năng chỉnh sửa thủ công** trực tiếp trên giao diện web, cho phép người dùng sửa lại các trường bị nhận diện sai trước khi lưu.

---

## 👥 Thông tin Đồ án
Đây là sản phẩm của Đồ án Cơ sở (ĐACS) - Học kỳ 1, năm học 2024-2025.

**Sinh viên thực hiện:**
* Hồ Gia Thành
* Huỳnh Thái Linh
* Trương Minh Khoa

**Lớp:** `22DKHA1` - Ngành **Khoa học Dữ liệu**

**Giảng viên hướng dẫn:** ThS. Nguyễn Quang Phúc

**Trường:** Trường Đại học Công nghệ TP. HCM (HUTECH) - 2025
