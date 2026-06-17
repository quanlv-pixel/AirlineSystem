from flask import Flask, jsonify, render_template_string
import socket

app = Flask(__name__)
# Database tạm thời trên RAM để lưu trạng thái thanh toán
PAYMENT_DB = {}

def get_local_ip():
    """Hàm tự động lấy chính xác địa chỉ IPv4 của máy tính"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Cố gắng kết nối ra internet để lấy IP nội bộ thực sự
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

# Giao diện Web hiển thị trên Điện thoại (Giống Order Summary)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JetJet Air - Thanh toán</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #F4F6FA; margin: 0; padding: 20px; color: #111827; }
        .card { background: white; border-radius: 20px; padding: 25px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); max-width: 400px; margin: 0 auto; }
        .header { color: #E53935; font-weight: 900; font-size: 26px; text-align: center; margin-bottom: 5px; letter-spacing: 1px;}
        .subheader { text-align: center; color: #9CA3AF; font-size: 14px; margin-bottom: 30px; font-weight: 600;}
        .row { display: flex; justify-content: space-between; margin-bottom: 15px; border-bottom: 1px dashed #E5E7EB; padding-bottom: 15px; font-size: 15px;}
        .label { color: #6B7280; font-weight: 600; }
        .value { font-weight: 800; color: #111827; }
        .total-row { display: flex; justify-content: space-between; margin-top: 20px; font-size: 18px; font-weight: 900; }
        .btn { background: #E53935; color: white; border: none; padding: 16px; width: 100%; border-radius: 12px; font-size: 16px; font-weight: bold; margin-top: 30px; cursor: pointer; transition: 0.3s;}
        .btn:active { transform: scale(0.98); background: #C62828;}
        .success { display: none; text-align: center; background: #DCFCE7; color: #16A34A; padding: 20px; border-radius: 12px; font-size: 16px; font-weight: bold; margin-top: 20px; border: 1px solid #BBF7D0;}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">✈ JETJET AIR</div>
        <div class="subheader">Thanh toán vé máy bay an toàn</div>
        
        <div class="row"><span class="label">Mã đặt chỗ (PNR)</span><span class="value">{{ pnr }}</span></div>
        <div class="row"><span class="label">Trạng thái</span><span class="value" style="color:#F59E0B;">Chờ thanh toán</span></div>
        <div class="total-row"><span class="label">TỔNG TIỀN</span><span class="value" style="color:#E53935; font-size: 24px;">${{ amount }}</span></div>
        
        <button class="btn" id="payBtn" onclick="confirmPayment()">THANH TOÁN NGAY</button>
        <div class="success" id="successMsg">
            <div style="font-size: 40px; margin-bottom: 10px;">✅</div>
            Đã thanh toán thành công!<br><span style="font-size: 14px; font-weight: normal; color: #4B5563;">Vui lòng kiểm tra màn hình máy tính.</span>
        </div>
    </div>

    <script>
        function confirmPayment() {
            document.getElementById('payBtn').innerText = "ĐANG XỬ LÝ...";
            fetch('/api/confirm/{{ pnr }}', {method: 'POST'})
            .then(r => r.json())
            .then(data => {
                document.getElementById('payBtn').style.display = 'none';
                document.getElementById('successMsg').style.display = 'block';
            });
        }
    </script>
</body>
</html>
"""

@app.route('/pay/<pnr>/<amount>')
def pay_page(pnr, amount):
    PAYMENT_DB[pnr] = "PENDING"
    return render_template_string(HTML_TEMPLATE, pnr=pnr, amount=amount)

@app.route('/api/confirm/<pnr>', methods=['POST'])
def confirm(pnr):
    PAYMENT_DB[pnr] = "PAID"
    return jsonify({"status": "SUCCESS"})

@app.route('/api/status/<pnr>')
def status(pnr):
    return jsonify({"status": PAYMENT_DB.get(pnr, "UNKNOWN")})

if __name__ == '__main__':
    ip = get_local_ip()
    print("===================================================")
    print(f"🚀 SERVER THANH TOÁN QR ĐANG CHẠY TẠI: http://{ip}:5000")
    print("   Hãy để cửa sổ này chạy ngầm và mở app PySide6 lên!")
    print("===================================================")
    app.run(host='0.0.0.0', port=5000)