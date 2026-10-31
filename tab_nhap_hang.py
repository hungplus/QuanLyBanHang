from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QLineEdit, QComboBox, QPushButton, QMessageBox, QCompleter, QDialog,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal, QStringListModel, QTime
from PyQt6.QtGui import QIntValidator, QFont

# ==============================================================
# CỬA SỔ POPUP THÊM ĐỐI TÁC
# ==============================================================
class PopupThemNPP(QDialog):
    def __init__(self, db_manager, danh_sach_npp_hien_tai, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.setWindowTitle("Thêm Đối Tác / Nhân Viên Mới")
        
        # SỬA LỖI: Cấu hình kích thước tối thiểu cho phép kéo giãn
        self.setMinimumSize(550, 350)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        
        # SỬA LỖI: Dùng đúng hàm setStyleSheet để định dạng chữ cho các nhãn
        self.setStyleSheet("QLabel { font-size: 20px; font-weight: bold; color: #2c3e50; }")

        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # CẬP NHẬT: Kích thước chữ và khung nhập liệu to như bên tab Quản lý Kho
        css_input = "font-size: 22px; padding: 10px; border: 2px solid #bdc3c7; border-radius: 6px;"
        
        self.cb_ten_npp = QComboBox()
        self.cb_ten_npp.setEditable(True) 
        self.cb_ten_npp.setStyleSheet(css_input)
        self.cb_ten_npp.lineEdit().setPlaceholderText("Có thể bỏ qua hoặc chọn/gõ tên...")
        self.cb_ten_npp.addItem("")
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
        
        # CẬP NHẬT: Nút Hủy và Lưu to hơn, viền bo tròn giống tab Quản lý Kho
        btn_huy = QPushButton("Hủy")
        btn_huy.setStyleSheet("""
            QPushButton {font-size: 22px; font-weight: bold; background-color: #ecf0f1; color: #2c3e50; padding: 12px 20px; border: 2px solid #bdc3c7; border-radius: 6px;}
            QPushButton:hover {background-color: #bdc3c7;}
        """)
        btn_huy.clicked.connect(self.reject)
        
        btn_luu = QPushButton("💾 LƯU THÔNG TIN")
        btn_luu.setStyleSheet("""
            QPushButton {font-size: 22px; font-weight: bold; background-color: #2980b9; color: white; padding: 12px 20px; border: 2px solid #2980b9; border-radius: 6px;}
            QPushButton:hover {background-color: #3498db; border: 2px solid #3498db;}
        """)
        btn_luu.clicked.connect(self.xu_ly_luu)
        
        btn_layout.addWidget(btn_huy)
        btn_layout.addWidget(btn_luu)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def xu_ly_luu(self):
        ten_npp = self.cb_ten_npp.currentText().strip()
        ten_sale = self.txt_ten_sale.text().strip()
        sdt = self.txt_sdt.text().strip()

        if not ten_sale or not sdt:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đầy đủ Tên Nhân viên Sales và Số điện thoại!")
            return
            
        if not ten_npp:
            ten_npp = "Khách lẻ / Sale tự do"

        try:
            self.db.them_doi_tac(ten_npp, ten_sale, sdt)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể thêm.\nLỗi: {e}")

# ==============================================================
# GIAO DIỆN CHÍNH TAB NHẬP HÀNG
# ==============================================================
class TabNhapHang(QWidget):
    yeu_cau_lam_moi = pyqtSignal()

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        lbl_tieu_de = QLabel("📦 NHẬP HÀNG TỪ TOA")
        lbl_tieu_de.setStyleSheet("font-size: 28px; font-weight: bold; color: #27ae60; margin-bottom: 10px;")
        lbl_tieu_de.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(lbl_tieu_de)

        # KHU VỰC 1: FORM NHẬP LIỆU
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setSpacing(15)
        
        css_input = "font-size: 22px; padding: 10px; border: 1px solid #7f8c8d; border-radius: 4px;"
        lbl_style = "font-size: 22px; font-weight: bold;"

        self.txt_ma_vach = QLineEdit()
        self.txt_ma_vach.setStyleSheet(css_input)
        self.txt_ma_vach.setPlaceholderText("Tít mã vạch hoặc gõ mã SKU...")
        self.txt_ma_vach.returnPressed.connect(self.xu_ly_quet_ma_vach)

        npp_layout = QHBoxLayout()
        self.txt_npp = QLineEdit()
        self.txt_npp.setStyleSheet(css_input)
        self.txt_npp.setPlaceholderText("Gõ để tìm (hoặc bỏ trống)...")
        
        self.completer_npp = QCompleter([], self)
        self.completer_npp.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer_npp.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer_npp.popup().setStyleSheet("QListView { font-size: 20px; }")
        self.txt_npp.setCompleter(self.completer_npp)
        
        self.btn_them_npp = QPushButton(" ➕ ")
        self.btn_them_npp.setStyleSheet("""
            QPushButton { font-size: 22px; font-weight: bold; background-color: #27ae60; color: white; padding: 5px 15px; border-radius: 4px;}
            QPushButton:hover { background-color: #2ecc71; }
        """)
        self.btn_them_npp.clicked.connect(self.mo_popup_them_npp)
        npp_layout.addWidget(self.txt_npp)
        npp_layout.addWidget(self.btn_them_npp)

        self.txt_sale = QLineEdit()
        self.txt_sale.setStyleSheet(css_input)
        
        self.completer_sale = QCompleter([], self)
        self.completer_sale.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer_sale.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer_sale.popup().setStyleSheet("QListView { font-size: 20px; }")
        self.txt_sale.setCompleter(self.completer_sale)
        self.txt_npp.textChanged.connect(self.cap_nhat_goi_y_sale)

        self.txt_san_pham_nhap = QLineEdit()
        self.txt_san_pham_nhap.setStyleSheet(css_input)
        
        self.completer_nhap = QCompleter([], self)
        self.completer_nhap.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer_nhap.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer_nhap.popup().setStyleSheet("QListView { font-size: 20px; }")
        self.txt_san_pham_nhap.setCompleter(self.completer_nhap)

        sl_layout = QHBoxLayout()
        self.txt_so_luong = QLineEdit()
        self.txt_so_luong.setStyleSheet(css_input)
        self.txt_so_luong.setFixedWidth(100)
        self.txt_so_luong.setValidator(QIntValidator(1, 100000, self))
        
        lbl_nhan = QLabel("✖")
        lbl_nhan.setStyleSheet("font-size: 22px; font-weight: bold; color: #7f8c8d;")
        
        self.txt_quy_cach = QLineEdit("1")
        self.txt_quy_cach.setStyleSheet(css_input)
        self.txt_quy_cach.setFixedWidth(100)
        self.txt_quy_cach.setValidator(QIntValidator(1, 1000, self))
        
        self.lbl_tong_nhap = QLabel("= Tổng: 0 đơn vị")
        self.lbl_tong_nhap.setStyleSheet("font-size: 22px; font-weight: bold; color: #2980b9; margin-left: 10px;")
        
        self.txt_so_luong.textChanged.connect(self.tinh_nham_so_luong)
        self.txt_quy_cach.textChanged.connect(self.tinh_nham_so_luong)
        
        sl_layout.addWidget(self.txt_so_luong)
        sl_layout.addWidget(lbl_nhan)
        sl_layout.addWidget(self.txt_quy_cach)
        sl_layout.addWidget(self.lbl_tong_nhap)
        sl_layout.addStretch()

        gia_layout = QHBoxLayout()
        self.txt_gia_von = QLineEdit()
        self.txt_gia_von.setStyleSheet(css_input)
        self.txt_gia_von.setPlaceholderText("Vốn: 31,8")
        
        self.txt_gia_ban = QLineEdit()
        self.txt_gia_ban.setStyleSheet(css_input)
        self.txt_gia_ban.setPlaceholderText("Bán lẻ: 35,0")
        
        self.btn_dau_phay = QPushButton(" , ")
        self.btn_dau_phay.setStyleSheet("QPushButton { font-size: 24px; font-weight: bold; background-color: #ecf0f1; border: 1px solid #7f8c8d; border-radius: 4px; padding: 4px 20px;}")
        self.btn_dau_phay.clicked.connect(self.them_dau_phay)
        
        gia_layout.addWidget(self.txt_gia_von)
        gia_layout.addWidget(self.txt_gia_ban)
        gia_layout.addWidget(self.btn_dau_phay)

        form_layout.addRow(QLabel("Mã Vạch (SKU):", styleSheet=lbl_style), self.txt_ma_vach)
        form_layout.addRow(QLabel("Nhà Phân Phối:", styleSheet=lbl_style), npp_layout)
        form_layout.addRow(QLabel("Nhân Viên (Sale):", styleSheet=lbl_style), self.txt_sale)
        form_layout.addRow(QLabel("Tên Sản Phẩm:", styleSheet=lbl_style), self.txt_san_pham_nhap)
        form_layout.addRow(QLabel("Số Lượng × Quy Cánh:", styleSheet=lbl_style), sl_layout)
        form_layout.addRow(QLabel("Giá Vốn / Bán Lẻ:", styleSheet=lbl_style), gia_layout)

        form_container = QWidget()
        form_container.setLayout(form_layout)
        form_container.setMaximumWidth(950)
        form_container.setMinimumWidth(700)
        
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(form_container)
        center_layout.addStretch()
        main_layout.addLayout(center_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_luu_kho = QPushButton("💾 LƯU VÀO KHO")
        self.btn_luu_kho.setStyleSheet("QPushButton { font-size: 22px; font-weight: bold; background-color: #27ae60; color: white; padding: 15px 50px; border-radius: 8px; margin-top: 10px;}")
        self.btn_luu_kho.clicked.connect(self.xu_ly_luu_kho)
        btn_layout.addWidget(self.btn_luu_kho)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        lbl_lich_su = QLabel("🕒 LỊCH SỬ NHẬP VỪA XONG")
        lbl_lich_su.setStyleSheet("font-size: 18px; font-weight: bold; color: #34495e; margin-top: 20px;")
        main_layout.addWidget(lbl_lich_su)

        self.bang_lich_su = QTableWidget()
        self.bang_lich_su.setColumnCount(5)
        self.bang_lich_su.setHorizontalHeaderLabels(["Thời Gian", "Mã Vạch", "Tên Sản Phẩm", "Số Lượng", "Giá Vốn"])
        self.bang_lich_su.verticalHeader().setVisible(False)
        self.bang_lich_su.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.bang_lich_su.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.bang_lich_su.setStyleSheet("""
            QTableWidget { font-size: 24px; gridline-color: #bdc3c7;} 
            QHeaderView::section { background-color: #7f8c8d; color: white; font-size: 22px; font-weight: bold; padding: 6px;}
        """)
        self.bang_lich_su.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.bang_lich_su.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        
        # Cột Tên Sản Phẩm sẽ tự động lấy phần không gian còn dư
        self.bang_lich_su.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        # Ép chiều rộng cho cột Số Lượng to ra (Bạn có thể tăng giảm số 150)
        self.bang_lich_su.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.bang_lich_su.setColumnWidth(3, 150)
        
        # Ép chiều rộng cho cột Giá Vốn to ra (Bạn có thể tăng giảm số 200)
        self.bang_lich_su.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        self.bang_lich_su.setColumnWidth(4, 200)

        main_layout.addWidget(self.bang_lich_su)

        self.setLayout(main_layout)
        self.tai_du_lieu()

    def tai_du_lieu(self):
        ds_npp = self.db.lay_danh_sach_npp_hoat_dong()
        danh_sach_goi_y_npp = ["Khách lẻ / Sale tự do"] + ds_npp
        self.completer_npp.setModel(QStringListModel(danh_sach_goi_y_npp))
        
        self.ds_tat_ca_sale = []
        for npp in danh_sach_goi_y_npp: 
            sales = self.db.lay_danh_sach_sale_theo_npp(npp)
            if sales:
                self.ds_tat_ca_sale.extend([f"{t} - {s}" if s else t for t, s in sales])
        
        self.ds_tat_ca_sale = list(set(self.ds_tat_ca_sale))
        self.completer_sale.setModel(QStringListModel(self.ds_tat_ca_sale))
        
        ds_sp = self.db.lay_danh_sach_ten_san_pham()
        self.completer_nhap.setModel(QStringListModel(ds_sp))

    def cap_nhat_goi_y_sale(self):
        ten_npp_chon = self.txt_npp.text().strip()
        if not ten_npp_chon or ten_npp_chon == "Khách lẻ / Sale tự do":
            self.completer_sale.setModel(QStringListModel(self.ds_tat_ca_sale))
        else:
            ds_sale = self.db.lay_danh_sach_sale_theo_npp(ten_npp_chon)
            if ds_sale: 
                ds_goi_y = [f"{t} - {s}" if s else t for t, s in ds_sale]
                self.completer_sale.setModel(QStringListModel(ds_goi_y))
            else:
                self.completer_sale.setModel(QStringListModel(self.ds_tat_ca_sale))

    def mo_popup_them_npp(self):
        popup = PopupThemNPP(self.db, self.db.lay_danh_sach_npp_hoat_dong(), self)
        if popup.exec():
            self.yeu_cau_lam_moi.emit()
            self.tai_du_lieu()

    def tinh_nham_so_luong(self):
        sl = int(self.txt_so_luong.text() or 0)
        qc = int(self.txt_quy_cach.text() or 1)
        self.lbl_tong_nhap.setText(f"= Tổng: {sl * qc} đơn vị")

    def them_dau_phay(self):
        if self.txt_gia_ban.hasFocus():
            hien_tai = self.txt_gia_ban.text()
            if "," not in hien_tai and "." not in hien_tai:
                self.txt_gia_ban.setText(hien_tai + "," if hien_tai else "0,")
        else:
            hien_tai = self.txt_gia_von.text()
            if "," not in hien_tai and "." not in hien_tai:
                self.txt_gia_von.setText(hien_tai + "," if hien_tai else "0,")
            self.txt_gia_von.setFocus()

    def xu_ly_quet_ma_vach(self):
        ma_vach = self.txt_ma_vach.text().strip()
        if ma_vach:
            self.txt_san_pham_nhap.setFocus()

    def xu_ly_luu_kho(self):
        ma_vach = self.txt_ma_vach.text().strip()
        ten_npp = self.txt_npp.text().strip() or "Khách lẻ / Sale tự do"
        chuoi_sale = self.txt_sale.text().strip()
        san_pham = self.txt_san_pham_nhap.text().strip()
        sl_str = self.txt_so_luong.text().strip()
        gia_von_str = self.txt_gia_von.text().strip()
        gia_ban_str = self.txt_gia_ban.text().strip()

        if not chuoi_sale or not san_pham or not sl_str or not gia_von_str:
            QMessageBox.warning(self, "Lỗi", "Vui lòng điền đủ Tên Sản phẩm, Sale, Số lượng và Giá vốn!")
            return

        try:
            tong_so_luong = int(sl_str) * int(self.txt_quy_cach.text() or 1)
            gia_von = float(gia_von_str.replace(',', '.'))
            gia_ban = float(gia_ban_str.replace(',', '.')) if gia_ban_str else 0.0
            if tong_so_luong <= 0: raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Số lượng hoặc Giá tiền sai định dạng!")
            return

        ten_sale = chuoi_sale.split(" - ")[0].strip()
        
        thanh_cong, thong_bao = self.db.nghiep_vu_nhap_kho(ten_npp, ten_sale, san_pham, tong_so_luong, gia_von, ma_vach, gia_ban)
        
        if thanh_cong:
            self.bang_lich_su.insertRow(0)
            self.bang_lich_su.setItem(0, 0, QTableWidgetItem(QTime.currentTime().toString("HH:mm:ss")))
            self.bang_lich_su.setItem(0, 1, QTableWidgetItem(ma_vach))
            self.bang_lich_su.setItem(0, 2, QTableWidgetItem(san_pham))
            self.bang_lich_su.setItem(0, 3, QTableWidgetItem(str(tong_so_luong)))
            self.bang_lich_su.setItem(0, 4, QTableWidgetItem(str(gia_von)))

            self.txt_ma_vach.clear()
            self.txt_san_pham_nhap.clear()
            self.txt_so_luong.clear()
            self.txt_quy_cach.setText("1")
            self.txt_gia_von.clear()
            self.txt_gia_ban.clear()
            self.txt_ma_vach.setFocus()
            self.yeu_cau_lam_moi.emit()
        else:
            QMessageBox.critical(self, "Lỗi SQL", f"Lỗi: {thong_bao}")