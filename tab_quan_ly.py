from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QLineEdit, QComboBox, QPushButton, QMessageBox, QTableWidget, 
    QTableWidgetItem, QHeaderView, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIntValidator

class PopupSuaSP(QDialog):
    def __init__(self, db_manager, danh_sach_npp, sp_id, sp_ten, sp_ton, sp_npp, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.sp_id = sp_id
        self.setWindowTitle("Sửa Thông Tin Sản Phẩm")
        self.setFixedSize(450, 250)

        layout = QVBoxLayout(); form_layout = QFormLayout()
        css = "font-size: 16px; padding: 6px; border: 1px solid #ccc; border-radius: 4px;"

        self.txt_ten = QLineEdit(sp_ten); self.txt_ten.setStyleSheet(css)
        self.txt_ton = QLineEdit(str(sp_ton)); self.txt_ton.setStyleSheet(css); self.txt_ton.setValidator(QIntValidator(0, 100000, self))
        self.cb_npp = QComboBox(); self.cb_npp.setStyleSheet(css)
        self.cb_npp.addItem("Khách lẻ / Sale tự do"); self.cb_npp.addItems(danh_sach_npp)
        idx = self.cb_npp.findText(sp_npp)
        if idx >= 0: self.cb_npp.setCurrentIndex(idx)

        form_layout.addRow("Tên Sản Phẩm:", self.txt_ten); form_layout.addRow("Tồn Kho:", self.txt_ton); form_layout.addRow("Nhà Phân Phối:", self.cb_npp)
        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        btn_luu = QPushButton("💾 CẬP NHẬT"); btn_luu.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #f39c12; color: white; padding: 10px;"); btn_luu.clicked.connect(self.luu)
        btn_huy = QPushButton("Hủy"); btn_huy.setStyleSheet("font-size: 16px; padding: 10px;"); btn_huy.clicked.connect(self.reject)
        btn_layout.addWidget(btn_huy); btn_layout.addWidget(btn_luu)
        layout.addLayout(btn_layout); self.setLayout(layout)

    def luu(self):
        ten_moi = self.txt_ten.text().strip(); ton_moi = self.txt_ton.text().strip(); npp_moi = self.cb_npp.currentText()
        if not ten_moi or not ton_moi: return
        try:
            self.db.cap_nhat_san_pham(self.sp_id, ten_moi, int(ton_moi), npp_moi)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

class TabQuanLy(QWidget):
    yeu_cau_lam_moi = pyqtSignal()

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        lbl_tieu_de = QLabel("⚙️ QUẢN LÝ DANH MỤC HÀNG HÓA")
        lbl_tieu_de.setStyleSheet("font-size: 22px; font-weight: bold; color: #8e44ad; margin-bottom: 10px;"); lbl_tieu_de.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_tieu_de)

        btn_layout = QHBoxLayout(); btn_layout.addStretch()
        self.btn_sua = QPushButton("✏️ Sửa"); self.btn_sua.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #f39c12; color: white; padding: 8px 20px;")
        self.btn_xoa = QPushButton("❌ Xóa"); self.btn_xoa.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #c0392b; color: white; padding: 8px 20px;")
        btn_layout.addWidget(self.btn_sua); btn_layout.addWidget(self.btn_xoa); layout.addLayout(btn_layout)

        self.bang = QTableWidget(0, 4)
        self.bang.setHorizontalHeaderLabels(["ID", "Tên Sản Phẩm", "Tồn Kho", "Nhà Phân Phối"])
        self.bang.verticalHeader().setVisible(False); self.bang.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows); self.bang.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers); self.bang.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.bang.setStyleSheet("QTableWidget { font-size: 16px; outline: 0; } QHeaderView::section { background-color: #34495e; color: white; font-size: 16px; font-weight: bold; padding: 8px;} QTableWidget::item:selected { background-color: #d6eaf8; color: #2c3e50; font-weight: bold;}")
        
        header = self.bang.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents); header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents); header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.bang)
        
        self.btn_sua.clicked.connect(self.sua_sp)
        self.btn_xoa.clicked.connect(self.xoa_sp)
        self.setLayout(layout)
        self.tai_du_lieu()

    def tai_du_lieu(self):
        du_lieu = self.db.lay_danh_sach_quan_ly_sp()
        self.bang.setRowCount(len(du_lieu))
        for r, row in enumerate(du_lieu):
            item_id = QTableWidgetItem(str(row[0])); item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_ton = QTableWidgetItem(str(row[2])); item_ton.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.bang.setItem(r, 0, item_id); self.bang.setItem(r, 1, QTableWidgetItem(row[1]))
            self.bang.setItem(r, 2, item_ton); self.bang.setItem(r, 3, QTableWidgetItem(row[3] or "Khách lẻ / Sale tự do"))

    def sua_sp(self):
        row = self.bang.currentRow()
        if row < 0: return QMessageBox.warning(self, "Lỗi", "Vui lòng chọn 1 mặt hàng!")
        
        sp_id = int(self.bang.item(row, 0).text())
        sp_ten = self.bang.item(row, 1).text()
        sp_ton = int(self.bang.item(row, 2).text())
        sp_npp = self.bang.item(row, 3).text()

        popup = PopupSuaSP(self.db, self.db.lay_danh_sach_npp_hoat_dong(), sp_id, sp_ten, sp_ton, sp_npp, self)
        if popup.exec():
            QMessageBox.information(self, "Xong", "Đã cập nhật!")
            self.yeu_cau_lam_moi.emit()

    def xoa_sp(self):
        row = self.bang.currentRow()
        if row < 0: return QMessageBox.warning(self, "Lỗi", "Vui lòng chọn 1 mặt hàng!")
        sp_id = int(self.bang.item(row, 0).text())
        sp_ten = self.bang.item(row, 1).text()

        if QMessageBox.question(self, "Xóa", f"Xóa vĩnh viễn [{sp_ten}]?") == QMessageBox.StandardButton.Yes:
            tc, tb = self.db.nghiep_vu_xoa_san_pham(sp_id)
            if tc:
                QMessageBox.information(self, "Xong", f"Đã xóa {sp_ten}")
                self.yeu_cau_lam_moi.emit()
            else:
                QMessageBox.critical(self, "Lỗi", tb)