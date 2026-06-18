from PySide6.QtCore import Qt, QDateTime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QDoubleSpinBox, QSpinBox, QDateTimeEdit,
    QMessageBox, QWidget, QComboBox
)

from shared.services.flight_service import create_flight, update_flight, delete_flight
from shared.services.flight_utils import (
    generate_flight_code,
    calculate_duration,
    get_delay,
    calculate_price
)

from datetime import timedelta

AIRPORTS = [
    "SGN", "HAN", "DAD", "PQC",
    "CXR", "SIN", "ICN", "NRT"
]

C_RED = "#E53935"
C_TEXT = "#111827"
C_BORDER = "#E4E6F0"
C_SOFT = "#F3F4F6"

class FlightDialog(QDialog):
    def __init__(self, flight=None, parent=None):
        super().__init__(parent)
        self.flight = flight
        self.is_edit_mode = flight is not None

        title = "Chỉnh sửa Chuyến bay" if self.is_edit_mode else "Thêm Chuyến bay mới"
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.setStyleSheet(f"background-color: white; color: {C_TEXT};")

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title Label
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_lbl)

        # Form Fields
        self.code_input = self._create_input("Mã chuyến bay (vd: VN123):")
        
        layout.addWidget(QLabel("Sân bay đi:"))
        self.dep_input = QComboBox()
        self.dep_input.addItems(AIRPORTS)
        layout.addWidget(self.dep_input)

        layout.addWidget(QLabel("Sân bay đến:"))
        self.arr_input = QComboBox()
        self.arr_input.addItems(AIRPORTS)
        layout.addWidget(self.arr_input)
        
        # Departure Time
        layout.addWidget(QLabel("Thời gian khởi hành:"))
        self.dep_time = QDateTimeEdit(QDateTime.currentDateTime())
        self.dep_time.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.dep_time.setStyleSheet(self._input_style())
        layout.addWidget(self.dep_time)

        # Arrival Time
        layout.addWidget(QLabel("Thời gian đến (Tự động tính):"))
        self.arr_time = QDateTimeEdit(QDateTime.currentDateTime().addSecs(7200))
        self.arr_time.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.arr_time.setStyleSheet(self._input_style(readonly=True))
        self.arr_time.setReadOnly(True) # Không cho sửa tay, hệ thống sẽ tự tính
        layout.addWidget(self.arr_time)

        # Seats
        layout.addWidget(QLabel("Tổng số ghế:"))
        self.seats_input = QSpinBox()
        self.seats_input.setMaximum(1000)
        self.seats_input.setValue(180)
        self.seats_input.setStyleSheet(self._input_style())
        layout.addWidget(self.seats_input)

        # TIỀN VÉ (PRICE) - Thêm mới
        layout.addWidget(QLabel("Giá vé ($):"))
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(10000.0)
        self.price_input.setStyleSheet(self._input_style())
        layout.addWidget(self.price_input)

        # Tự động tính giá vé dựa trên chặng bay khi thay đổi sân bay
        self.dep_input.currentTextChanged.connect(self._auto_update_price)
        self.arr_input.currentTextChanged.connect(self._auto_update_price)

        # Pre-populate if editing
        if self.is_edit_mode:
            self.code_input.setText(getattr(self.flight, 'flight_number', ''))
            self.code_input.setReadOnly(True)
            self.code_input.setStyleSheet(self._input_style(readonly=True))
            
            self.dep_input.setCurrentText(getattr(self.flight, 'departure', ''))
            self.dep_input.setEnabled(False)
            self.dep_input.setStyleSheet(self._input_style(readonly=True))
            
            self.arr_input.setCurrentText(getattr(self.flight, 'destination', ''))
            self.arr_input.setEnabled(False)
            self.arr_input.setStyleSheet(self._input_style(readonly=True))
            
            try:
                dt_dep = QDateTime.fromString(self.flight.departure_time, "yyyy-MM-dd HH:mm:ss")
                if dt_dep.isValid(): self.dep_time.setDateTime(dt_dep)
                dt_arr = QDateTime.fromString(self.flight.arrival_time, "yyyy-MM-dd HH:mm:ss")
                if dt_arr.isValid(): self.arr_time.setDateTime(dt_arr)
            except Exception:
                pass
                
            self.seats_input.setValue(getattr(self.flight, 'total_seats', 0))
            self.seats_input.setReadOnly(True)
            self.seats_input.setStyleSheet(self._input_style(readonly=True))
            
            # Đổ dữ liệu giá vé lên ô nhập
            self.price_input.setValue(getattr(self.flight, 'ticket_price', 0.0))
        else:
            self.code_input.setReadOnly(True)
            self.code_input.setPlaceholderText("Tự động tạo")
            self.code_input.setStyleSheet(self._input_style(readonly=True))
            self._auto_update_price()

        layout.addSpacing(10)

        # Buttons
        btn_layout = QHBoxLayout()
        
        if self.is_edit_mode:
            self.del_btn = QPushButton("XÓA")
            self.del_btn.setStyleSheet(f"background-color: #EF4444; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold;")
            self.del_btn.clicked.connect(self.handle_delete)
            btn_layout.addWidget(self.del_btn)

        btn_layout.addStretch()

        self.cancel_btn = QPushButton("Hủy")
        self.cancel_btn.setStyleSheet(f"background-color: {C_SOFT}; color: {C_TEXT}; padding: 8px 16px; border-radius: 6px;")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("LƯU")
        self.save_btn.setStyleSheet(f"background-color: {C_RED}; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold;")
        self.save_btn.clicked.connect(self.handle_save)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)

        layout.addLayout(btn_layout)

    def _auto_update_price(self, *_):
        """Hàm tự động gọi API/Utils để lấy giá vé tham khảo khi đổi sân bay"""
        if not self.is_edit_mode:
            dep = self.dep_input.currentText()
            arr = self.arr_input.currentText()
            if dep and arr:
                self.price_input.setValue(calculate_price(dep, arr))

    def _input_style(self, readonly=False):
        bg = "#EEEEEE" if readonly else "white"
        return f"""
            border: 1px solid {C_BORDER};
            border-radius: 6px;
            padding: 6px;
            background-color: {bg};
        """

    def _create_input(self, label_text):
        self.layout().addWidget(QLabel(label_text))
        inp = QLineEdit()
        inp.setStyleSheet(self._input_style())
        self.layout().addWidget(inp)
        return inp

    def handle_save(self):
        dep = self.dep_input.currentText()
        arr = self.arr_input.currentText()
        
        if dep == arr:
            QMessageBox.warning(self, "Lỗi", "Sân bay đi và đến không được trùng nhau!")
            return

        if not self.is_edit_mode:
            f_code = generate_flight_code(dep, arr)
        else:
            f_code = getattr(self.flight, 'flight_number', '')
            
        d_time = self.dep_time.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        duration = calculate_duration(dep, arr)
        delay = get_delay(dep)

        minutes = duration + delay
        arrival = self.dep_time.dateTime()
        arrival = arrival.addSecs(minutes * 60)
        a_time = arrival.toString("yyyy-MM-dd HH:mm:ss")
        
        seats = self.seats_input.value()
        price = self.price_input.value()  # Lấy giá vé từ giao diện

        if self.is_edit_mode:
            # Gửi giá vé mới vào database
            success = update_flight(
                flight_id=self.flight.flight_id,
                departure_time=d_time,
                arrival_time=a_time,
                ticket_price=price,
                status="Scheduled"
            )
            if success:
                QMessageBox.information(self, "Thành công", "Đã cập nhật chuyến bay!")
                self.accept()
            else:
                QMessageBox.warning(self, "Lỗi", "Lỗi khi cập nhật chuyến bay.")
        else:
            # Lưu giá vé được tinh chỉnh
            success, msg = create_flight(
                flight_number=f_code,
                airline_name="JetJet Air",
                departure=dep,
                destination=arr,
                departure_time=d_time,
                arrival_time=a_time,
                total_seats=seats,
                ticket_price=price,
                aircraft="A320",
                gate="G1",
                terminal="T1"
            )
            if success:
                QMessageBox.information(self, "Thành công", msg)
                self.accept()
            else:
                QMessageBox.warning(self, "Lỗi", msg)

    def handle_delete(self):
        reply = QMessageBox.question(self, 'Xác nhận xóa', 
                                     'Bạn có chắc chắn muốn xóa chuyến bay này?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if delete_flight(self.flight.flight_id):
                QMessageBox.information(self, "Thành công", "Đã xóa chuyến bay.")
                self.accept()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể xóa chuyến bay này.")