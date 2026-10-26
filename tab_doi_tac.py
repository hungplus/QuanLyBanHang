from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

class TabDoiTac(QWidget):
    yeu_cau_lam_moi = pyqtSignal()

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        lbl_tieu_de = QLabel("🤝 QUẢN LÝ ĐỐI TÁC & NHÂN VIÊN GIAO HÀNG")
        lbl_tieu_de.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;"); lbl_tieu_de.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_tieu_de)

        btn_layout = QHBoxLayout(); btn_layout.addStretch()
        self.btn_khoa = QPushButton("Khóa / Mở khóa")
        self.btn_khoa.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #34495e; color: white; padding: 8px 20px; border-radius: 4px;")
        self.btn_khoa.clicked.connect(self.khoa_doi_tac)
        btn_layout.addWidget(self.btn_khoa); layout.addLayout(btn_layout)

        self.bang = QTableWidget(0, 5)
        self.bang.setHorizontalHeaderLabels(["ID", "Nhà Phân Phối", "Tên Nhân Viên", "Số Điện Thoại", "Trạng Thái"])
        self.bang.verticalHeader().setVisible(False); self.bang.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows); self.bang.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers); self.bang.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.bang.setStyleSheet("QTableWidget { font-size: 16px; outline: 0; } QHeaderView::section { background-color: #7f8c8d; color: white; font-size: 16px; font-weight: bold; padding: 8px;} QTableWidget::item:selected { background-color: #d6eaf8; color: #2c3e50; font-weight: bold;}")
        
        header = self.bang.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents); header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        for col in range(1, 4): header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.bang)
        self.setLayout(layout)
        self.tai_du_lieu()

    def tai_du_lieu(self):
        du_lieu = self.db.lay_danh_sach_doi_tac()
        self.bang.setRowCount(len(du_lieu))
        for r, row in enumerate(du_lieu):
            item_id = QTableWidgetItem(str(row[0])); item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_sdt = QTableWidgetItem(row[3]); item_sdt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            tt_str = "🟢 Đang làm" if row[4] == 1 else "🔴 Đã nghỉ"
            item_tt = QTableWidgetItem(tt_str); item_tt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if row[4] == 0: item_tt.setForeground(QColor("#c0392b"))

            self.bang.setItem(r, 0, item_id); self.bang.setItem(r, 1, QTableWidgetItem(row[1])); self.bang.setItem(r, 2, QTableWidgetItem(row[2]))
            self.bang.setItem(r, 3, item_sdt); self.bang.setItem(r, 4, item_tt)

    def khoa_doi_tac(self):
        row = self.bang.currentRow()
        if row < 0: return QMessageBox.warning(self, "Lỗi", "Vui lòng chọn 1 đối tác!")
        
        npp_id = int(self.bang.item(row, 0).text())
        ten_sale = self.bang.item(row, 2).text()
        
        tt_hien_tai = self.db.lay_trang_thai_doi_tac(npp_id)
        tt_moi = 0 if tt_hien_tai == 1 else 1
        hanh_dong = "khóa" if tt_moi == 0 else "mở khóa"

        if QMessageBox.question(self, "Xác nhận", f"Xác nhận {hanh_dong} [{ten_sale}]?") == QMessageBox.StandardButton.Yes:
            self.db.cap_nhat_trang_thai_doi_tac(npp_id, tt_moi)
            QMessageBox.information(self, "Xong", f"Đã cập nhật trạng thái [{ten_sale}].")
            self.yeu_cau_lam_moi.emit()