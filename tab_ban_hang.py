from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QCompleter, 
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal, QStringListModel
from PyQt6.QtGui import QIntValidator

class TabBanHang(QWidget):
    yeu_cau_lam_moi = pyqtSignal()

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.tong_tien_hoa_don = 0
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        lbl_tieu_de = QLabel("🛒 BÁN HÀNG & THANH TOÁN (POS)")
        lbl_tieu_de.setStyleSheet("font-size: 22px; font-weight: bold; color: #2980b9; margin-bottom: 10px;")
        lbl_tieu_de.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_tieu_de)

        # Khu vực nhập hàng vào giỏ
        form_layout = QHBoxLayout()
        css_input = "font-size: 18px; padding: 8px; border: 1px solid #7f8c8d; border-radius: 4px;"
        
        self.txt_sp = QLineEdit()
        self.txt_sp.setPlaceholderText("Gõ tên sản phẩm...")
        self.txt_sp.setStyleSheet(css_input)
        self.completer = QCompleter([], self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.txt_sp.setCompleter(self.completer)

        self.txt_sl = QLineEdit("1")
        self.txt_sl.setFixedWidth(80)
        self.txt_sl.setStyleSheet(css_input)
        self.txt_sl.setValidator(QIntValidator(1, 10000, self))
        self.txt_sl.returnPressed.connect(self.them_vao_gio)

        btn_them = QPushButton("➕ Thêm vào giỏ")
        btn_them.setStyleSheet("font-size: 18px; font-weight: bold; background-color: #f1c40f; padding: 8px 15px; border-radius: 4px;")
        btn_them.clicked.connect(self.them_vao_gio)

        form_layout.addWidget(QLabel("Sản phẩm:", styleSheet="font-size: 18px; font-weight:bold;"))
        form_layout.addWidget(self.txt_sp, stretch=1)
        form_layout.addWidget(QLabel("SL:", styleSheet="font-size: 18px; font-weight:bold;"))
        form_layout.addWidget(self.txt_sl)
        form_layout.addWidget(btn_them)
        layout.addLayout(form_layout)

        # Bảng giỏ hàng
        self.bang = QTableWidget(0, 6)
        self.bang.setHorizontalHeaderLabels(["ID", "Tên Sản Phẩm", "Đơn Giá", "Số Lượng", "Thành Tiền", "Xóa"])
        self.bang.verticalHeader().setVisible(False)
        self.bang.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.bang.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.bang.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.bang.setStyleSheet("QTableWidget { font-size: 16px; outline: 0; } QHeaderView::section { background-color: #34495e; color: white; font-size: 16px; font-weight: bold; padding: 8px;}")
        
        header = self.bang.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for col in range(2, 6): header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.bang)

        # Khu vực tổng tiền và thanh toán
        bottom_layout = QHBoxLayout()
        self.lbl_tong_tien = QLabel("Tổng tiền: 0 đ")
        self.lbl_tong_tien.setStyleSheet("font-size: 24px; font-weight: bold; color: #c0392b;")
        
        btn_thanh_toan = QPushButton("💳 XÁC NHẬN THANH TOÁN")
        btn_thanh_toan.setStyleSheet("font-size: 20px; font-weight: bold; background-color: #27ae60; color: white; padding: 15px 30px; border-radius: 8px;")
        btn_thanh_toan.clicked.connect(self.thanh_toan)

        bottom_layout.addWidget(self.lbl_tong_tien)
        bottom_layout.addStretch()
        bottom_layout.addWidget(btn_thanh_toan)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)
        self.tai_du_lieu()

    def tai_du_lieu(self):
        ds_sp = self.db.lay_danh_sach_ten_san_pham()
        self.completer.setModel(QStringListModel(ds_sp))

    def them_vao_gio(self):
        ten_sp = self.txt_sp.text().strip()
        sl_nhap = int(self.txt_sl.text() or 1)
        if not ten_sp: return

        thong_tin = self.db.lay_thong_tin_sp_ban_hang(ten_sp)
        if not thong_tin:
            return QMessageBox.warning(self, "Lỗi", "Không tìm thấy sản phẩm!")
        
        id_sp, gia_ban, ton_kho = thong_tin

        # Kiểm tra trùng lặp trong giỏ hàng
        so_luong_da_co = 0
        dong_ton_tai = -1
        for r in range(self.bang.rowCount()):
            if int(self.bang.item(r, 0).text()) == id_sp:
                so_luong_da_co = int(self.bang.item(r, 3).text())
                dong_ton_tai = r
                break

        tong_sl_muon_mua = so_luong_da_co + sl_nhap
        if ton_kho < tong_sl_muon_mua:
            return QMessageBox.warning(self, "Hết hàng", f"Trong kho chỉ còn {ton_kho} đơn vị!")

        thanh_tien = tong_sl_muon_mua * gia_ban

        if dong_ton_tai >= 0:
            self.bang.item(dong_ton_tai, 3).setText(str(tong_sl_muon_mua))
            self.bang.item(dong_ton_tai, 4).setText(str(thanh_tien))
        else:
            r = self.bang.rowCount()
            self.bang.insertRow(r)
            
            item_id = QTableWidgetItem(str(id_sp)); item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_gia = QTableWidgetItem(str(gia_ban)); item_gia.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_sl = QTableWidgetItem(str(sl_nhap)); item_sl.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_tt = QTableWidgetItem(str(thanh_tien)); item_tt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.bang.setItem(r, 0, item_id)
            self.bang.setItem(r, 1, QTableWidgetItem(ten_sp))
            self.bang.setItem(r, 2, item_gia)
            self.bang.setItem(r, 3, item_sl)
            self.bang.setItem(r, 4, item_tt)

            btn_xoa = QPushButton("❌")
            btn_xoa.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
            btn_xoa.clicked.connect(self.xoa_khoi_gio)
            self.bang.setCellWidget(r, 5, btn_xoa)

        self.txt_sp.clear()
        self.txt_sl.setText("1")
        self.txt_sp.setFocus()
        self.tinh_tong_tien()

    def xoa_khoi_gio(self):
        btn = self.sender()
        if btn:
            for r in range(self.bang.rowCount()):
                if self.bang.cellWidget(r, 5) == btn:
                    self.bang.removeRow(r)
                    self.tinh_tong_tien()
                    break

    def tinh_tong_tien(self):
        self.tong_tien_hoa_don = sum(int(self.bang.item(r, 4).text()) for r in range(self.bang.rowCount()))
        self.lbl_tong_tien.setText(f"Tổng tiền: {self.tong_tien_hoa_don:,.0f} đ")

    def thanh_toan(self):
        if self.bang.rowCount() == 0: return

        danh_sach_hang = []
        for r in range(self.bang.rowCount()):
            danh_sach_hang.append({
                'id_sp': int(self.bang.item(r, 0).text()),
                'so_luong': int(self.bang.item(r, 3).text()),
                'gia_ban': int(self.bang.item(r, 2).text()),
                'thanh_tien': int(self.bang.item(r, 4).text())
            })

        thanh_cong, thong_bao = self.db.nghiep_vu_ban_hang(self.tong_tien_hoa_don, danh_sach_hang)
        
        if thanh_cong:
            QMessageBox.information(self, "Hoàn tất", f"Đã thanh toán thành công!\n{self.lbl_tong_tien.text()}")
            self.bang.setRowCount(0)
            self.tinh_tong_tien()
            self.yeu_cau_lam_moi.emit()
        else:
            QMessageBox.critical(self, "Lỗi", thong_bao)