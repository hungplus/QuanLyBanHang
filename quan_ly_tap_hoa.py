import sqlite3
import os

def create_database():
    # Kết nối đến file database (nếu chưa có, SQLite sẽ tự động tạo file mới)
    db_path = 'quanly_taphoa.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Bật tính năng khóa ngoại (Foreign Key) cho SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Tạo bảng Nhà Phân Phối
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Nha_Phan_Phoi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ten_npp TEXT NOT NULL,
            ten_sale TEXT,
            sdt_sale TEXT
        )
    ''')

    # 2. Tạo bảng Sản Phẩm
    # id_npp là khóa ngoại liên kết với bảng Nha_Phan_Phoi
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS San_Pham (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ten_sp TEXT NOT NULL UNIQUE,
            gia_ban INTEGER DEFAULT 0,
            ton_kho INTEGER DEFAULT 0,
            ton_toithieu INTEGER DEFAULT 5,
            id_npp INTEGER,
            FOREIGN KEY (id_npp) REFERENCES Nha_Phan_Phoi(id)
        )
    ''')

    # 3. Tạo bảng Lịch Sử Nhập Hàng
    # id_sp là khóa ngoại liên kết với bảng San_Pham
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Lich_Su_Nhap (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_sp INTEGER,
            ngay_nhap DATETIME DEFAULT CURRENT_TIMESTAMP,
            gia_nhap INTEGER DEFAULT 0,
            so_luong INTEGER DEFAULT 0,
            FOREIGN KEY (id_sp) REFERENCES San_Pham(id)
        )
    ''')

    # Lưu thay đổi và đóng kết nối
    conn.commit()
    conn.close()
    print(f"Khởi tạo thành công database tại: {os.path.abspath(db_path)}")

if __name__ == '__main__':
    create_database()