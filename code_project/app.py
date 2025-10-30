import os
from flask import Flask, request, render_template, flash, redirect, url_for,session
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import pandas as pd
import json
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Đường dẫn trên Windows
from optimal_model import optimal_model
from output import export

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


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
                session['ocr_result'] = result
                return render_template('result.html', result=result, none_counter=none_counter)
            except Exception as e:
                flash(f'Lỗi xử lý hình ảnh: {str(e)}')
                return redirect(request.url)
    return render_template('upload.html')

@app.route('/save_to_csv', methods=['POST'])
def save_to_csv():
    try:
        result = request.form['result']
        
        result_dict = json.loads(result)
        print("This is result_dict:", result_dict)
        
        export(result_dict)
        df = pd.DataFrame(result_dict)
        df.to_csv('result.csv', index=False)
        flash('Dữ liệu đã được lưu vào file CSV', 'success')
    except Exception as e:
        flash(f'Lỗi khi lưu dữ liệu vào CSV: {str(e)}', 'error')
    
    return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(debug=True)