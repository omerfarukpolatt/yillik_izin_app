# ui/izin_view.py
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
from database.db_manager import baglanti_ac
from services.leave_logic import tatil_mi_veya_pazar_mi
from ui.components import ModernDatePicker

class IzinPage:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.create_widgets()

    def create_widgets(self):
        lbl = ctk.CTkLabel(self.parent, text="Toplu İzin Tarih Aralığı Girişi", font=ctk.CTkFont(size=18, weight="bold"))
        lbl.pack(pady=15, padx=20, anchor="w")
        
        form_card = ctk.CTkFrame(self.parent, fg_color="#2b2b2b", corner_radius=10)
        form_card.pack(fill="x", padx=20, pady=10)
        
        with baglanti_ac() as conn:
            personeller = conn.execute("SELECT id, ad_soyad FROM personeller ORDER BY ad_soyad ASC").fetchall()
        
        p_dict = {f"{p[1]} (ID: {p[0]})": p[0] for p in personeller}
        
        lbl_p = ctk.CTkLabel(form_card, text="Personel Seç:")
        lbl_p.pack(pady=5, padx=15, anchor="w")
        
        self.combo_p = ctk.CTkOptionMenu(form_card, values=list(p_dict.keys()) if p_dict else ["Kayıt Yok"], width=300)
        self.combo_p.pack(pady=5, padx=15, anchor="w")
        self.p_dict = p_dict
        
        lbl_b = ctk.CTkLabel(form_card, text="Başlangıç Tarihi:")
        lbl_b.pack(pady=5, padx=15, anchor="w")
        self.cal_baslangic = ModernDatePicker(form_card)
        self.cal_baslangic.pack(pady=5, padx=15, anchor="w")
        
        lbl_bt = ctk.CTkLabel(form_card, text="Bitiş Tarihi:")
        lbl_bt.pack(pady=5, padx=15, anchor="w")
        self.cal_bitis = ModernDatePicker(form_card)
        self.cal_bitis.pack(pady=5, padx=15, anchor="w")
        
        btn_kaydet = ctk.CTkButton(form_card, text="İzin Aralığını İşle ve Kaydet", command=self.izin_isle, height=40, fg_color="#2fa572")
        btn_kaydet.pack(pady=20, padx=15, anchor="w")

    def izin_isle(self):
        secilen = self.combo_p.get()
        if not secilen or secilen == "Kayıt Yok":
            messagebox.showwarning("Uyarı", "Lütfen geçerli bir personel seçin!")
            return
        p_id = self.p_dict[secilen]
        
        d1_str = self.cal_baslangic.get()
        d2_str = self.cal_bitis.get()
        
        try:
            d1 = datetime.strptime(d1_str, "%d.%m.%Y")
            d2 = datetime.strptime(d2_str, "%d.%m.%Y")
            
            if d2 < d1:
                messagebox.showerror("Hata", "Bitiş tarihi başlangıçtan önce olamaz!")
                return
            
            curr = d1
            islenen_gun = 0
            atlanan_tatil_gunu = 0
            
            with baglanti_ac() as conn:
                while curr <= d2:
                    t_str = curr.strftime("%d.%m.%Y")
                    tatil_mi, _ = tatil_mi_veya_pazar_mi(t_str)
                    
                    if tatil_mi:
                        atlanan_tatil_gunu += 1
                    else:
                        kayit = conn.execute("SELECT id FROM gunluk_izinler WHERE personel_id = ? AND tarih = ?", (p_id, t_str)).fetchone()
                        if not kayit:
                            conn.execute("INSERT INTO gunluk_izinler (personel_id, tarih) VALUES (?, ?)", (p_id, t_str))
                            islenen_gun += 1
                            
                    curr += timedelta(days=1)
                
                if islenen_gun > 0:
                    conn.execute("UPDATE personeller SET kalan_izin = kalan_izin - ? WHERE id = ?", (islenen_gun, p_id))
                
                conn.commit()
            
            messagebox.showinfo("Başarılı", f"{islenen_gun} günlük izin işlendi.\n({atlanan_tatil_gunu} gün Pazar/Resmi tatil olduğu için izinden düşülmedi.)")
            
        except Exception as e:
            messagebox.showerror("Hata", f"İşlem hatası: {e}")