# ui/rapor_view.py
import customtkinter as ctk
from database.db_manager import baglanti_ac

class RaporPage:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.create_widgets()

    def create_widgets(self):
        lbl = ctk.CTkLabel(self.parent, text="Birimler İçin Toplu İzin Listesi Raporu", font=ctk.CTkFont(size=18, weight="bold"))
        lbl.pack(pady=15, padx=20, anchor="w")
        
        txt_box = ctk.CTkTextbox(self.parent, width=650, height=450, fg_color="#1a1a1a", text_color="white", font=('Consolas', 12))
        txt_box.pack(pady=10, padx=20, fill="both", expand=True)
        
        with baglanti_ac() as conn:
            rows = conn.execute("SELECT ad_soyad, kalan_izin FROM personeller ORDER BY ad_soyad ASC").fetchall()
        
        liste_metni = "========================================\n"
        liste_metni += "       PERSONEL KALAN İZİN LİSTESİ       \n"
        liste_metni += "========================================\n\n"
        
        for r in rows:
            liste_metni += f"• {r[0]:<25} : {r[1]} Gün\n"
            
        txt_box.insert("0.0", liste_metni)
        txt_box.configure(state="disabled") # Kullanıcının rapora yanlışlıkla müdahale etmesini engeller