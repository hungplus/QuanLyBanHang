from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, 
    QHeaderView, QDialog, QFormLayout, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

# ==============================================================
# POPUP 1: SỬA THÔNG TIN ĐỐI TÁC VÀ ĐỔI TRẠNG THÁI
# ==============================================================
class PopupSuaDoiTac(QDialog):
    def __init__(self, db_manager, dt_id, ten_npp, ten_sale, sdt, trang_thai, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.dt_id = dt_id
        self.setWindowTitle("Sửa Thông Tin & Trạng Thái")
        self.setFixedSize(400, 250)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        layout = QVBoxLayout()
        form_layout = QFormLayout()
        css_input = "font-size: 16px; padding: 6px; border: 1px solid #ccc; border-radius: 4px;"

        self.txt_ten_npp = QLineEdit(ten_npp)
        self.txt_ten_npp.setStyleSheet(css_input)

        self.txt_ten_sale = QLineEdit(ten_sale)
        self.txt_ten_sale.setStyleSheet(css_input)

        self.txt_sdt = QLineEdit(sdt)
        self.txt_sdt.setStyleSheet(css_input)

        # Nút gạt trạng thái
        self.cb_trang_thai = QComboBox()
        self.cb_trang_thai.setStyleSheet(css_input)
        self.cb_trang_thai.addItem("🟢 Đang hoạt động", 1)
        self.cb_trang_thai.addItem("🔴 Đã nghỉ / Ngừng nhập", 0)
        
        # Đặt lại đúng trạng thái cũ
        if trang_thai == 0:
            self.cb_trang_thai.setCurrentIndex(1)

        form_layout.addRow("Công ty/Đại lý:", self.txt_ten_npp)
        form_layout.addRow("Tên Nhân viên:", self.txt_ten_sale)
        form_layout.addRow("Số điện thoại:", self.txt_sdt)
        form_layout.addRow("Trạng thái:", self.cb_trang_thai)
        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        btn_luu = QPushButton("💾 CẬP NHẬT")
        btn_luu.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #f39c12; color: white; padding: 10px; border-radius: 4px;")
        btn_luu.clicked.connect(self.xu_ly_luu)
        
        btn_huy = QPushButton("Hủy")
        btn_huy.setStyleSheet("font-size: 16px; padding: 10px; border-radius: 4px;")
        btn_huy.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_huy)
        btn_layout.addWidget(btn_luu)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def xu_ly_luu(self):
        npp_moi = self.txt_ten_npp.text().strip() or "Khách lẻ / Sale tự do"
        sale_moi = self.txt_ten_sale.text().strip()
        sdt_moi = self.txt_sdt.text().strip()
        tt_moi = self.cb_trang_thai.currentData()

        if not sale_moi:
            QMessageBox.warning(self, "Lỗi", "Tên nhân viên không được để trống!")
            return

        try:
            # Sử dụng con trỏ database trực tiếp để update
            self.db.cursor.execute(
                "UPDATE Nha_Phan_Phoi SET ten_npp = ?, ten_sale = ?, sdt_sale = ?, trang_thai = ? WHERE id = ?",
                (npp_moi, sale_moi, sdt_moi, tt_moi, self.dt_id)
            )
            self.db.conn.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi SQL", f"Không thể cập nhật: {e}")


# ==============================================================
# POPUP 2: XEM DANH SÁCH SẢN PHẨM CỦA ĐỐI TÁC
# ==============================================================
class PopupXemSanPham(QDialog):
    def __init__(self, db_manager, npp_id, ten_sale, ten_npp, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"📦 Hàng hóa từ: {ten_sale} ({ten_npp})")
        self.setFixedSize(600, 400)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        layout = QVBoxLayout()
        
        bang_sp = QTableWidget()
        bang_sp.setColumnCount(2)
        bang_sp.setHorizontalHeaderLabels(["Tên Sản Phẩm", "Tồn Kho Hiện Tại"])
        bang_sp.verticalHeader().setVisible(False)
        bang_sp.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        bang_sp.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        bang_sp.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        bang_sp.setStyleSheet("""
            QTableWidget { font-size: 16px; gridline-color: #bdc3c7; }
            QHeaderView::section { background-color: #34495e; color: white; font-size: 16px; font-weight: bold; padding: 6px; }
        """)
        bang_sp.setAlternatingRowColors(True)
        bang_sp.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        bang_sp.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

        try:
            db_manager.cursor.execute("SELECT ten_sp, ton_kho FROM San_Pham WHERE id_npp = ?", (npp_id,))
            du_lieu = db_manager.cursor.fetchall()
            
            if not du_lieu:
                layout.addWidget(QLabel("<i>(Chưa có mặt hàng nào nhập từ người này)</i>"))
            else:
                bang_sp.setRowCount(len(du_lieu))
                for r, row in enumerate(du_lieu):
                    bang_sp.setItem(r, 0, QTableWidgetItem(row[0]))
                    item_ton = QTableWidgetItem(str(row[1]))
                    item_ton.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    # Đổi màu đỏ nếu hết hàng
                    if row[1] == 0:
                        item_ton.setForeground(QColor("#c0392b"))
                        
                    bang_sp.setItem(r, 1, item_ton)
                layout.addWidget(bang_sp)
        except Exception as e:
            layout.addWidget(QLabel(f"Lỗi tải dữ liệu: {e}"))
            
        self.setLayout(layout)


# ==============================================================
# GIAO DIỆN CHÍNH TAB ĐỐI TÁC
# ==============================================================
class TabDoiTac(QWidget):
    yeu_cau_lam_moi = pyqtSignal()

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        lbl_tieu_de = QLabel("🤝 QUẢN LÝ DANH BẠ ĐỐI TÁC")
        lbl_tieu_de.setStyleSheet("font-size: 25px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        lbl_tieu_de.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_tieu_de)

        # Thanh công cụ: Tìm kiếm & Lọc & Nút Sửa
        toolbar_layout = QHBoxLayout()
        
        self.txt_tim_kiem = QLineEdit()
        self.txt_tim_kiem.setPlaceholderText("🔍 Gõ tên Đại lý, Tên Sale hoặc SĐT để tìm nhanh...")
        self.txt_tim_kiem.setStyleSheet("font-size: 22px; padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
        self.txt_tim_kiem.textChanged.connect(self.loc_du_lieu)
        
        self.cb_loc_trang_thai = QComboBox()
        self.cb_loc_trang_thai.addItems(["🟢 Đang hoạt động", "🔴 Đã nghỉ", "Trang thái: Tất cả"])
        self.cb_loc_trang_thai.setStyleSheet("font-size: 22px; padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
        self.cb_loc_trang_thai.currentIndexChanged.connect(self.loc_du_lieu)
        
        self.btn_sua = QPushButton("✏️ Sửa thông tin")
        self.btn_sua.setStyleSheet("""
            QPushButton { font-size: 22px; font-weight: bold; background-color: #f39c12; color: white; padding: 8px 20px; border-radius: 4px;}
            QPushButton:hover { background-color: #e67e22; }
        """)
        self.btn_sua.clicked.connect(self.mo_popup_sua)

        toolbar_layout.addWidget(self.txt_tim_kiem, stretch=2)
        toolbar_layout.addWidget(self.cb_loc_trang_thai, stretch=1)
        toolbar_layout.addWidget(self.btn_sua)
        layout.addLayout(toolbar_layout)

        # Bảng hiển thị
        self.bang = QTableWidget()
        self.bang.setColumnCount(4) # Cột 0 chứa ID ẩn, hiển thị 3 cột còn lại
        self.bang.setHorizontalHeaderLabels(["ID", "Nhà Phân Phối", "Tên Nhân Viên", "Số Điện Thoại"])
        
        # Ẩn cột ID và Cột số thứ tự ngoài cùng
        self.bang.setColumnHidden(0, True)
        self.bang.verticalHeader().setVisible(False)
        
        # Bật tính năng Sắp xếp khi click vào tiêu đề
        self.bang.setSortingEnabled(True)
        
        self.bang.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.bang.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.bang.setFocusPolicy(Qt.FocusPolicy.NoFocus) 
        self.bang.setStyleSheet("""
            QTableWidget { font-size: 20px; gridline-color: #bdc3c7; outline: 0; } 
            QHeaderView::section { background-color: #7f8c8d; color: white; font-size: 16px; font-weight: bold; padding: 8px; border: 1px solid #bdc3c7;}
            QTableWidget::item:selected { background-color: #d6eaf8; color: #2c3e50; font-weight: bold;}
        """)
        self.bang.setAlternatingRowColors(True)
        
        header = self.bang.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        # Bắt sự kiện Nhấp đúp chuột để xem hàng hóa
        self.bang.cellDoubleClicked.connect(self.xem_san_pham)
        
        layout.addWidget(self.bang)
        
        # Hướng dẫn nhỏ bên dưới
        huong_dan = QLabel("💡 <i>Gợi ý: Nhấp đúp chuột vào một dòng để xem các mặt hàng đã nhập từ người này. Click vào tiêu đề cột để sắp xếp A-Z.</i>")
        huong_dan.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        layout.addWidget(huong_dan)

        self.setLayout(layout)
        self.tai_du_lieu()

    def tai_du_lieu(self):
        # Tạm tắt sắp xếp lúc nạp dữ liệu để tránh lỗi logic
        self.bang.setSortingEnabled(False)
        
        self.db.cursor.execute("SELECT id, ten_npp, ten_sale, sdt_sale, trang_thai FROM Nha_Phan_Phoi ORDER BY trang_thai DESC, id DESC")
        du_lieu = self.db.cursor.fetchall()
        
        self.bang.setRowCount(len(du_lieu))
        for r, row in enumerate(du_lieu):
            dt_id, ten_npp, ten_sale, sdt, trang_thai = row
            
            # Cột 0: ID (Ẩn) - Ta nhét thêm dữ liệu trang_thai vào UserRole để lúc lọc gọi ra dùng
            item_id = QTableWidgetItem()
            item_id.setData(Qt.ItemDataRole.EditRole, dt_id) # Dùng EditRole để sắp xếp số đúng chuẩn
            item_id.setData(Qt.ItemDataRole.UserRole, trang_thai)
            self.bang.setItem(r, 0, item_id)
            
            self.bang.setItem(r, 1, QTableWidgetItem(ten_npp))
            self.bang.setItem(r, 2, QTableWidgetItem(ten_sale))
            
            item_sdt = QTableWidgetItem(sdt)
            item_sdt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.bang.setItem(r, 3, item_sdt)
            
            # Làm mờ chữ đi nếu đã nghỉ
            if trang_thai == 0:
                mau_xam = QColor("#95a5a6")
                self.bang.item(r, 1).setForeground(mau_xam)
                self.bang.item(r, 2).setForeground(mau_xam)
                self.bang.item(r, 3).setForeground(mau_xam)

        # Bật lại tính năng sắp xếp
        self.bang.setSortingEnabled(True)
        self.loc_du_lieu()

    def loc_du_lieu(self):
        tu_khoa = self.txt_tim_kiem.text().lower()
        kieu_loc = self.cb_loc_trang_thai.currentIndex() # 0: Đang làm, 1: Đã nghỉ, 2: Tất cả
        
        tt_can_tim = 1 if kieu_loc == 0 else (0 if kieu_loc == 1 else -1)

        for r in range(self.bang.rowCount()):
            # Lấy các giá trị
            trang_thai = self.bang.item(r, 0).data(Qt.ItemDataRole.UserRole)
            ten_npp = self.bang.item(r, 1).text().lower()
            ten_sale = self.bang.item(r, 2).text().lower()
            sdt = self.bang.item(r, 3).text().lower()
            
            # Kiểm tra trạng thái
            khop_trang_thai = (tt_can_tim == -1) or (trang_thai == tt_can_tim)
            # Kiểm tra từ khóa
            khop_tu_khoa = (tu_khoa in ten_npp) or (tu_khoa in ten_sale) or (tu_khoa in sdt)
            
            # Nếu thỏa mãn cả 2 thì hiện, không thì ẩn
            self.bang.setRowHidden(r, not (khop_trang_thai and khop_tu_khoa))

    def mo_popup_sua(self):
        row_dang_chon = self.bang.currentRow()
        if row_dang_chon < 0:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn 1 đối tác trong bảng để sửa thông tin!")
            return
            
        dt_id = self.bang.item(row_dang_chon, 0).data(Qt.ItemDataRole.EditRole)
        trang_thai = self.bang.item(row_dang_chon, 0).data(Qt.ItemDataRole.UserRole)
        ten_npp = self.bang.item(row_dang_chon, 1).text()
        ten_sale = self.bang.item(row_dang_chon, 2).text()
        sdt = self.bang.item(row_dang_chon, 3).text()

        popup = PopupSuaDoiTac(self.db, dt_id, ten_npp, ten_sale, sdt, trang_thai, self)
        if popup.exec():
            self.tai_du_lieu()
            self.yeu_cau_lam_moi.emit()
            QMessageBox.information(self, "Thành công", "Đã cập nhật thông tin đối tác!")

    def xem_san_pham(self, row, column):
        dt_id = self.bang.item(row, 0).data(Qt.ItemDataRole.EditRole)
        ten_npp = self.bang.item(row, 1).text()
        ten_sale = self.bang.item(row, 2).text()
        
        popup = PopupXemSanPham(self.db, dt_id, ten_sale, ten_npp, self)
        popup.exec()