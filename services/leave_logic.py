# services/leave_logic.py
from datetime import datetime
from config import RESMI_TATILLER_2026
from database.db_manager import baglanti_ac

def parse_tarih(tarih_str):
    tarih_str = str(tarih_str).strip()
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(tarih_str, fmt)
        except ValueError:
            pass
    raise ValueError(f"Geçersiz tarih formatı: {tarih_str}")

def tatil_mi_veya_pazar_mi(tarih_str):
    dt = parse_tarih(tarih_str)
    canonical = dt.strftime("%d.%m.%Y")
    if dt.weekday() == 6:
        return True, "Pazar (Hafta Tatili)"
    if canonical in RESMI_TATILLER_2026:
        return True, "Resmi Tatil"
    return False, ""

def yillik_izin_hakki(hizmet_yili):
    if hizmet_yili <= 5:
        return 14
    if hizmet_yili < 15:
        return 20
    return 26

def otomatik_hakedis_guncelle(bugun=None):
    if bugun is None:
        bugun = datetime.now()
    elif isinstance(bugun, str):
        bugun = parse_tarih(bugun)

    with baglanti_ac() as conn:
        personeller = conn.execute("SELECT id, giris_tarihi FROM personeller").fetchall()

        for p_id, giris_tarihi_str in personeller:
            try:
                giris_tarihi = parse_tarih(giris_tarihi_str)
            except ValueError:
                continue

            for yil in range(giris_tarihi.year + 1, bugun.year + 1):
                try:
                    yildonumu = giris_tarihi.replace(year=yil)
                except ValueError:
                    yildonumu = datetime(yil, 2, 28)

                if bugun < yildonumu:
                    continue

                cur = conn.execute(
                    "INSERT OR IGNORE INTO hakedis_gecmisi (personel_id, hakedis_yili) VALUES (?, ?)",
                    (p_id, yil),
                )
                if cur.rowcount == 1:
                    hizmet_yili = yil - giris_tarihi.year
                    gun = yillik_izin_hakki(hizmet_yili)
                    conn.execute(
                        "UPDATE personeller SET kalan_izin = kalan_izin + ? WHERE id = ?",
                        (gun, p_id),
                    )