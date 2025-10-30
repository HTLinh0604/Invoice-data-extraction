from ocr_structure import extract_structured_receipt_fields
from io import StringIO
import pandas as pd
from flask import Response
def export(data):
    buffer = StringIO()
    metadata = {
        "Tên cửa hàng": [data.get("Store Name")],
        "Địa chỉ": [data.get("Address")],
        "Ngày": [data.get("Date")],
        "Nhân viên": [data.get("Employee")],
        "Mã hóa đơn": [data.get("Bill no")],
        'Products': [data.get('Products')],
        "Tổng tiền sản phẩm": [data.get("Total_products")],
        "Đã thanh toán": [data.get("Paid")],
        "Tiền thối": [data.get("Change")],
        "Giảm giá": [data.get("Discount")]
    }
    metadata_df = pd.DataFrame(metadata)

    # Sản phẩm

    # products = data.get("Products",[])
    # product_df = pd.DataFrame(products)
    # product_df.columns = ["Name", "Quantity", "Price", "Total"]

    # Tạo buffer
    buffer = StringIO()
    metadata_df.to_csv(buffer, index=False,encoding='utf-8-sig')
    # buffer.write("\nDanh sách sản phẩm:\n")
    # product_df.to_csv(buffer, index=False)
    csv_data = buffer.getvalue()
    buffer.close()

    return Response(
        csv_data,
        mimetype='text/csv',
        headers={"Content-disposition": "attachment; filename=result.csv"}
    )
