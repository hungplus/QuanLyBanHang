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
        lbl_tieu_de.setStyleSheet("font-size: 22px; font-weight: bold; color: #c0392b;")
        
        btn_copy_ds = QPushButton("📋 Copy danh sách")
        btn_copy_ds.setStyleSheet("QPushButton {font-size: 16px; font-weight: bold; background-color: #3498db; color: white; padding: 8px 16px; border-radius: 5px;}")
        btn_copy_ds.clicked.connect(self.copy_danh_sach)
        
        top_layout.addWidget(lbl_tieu_de); top_layout.addStretch(); top_layout.addWidget(btn_copy_ds)
        layout.addLayout(top_layout)

        self.bang = QTableWidget(0, 6)
        self.bang.setHorizontalHeaderLabels(["STT", "Tên Sản Phẩm", "Tồn Kho", "Nhà Phân Phối", "Người Liên Hệ", "Số Điện Thoại"])
        self.bang.verticalHeader().setVisible(False)
        self.bang.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.bang.setStyleSheet("QTableWidget { font-size: 16px; gridline-color: #bdc3c7; outline: 0;} QHeaderView::section { background-color: #34495e; color: white; font-size: 16px; font-weight: bold; padding: 8px;}")
        self.bang.setAlternatingRowColors(True)

        header = self.bang.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for col in range(2, 6): header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.bang)
        self.setLayout(layout)
        self.tai_du_lieu()

    def tao_o_chu(self, text, can_giua=False, mau_do=False):
        lbl = QLabel(str(text))
        lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter if can_giua else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        style = "font-size: 16px; padding: 4px 8px; background: transparent;"
        if mau_do: style += " color: #c0392b; font-weight: bold;"
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