from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QCompleter
from PyQt6.QtCore import Qt, QStringListModel

class TabTraCuu(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        lbl_hd = QLabel('Nhập tên sản phẩm cần tìm:'); lbl_hd.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText('VD: Omo, Coast...')
        self.search_bar.setStyleSheet("QLineEdit { font-size: 18px; padding: 10px; border: 2px solid #ccc; border-radius: 5px; }")
        
        self.result_label = QLabel('Chọn một sản phẩm để xem thông tin...')
        self.result_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.result_label.setStyleSheet("font-size: 18px; color: #2c3e50; margin-top: 20px; background-color: #ecf0f1; padding: 15px; border-radius: 5px;")
        
        layout.addWidget(lbl_hd); layout.addWidget(self.search_bar); layout.addWidget(self.result_label); layout.addStretch()
        self.setLayout(layout)

        self.completer = QCompleter([], self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.popup().setStyleSheet("QListView { font-size: 18px; }")
        self.search_bar.setCompleter(self.completer)
        self.completer.activated.connect(self.hien_thi)
        self.tai_du_lieu()

    def tai_du_lieu(self):
        ds = self.db.lay_danh_sach_ten_san_pham()
        self.completer.setModel(QStringListModel(ds))

    def hien_thi(self, ten_sp):
        sp = self.db.lay_thong_tin_san_pham_chi_tiet(ten_sp)
        if not sp: return
        ls = self.db.lay_lich_su_nhap_gan_nhat(sp[0])
        chuoi_ls = "".join([f"💵 Nhập {sl} cái, giá {gia}, ngày {ngay}<br>" for gia, sl, ngay in ls]) or "Chưa có lịch sử nhập"
        
        self.result_label.setText(f"<b>📦 {ten_sp}</b><br>Tồn: {sp[1]}<br>---<br>{chuoi_ls}<br>NPP: {sp[3]}")
        self.search_bar.clear()