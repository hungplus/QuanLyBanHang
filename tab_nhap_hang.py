from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QLineEdit, QComboBox, QPushButton, QMessageBox, QCompleter, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QStringListModel
from PyQt6.QtGui import QIntValidator

class PopupThemNPP(QDialog):
    def __init__(self, db_manager, danh_sach_npp_hien_tai, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.setWindowTitle("Thêm Đối Tác / Nhân Viên Mới")
        self.setFixedSize(450, 250)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        layout = QVBoxLayout()
        form_layout = QFormLayout()
        css_input = "font-size: 16px; padding: 6px; border: 1px solid #ccc; border-radius: 4px;"
        
        self.cb_ten_npp = QComboBox()
        self.cb_ten_npp.setEditable(True) 
        self.cb_ten_npp.setStyleSheet(css_input)
        self.cb_ten_npp.lineEdit().setPlaceholderText("Có thể bỏ qua hoặc chọn/gõ tên...")
        self.cb_ten_npp.addItem("") # Thêm một tùy chọn rỗng ở đầu
        self.cb_ten_npp.addItem("Khách lẻ / Sale tự do")
        self.cb_ten_npp.addItems(danh_sach_npp_hien_tai)

        self.txt_ten_sale = QLineEdit()
        self.txt_ten_sale.setStyleSheet(css_input)
        self.txt_ten_sale.setPlaceholderText("Bắt buộc nhập (VD: Anh Hoàng...)")
        
        self.txt_sdt = QLineEdit()
        self.txt_sdt.setStyleSheet(css_input)
        self.txt_sdt.setPlaceholderText("Bắt buộc nhập (VD: 0912345678)")

        form_layout.addRow("Tên Công ty/Đại lý:", self.cb_ten_npp)
        form_layout.addRow("Tên Nhân viên Sales:", self.txt_ten_sale)
        form_layout.addRow("Số điện thoại:", self.txt_sdt)
        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        
        btn_luu = QPushButton("💾 LƯU THÔNG TIN")
        # Fix lỗi mất chữ khi hover bằng cách khai báo rõ màu chữ trong state :hover
        btn_luu.setStyleSheet("""
            QPushButton {
                font-size: 16px; font-weight: bold; background-color: #2980b9; 
                color: white; padding: 10px; border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3498db; color: white;
            }
        """)
        btn_luu.clicked.connect(self.xu_ly_luu)
        
        btn_huy = QPushButton("Hủy")
        btn_huy.setStyleSheet("font-size: 16px; padding: 10px; border-radius: 4px;")
        btn_huy.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_huy)
        btn_layout.addWidget(btn_luu)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)

    def xu_ly_luu(self):
        ten_npp = self.cb_ten_npp.currentText().strip()
        ten_sale = self.txt_ten_sale.text().strip()
        sdt = self.txt_sdt.text().strip()

        # Logic bắt buộc: Phải có Tên Sale và Số điện thoại
        if not ten_sale or not sdt:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đầy đủ Tên Nhân viên Sales và Số điện thoại!")
            return
            
        # Logic tự động: Nếu bỏ trống Tên Công ty, tự gán thành Khách lẻ
        if not ten_npp:
            ten_npp = "Khách lẻ / Sale tự do"

        try:
            self.db.them_doi_tac(ten_npp, ten_sale, sdt)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể thêm.\nLỗi: {e}")

class TabNhapHang(QWidget):
    yeu_cau_lam_moi = pyqtSignal() # Báo hiệu cần refresh các tab khác

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        lbl_tieu_de = QLabel("📦 NHẬP HÀNG TỪ TOA")
        lbl_tieu_de.setStyleSheet("font-size: 22px; font-weight: bold; color: #27ae60; margin-bottom: 20px;")
        lbl_tieu_de.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_tieu_de)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setSpacing(15)
        css_input = "font-size: 18px; padding: 8px; border: 1px solid #7f8c8d; border-radius: 4px;"

        npp_layout = QHBoxLayout()
        self.cb_npp = QComboBox()
        self.cb_npp.setStyleSheet(css_input)
        self.cb_npp.setSizePolicy(self.cb_npp.sizePolicy().Policy.Expanding, self.cb_npp.sizePolicy().Policy.Fixed)
        
        self.btn_them_npp = QPushButton(" ➕ ")
        self.btn_them_npp.setStyleSheet("""
            QPushButton { 
                font-size: 18px; font-weight: bold; background-color: #27ae60; 
                color: white; padding: 5px 12px; border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.btn_them_npp.clicked.connect(self.mo_popup_them_npp)
        npp_layout.addWidget(self.cb_npp)
        npp_layout.addWidget(self.btn_them_npp)

        self.cb_sale = QComboBox()
        self.cb_sale.setStyleSheet(css_input)
        self.cb_npp.currentTextChanged.connect(self.cap_nhat_combo_sale)

        self.txt_san_pham_nhap = QLineEdit()
        self.txt_san_pham_nhap.setPlaceholderText("Gõ tên sản phẩm...")
        self.txt_san_pham_nhap.setStyleSheet(css_input)
        
        self.completer_nhap = QCompleter([], self)
        self.completer_nhap.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer_nhap.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer_nhap.popup().setStyleSheet("QListView { font-size: 18px; }")
        self.txt_san_pham_nhap.setCompleter(self.completer_nhap)
        
        sl_layout = QHBoxLayout()
        self.txt_so_luong = QLineEdit()
        self.txt_so_luong.setStyleSheet(css_input)
        self.txt_so_luong.setFixedWidth(90)
        self.txt_so_luong.setValidator(QIntValidator(1, 100000, self))
        
        lbl_nhan = QLabel("✖")
        lbl_nhan.setStyleSheet("font-size: 18px; font-weight: bold; color: #7f8c8d;")
        
        self.txt_quy_cach = QLineEdit("1")
        self.txt_quy_cach.setStyleSheet(css_input)
        self.txt_quy_cach.setFixedWidth(90)
        self.txt_quy_cach.setValidator(QIntValidator(1, 1000, self))
        
        self.lbl_tong_nhap = QLabel("= Tổng nhập: 0 đơn vị")
        self.lbl_tong_nhap.setStyleSheet("font-size: 18px; font-weight: bold; color: #2980b9; margin-left: 10px;")
        self.lbl_tong_nhap.setMinimumWidth(220)
        
        self.txt_so_luong.textChanged.connect(self.tinh_nham_so_luong)
        self.txt_quy_cach.textChanged.connect(self.tinh_nham_so_luong)
        
        sl_layout.addWidget(self.txt_so_luong)
        sl_layout.addWidget(lbl_nhan)
        sl_layout.addWidget(self.txt_quy_cach)
        sl_layout.addWidget(self.lbl_tong_nhap)
        sl_layout.addStretch()

        gia_von_layout = QHBoxLayout()
        
        self.txt_gia_von = QLineEdit()
        self.txt_gia_von.setStyleSheet(css_input)
        self.txt_gia_von.setPlaceholderText("VD: 31,8")
        self.txt_gia_von.setFixedWidth(200)
        
        self.btn_dau_phay = QPushButton(" , ")
        self.btn_dau_phay.setStyleSheet("QPushButton { font-size: 22px; font-weight: bold; background-color: #ecf0f1; border: 1px solid #7f8c8d; border-radius: 4px; padding: 4px 16px;}")
        self.btn_dau_phay.clicked.connect(self.them_dau_phay)
        
        gia_von_layout.addWidget(self.txt_gia_von)
        gia_von_layout.addWidget(self.btn_dau_phay)
        gia_von_layout.addStretch()

        lbl_style = "font-size: 18px; font-weight: bold;"
        form_layout.addRow(QLabel("Nhà Phân Phối:", styleSheet=lbl_style), npp_layout)
        form_layout.addRow(QLabel("Nhân Viên (Sale):", styleSheet=lbl_style), self.cb_sale)
        form_layout.addRow(QLabel("Tên Sản Phẩm:", styleSheet=lbl_style), self.txt_san_pham_nhap)
        form_layout.addRow(QLabel("Số Lượng × Quy Cách:", styleSheet=lbl_style), sl_layout)
        form_layout.addRow(QLabel("Giá Vốn Đợt Này:", styleSheet=lbl_style), gia_von_layout)

        form_container = QWidget()
        form_container.setLayout(form_layout)
        form_container.setMaximumWidth(850)
        form_container.setMinimumWidth(600)
        
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(form_container)
        center_layout.addStretch()
        
        layout.addLayout(center_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_luu_kho = QPushButton("💾 LƯU VÀO KHO")
        self.btn_luu_kho.setStyleSheet("QPushButton { font-size: 20px; font-weight: bold; background-color: #27ae60; color: white; padding: 15px 40px; border-radius: 8px; margin-top: 20px;}")
        self.btn_luu_kho.clicked.connect(self.xu_ly_luu_kho)
        
        btn_layout.addWidget(self.btn_luu_kho)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        self.tai_du_lieu()

    def tai_du_lieu(self):
        # Nạp Nhà phân phối
        ds_npp = self.db.lay_danh_sach_npp_hoat_dong()
        self.cb_npp.blockSignals(True)
        self.cb_npp.clear()
        self.cb_npp.addItem("-- Chọn Nhà Phân Phối --")
        self.cb_npp.addItem("Khách lẻ / Sale tự do")
        self.cb_npp.addItems(ds_npp)
        self.cb_npp.blockSignals(False)
        
        # Nạp gợi ý Sản phẩm
        ds_sp = self.db.lay_danh_sach_ten_san_pham()
        self.completer_nhap.setModel(QStringListModel(ds_sp))

    def cap_nhat_combo_sale(self, ten_npp_chon):
        self.cb_sale.clear()
        if ten_npp_chon == "-- Chọn Nhà Phân Phối --":
            self.cb_sale.addItem("-- Chọn Nhân Viên Sales --")
        else:
            ds_sale = self.db.lay_danh_sach_sale_theo_npp(ten_npp_chon)
            if not ds_sale:
                self.cb_sale.addItem("-- Chưa có Nhân viên nào --")
            else:
                self.cb_sale.addItems([f"{t} - {s}" if s else t for t, s in ds_sale])

    def mo_popup_them_npp(self):
        popup = PopupThemNPP(self.db, self.db.lay_danh_sach_npp_hoat_dong(), self)
        if popup.exec():
            QMessageBox.information(self, "Thành Công", "Đã thêm đối tác mới!")
            self.yeu_cau_lam_moi.emit() # Thông báo cho cả hệ thống cập nhật

    def tinh_nham_so_luong(self):
        sl = int(self.txt_so_luong.text() or 0)
        qc = int(self.txt_quy_cach.text() or 1)
        self.lbl_tong_nhap.setText(f"= Tổng nhập: {sl * qc} đơn vị")

    def them_dau_phay(self):
        hien_tai = self.txt_gia_von.text()
        if "," not in hien_tai and "." not in hien_tai:
            self.txt_gia_von.setText(hien_tai + "," if hien_tai else "0,")
        self.txt_gia_von.setFocus()

    def xu_ly_luu_kho(self):
        ten_npp = self.cb_npp.currentText()
        chuoi_sale = self.cb_sale.currentText()
        san_pham = self.txt_san_pham_nhap.text().strip()
        sl_str = self.txt_so_luong.text().strip()
        gia_von_str = self.txt_gia_von.text().strip()

        if ten_npp == "-- Chọn Nhà Phân Phối --" or chuoi_sale in ["-- Chọn Nhân Viên Sales --", "-- Chưa có Nhân viên nào --"] or not san_pham or not sl_str or not gia_von_str:
            QMessageBox.warning(self, "Lỗi", "Vui lòng điền đủ thông tin!")
            return

        try:
            tong_so_luong = int(sl_str) * int(self.txt_quy_cach.text() or 1)
            gia_von = float(gia_von_str.replace(',', '.'))
            if tong_so_luong <= 0: raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Số lượng hoặc Giá vốn sai định dạng!")
            return

        ten_sale = chuoi_sale.split(" - ")[0].strip()
        thanh_cong, thong_bao = self.db.nghiep_vu_nhap_kho(ten_npp, ten_sale, san_pham, tong_so_luong, gia_von)
        
        if thanh_cong:
            QMessageBox.information(self, "Thành Công", f"Đã nhập {tong_so_luong} x [{san_pham}].")
            self.txt_san_pham_nhap.clear()
            self.txt_so_luong.clear()
            self.txt_quy_cach.setText("1")
            self.txt_gia_von.clear()
            self.txt_san_pham_nhap.setFocus()
            self.yeu_cau_lam_moi.emit()
        else:
            QMessageBox.critical(self, "Lỗi SQL", f"Lỗi: {thong_bao}")