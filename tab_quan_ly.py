from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QFormLayout, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIntValidator, QColor

# ==============================================================
# CỬA SỔ POPUP SỬA THÔNG TIN SẢN PHẨM
# ==============================================================
class PopupSuaSP(QDialog):
    def __init__(self, db_manager, sp_id, sp_ten, sp_ton, id_npp_hien_tai, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.sp_id = sp_id
        self.setWindowTitle("Sửa Thông Tin Sản Phẩm")
        self.setMinimumSize(550, 350)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet("QLabel { font-size: 20px; font-weight: bold; color: #2c3e50; }")

        layout = QVBoxLayout()
        form_layout = QFormLayout()
        css_input = "font-size: 22px; padding: 10px; border: 2px solid #ccc; border-radius: 6px;"

        self.txt_ten_sp = QLineEdit(sp_ten)
        self.txt_ten_sp.setStyleSheet(css_input)

        self.txt_ton_kho = QLineEdit(str(sp_ton))
        self.txt_ton_kho.setStyleSheet(css_input)
        self.txt_ton_kho.setValidator(QIntValidator(0, 100000, self))

        self.cb_npp = QComboBox()
        self.cb_npp.setStyleSheet(css_input)
        
        # Nạp dữ liệu NPP kết hợp Tên Sale để chọn chính xác
        self.cb_npp.addItem("Khách lẻ / Sale tự do", None)
        
        self.db.cursor.execute("SELECT id, ten_npp, ten_sale FROM Nha_Phan_Phoi WHERE trang_thai = 1")
        danh_sach_npp = self.db.cursor.fetchall()
        
        chi_muc_chon = 0
        for idx, row in enumerate(danh_sach_npp, start=1):
            npp_id, npp_ten, sale_ten = row
            chuoi_hien_thi = f"{npp_ten} - {sale_ten}" if sale_ten else npp_ten
            self.cb_npp.addItem(chuoi_hien_thi, npp_id) # Lưu ngầm ID vào combobox
            
            # Trỏ đúng về người bán hiện tại
            if npp_id == id_npp_hien_tai:
                chi_muc_chon = idx
                
        self.cb_npp.setCurrentIndex(chi_muc_chon)

        form_layout.addRow("Tên Sản Phẩm:", self.txt_ten_sp)
        form_layout.addRow("Tồn Kho Hiện Tại:", self.txt_ton_kho)
        form_layout.addRow("Đổi Người Bán:", self.cb_npp)
        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        btn_luu = QPushButton("💾 CẬP NHẬT")
        btn_luu.setStyleSheet("""
            QPushButton {font-size: 22px; font-weight: bold; background-color: #f39c12; color: white; padding: 12px 20px; border: 2px solid #e67e22; border-radius: 6px;}
            QPushButton:hover {background-color: #e67e22;}
        """)
        btn_luu.clicked.connect(self.xu_ly_luu)

        btn_huy = QPushButton("Hủy")
        btn_huy.setStyleSheet("""
            QPushButton {font-size: 22px; font-weight: bold; background-color: #ecf0f1; color: #2c3e50; padding: 12px 20px; border: 2px solid #bdc3c7; border-radius: 6px;}
            QPushButton:hover {background-color: #bdc3c7;}
        """)
        btn_huy.clicked.connect(self.reject)

        btn_layout.addWidget(btn_huy)
        btn_layout.addWidget(btn_luu)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def xu_ly_luu(self):
        ten_moi = self.txt_ten_sp.text().strip()
        ton_moi = self.txt_ton_kho.text().strip()
        id_npp_moi = self.cb_npp.currentData() # Lấy ID ngầm đã lưu

        if not ten_moi or not ton_moi:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đủ Tên và Tồn kho!")
            return

        try:
            self.db.cursor.execute(
                "UPDATE San_Pham SET ten_sp = ?, ton_kho = ?, id_npp = ? WHERE id = ?",
                (ten_moi, int(ton_moi), id_npp_moi, self.sp_id)
            )
            self.db.conn.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật: {e}")

# ==============================================================
# GIAO DIỆN CHÍNH TAB QUẢN LÝ KHO
# ==============================================================
class TabQuanLy(QWidget):
    yeu_cau_lam_moi = pyqtSignal()

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        lbl_tieu_de = QLabel("⚙️ QUẢN LÝ DANH MỤC HÀNG HÓA")
        lbl_tieu_de.setStyleSheet("font-size: 25px; font-weight: bold; color: #8e44ad; margin-bottom: 10px;")
        lbl_tieu_de.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_tieu_de)

        # Thanh công cụ: Đã căn chỉnh lại kích thước dài hơn
        toolbar_layout = QHBoxLayout()

        self.txt_tim_kiem = QLineEdit()
        self.txt_tim_kiem.setPlaceholderText("🔍 Tìm theo Tên SP hoặc Tên Người Bán...")
        self.txt_tim_kiem.setStyleSheet("font-size: 22px; padding: 12px; border: 1px solid #ccc; border-radius: 4px;")
        self.txt_tim_kiem.setMinimumWidth(350)
        self.txt_tim_kiem.textChanged.connect(self.loc_du_lieu)

        self.btn_sua_sp = QPushButton("✏️ Sửa thông tin")
        self.btn_sua_sp.setMinimumWidth(150)
        self.btn_sua_sp.setStyleSheet("""
            QPushButton {font-size: 22px; font-weight: bold; background-color: #f39c12; color: white; padding: 12px 20px; border-radius: 4px;}
            QPushButton:hover {background-color: #e67e22;}
        """)
        self.btn_sua_sp.clicked.connect(self.mo_popup_sua_sp)

        self.btn_xoa_sp = QPushButton("❌ Xóa sản phẩm")
        self.btn_xoa_sp.setMinimumWidth(150)
        self.btn_xoa_sp.setStyleSheet("""
            QPushButton {font-size: 22px; font-weight: bold; background-color: #c0392b; color: white; padding: 12px 20px; border-radius: 4px;}
            QPushButton:hover {background-color: #a93226;}
        """)
        self.btn_xoa_sp.clicked.connect(self.xu_ly_xoa_sp)

        toolbar_layout.addWidget(self.txt_tim_kiem, stretch=3)
        toolbar_layout.addWidget(self.btn_sua_sp, stretch=1)
        toolbar_layout.addWidget(self.btn_xoa_sp, stretch=1)
        layout.addLayout(toolbar_layout)

        # Bảng dữ liệu tổng hợp
        self.bang_quan_ly = QTableWidget()
        self.bang_quan_ly.setColumnCount(6)
        self.bang_quan_ly.setHorizontalHeaderLabels(["ID", "STT", "Tên Sản Phẩm", "Tồn Kho", "Người Bán", "Số Điện Thoại"])
        
        self.bang_quan_ly.setColumnHidden(0, True)
        self.bang_quan_ly.verticalHeader().setVisible(False)
        self.bang_quan_ly.setSortingEnabled(True)
        self.bang_quan_ly.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.bang_quan_ly.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.bang_quan_ly.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.bang_quan_ly.setStyleSheet("""
            QTableWidget { font-size: 24px; gridline-color: #bdc3c7; outline: 0;} 
            QHeaderView::section { background-color: #34495e; color: white; font-size: 22px; font-weight: bold; padding: 8px; border: 1px solid #bdc3c7;}
            QTableWidget::item:selected { background-color: #d6eaf8; color: #2c3e50; font-weight: bold;}
        """)
        self.bang_quan_ly.setAlternatingRowColors(True)

        header = self.bang_quan_ly.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.bang_quan_ly)
        self.setLayout(layout)
        self.tai_du_lieu()

    def tao_item_so(self, giatri):
        item = QTableWidgetItem()
        item.setData(Qt.ItemDataRole.EditRole, giatri)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def tai_du_lieu(self):
        self.bang_quan_ly.setSortingEnabled(False)
        
        self.db.cursor.execute('''
            SELECT sp.id, sp.ten_sp, sp.ton_kho, npp.ten_npp, npp.ten_sale, npp.sdt_sale, sp.id_npp
            FROM San_Pham sp
            LEFT JOIN Nha_Phan_Phoi npp ON sp.id_npp = npp.id
            ORDER BY sp.id DESC
        ''')
        du_lieu = self.db.cursor.fetchall()
        self.bang_quan_ly.setRowCount(len(du_lieu))

        for r, row in enumerate(du_lieu):
            sp_id, ten_sp, ton_kho, ten_npp, ten_sale, sdt_sale, id_npp = row
            
            nguoi_ban = ten_sale if ten_sale else (ten_npp or "Khách lẻ / Sale tự do")
            sdt = sdt_sale if sdt_sale else ""

            # ID CSDL + ID Nhà phân phối lưu ngầm vào cột 0
            item_id = self.tao_item_so(sp_id)
            item_id.setData(Qt.ItemDataRole.UserRole, id_npp)
            self.bang_quan_ly.setItem(r, 0, item_id)
            
            self.bang_quan_ly.setItem(r, 1, self.tao_item_so(r + 1))
            self.bang_quan_ly.setItem(r, 2, QTableWidgetItem(ten_sp))

            item_ton = self.tao_item_so(ton_kho)
            if ton_kho == 0:
                item_ton.setForeground(QColor("#c0392b"))
            self.bang_quan_ly.setItem(r, 3, item_ton)
            self.bang_quan_ly.setItem(r, 4, QTableWidgetItem(nguoi_ban))
            
            item_sdt = QTableWidgetItem(sdt)
            item_sdt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.bang_quan_ly.setItem(r, 5, item_sdt)

        self.bang_quan_ly.setSortingEnabled(True)
        self.loc_du_lieu() 

    def loc_du_lieu(self):
        tu_khoa = self.txt_tim_kiem.text().lower()
        for r in range(self.bang_quan_ly.rowCount()):
            ten_sp = self.bang_quan_ly.item(r, 2).text().lower()
            nguoi_ban = self.bang_quan_ly.item(r, 4).text().lower()
            khop = (tu_khoa in ten_sp) or (tu_khoa in nguoi_ban)
            self.bang_quan_ly.setRowHidden(r, not khop)

    def mo_popup_sua_sp(self):
        row_dang_chon = self.bang_quan_ly.currentRow()
        if row_dang_chon < 0:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng click chọn 1 mặt hàng trong bảng để sửa!")
            return

        sp_id = self.bang_quan_ly.item(row_dang_chon, 0).data(Qt.ItemDataRole.EditRole)
        id_npp_hien_tai = self.bang_quan_ly.item(row_dang_chon, 0).data(Qt.ItemDataRole.UserRole)
        sp_ten = self.bang_quan_ly.item(row_dang_chon, 2).text()
        sp_ton = self.bang_quan_ly.item(row_dang_chon, 3).data(Qt.ItemDataRole.EditRole)

        popup = PopupSuaSP(self.db, sp_id, sp_ten, sp_ton, id_npp_hien_tai, self)

        if popup.exec():
            self.tai_du_lieu()
            self.yeu_cau_lam_moi.emit()
            QMessageBox.information(self, "Thành Công", "Đã cập nhật thông tin mặt hàng!")

    def xu_ly_xoa_sp(self):
        row_dang_chon = self.bang_quan_ly.currentRow()
        if row_dang_chon < 0:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng click chọn 1 mặt hàng trong bảng để xóa!")
            return

        sp_id = self.bang_quan_ly.item(row_dang_chon, 0).data(Qt.ItemDataRole.EditRole)
        sp_ten = self.bang_quan_ly.item(row_dang_chon, 2).text()

        traloi = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa vĩnh viễn mặt hàng:\n[{sp_ten}]\nkhỏi hệ thống không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if traloi == QMessageBox.StandardButton.Yes:
            try:
                self.db.cursor.execute("DELETE FROM Lich_Su_Nhap WHERE id_sp = ?", (sp_id,))
                self.db.cursor.execute("DELETE FROM San_Pham WHERE id = ?", (sp_id,))
                self.db.conn.commit()

                self.tai_du_lieu()
                self.yeu_cau_lam_moi.emit()
                QMessageBox.information(self, "Đã xóa", f"Đã xóa [{sp_ten}] thành công!")
            except Exception as e:
                self.db.conn.rollback()
                # Xử lý riêng lỗi Foreign Key constraint
                if "FOREIGN KEY" in str(e).upper():
                    QMessageBox.warning(self, "Không thể xóa vĩnh viễn", 
                        f"Sản phẩm [{sp_ten}] đã phát sinh giao dịch bán hàng (tồn tại trong hóa đơn cũ).\n\n"
                        "Hệ thống khóa chức năng xóa để bảo vệ sổ sách tài chính không bị sai lệch.\n\n"
                        "💡 Gợi ý: Hãy bấm nút 'Sửa thông tin', cập nhật Tồn kho về 0 và đổi tên thành '[Ngừng kinh doanh] {sp_ten}'."
                    )
                else:
                    QMessageBox.critical(self, "Lỗi", f"Không thể xóa: {e}")