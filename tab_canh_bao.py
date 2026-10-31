from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QHeaderView, QApplication, QMessageBox
from PyQt6.QtCore import Qt

class TabCanhBao(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        
        lbl_tieu_de = QLabel("⚠️ DANH SÁCH MẶT HÀNG SẮP HẾT CẦN GỌI NHẬP THÊM")
        # Phóng to tiêu đề lên 28px
        lbl_tieu_de.setStyleSheet("font-size: 28px; font-weight: bold; color: #c0392b;")
        
        btn_copy_ds = QPushButton("📋 Copy danh sách")
        # Phóng to nút bấm lên 22px, bo góc và đệm rộng hơn
        btn_copy_ds.setStyleSheet("""
            QPushButton {font-size: 22px; font-weight: bold; background-color: #3498db; color: white; padding: 12px 20px; border-radius: 6px;}
            QPushButton:hover {background-color: #2980b9;}
        """)
        btn_copy_ds.clicked.connect(self.copy_danh_sach)
        
        top_layout.addWidget(lbl_tieu_de)
        top_layout.addStretch()
        top_layout.addWidget(btn_copy_ds)
        layout.addLayout(top_layout)

        self.bang = QTableWidget(0, 6)
        self.bang.setHorizontalHeaderLabels(["STT", "Tên Sản Phẩm", "Tồn Kho", "Nhà Phân Phối", "Người Liên Hệ", "Số Điện Thoại"])
        self.bang.verticalHeader().setVisible(False)
        self.bang.verticalHeader().setDefaultSectionSize(55)
        self.bang.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Tăng font chữ header lên 22px, chữ trong bảng lên 24px
        self.bang.setStyleSheet("""
            QTableWidget { font-size: 24px; gridline-color: #bdc3c7; outline: 0;} 
            QHeaderView::section { background-color: #34495e; color: white; font-size: 22px; font-weight: bold; padding: 12px; border: 1px solid #bdc3c7;}
        """)
        self.bang.setAlternatingRowColors(True)

        # ĐIỀU CHỈNH LẠI KÍCH THƯỚC CÁC CỘT CHO CÂN ĐỐI
        header = self.bang.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # STT bó sát
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)          # Tên SP giãn đều
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents) # Tồn kho bó sát
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)          # NPP giãn đều
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)          # Người liên hệ giãn đều
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)          # SĐT giãn đều

        layout.addWidget(self.bang)
        self.setLayout(layout)
        self.tai_du_lieu()

    def tao_o_chu(self, text, can_giua=False, mau_do=False):
        lbl = QLabel(str(text))
        lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter if can_giua else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # Phóng to chữ ở các ô dữ liệu (đang dùng QLabel) lên 24px
        style = "font-size: 24px; padding: 6px 12px; background: transparent;"
        if mau_do: 
            style += " color: #c0392b; font-weight: bold;"
        lbl.setStyleSheet(style)
        return lbl

    def tai_du_lieu(self):
        du_lieu = self.db.lay_danh_sach_canh_bao()
        self.bang.setRowCount(len(du_lieu))
        for r, row in enumerate(du_lieu):
            self.bang.setCellWidget(r, 0, self.tao_o_chu(r + 1, can_giua=True))
            self.bang.setCellWidget(r, 1, self.tao_o_chu(row[0]))
            self.bang.setCellWidget(r, 2, self.tao_o_chu(row[1], can_giua=True, mau_do=True))
            self.bang.setCellWidget(r, 3, self.tao_o_chu(row[2] or ""))
            self.bang.setCellWidget(r, 4, self.tao_o_chu(row[3] or ""))
            self.bang.setCellWidget(r, 5, self.tao_o_chu(row[4] or "", can_giua=True))

    def copy_danh_sach(self):
        if self.bang.rowCount() == 0: return
        ds = [self.bang.cellWidget(r, 1).text() for r in range(self.bang.rowCount())]
        QApplication.clipboard().setText("\n".join(ds))
        QMessageBox.information(self, "Đã Copy", "Đã copy toàn bộ tên sản phẩm!")