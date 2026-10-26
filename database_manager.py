# file: database_manager.py
import sqlite3

class DatabaseManager:
    def __init__(self, db_path='quanly_taphoa.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self._khoi_tao_db()

    def close(self):
        if self.conn:
            self.conn.close()

    def _khoi_tao_db(self):
        """Tự động nâng cấp bảng và tạo dữ liệu mẫu nếu DB trống"""
        self.cursor.execute("PRAGMA table_info(Nha_Phan_Phoi)")
        cac_cot = [col[1] for col in self.cursor.fetchall()]
        if 'trang_thai' not in cac_cot:
            self.cursor.execute("ALTER TABLE Nha_Phan_Phoi ADD COLUMN trang_thai INTEGER DEFAULT 1")
        
        # Tự động tạo bảng quản lý Hóa đơn nếu chưa có
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Hoa_Don (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ngay_ban DATETIME DEFAULT CURRENT_TIMESTAMP,
                tong_tien INTEGER DEFAULT 0,
                ghi_chu TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Chi_Tiet_Hoa_Don (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_hoa_don INTEGER,
                id_sp INTEGER,
                so_luong INTEGER NOT NULL,
                gia_ban_thuc_te INTEGER NOT NULL,
                thanh_tien INTEGER NOT NULL,
                FOREIGN KEY (id_hoa_don) REFERENCES Hoa_Don(id),
                FOREIGN KEY (id_sp) REFERENCES San_Pham(id)
            )
        """)
        self.conn.commit()
        
        self.cursor.execute("SELECT COUNT(*) FROM Nha_Phan_Phoi")
        if self.cursor.fetchone()[0] == 0:
            npp_mau = [("Đại lý Unilever", "Anh Hùng", "0901.123.456", 1)]
            self.cursor.executemany("INSERT INTO Nha_Phan_Phoi (ten_npp, ten_sale, sdt_sale, trang_thai) VALUES (?, ?, ?, ?)", npp_mau)
            self.conn.commit()
    # ==========================================
    # CÁC HÀM LẤY DỮ LIỆU (SELECT)
    # ==========================================
    def lay_danh_sach_ten_san_pham(self):
        self.cursor.execute("SELECT ten_sp FROM San_Pham")
        return [item[0] for item in self.cursor.fetchall()]

    def lay_danh_sach_npp_hoat_dong(self):
        self.cursor.execute("SELECT DISTINCT ten_npp FROM Nha_Phan_Phoi WHERE ten_npp != 'Khách lẻ / Sale tự do' AND trang_thai = 1")
        return [item[0] for item in self.cursor.fetchall() if item[0]]

    def lay_danh_sach_sale_theo_npp(self, ten_npp_chon):
        self.cursor.execute("SELECT ten_sale, sdt_sale FROM Nha_Phan_Phoi WHERE ten_npp = ? AND trang_thai = 1", (ten_npp_chon,))
        return self.cursor.fetchall()

    def lay_danh_sach_canh_bao(self):
        self.cursor.execute('''
            SELECT sp.ten_sp, sp.ton_kho, npp.ten_npp, npp.ten_sale, npp.sdt_sale
            FROM San_Pham sp LEFT JOIN Nha_Phan_Phoi npp ON sp.id_npp = npp.id
            WHERE sp.ton_kho <= sp.ton_toithieu ORDER BY sp.ton_kho ASC
        ''')
        return self.cursor.fetchall()

    def lay_thong_tin_san_pham_chi_tiet(self, ten_sp):
        self.cursor.execute('''
            SELECT sp.id, sp.ton_kho, sp.gia_ban, npp.ten_npp, npp.ten_sale, npp.sdt_sale
            FROM San_Pham sp LEFT JOIN Nha_Phan_Phoi npp ON sp.id_npp = npp.id 
            WHERE sp.ten_sp = ?''', (ten_sp,)
        )
        return self.cursor.fetchone()

    def lay_lich_su_nhap_gan_nhat(self, id_sp, limit=2):
        self.cursor.execute('''
            SELECT gia_nhap, so_luong, strftime('%d/%m/%Y %H:%M', ngay_nhap) 
            FROM Lich_Su_Nhap WHERE id_sp = ? ORDER BY ngay_nhap DESC, id DESC LIMIT ?
        ''', (id_sp, limit))
        return self.cursor.fetchall()

    def lay_danh_sach_quan_ly_sp(self):
        self.cursor.execute('''
            SELECT sp.id, sp.ten_sp, sp.ton_kho, npp.ten_npp
            FROM San_Pham sp LEFT JOIN Nha_Phan_Phoi npp ON sp.id_npp = npp.id
            ORDER BY sp.id DESC
        ''')
        return self.cursor.fetchall()

    def lay_danh_sach_doi_tac(self):
        self.cursor.execute("SELECT id, ten_npp, ten_sale, sdt_sale, trang_thai FROM Nha_Phan_Phoi ORDER BY trang_thai DESC, id DESC")
        return self.cursor.fetchall()

    def lay_trang_thai_doi_tac(self, npp_id):
        self.cursor.execute("SELECT trang_thai FROM Nha_Phan_Phoi WHERE id = ?", (npp_id,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    # ==========================================
    # CÁC HÀM THÊM / SỬA / XÓA ĐƠN GIẢN
    # ==========================================
    def them_doi_tac(self, ten_npp, ten_sale, sdt):
        self.cursor.execute("INSERT INTO Nha_Phan_Phoi (ten_npp, ten_sale, sdt_sale) VALUES (?, ?, ?)", (ten_npp, ten_sale, sdt))
        self.conn.commit()

    def cap_nhat_san_pham(self, sp_id, ten_moi, ton_moi, npp_moi):
        id_npp = None
        if npp_moi != "Khách lẻ / Sale tự do":
            self.cursor.execute("SELECT id FROM Nha_Phan_Phoi WHERE ten_npp = ? LIMIT 1", (npp_moi,))
            row = self.cursor.fetchone()
            if row: id_npp = row[0]

        self.cursor.execute("UPDATE San_Pham SET ten_sp = ?, ton_kho = ?, id_npp = ? WHERE id = ?", (ten_moi, ton_moi, id_npp, sp_id))
        self.conn.commit()

    def cap_nhat_trang_thai_doi_tac(self, npp_id, tt_moi):
        self.cursor.execute("UPDATE Nha_Phan_Phoi SET trang_thai = ? WHERE id = ?", (tt_moi, npp_id))
        self.conn.commit()

    # ==========================================
    # CÁC HÀM XỬ LÝ NGHIỆP VỤ PHỨC TẠP (CÓ TRANSACTION)
    # ==========================================
    def nghiep_vu_nhap_kho(self, ten_npp, ten_sale, ten_sp, tong_so_luong, gia_von):
        """Xử lý nhập hàng: Kiểm tra, cập nhật tồn kho và lưu lịch sử"""
        try:
            self.cursor.execute("BEGIN TRANSACTION;")
            
            # 1. Tìm ID nhà phân phối
            self.cursor.execute("SELECT id FROM Nha_Phan_Phoi WHERE ten_npp = ? AND ten_sale = ?", (ten_npp, ten_sale))
            id_npp_row = self.cursor.fetchone()
            id_npp = id_npp_row[0] if id_npp_row else None

            # 2. Xử lý Sản phẩm (Cập nhật hoặc Thêm mới)
            self.cursor.execute("SELECT id FROM San_Pham WHERE ten_sp = ?", (ten_sp,))
            sp_row = self.cursor.fetchone()
            
            if sp_row:
                id_sp = sp_row[0]
                self.cursor.execute("UPDATE San_Pham SET ton_kho = ton_kho + ?, id_npp = ? WHERE id = ?", (tong_so_luong, id_npp, id_sp))
            else:
                self.cursor.execute("INSERT INTO San_Pham (ten_sp, ton_kho, id_npp) VALUES (?, ?, ?)", (ten_sp, tong_so_luong, id_npp))
                id_sp = self.cursor.lastrowid

            # 3. Lưu lịch sử nhập
            self.cursor.execute("INSERT INTO Lich_Su_Nhap (id_sp, gia_nhap, so_luong) VALUES (?, ?, ?)", (id_sp, gia_von, tong_so_luong))
            
            self.conn.commit()
            return True, "Thành công"
        except Exception as e:
            self.conn.rollback()
            return False, str(e)

    def nghiep_vu_tru_kho(self, ten_sp, so_luong_tru):
        """Xử lý trừ kho độc lập: Kiểm tra số lượng tồn trước khi trừ"""
        try:
            self.cursor.execute("SELECT id, ton_kho FROM San_Pham WHERE ten_sp = ?", (ten_sp,))
            row = self.cursor.fetchone()
            if not row:
                return False, "Không có sản phẩm này trong kho!"
            
            id_sp, ton_kho = row[0], row[1]
            if ton_kho < so_luong_tru:
                return False, f"Trong kho chỉ còn {ton_kho}!"

            self.cursor.execute("UPDATE San_Pham SET ton_kho = ton_kho - ? WHERE id = ?", (so_luong_tru, id_sp))
            self.conn.commit()
            return True, "Thành công"
        except Exception as e:
            self.conn.rollback()
            return False, str(e)

    def nghiep_vu_xoa_san_pham(self, sp_id):
        """Xóa sản phẩm an toàn: Xóa lịch sử trước, xóa sản phẩm sau"""
        try:
            self.cursor.execute("BEGIN TRANSACTION;")
            self.cursor.execute("DELETE FROM Lich_Su_Nhap WHERE id_sp = ?", (sp_id,))
            self.cursor.execute("DELETE FROM San_Pham WHERE id = ?", (sp_id,))
            self.conn.commit()
            return True, "Thành công"
        except Exception as e:
            self.conn.rollback()
            return False, str(e)

    def lay_thong_tin_sp_ban_hang(self, ten_sp):
        """Lấy ID, giá bán và tồn kho để đưa vào giỏ hàng"""
        self.cursor.execute("SELECT id, gia_ban, ton_kho FROM San_Pham WHERE ten_sp = ?", (ten_sp,))
        return self.cursor.fetchone()

    def nghiep_vu_ban_hang(self, tong_tien, danh_sach_hang):
        """Lưu hóa đơn, lưu chi tiết và trừ tồn kho bằng Transaction an toàn"""
        try:
            self.cursor.execute("BEGIN TRANSACTION;")
            
            self.cursor.execute("INSERT INTO Hoa_Don (tong_tien) VALUES (?)", (tong_tien,))
            id_hoa_don = self.cursor.lastrowid

            for mon in danh_sach_hang:
                # Kiểm tra tồn kho chéo một lần nữa trước khi trừ
                self.cursor.execute("SELECT ton_kho FROM San_Pham WHERE id = ?", (mon['id_sp'],))
                ton_kho = self.cursor.fetchone()[0]
                if ton_kho < mon['so_luong']:
                    raise ValueError(f"Mặt hàng ID {mon['id_sp']} không đủ số lượng (còn {ton_kho}).")

                self.cursor.execute(
                    """INSERT INTO Chi_Tiet_Hoa_Don (id_hoa_don, id_sp, so_luong, gia_ban_thuc_te, thanh_tien) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (id_hoa_don, mon['id_sp'], mon['so_luong'], mon['gia_ban'], mon['thanh_tien'])
                )
                self.cursor.execute(
                    "UPDATE San_Pham SET ton_kho = ton_kho - ? WHERE id = ?",
                    (mon['so_luong'], mon['id_sp'])
                )

            self.conn.commit()
            return True, "Thanh toán thành công!"
        except Exception as e:
            self.conn.rollback()
            return False, f"Lỗi giao dịch: {str(e)}"