import os
from flask import Flask, request, render_template, flash, redirect, url_for
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Đường dẫn trên Windows
import re
from deskew import determine_skew
import math
import uuid
from typing import Union, Tuple
from PIL import Image
import imutils
from pytesseract import Output

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Set Tesseract path (adjust based on your system)

# For Windows, uncomment and adjust:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def rotate(
        image: np.ndarray, angle: float, background: Union[int, Tuple[int, int, int]]
) -> np.ndarray:
    old_width, old_height = image.shape[:2]
    angle_radian = math.radians(angle)
    width = abs(np.sin(angle_radian) * old_height) + abs(np.cos(angle_radian) * old_width)
    height = abs(np.sin(angle_radian) * old_width) + abs(np.cos(angle_radian) * old_height)
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    rot_mat[1, 2] += (width - old_width) / 2
    rot_mat[0, 2] += (height - old_height) / 2
    return cv2.warpAffine(image, rot_mat, (int(round(height)), int(round(width))), borderValue=background)

def auto_morphology(thresh):
    text_pixels = cv2.countNonZero(thresh)
    total_pixels = thresh.shape[0] * thresh.shape[1]
    density = text_pixels / total_pixels
    if density > 0.10:
      ksize = (1, 1)
    elif density > 0.05:
      ksize = (3, 3)
    elif density > 0.01:
      ksize = (5, 5)
    else:
      ksize = (7, 7)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, ksize)
    dilated = cv2.dilate(thresh, kernel, iterations=2)
    closed = cv2.erode(dilated, kernel, iterations=2)
    return closed

def preprocess_pipeline(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    angle = determine_skew(gray)
    if angle == None:
      angle = 0
    gray = rotate(gray, angle, (0, 0, 0))
    background = cv2.GaussianBlur(gray, (55, 55), 0)
    flattened = cv2.divide(gray, background, scale=255)
    thresh = cv2.threshold(flattened, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    closed = auto_morphology(thresh)
    scaled = cv2.resize(closed, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    # Xóa cv2_imshow vì không khả dụng trong Flask
    return scaled

def crop_image(image):
  h, w = image.shape[:2]
  cropped_images = []
  for i in range(0, h, 50):
      # Create a fresh blank mask each time
      print(i)
      mask = np.zeros((h, w), dtype='uint8')

      # Define bottom y position (capped at image height)
      y_end = min(i + 100, h)

      # Draw the moving rectangle
      cv2.rectangle(mask, (0, i), (w, y_end), 255, -1)

      # Apply the mask
      combined = cv2.bitwise_and(image, image, mask=mask)

      # Compute bounding box of the white mask region
      ys, xs = np.where(mask == 255)
      if ys.size > 0 and xs.size > 0:
          top_y, bottom_y = ys.min(), ys.max()
          left_x, right_x = xs.min(), xs.max()

          cropped = combined[top_y:bottom_y+1, left_x:right_x+1]
      else:
          cropped = combined  # fallback
      # resize cropped block for better OCR visibility
      scaled_img = cv2.resize(cropped, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
      # preprocess each cropped image
      processed_cropped_img = preprocess_pipeline(scaled_img)
      cropped_images.append(processed_cropped_img)
      # Xóa cv2_imshow vì không khả dụng trong Flask
  return cropped_images

def extract_structured_receipt_fields(ocr_text: str) -> dict:
    lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
    data = {
        "Store Name": None,
        "Address": None,
        "Date": None,
        "Employee": None,
        "Bill no": None,
        "Products": [],
        "Total_products": None,
        "Paid": None,
        "Change": None,
        "Discount": None
    }

    # Store name and address
    for i, line in enumerate(lines):
        if any(keyword in line.lower() for keyword in ["bách hóa xanh", "hóa xanh", "bách hóa", "bách xanh"]):
            data["Store Name"] = "Bách Hóa Xanh"
            if i + 1 < len(lines):
                next_line = lines[i + 1].lower()
                if not (re.search(r'\d{2}/\d{2}/\d{4}', next_line) or any(keyword in next_line for keyword in ["bách hóa xanh", "hóa xanh"])):
                    if "www" in next_line and "com" in next_line and i + 2 < len(lines):
                        data["Address"] = lines[i + 2].strip()
                    else:
                        data["Address"] = next_line.strip()
            break

    # Date
    date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{4}\s*(?:\d{1,2}:\d{2})?)'
    for line in lines:
        if any(keyword in line.lower() for keyword in ["ngày", "ct", "số ct", "ngày ct"]):
            date_match = re.search(date_pattern, line)
            if date_match and date_match.group(0):
                data["Date"] = date_match.group(0).replace("-", "/")

    # Employee
    for line in lines:
        if any(keyword in line.lower() for keyword in ["nhân viên", "nhân", "viên", "nv"]):
            employee_match = re.search(r'(?:nhân viên|nhân|viên|nv)[:\s]+(.+)', line, flags=re.IGNORECASE)
            if employee_match and employee_match.group(1):
                data["Employee"] = employee_match.group(1).strip().replace("—", "").strip()

    # Bill number
    for line in lines:
        if any(keyword in line.lower() for keyword in ["số ct", "mã hóa đơn", "mã tra cứu", "ct"]):
            bill_no_match = re.search(r'[A-Z0-9]{6,}', line)
            if bill_no_match and bill_no_match.group(0):
                data["Bill no"] = bill_no_match.group(0)

    # Products
    products = []
    i = 0
    while i < len(lines) - 1:
        name_line = lines[i].strip()
        next_line = lines[i + 1].strip().replace("|", " ").replace(":", " ")

        # Bỏ qua nếu là dòng không phải sản phẩm
        if (re.match(r'^\d+$', name_line) or not name_line or
            any(keyword in name_line.lower() for keyword in ["tổng", "thanh toán", "tiền thối", "lưu ý", "xin cảm ơn"])):
            i += 1
            continue

        # Tìm mẫu: số lượng, đơn giá, [giá giảm], tổng
        match = re.match(r'(\d+(?:[.,]\d+)?)\s+([\d,.]+)\s*(?:([\d,.]+)\s*)?([\d,.]+)?', next_line)
        if match:
            quantity_str = match.group(1).replace(",", ".").strip() or "1"
            unit_price_str = match.group(2).replace(",", ".").replace(".", "").strip() or "0"
            discount_price_str = match.group(3).replace(",", ".").replace(".", "").strip() if match.group(3) else None
            total_price_str = match.group(4).replace(",", ".").replace(".", "").strip() if match.group(4) else None

            try:
                quantity = float(quantity_str) if quantity_str else 1.0
                unit_price = float(unit_price_str) if unit_price_str else 0.0
                total_price = float(total_price_str) if total_price_str else (quantity * unit_price)
                if discount_price_str:
                    total_price = float(discount_price_str) if discount_price_str else total_price

                products.append({
                    "name": name_line,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": total_price
                })
                i += 2
            except ValueError:
                i += 1
                continue
        else:
            i += 1

    if products:
        data["Products"] = products

    # Total products, Paid, Change
    amount_pattern = r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?)'
    for line in lines:
        if any(keyword in line.lower() for keyword in ["tổng tiền hàng", "tổng tiền", "tiền hàng"]):
            total_match = re.search(amount_pattern, line)
            if total_match and total_match.group(1):
                try:
                    data["Total_products"] = float(total_match.group(1).replace(",", ".").replace(".", ""))
                except ValueError:
                    data["Total_products"] = total_match.group(1)
        if any(keyword in line.lower() for keyword in ["thanh toán", "toán", "tiền khách đưa", "đã làm tròn"]):
            paid_match = re.search(amount_pattern, line)
            if paid_match and paid_match.group(1):
                try:
                    data["Paid"] = float(paid_match.group(1).replace(",", ".").replace(".", ""))
                except ValueError:
                    data["Paid"] = paid_match.group(1)
        if any(keyword in line.lower() for keyword in ["tiền thối lại", "thối lại", "tiền lại"]):
            change_match = re.search(amount_pattern, line)
            if change_match and change_match.group(1):
                try:
                    data["Change"] = float(change_match.group(1).replace(",", ".").replace(".", ""))
                except ValueError:
                    data["Change"] = change_match.group(1)

    # Discount
    for line in lines:
        if any(keyword in line.lower() for keyword in ["giảm giá", "mã qr", "mã"]):
            discount_match = re.search(r'\d+', line)
            if discount_match and discount_match.group(0):
                try:
                    data["Discount"] = int(discount_match.group(0))
                except ValueError:
                    data["Discount"] = None

    return data

def extract_from_crops(cropped_images):
    custom_config = r'--oem 3 --psm 6'
    all_lines = []

    for crop in cropped_images:
        ocr_data = pytesseract.image_to_data(
            crop,
            output_type=Output.DICT,
            config=custom_config,
            lang="vie"
        )

        line_dict = {}
        for i in range(len(ocr_data['text'])):
            word = ocr_data['text'][i].strip()
            conf = int(ocr_data['conf'][i])
            line_num = ocr_data['line_num'][i]

            if word and conf >= 70:
                if line_num not in line_dict:
                    line_dict[line_num] = []
                line_dict[line_num].append(word)

        for line_words in line_dict.values():
            line = " ".join(line_words)
            if line:
                all_lines.append(line)

    final_text = "\n".join(all_lines)
    print(final_text)
    return extract_structured_receipt_fields(final_text)

def optimal_model(image):
  custom_config = r'--oem 3 --psm 6'
  text = pytesseract.image_to_string(image, lang="vie")
  result = extract_structured_receipt_fields(text)
  print(text)
  none_counter = 0
  check_list = ["Store Name","Address","Date","Employee","Products","Total_products","Paid",'Change','Discount']
  for i in check_list:
    if result[i] == None:
      none_counter += 1
  if none_counter > 3:
    cropped_images = crop_image(image)
    result = extract_from_crops(cropped_images)
  return result, none_counter

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Không có file được chọn')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Chưa chọn file')
            return redirect(request.url)
        if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                # Đọc file ảnh trực tiếp từ bộ nhớ mà không lưu xuống đĩa
                file_bytes = file.read()
                nparr = np.frombuffer(file_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if image is None:
                    flash('Lỗi: File ảnh không hợp lệ')
                    return redirect(request.url)
                result, none_counter = optimal_model(image)
                return render_template('result.html', result=result, none_counter=none_counter)
            except Exception as e:
                flash(f'Lỗi xử lý hình ảnh: {str(e)}')
                return redirect(request.url)
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)