# database/db_manager.py
import sqlite3
from config import DB_PATH

def baglanti_ac():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with baglanti_ac() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS personeller (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad_soyad TEXT NOT NULL,
                giris_tarihi TEXT NOT NULL,
                kalan_izin REAL NOT NULL DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS gunluk_izinler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                personel_id INTEGER NOT NULL,
                tarih TEXT NOT NULL,
                FOREIGN KEY(personel_id) REFERENCES personeller(id) ON DELETE CASCADE,
                UNIQUE(personel_id, tarih)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS hakedis_gecmisi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                personel_id INTEGER NOT NULL,
                hakedis_yili INTEGER NOT NULL,
                FOREIGN KEY(personel_id) REFERENCES personeller(id) ON DELETE CASCADE,
                UNIQUE(personel_id, hakedis_yili)
            )
        """)