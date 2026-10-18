import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
    QHBoxLayout, QFormLayout, QLabel, QLineEdit, QComboBox, 
    QSpinBox, QPushButton, QMessageBox, QCompleter, 
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog
)
from PyQt6.QtCore import Qt, QStringListModel, QEvent
from PyQt6.QtGui import QColor, QIntValidator

# CỬA SỔ POPUP THÊM NHÀ PHÂN PHỐI / NHÂN VIÊN MỚI
class PopupThemNPP(QDialog):
    def __init__(self, cursor, danh_sach_npp_hien_tai, parent=None):
        super().__init__(parent)
        self.cursor = cursor
        self.setWindowTitle("Thêm Đối Tác / Nhân Viên Mới")
        self.setFixedSize(450, 250)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        layout = QVBoxLayout()
        form_layout = QFormLayout()
        css_input = "font-size: 16px; padding: 6px; border: 1px solid #ccc; border-radius: 4px;"
        
        self.cb_ten_npp = QComboBox()
        self.cb_ten_npp.setEditable(True) 
        self.cb_ten_npp.setStyleSheet(css_input)
        self.cb_ten_npp.lineEdit().setPlaceholderText("Gõ tên NPP mới hoặc chọn NPP cũ...")
        self.cb_ten_npp.addItem("Khách lẻ / Sale tự do")
        self.cb_ten_npp.addItems(danh_sach_npp_hien_tai)

        self.txt_ten_sale = QLineEdit()
        self.txt_ten_sale.setStyleSheet(css_input)
        self.txt_ten_sale.setPlaceholderText("VD: Anh Hoàng...")

        self.txt_sdt = QLineEdit()
        self.txt_sdt.setStyleSheet(css_input)
        self.txt_sdt.setPlaceholderText("VD: 0912345678")

        form_layout.addRow("Tên Công ty/Đại lý:", self.cb_ten_npp)
        form_layout.addRow("Tên Nhân viên Sales:", self.txt_ten_sale)
        form_layout.addRow("Số điện thoại:", self.txt_sdt)
        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        btn_luu = QPushButton("💾 LƯU THÔNG TIN")
        btn_luu.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #2980b9; color: white; padding: 10px;")
        btn_luu.clicked.connect(self.xu_ly_luu)
        
        btn_huy = QPushButton("Hủy")
        btn_huy.setStyleSheet("font-size: 16px; padding: 10px;")
        btn_huy.clicked.connect(self.reject)

        btn_layout.addWidget(btn_huy)
        btn_layout.addWidget(btn_luu)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def xu_ly_luu(self):
        ten_npp = self.cb_ten_npp.currentText().strip()
        ten_sale = self.txt_ten_sale.text().strip()
        sdt = self.txt_sdt.text().strip()

        if not ten_sale:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập ít nhất là Tên Nhân Viên Sales!")
            self.txt_ten_sale.setFocus()
            return

        try:
            self.cursor.execute(
                "INSERT INTO Nha_Phan_Phoi (ten_npp, ten_sale, sdt_sale) VALUES (?, ?, ?)", 
                (ten_npp, ten_sale, sdt)
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể thêm.\nLỗi: {e}")

# ==============================================================
# 1. CỬA SỔ POPUP THÊM NHÀ PHÂN PHỐI / NHÂN VIÊN MỚI
# ==============================================================
class PopupSuaSP(QDialog):
    def __init__(self, cursor, danh_sach_npp, sp_id, sp_ten, sp_ton, sp_npp, parent=None):
        super().__init__(parent)
        self.cursor = cursor
        self.sp_id = sp_id
        self.setWindowTitle("Sửa Thông Tin Sản Phẩm")
        self.setFixedSize(450, 250)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        layout = QVBoxLayout()
        form_layout = QFormLayout()
        css_input = "font-size: 16px; padding: 6px; border: 1px solid #ccc; border-radius: 4px;"

        self.txt_ten_sp = QLineEdit(sp_ten)
        self.txt_ten_sp.setStyleSheet(css_input)

        self.txt_ton_kho = QLineEdit(str(sp_ton))
        self.txt_ton_kho.setStyleSheet(css_input)
        self.txt_ton_kho.setValidator(QIntValidator(0, 100000, self))

        self.cb_npp = QComboBox()
        self.cb_npp.setStyleSheet(css_input)
        self.cb_npp.addItem("Khách lẻ / Sale tự do")
        self.cb_npp.addItems(danh_sach_npp)
        
        # Tự động trỏ thanh cuộn về đúng Nhà phân phối cũ của sản phẩm
        idx = self.cb_npp.findText(sp_npp)
        if idx >= 0:
            self.cb_npp.setCurrentIndex(idx)

        form_layout.addRow("Tên Sản Phẩm:", self.txt_ten_sp)
        form_layout.addRow("Tồn Kho Hiện Tại:", self.txt_ton_kho)
        form_layout.addRow("Nhà Phân Phối:", self.cb_npp)
        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        btn_luu = QPushButton("💾 CẬP NHẬT")
        btn_luu.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #f39c12; color: white; padding: 10px;")
        btn_luu.clicked.connect(self.xu_ly_luu)

        btn_huy = QPushButton("Hủy")
        btn_huy.setStyleSheet("font-size: 16px; padding: 10px;")
        btn_huy.clicked.connect(self.reject)

        btn_layout.addWidget(btn_huy)
        btn_layout.addWidget(btn_luu)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def xu_ly_luu(self):
        ten_moi = self.txt_ten_sp.text().strip()
        ton_moi = self.txt_ton_kho.text().strip()
        npp_moi = self.cb_npp.currentText()

        if not ten_moi or not ton_moi:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đủ Tên và Tồn kho!")
            return
        
        try:
            id_npp = None
            if npp_moi != "Khách lẻ / Sale tự do":
                self.cursor.execute("SELECT id FROM Nha_Phan_Phoi WHERE ten_npp = ? LIMIT 1", (npp_moi,))
                row = self.cursor.fetchone()
                if row: id_npp = row[0]

            self.cursor.execute(
                "UPDATE San_Pham SET ten_sp = ?, ton_kho = ?, id_npp = ? WHERE id = ?",
                (ten_moi, int(ton_moi), id_npp, self.sp_id)
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật: {e}")


# ==============================================================
# 2. CLASS GIAO DIỆN CHÍNH
# ==============================================================
class PhanMemTapHoa(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ket_noi_db() 
        self.init_ui()
        QApplication.instance().installEventFilter(self)

    def ket_noi_db(self):
        try:
            self.conn = sqlite3.connect('quanly_taphoa.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute("PRAGMA foreign_keys = ON;")
            
            # TỰ ĐỘNG NÂNG CẤP DATABASE: Kiểm tra xem đã có cột trang_thai chưa, chưa có thì tự thêm vào
            self.cursor.execute("PRAGMA table_info(Nha_Phan_Phoi)")
            cac_cot = [col[1] for col in self.cursor.fetchall()]
            if 'trang_thai' not in cac_cot:
                self.cursor.execute("ALTER TABLE Nha_Phan_Phoi ADD COLUMN trang_thai INTEGER DEFAULT 1")
                self.conn.commit()
            
            self.cursor.execute("SELECT COUNT(*) FROM Nha_Phan_Phoi")
            if self.cursor.fetchone()[0] == 0:
                npp_mau = [
                    ("Đại lý Unilever", "Anh Hùng", "0901.123.456", 1),
                    ("Đại lý Unilever", "Chị Lan", "0909.999.888", 1),
                    ("NPP Phú Thái", "Chị Mai", "0988.765.432", 1)
                ]
                self.cursor.executemany("INSERT INTO Nha_Phan_Phoi (ten_npp, ten_sale, sdt_sale, trang_thai) VALUES (?, ?, ?, ?)", npp_mau)
                self.conn.commit()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi Database", f"Lỗi: {e}")
            sys.exit()

    def closeEvent(self, event):
        if hasattr(self, 'conn'): self.conn.close()
        event.accept()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            for lbl in self.findChildren(QLabel):
                if lbl is not obj and lbl.hasSelectedText():
                    lbl.setSelection(0, 0)
        return super().eventFilter(obj, event)

    # --- CÁC HÀM LẤY DỮ LIỆU THÔNG MINH MỚI ---
    def lay_danh_sach_san_pham(self):
        self.cursor.execute("SELECT ten_sp FROM San_Pham")
        return [item[0] for item in self.cursor.fetchall()]

    def lay_danh_sach_npp_duy_nhat(self):
        """Chỉ lấy danh sách các Nhà phân phối CÒN HOẠT ĐỘNG"""
        self.cursor.execute("SELECT DISTINCT ten_npp FROM Nha_Phan_Phoi WHERE ten_npp != 'Khách lẻ / Sale tự do' AND trang_thai = 1")
        return [item[0] for item in self.cursor.fetchall() if item[0]]

    def lay_danh_sach_sale_theo_npp(self, ten_npp_chon):
        """Chỉ lấy danh sách nhân viên CÒN LÀM VIỆC tương ứng với NPP"""
        self.cursor.execute("SELECT ten_sale, sdt_sale FROM Nha_Phan_Phoi WHERE ten_npp = ? AND trang_thai = 1", (ten_npp_chon,))
        ket_qua = []
        for row in self.cursor.fetchall():
            ten_sale, sdt = row[0], row[1]
            chuoi_hien_thi = f"{ten_sale} - {sdt}" if sdt else ten_sale
            ket_qua.append(chuoi_hien_thi)
        return ket_qua

    def lam_moi_danh_sach_goi_y(self):
        danh_sach_moi = self.lay_danh_sach_san_pham()
        model_moi = QStringListModel(danh_sach_moi)
        self.completer_tra_cuu.setModel(model_moi)
        self.completer_nhap.setModel(model_moi)
        self.completer_ban.setModel(model_moi)

    def tao_completer_chuan(self):
        danh_sach_sp = self.lay_danh_sach_san_pham()
        completer = QCompleter(danh_sach_sp, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setMaxVisibleItems(8)
        completer.popup().setStyleSheet("""
            QListView { font-size: 18px; background-color: #ffffff; border: 2px solid #3498db; outline: 0px; padding: 0px; margin: 0px;}
            QListView::item { padding: 10px 12px; min-height: 28px; color: #2c3e50; border-bottom: 1px solid #f0f0f0;}
            QListView::item:hover { background-color: #ebf5fb; color: #2980b9;}
            QListView::item:selected { background-color: #3498db; color: white; font-weight: bold;}
        """)
        return completer

    def init_ui(self):  
        self.setWindowTitle('Phần Mềm Quản Lý Tạp Hóa Gia Đình')
        self.resize(1000, 650)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab { font-size: 18px; font-weight: bold; padding: 12px 30px; background-color: #f0f0f0; border: 1px solid #ccc; border-top-left-radius: 8px; border-top-right-radius: 8px;}
            QTabBar::tab:selected { background-color: #3498db; color: white;}
            QWidget { background-color: white; }
        """)
        
        # === ĐOẠN ĐƯỢC CHỈNH SỬA / THÊM MỚI Ở ĐÂY ===
        self.tab_canh_bao = self.tao_tab_canh_bao()
        self.tab_tra_cuu = self.tao_tab_tra_cuu()
        self.tab_nhap_hang = self.tao_tab_nhap_hang()
        self.tab_tru_kho = self.tao_tab_tru_kho()
        self.tab_quan_ly = self.tao_tab_quan_ly() 
        self.tab_doi_tac = self.tao_tab_doi_tac()
        
        self.tabs.addTab(self.tab_canh_bao, "🚨 Cảnh báo Tồn kho")
        self.tabs.addTab(self.tab_tra_cuu, "🔍 Tra cứu Sản phẩm")
        self.tabs.addTab(self.tab_nhap_hang, "📦 Nhập hàng (Toa)")
        self.tabs.addTab(self.tab_tru_kho, "➖ Trừ kho Cuối ngày")
        self.tabs.addTab(self.tab_quan_ly, "⚙️ Quản lý Danh mục")
        self.tabs.addTab(self.tab_doi_tac, "🤝 Quản lý Đối tác")
        # ============================================

        self.setCentralWidget(self.tabs)

    # --- TAB 1: CẢNH BÁO ---
    def tao_tab_canh_bao(self):
        tab = QWidget()
        layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        lbl_tieu_de = QLabel("⚠️ DANH SÁCH MẶT HÀNG SẮP HẾT CẦN GỌI NHẬP THÊM")
        lbl_tieu_de.setStyleSheet("font-size: 22px; font-weight: bold; color: #c0392b;")
        self.btn_copy_ds = QPushButton("📋 Copy danh sách")
        self.btn_copy_ds.setStyleSheet("QPushButton {font-size: 16px; font-weight: bold; background-color: #3498db; color: white; padding: 8px 16px; border-radius: 5px;} QPushButton:hover { background-color: #2980b9; }")
        self.btn_copy_ds.clicked.connect(self.copy_danh_sach_canh_bao)
        top_layout.addWidget(lbl_tieu_de)
        top_layout.addStretch()
        top_layout.addWidget(self.btn_copy_ds)
        layout.addLayout(top_layout)

    # Tăng lên 6 cột và thêm STT lên đầu giống như bạn đã làm
        self.bang_canh_bao = QTableWidget()
        self.bang_canh_bao.setColumnCount(6)
        self.bang_canh_bao.setHorizontalHeaderLabels([
            "STT", "Tên Sản Phẩm", "Tồn Kho", "Nhà Phân Phối", "Người Liên Hệ", "Số Điện Thoại"
        ])
        
        # THÊM DÒNG NÀY: Ẩn cái cột số thứ tự mặc định của PyQt đi để không bị dư
        self.bang_canh_bao.verticalHeader().setVisible(False)
        
        self.bang_canh_bao.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.bang_canh_bao.setSelectionMode(QTableWidget.SelectionMode.NoSelection)

        self.bang_canh_bao.setStyleSheet("""
            QTableWidget { font-size: 16px; gridline-color: #bdc3c7; outline: 0;}
            QHeaderView::section {
                background-color: #34495e; color: white;
                font-size: 16px; font-weight: bold; padding: 8px; border: 1px solid #bdc3c7;
            }
        """)
        self.bang_canh_bao.setAlternatingRowColors(True)

        header = self.bang_canh_bao.horizontalHeader()
        # Chỉnh lại độ rộng: Cột 0 (STT) ép vừa chữ, Cột 1 (Tên SP) kéo giãn dài ra
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        # Các cột từ 2 đến 5 ép vừa chữ
        for col in range(2, 6): 
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.bang_canh_bao)
        self.tai_danh_sach_canh_bao()
        tab.setLayout(layout)
        return tab

    def tao_o_chu_copy_duoc(self, text, can_giua=False, mau_do=False):
        lbl = QLabel(str(text))
        lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter if can_giua else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        style = "font-size: 16px; padding: 4px 8px; background: transparent;"
        if mau_do: style += " color: #c0392b; font-weight: bold;"
        lbl.setStyleSheet(style)
        return lbl

    def copy_danh_sach_canh_bao(self):
        so_dong = self.bang_canh_bao.rowCount()
        if so_dong == 0: return
        ds_ten = [self.bang_canh_bao.cellWidget(row, 0).text() for row in range(so_dong)]
        QApplication.clipboard().setText("\n".join(ds_ten))
        QMessageBox.information(self, "Đã Copy", "Đã copy toàn bộ tên sản phẩm, bạn có thể ra ngoài bấm Ctrl+V để dán!")

    def tai_danh_sach_canh_bao(self):
        self.cursor.execute('''
            SELECT sp.ten_sp, sp.ton_kho, npp.ten_npp, npp.ten_sale, npp.sdt_sale
            FROM San_Pham sp LEFT JOIN Nha_Phan_Phoi npp ON sp.id_npp = npp.id
            WHERE sp.ton_kho <= sp.ton_toithieu ORDER BY sp.ton_kho ASC
        ''')
        du_lieu = self.cursor.fetchall()
        self.bang_canh_bao.setRowCount(len(du_lieu))
        for r, row in enumerate(du_lieu):
            # Cột 0: STT (Tự động tính từ số dòng r + 1, căn giữa)
            self.bang_canh_bao.setCellWidget(r, 0, self.tao_o_chu_copy_duoc(r + 1, can_giua=True))
            
            # Cột 1: Tên sản phẩm
            self.bang_canh_bao.setCellWidget(r, 1, self.tao_o_chu_copy_duoc(row[0]))
            
            # Cột 2: Tồn kho
            self.bang_canh_bao.setCellWidget(r, 2, self.tao_o_chu_copy_duoc(row[1], can_giua=True, mau_do=True))
            
            # Cột 3: Nhà phân phối
            self.bang_canh_bao.setCellWidget(r, 3, self.tao_o_chu_copy_duoc(row[2] or ""))
            
            # Cột 4: Người liên hệ
            self.bang_canh_bao.setCellWidget(r, 4, self.tao_o_chu_copy_duoc(row[3] or ""))
            
            # Cột 5: SĐT (chỉnh can_giua=True để số điện thoại hiển thị đẹp hơn)
            self.bang_canh_bao.setCellWidget(r, 5, self.tao_o_chu_copy_duoc(row[4] or "", can_giua=True))

    # --- TAB 2: TRA CỨU ---
    def tao_tab_tra_cuu(self):
        tab = QWidget()
        layout = QVBoxLayout()
        lbl_hd = QLabel('Nhập tên sản phẩm cần tìm:'); lbl_hd.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(lbl_hd)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText('VD: Omo, Coast, Kẹo dừa...')
        self.search_bar.setStyleSheet("QLineEdit { font-size: 18px; padding: 10px; border: 2px solid #ccc; border-radius: 5px; }")
        layout.addWidget(self.search_bar)
        self.result_label = QLabel('Chọn một sản phẩm để xem thông tin...')
        self.result_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.result_label.setStyleSheet("font-size: 18px; color: #2c3e50; margin-top: 20px; background-color: #ecf0f1; padding: 15px; border-radius: 5px;")
        layout.addWidget(self.result_label)
        layout.addStretch()
        self.completer_tra_cuu = self.tao_completer_chuan()
        self.search_bar.setCompleter(self.completer_tra_cuu)
        self.completer_tra_cuu.activated.connect(self.hien_thi_thong_tin_sp)
        tab.setLayout(layout)
        return tab

    # --- TAB 3: NHẬP HÀNG (CẬP NHẬT 2 THANH CUỘN LIÊN KẾT) ---
    def tao_tab_nhap_hang(self):
        tab = QWidget()
        layout = QVBoxLayout()
        lbl_tieu_de = QLabel("📦 NHẬP HÀNG TỪ TOA")
        lbl_tieu_de.setStyleSheet("font-size: 22px; font-weight: bold; color: #27ae60; margin-bottom: 20px;")
        lbl_tieu_de.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_tieu_de)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setSpacing(15)
        css_input = "font-size: 18px; padding: 8px; border: 1px solid #7f8c8d; border-radius: 4px;"

        # a1) Chọn Nhà Phân Phối
        npp_layout = QHBoxLayout()
        self.cb_npp = QComboBox()
        self.cb_npp.setStyleSheet(css_input)
        self.cb_npp.addItem("-- Chọn Nhà Phân Phối --")
        self.cb_npp.addItem("Khách lẻ / Sale tự do")
        self.cb_npp.addItems(self.lay_danh_sach_npp_duy_nhat())
        self.cb_npp.setSizePolicy(self.cb_npp.sizePolicy().Policy.Expanding, self.cb_npp.sizePolicy().Policy.Fixed)

        self.btn_them_npp = QPushButton(" ➕ ")
        self.btn_them_npp.setToolTip("Thêm Đối tác / Nhân viên Mới")
        self.btn_them_npp.setStyleSheet("QPushButton { font-size: 18px; font-weight: bold; background-color: #34495e; color: white; padding: 5px 12px; border-radius: 4px;} QPushButton:hover { background-color: #2c3e50; }")
        self.btn_them_npp.clicked.connect(self.mo_popup_them_npp)

        npp_layout.addWidget(self.cb_npp)
        npp_layout.addWidget(self.btn_them_npp)

        # a2) Chọn Nhân Viên Sales (Sẽ tự lọc theo NPP ở trên)
        self.cb_sale = QComboBox()
        self.cb_sale.setStyleSheet(css_input)
        self.cb_sale.addItem("-- Chọn Nhân Viên Sales --")
        # Kết nối sự kiện: Khi đổi NPP -> Cập nhật Sale
        self.cb_npp.currentTextChanged.connect(self.cap_nhat_combo_sale)

        # b) Nhập Tên Sản Phẩm
        self.txt_san_pham_nhap = QLineEdit()
        self.txt_san_pham_nhap.setPlaceholderText("Gõ tên sản phẩm (VD: Dầu ăn Cái Lân 1L)...")
        self.txt_san_pham_nhap.setStyleSheet(css_input)
        self.completer_nhap = self.tao_completer_chuan()
        self.txt_san_pham_nhap.setCompleter(self.completer_nhap)

        
        # c) Nhập Số Lượng
        sl_layout = QHBoxLayout()
        
        self.txt_so_luong = QLineEdit()
        self.txt_so_luong.setStyleSheet(css_input)
        self.txt_so_luong.setPlaceholderText("SL")
        self.txt_so_luong.setFixedWidth(90) # Đã thu gọn từ 130 xuống 90
        self.txt_so_luong.setValidator(QIntValidator(1, 100000, self))
        
        lbl_nhan = QLabel("✖")
        lbl_nhan.setStyleSheet("font-size: 18px; font-weight: bold; color: #7f8c8d;")
        
        self.txt_quy_cach = QLineEdit("1")
        self.txt_quy_cach.setStyleSheet(css_input)
        self.txt_quy_cach.setFixedWidth(90) # Đã thu gọn từ 130 xuống 90
        self.txt_quy_cach.setValidator(QIntValidator(1, 1000, self))
        
        self.lbl_tong_nhap = QLabel("= Tổng nhập: 0 đơn vị")
        self.lbl_tong_nhap.setStyleSheet("font-size: 18px; font-weight: bold; color: #2980b9; margin-left: 10px;")
        self.lbl_tong_nhap.setMinimumWidth(220) # Giữ không gian cố định không cho chữ bị ép
        
        self.txt_so_luong.textChanged.connect(self.tinh_nham_so_luong)
        self.txt_quy_cach.textChanged.connect(self.tinh_nham_so_luong)
        
        sl_layout.addWidget(self.txt_so_luong)
        sl_layout.addWidget(lbl_nhan)
        sl_layout.addWidget(self.txt_quy_cach)
        sl_layout.addWidget(self.lbl_tong_nhap)
        sl_layout.addStretch()

        # d) Nhập Giá Vốn
        gia_von_layout = QHBoxLayout()
        self.txt_gia_von = QLineEdit(); self.txt_gia_von.setStyleSheet(css_input); self.txt_gia_von.setPlaceholderText("VD: 31,8"); self.txt_gia_von.setFixedWidth(200)
        self.btn_dau_phay = QPushButton(" , ")
        self.btn_dau_phay.setStyleSheet("QPushButton { font-size: 22px; font-weight: bold; background-color: #ecf0f1; color: #2c3e50; padding: 4px 16px; border: 1px solid #7f8c8d; border-radius: 4px;} QPushButton:hover { background-color: #bdc3c7; }")
        self.btn_dau_phay.clicked.connect(self.them_dau_phay)
        gia_von_layout.addWidget(self.txt_gia_von); gia_von_layout.addWidget(self.btn_dau_phay); gia_von_layout.addStretch()

        lbl_style = "font-size: 18px; font-weight: bold;"
        lbl_1 = QLabel("Nhà Phân Phối:"); lbl_1.setStyleSheet(lbl_style); form_layout.addRow(lbl_1, npp_layout)
        lbl_1b = QLabel("Nhân Viên (Sale):"); lbl_1b.setStyleSheet(lbl_style); form_layout.addRow(lbl_1b, self.cb_sale)
        lbl_2 = QLabel("Tên Sản Phẩm:"); lbl_2.setStyleSheet(lbl_style); form_layout.addRow(lbl_2, self.txt_san_pham_nhap)
        lbl_3 = QLabel("Số Lượng × Quy Cách:"); lbl_3.setStyleSheet(lbl_style); form_layout.addRow(lbl_3, sl_layout)
        lbl_4 = QLabel("Giá Vốn Đợt Này:"); lbl_4.setStyleSheet(lbl_style); form_layout.addRow(lbl_4, gia_von_layout)

        #layout.addLayout(form_layout)
        # Đóng gói form vào một hộp chứa và khóa chiều rộng tối đa
        form_container = QWidget()
        form_container.setLayout(form_layout)
        form_container.setMaximumWidth(850)  # Ngăn form giãn dài quá 750px
        form_container.setMinimumWidth(600)  # Giữ form không bị ép quá nhỏ

        # Tạo thanh ngang dùng "lò xo" (stretch) ép hộp form ra giữa
        center_layout = QHBoxLayout()
        center_layout.addStretch()           # Lò xo tàng hình đẩy từ bên trái
        center_layout.addWidget(form_container)
        center_layout.addStretch()           # Lò xo tàng hình đẩy từ bên phải

        layout.addLayout(center_layout)

        btn_layout = QHBoxLayout(); btn_layout.addStretch()
        self.btn_luu_kho = QPushButton("💾 LƯU VÀO KHO")
        self.btn_luu_kho.setStyleSheet("QPushButton { font-size: 20px; font-weight: bold; background-color: #27ae60; color: white; padding: 15px 40px; border-radius: 8px; margin-top: 20px;} QPushButton:hover { background-color: #2ecc71; }")
        self.btn_luu_kho.clicked.connect(self.xu_ly_luu_kho)
        btn_layout.addWidget(self.btn_luu_kho); btn_layout.addStretch(); layout.addLayout(btn_layout); layout.addStretch()
        tab.setLayout(layout)
        return tab

    def cap_nhat_combo_sale(self, ten_npp_chon):
        """Tự động lọc danh sách Sale khi đổi Nhà Phân Phối"""
        self.cb_sale.clear()
        if ten_npp_chon == "-- Chọn Nhà Phân Phối --":
            self.cb_sale.addItem("-- Chọn Nhân Viên Sales --")
        else:
            ds_sale = self.lay_danh_sach_sale_theo_npp(ten_npp_chon)
            if not ds_sale:
                self.cb_sale.addItem("-- Chưa có Nhân viên nào --")
            else:
                self.cb_sale.addItems(ds_sale)

    def mo_popup_them_npp(self):
        danh_sach_hien_tai = self.lay_danh_sach_npp_duy_nhat()
        popup = PopupThemNPP(self.cursor, danh_sach_hien_tai, self)
        if popup.exec():
            self.conn.commit()
            ten_npp_vua_them = popup.cb_ten_npp.currentText().strip()
            
            # Reset combobox NPP
            self.cb_npp.blockSignals(True) # Tạm khóa sự kiện để không bị chớp giật
            self.cb_npp.clear()
            self.cb_npp.addItem("-- Chọn Nhà Phân Phối --")
            self.cb_npp.addItem("Khách lẻ / Sale tự do")
            self.cb_npp.addItems(self.lay_danh_sach_npp_duy_nhat())
            self.cb_npp.blockSignals(False)
            
            # Tự động trỏ thanh cuộn về cái tên vừa thêm
            idx = self.cb_npp.findText(ten_npp_vua_them)
            if idx >= 0:
                self.cb_npp.setCurrentIndex(idx)
            
            QMessageBox.information(self, "Thành Công", "Đã lưu thông tin đối tác thành công!")

    def tinh_nham_so_luong(self):
        sl = int(self.txt_so_luong.text() or 0)
        qc = int(self.txt_quy_cach.text() or 1)
        self.lbl_tong_nhap.setText(f"= Tổng nhập: {sl * qc} đơn vị")

    def them_dau_phay(self):
        hien_tai = self.txt_gia_von.text()
        if "," not in hien_tai and "." not in hien_tai:
            self.txt_gia_von.setText(hien_tai + "," if hien_tai else "0,")
        self.txt_gia_von.setFocus()

    # --- TAB 4: TRỪ KHO ---
    def tao_tab_tru_kho(self):
        tab = QWidget()
        layout = QVBoxLayout()
        lbl_tieu_de = QLabel("➖ TRỪ KHO CUỐI NGÀY")
        lbl_tieu_de.setStyleSheet("font-size: 22px; font-weight: bold; color: #d35400; margin-bottom: 20px;"); lbl_tieu_de.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_tieu_de)

        form_layout = QFormLayout(); form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight); form_layout.setSpacing(20)
        css_input = "font-size: 18px; padding: 10px; border: 1px solid #7f8c8d; border-radius: 4px;"

        self.txt_sp_ban = QLineEdit(); self.txt_sp_ban.setPlaceholderText("Gõ tên sản phẩm..."); self.txt_sp_ban.setStyleSheet(css_input)
        self.completer_ban = self.tao_completer_chuan(); self.txt_sp_ban.setCompleter(self.completer_ban)
        
        self.txt_sl_ban = QLineEdit(); self.txt_sl_ban.setStyleSheet(css_input); self.txt_sl_ban.setPlaceholderText("VD: 2"); self.txt_sl_ban.setFixedWidth(200); self.txt_sl_ban.setValidator(QIntValidator(1, 10000, self))
        self.txt_sl_ban.returnPressed.connect(self.xu_ly_tru_kho)

        lbl_style = "font-size: 18px; font-weight: bold;"
        lbl_1 = QLabel("Tên Sản Phẩm:"); lbl_1.setStyleSheet(lbl_style); form_layout.addRow(lbl_1, self.txt_sp_ban)
        lbl_2 = QLabel("Số Lượng Đã Bán:"); lbl_2.setStyleSheet(lbl_style); form_layout.addRow(lbl_2, self.txt_sl_ban)
        #layout.addLayout(form_layout)
        # Đóng gói form vào một hộp chứa và khóa chiều rộng tối đa
        form_container = QWidget()
        form_container.setLayout(form_layout)
        form_container.setMaximumWidth(750)  # Ngăn form giãn dài quá 750px
        form_container.setMinimumWidth(600)  # Giữ form không bị ép quá nhỏ

        # Tạo thanh ngang dùng "lò xo" (stretch) ép hộp form ra giữa
        center_layout = QHBoxLayout()
        center_layout.addStretch()           # Lò xo tàng hình đẩy từ bên trái
        center_layout.addWidget(form_container)
        center_layout.addStretch()           # Lò xo tàng hình đẩy từ bên phải

        layout.addLayout(center_layout)

        btn_layout = QHBoxLayout(); btn_layout.addStretch()
        self.btn_tru_kho = QPushButton("➖ XÁC NHẬN TRỪ KHO")
        self.btn_tru_kho.setStyleSheet("QPushButton { font-size: 20px; font-weight: bold; background-color: #e67e22; color: white; padding: 15px 40px; border-radius: 8px; margin-top: 20px;} QPushButton:hover { background-color: #d35400; }")
        self.btn_tru_kho.clicked.connect(self.xu_ly_tru_kho)
        btn_layout.addWidget(self.btn_tru_kho); btn_layout.addStretch(); layout.addLayout(btn_layout); layout.addStretch()
        tab.setLayout(layout)
        return tab

    def tao_tab_quan_ly(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        lbl_tieu_de = QLabel("⚙️ QUẢN LÝ DANH MỤC HÀNG HÓA")
        lbl_tieu_de.setStyleSheet("font-size: 22px; font-weight: bold; color: #8e44ad; margin-bottom: 10px;")
        lbl_tieu_de.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_tieu_de)

        # Cụm nút thao tác
        btn_layout = QHBoxLayout()
        self.btn_sua_sp = QPushButton("✏️ Sửa thông tin")
        self.btn_sua_sp.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #f39c12; color: white; padding: 8px 20px; border-radius: 4px;")
        
        self.btn_xoa_sp = QPushButton("❌ Xóa sản phẩm")
        self.btn_xoa_sp.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #c0392b; color: white; padding: 8px 20px; border-radius: 4px;")
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_sua_sp)
        btn_layout.addWidget(self.btn_xoa_sp)
        layout.addLayout(btn_layout)

        # Bảng dữ liệu tổng hợp
        self.bang_quan_ly = QTableWidget()
        self.bang_quan_ly.setColumnCount(4)
        self.bang_quan_ly.setHorizontalHeaderLabels(["ID", "Tên Sản Phẩm", "Tồn Kho", "Nhà Phân Phối"])
        self.bang_quan_ly.verticalHeader().setVisible(False)
        self.bang_quan_ly.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows) # Bấm vào là chọn nguyên dòng
        self.bang_quan_ly.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Khóa sửa trực tiếp trên bảng
        
        # 1. THÊM DÒNG NÀY: Tắt hoàn toàn khung nét đứt khi click chuột
        self.bang_quan_ly.setFocusPolicy(Qt.FocusPolicy.NoFocus) 
        
        # 2. CẬP NHẬT CSS: Xóa lỗi xám caro ở Header và làm dịu màu xanh khi chọn dòng
        self.bang_quan_ly.setStyleSheet("""
            QTableWidget { 
                font-size: 16px; 
                gridline-color: #bdc3c7; 
                outline: 0; 
            } 
            QHeaderView::section { 
                background-color: #34495e; 
                color: white; 
                font-size: 16px; 
                font-weight: bold; 
                padding: 8px; 
                border: 1px solid #bdc3c7; /* Cứu tinh giúp xóa lớp xám caro khi click */
            }
            QTableWidget::item:selected {
                background-color: #d6eaf8; /* Đổi sang màu xanh nhạt dịu mắt */
                color: #2c3e50;            /* Đổi chữ thành màu tối để dễ đọc */
                font-weight: bold;
            }
        """)
        self.bang_quan_ly.setAlternatingRowColors(True)
        
        header = self.bang_quan_ly.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # Cột ID ép vừa chữ
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)          # Cột Tên kéo giãn
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents) # Cột Tồn kho ép vừa chữ
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)          # Cột NPP kéo giãn
        
        layout.addWidget(self.bang_quan_ly)
        
        self.tai_danh_sach_quan_ly() # Hàm nạp dữ liệu (Sẽ kích hoạt ở bước sau)
        # Kết nối sự kiện cho 2 nút bấm
        self.btn_sua_sp.clicked.connect(self.mo_popup_sua_sp)
        self.btn_xoa_sp.clicked.connect(self.xu_ly_xoa_sp)
        
        # Nạp dữ liệu vào bảng
        self.tai_danh_sach_quan_ly()
        
        tab.setLayout(layout)
        return tab

    # ==========================================================
    # CÁC HÀM XỬ LÝ SỰ KIỆN & LỆNH SQL
    # ==========================================================
    def hien_thi_thong_tin_sp(self, ten_sp):
        try:
            self.cursor.execute('''SELECT sp.id, sp.ton_kho, sp.gia_ban, npp.ten_npp, npp.ten_sale, npp.sdt_sale
                                   FROM San_Pham sp LEFT JOIN Nha_Phan_Phoi npp ON sp.id_npp = npp.id WHERE sp.ten_sp = ?''', (ten_sp,))
            sp_row = self.cursor.fetchone()
            if not sp_row:
                self.result_label.setText("Không tìm thấy thông tin sản phẩm này!"); return
            id_sp, ton_kho, gia_ban, ten_npp, ten_sale, sdt_sale = sp_row

            self.cursor.execute("SELECT gia_nhap, so_luong, strftime('%d/%m/%Y %H:%M', ngay_nhap) FROM Lich_Su_Nhap WHERE id_sp = ? ORDER BY ngay_nhap DESC, id DESC LIMIT 2", (id_sp,))
            lich_su = self.cursor.fetchall()
            chuoi_gia_nhap = ""
            if not lich_su: chuoi_gia_nhap = "<i>Chưa có lịch sử nhập hàng</i><br>"
            else:
                for idx, (gia, sl, ngay) in enumerate(lich_su, start=1):
                    gia_dep = str(int(gia)) if gia == int(gia) else str(gia).replace('.', ',')
                    nhan_lan = "Gần nhất (Lần 1)" if idx == 1 else "Lần trước đó (Lần 2)"
                    chuoi_gia_nhap += f"💵 <b>{nhan_lan}:</b> <span style='color:#c0392b; font-weight:bold;'>{gia_dep}</span> (Nhập {sl} đơn vị - Ngày {ngay})<br>"

            thong_tin = f"""
            <span style='font-size: 22px; color: #2980b9;'><b>📦 {ten_sp}</b></span><br><br>
            🔢 <b>Tồn kho hiện tại:</b> <span style='font-size: 20px; color: #27ae60;'><b>{ton_kho}</b></span> đơn vị<br>
            -----------------------------------------<br>{chuoi_gia_nhap}-----------------------------------------<br>
            🚚 <b>Nhà phân phối:</b> {ten_npp or 'Khách lẻ'}<br>
            👤 <b>Nhân viên / Liên hệ:</b> {ten_sale or 'Chưa rõ'} — 📞 <b>SĐT:</b> <span style='color:#2980b9;'><b>{sdt_sale or 'Chưa có'}</b></span>
            """
            self.result_label.setText(thong_tin); self.search_bar.clear()
        except Exception as e: QMessageBox.critical(self, "Lỗi", f"Lỗi: {e}")

    def xu_ly_luu_kho(self):
        ten_npp = self.cb_npp.currentText()
        chuoi_sale = self.cb_sale.currentText()
        san_pham = self.txt_san_pham_nhap.text().strip()
        sl_str = self.txt_so_luong.text().strip()
        gia_von_str = self.txt_gia_von.text().strip()

        if ten_npp == "-- Chọn Nhà Phân Phối --" or chuoi_sale in ["-- Chọn Nhân Viên Sales --", "-- Chưa có Nhân viên nào --"] or not san_pham or not sl_str or not gia_von_str:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng điền đủ Tên hàng, Số lượng, Giá vốn và chọn đúng NPP/Nhân viên!")
            return

        try:
            sl_nhap = int(sl_str); quy_cach = int(self.txt_quy_cach.text() or 1)
            tong_so_luong = sl_nhap * quy_cach
            if tong_so_luong <= 0: raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Số lượng phải > 0!"); return

        try: gia_von = float(gia_von_str.replace(',', '.')); 
        except ValueError: QMessageBox.warning(self, "Lỗi", "Giá vốn sai!"); return

        # Tách tên Sale từ chuỗi "Tên - SĐT"
        ten_sale = chuoi_sale.split(" - ")[0].strip()

        try:
            # Tìm ID của đúng bộ đôi (Nhà Phân Phối + Tên Sale)
            self.cursor.execute("SELECT id FROM Nha_Phan_Phoi WHERE ten_npp = ? AND ten_sale = ?", (ten_npp, ten_sale))
            id_npp_row = self.cursor.fetchone()
            id_npp = id_npp_row[0] if id_npp_row else None

            self.cursor.execute("SELECT id FROM San_Pham WHERE ten_sp = ?", (san_pham,))
            sp_row = self.cursor.fetchone()
            if sp_row:
                id_sp = sp_row[0]
                self.cursor.execute("UPDATE San_Pham SET ton_kho = ton_kho + ?, id_npp = ? WHERE id = ?", (tong_so_luong, id_npp, id_sp))
            else:
                self.cursor.execute("INSERT INTO San_Pham (ten_sp, ton_kho, id_npp) VALUES (?, ?, ?)", (san_pham, tong_so_luong, id_npp))
                id_sp = self.cursor.lastrowid

            self.cursor.execute("INSERT INTO Lich_Su_Nhap (id_sp, gia_nhap, so_luong) VALUES (?, ?, ?)", (id_sp, gia_von, tong_so_luong))
            self.conn.commit()

            QMessageBox.information(self, "Thành Công", f"Đã nhập thêm {tong_so_luong} [{san_pham}] vào kho.")
            self.txt_san_pham_nhap.clear(); self.txt_so_luong.clear(); self.txt_quy_cach.setText("1"); self.txt_gia_von.clear(); self.txt_san_pham_nhap.setFocus()
            self.lam_moi_danh_sach_goi_y(); self.tai_danh_sach_canh_bao()
        except Exception as e: self.conn.rollback(); QMessageBox.critical(self, "Lỗi SQL", f"Lỗi: {e}")

    def xu_ly_tru_kho(self):
        san_pham = self.txt_sp_ban.text().strip()
        so_luong_str = self.txt_sl_ban.text().strip()
        if not san_pham or not so_luong_str: return
        try:
            so_luong = int(so_luong_str)
            self.cursor.execute("SELECT id, ton_kho FROM San_Pham WHERE ten_sp = ?", (san_pham,))
            row = self.cursor.fetchone()
            if not row: QMessageBox.warning(self, "Lỗi", "Không có sản phẩm này trong kho!"); return
            id_sp, ton_kho = row[0], row[1]
            if ton_kho < so_luong: QMessageBox.warning(self, "Cảnh báo", f"Trong kho chỉ còn {ton_kho}!"); return

            self.cursor.execute("UPDATE San_Pham SET ton_kho = ton_kho - ? WHERE id = ?", (so_luong, id_sp))
            self.conn.commit()
            self.tai_danh_sach_canh_bao()
            QMessageBox.information(self, "Thành Công", f"Đã trừ {so_luong} x [{san_pham}].")
            self.txt_sp_ban.clear(); self.txt_sl_ban.clear(); self.txt_sp_ban.setFocus()
        except Exception as e: self.conn.rollback(); QMessageBox.critical(self, "Lỗi", str(e))

    # ==========================================================
    # CÁC HÀM XỬ LÝ CHO TAB 5: QUẢN LÝ DANH MỤC
    # ==========================================================
    def tai_danh_sach_quan_ly(self):
        """Lấy toàn bộ sản phẩm đưa lên Bảng quản lý"""
        self.cursor.execute('''
            SELECT sp.id, sp.ten_sp, sp.ton_kho, npp.ten_npp
            FROM San_Pham sp
            LEFT JOIN Nha_Phan_Phoi npp ON sp.id_npp = npp.id
            ORDER BY sp.id DESC
        ''')
        du_lieu = self.cursor.fetchall()
        self.bang_quan_ly.setRowCount(len(du_lieu))
        
        for r, row in enumerate(du_lieu):
            # Cột 0: ID (Căn giữa)
            item_id = QTableWidgetItem(str(row[0]))
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.bang_quan_ly.setItem(r, 0, item_id)
            
            # Cột 1: Tên Sản Phẩm
            self.bang_quan_ly.setItem(r, 1, QTableWidgetItem(row[1]))
            
            # Cột 2: Tồn kho (Căn giữa)
            item_ton = QTableWidgetItem(str(row[2]))
            item_ton.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.bang_quan_ly.setItem(r, 2, item_ton)
            
            # Cột 3: Nhà Phân Phối
            self.bang_quan_ly.setItem(r, 3, QTableWidgetItem(row[3] or "Khách lẻ / Sale tự do"))

    def mo_popup_sua_sp(self):
        """Mở cửa sổ sửa khi click chọn 1 dòng trên bảng"""
        row_dang_chon = self.bang_quan_ly.currentRow()
        if row_dang_chon < 0:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng click chọn 1 mặt hàng trong bảng để sửa!")
            return
        
        # Lấy dữ liệu của dòng đang chọn
        sp_id = int(self.bang_quan_ly.item(row_dang_chon, 0).text())
        sp_ten = self.bang_quan_ly.item(row_dang_chon, 1).text()
        sp_ton = int(self.bang_quan_ly.item(row_dang_chon, 2).text())
        sp_npp = self.bang_quan_ly.item(row_dang_chon, 3).text()

        # Mở Popup
        danh_sach_npp = self.lay_danh_sach_npp_duy_nhat()
        popup = PopupSuaSP(self.cursor, danh_sach_npp, sp_id, sp_ten, sp_ton, sp_npp, self)
        
        if popup.exec():
            self.conn.commit() # Lưu vào database
            # Làm mới lại tất cả các nơi liên quan
            self.tai_danh_sach_quan_ly()
            self.tai_danh_sach_canh_bao()
            self.lam_moi_danh_sach_goi_y()
            QMessageBox.information(self, "Thành Công", "Đã cập nhật thông tin mặt hàng!")

    def xu_ly_xoa_sp(self):
        """Xóa vĩnh viễn mặt hàng cùng lịch sử nhập của nó"""
        row_dang_chon = self.bang_quan_ly.currentRow()
        if row_dang_chon < 0:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng click chọn 1 mặt hàng trong bảng để xóa!")
            return
        
        sp_id = int(self.bang_quan_ly.item(row_dang_chon, 0).text())
        sp_ten = self.bang_quan_ly.item(row_dang_chon, 1).text()

        # Hiện hộp thoại xác nhận (Cơ chế an toàn)
        traloi = QMessageBox.question(
            self, "Xác nhận xóa", 
            f"Bạn có chắc chắn muốn xóa vĩnh viễn mặt hàng:\n[{sp_ten}]\nkhỏi hệ thống không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if traloi == QMessageBox.StandardButton.Yes:
            try:
                # Phải xóa Lịch sử nhập hàng của mặt hàng này trước để tránh lỗi khóa ngoại (Foreign Key)
                self.cursor.execute("DELETE FROM Lich_Su_Nhap WHERE id_sp = ?", (sp_id,))
                
                # Sau đó mới xóa sản phẩm
                self.cursor.execute("DELETE FROM San_Pham WHERE id = ?", (sp_id,))
                self.conn.commit()

                # Cập nhật lại giao diện
                self.tai_danh_sach_quan_ly()
                self.tai_danh_sach_canh_bao()
                self.lam_moi_danh_sach_goi_y()
                QMessageBox.information(self, "Đã xóa", f"Đã xóa [{sp_ten}] thành công!")
            except Exception as e:
                self.conn.rollback()
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa: {e}")

    # ==========================================================
    # CÁC HÀM XỬ LÝ CHO TAB 6: QUẢN LÝ ĐỐI TÁC (NHÀ PHÂN PHỐI / SALE)
    # ==========================================================
    def tao_tab_doi_tac(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        lbl_tieu_de = QLabel("🤝 QUẢN LÝ ĐỐI TÁC & NHÂN VIÊN GIAO HÀNG")
        lbl_tieu_de.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        lbl_tieu_de.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_tieu_de)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_khoa_doi_tac = QPushButton("Khóa / Mở khóa Đối tác (Cho nghỉ)")
        self.btn_khoa_doi_tac.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #34495e; color: white; padding: 8px 20px; border-radius: 4px;")
        self.btn_khoa_doi_tac.clicked.connect(self.xu_ly_khoa_doi_tac)
        btn_layout.addWidget(self.btn_khoa_doi_tac)
        layout.addLayout(btn_layout)

        self.bang_doi_tac = QTableWidget()
        self.bang_doi_tac.setColumnCount(5)
        self.bang_doi_tac.setHorizontalHeaderLabels(["ID", "Nhà Phân Phối", "Tên Nhân Viên", "Số Điện Thoại", "Trạng Thái"])
        self.bang_doi_tac.verticalHeader().setVisible(False)
        self.bang_doi_tac.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.bang_doi_tac.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.bang_doi_tac.setFocusPolicy(Qt.FocusPolicy.NoFocus) 
        
        self.bang_doi_tac.setStyleSheet("""
            QTableWidget { font-size: 16px; gridline-color: #bdc3c7; outline: 0; } 
            QHeaderView::section { background-color: #7f8c8d; color: white; font-size: 16px; font-weight: bold; padding: 8px; border: 1px solid #bdc3c7;}
            QTableWidget::item:selected { background-color: #d6eaf8; color: #2c3e50; font-weight: bold;}
        """)
        self.bang_doi_tac.setAlternatingRowColors(True)
        
        header = self.bang_doi_tac.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.bang_doi_tac)
        self.tai_danh_sach_doi_tac()
        tab.setLayout(layout)
        return tab

    def tai_danh_sach_doi_tac(self):
        self.cursor.execute("SELECT id, ten_npp, ten_sale, sdt_sale, trang_thai FROM Nha_Phan_Phoi ORDER BY trang_thai DESC, id DESC")
        du_lieu = self.cursor.fetchall()
        self.bang_doi_tac.setRowCount(len(du_lieu))
        
        for r, row in enumerate(du_lieu):
            item_id = QTableWidgetItem(str(row[0]))
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.bang_doi_tac.setItem(r, 0, item_id)
            
            self.bang_doi_tac.setItem(r, 1, QTableWidgetItem(row[1]))
            self.bang_doi_tac.setItem(r, 2, QTableWidgetItem(row[2]))
            
            item_sdt = QTableWidgetItem(row[3])
            item_sdt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.bang_doi_tac.setItem(r, 3, item_sdt)
            
            # Cột trạng thái
            trang_thai = "🟢 Đang làm" if row[4] == 1 else "🔴 Đã nghỉ"
            item_tt = QTableWidgetItem(trang_thai)
            item_tt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if row[4] == 0:
                item_tt.setForeground(QColor("#c0392b")) # Chữ đỏ nếu đã nghỉ
            self.bang_doi_tac.setItem(r, 4, item_tt)

    def xu_ly_khoa_doi_tac(self):
        row_dang_chon = self.bang_doi_tac.currentRow()
        if row_dang_chon < 0:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn 1 đối tác / nhân viên để thao tác!")
            return
        
        npp_id = int(self.bang_doi_tac.item(row_dang_chon, 0).text())
        ten_sale = self.bang_doi_tac.item(row_dang_chon, 2).text()
        
        # Lấy trạng thái hiện tại từ DB
        self.cursor.execute("SELECT trang_thai FROM Nha_Phan_Phoi WHERE id = ?", (npp_id,))
        tt_hien_tai = self.cursor.fetchone()[0]
        
        tt_moi = 0 if tt_hien_tai == 1 else 1
        hanh_dong = "ngừng hợp tác (khóa)" if tt_moi == 0 else "kích hoạt lại"

        traloi = QMessageBox.question(self, "Xác nhận", f"Bạn có chắc muốn {hanh_dong} đối với nhân viên [{ten_sale}] không?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if traloi == QMessageBox.StandardButton.Yes:
            self.cursor.execute("UPDATE Nha_Phan_Phoi SET trang_thai = ? WHERE id = ?", (tt_moi, npp_id))
            self.conn.commit()
            
            # Reset lại thanh cuộn ở Tab Nhập hàng
            self.cb_npp.clear()
            self.cb_npp.addItem("-- Chọn Nhà Phân Phối --")
            self.cb_npp.addItem("Khách lẻ / Sale tự do")
            self.cb_npp.addItems(self.lay_danh_sach_npp_duy_nhat())
            
            self.tai_danh_sach_doi_tac()
            QMessageBox.information(self, "Thành công", f"Đã cập nhật trạng thái cho [{ten_sale}].")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PhanMemTapHoa()
    window.show()
    sys.exit(app.exec())