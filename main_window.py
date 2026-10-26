from PyQt6.QtWidgets import QMainWindow, QTabWidget, QApplication, QLabel
from PyQt6.QtCore import QEvent, Qt

from database_manager import DatabaseManager
from tab_canh_bao import TabCanhBao
from tab_tra_cuu import TabTraCuu
from tab_ban_hang import TabBanHang
from tab_nhap_hang import TabNhapHang
from tab_quan_ly import TabQuanLy
from tab_doi_tac import TabDoiTac

class PhanMemTapHoa(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        
        self.setWindowTitle('Phần Mềm Quản Lý Tạp Hóa - POS')
        self.resize(1100, 700)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab { font-size: 18px; font-weight: bold; padding: 12px 30px; background-color: #f0f0f0; border: 1px solid #ccc; border-top-left-radius: 8px; border-top-right-radius: 8px;}
            QTabBar::tab:selected { background-color: #3498db; color: white;}
            QWidget { background-color: white; }
        """)

        # 1. KHỞI TẠO CÁC TAB
        self.tab_cb = TabCanhBao(self.db)
        self.tab_tc = TabTraCuu(self.db)
        self.tab_bh = TabBanHang(self.db)
        self.tab_nh = TabNhapHang(self.db)
        self.tab_ql = TabQuanLy(self.db)
        self.tab_dt = TabDoiTac(self.db)

        # 2. LẮP TAB VÀO GIAO DIỆN CHÍNH
        self.tabs.addTab(self.tab_bh, "🛒 Bán hàng (POS)")
        self.tabs.addTab(self.tab_cb, "🚨 Cảnh báo")
        self.tabs.addTab(self.tab_tc, "🔍 Tra cứu")
        self.tabs.addTab(self.tab_nh, "📦 Nhập hàng")
        self.tabs.addTab(self.tab_ql, "⚙️ Quản lý Kho")
        self.tabs.addTab(self.tab_dt, "🤝 Đối tác")
        
        self.setCentralWidget(self.tabs)

        # 3. KẾT NỐI TÍN HIỆU ĐỒNG BỘ DỮ LIỆU
        self.tab_bh.yeu_cau_lam_moi.connect(self.tai_lai_toan_bo_du_lieu)
        self.tab_nh.yeu_cau_lam_moi.connect(self.tai_lai_toan_bo_du_lieu)
        self.tab_ql.yeu_cau_lam_moi.connect(self.tai_lai_toan_bo_du_lieu)
        self.tab_dt.yeu_cau_lam_moi.connect(self.tai_lai_toan_bo_du_lieu)
        
        QApplication.instance().installEventFilter(self)

    def tai_lai_toan_bo_du_lieu(self):
        """Kích hoạt tải lại dữ liệu trên tất cả các tab khi có thay đổi từ một tab bất kỳ"""
        self.tab_cb.tai_du_lieu()
        self.tab_tc.tai_du_lieu()
        self.tab_bh.tai_du_lieu()
        self.tab_nh.tai_du_lieu()
        self.tab_ql.tai_du_lieu()
        self.tab_dt.tai_du_lieu()

    def closeEvent(self, event):
        self.db.close()
        event.accept()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            for lbl in self.findChildren(QLabel):
                if lbl is not obj and lbl.hasSelectedText(): 
                    lbl.setSelection(0, 0)
        return super().eventFilter(obj, event)