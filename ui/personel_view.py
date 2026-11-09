# ui/personel_view.py
import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
from database.db_manager import baglanti_ac
from services.leave_logic import otomatik_hakedis_guncelle, tatil_mi_veya_pazar_mi
from ui.components import ModernDatePicker, ToolTip

class PersonelPage:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.create_widgets()

    def create_widgets(self):
        lbl = ctk.CTkLabel(self.parent, text="Personel Yönetimi (Personelin üzerine tıklayın ve Matrisi Aç deyin)", font=ctk.CTkFont(size=15, weight="bold"))
        lbl.pack(pady=15, padx=20, anchor="w")
        
        form_card = ctk.CTkFrame(self.parent, fg_color="#2b2b2b", corner_radius=10)
        form_card.pack(fill="x", padx=20, pady=5)
        
        self.ent_ad = ctk.CTkEntry(form_card, placeholder_text="Ad Soyad", width=180, height=35)
        self.ent_ad.pack(side="left", padx=10, pady=12)
        
        lbl_tarih = ctk.CTkLabel(form_card, text="Giriş:", font=ctk.CTkFont(size=12))
        lbl_tarih.pack(side="left", padx=2)
        
        self.cal_giris = ModernDatePicker(form_card)
        self.cal_giris.pack(side="left", padx=5, pady=12)
        
        self.ent_izin = ctk.CTkEntry(form_card, placeholder_text="Başlangıç İzin (Boş=0)", width=140, height=35)
        self.ent_izin.pack(side="left", padx=10, pady=12)
        
        btn_ekle = ctk.CTkButton(form_card, text="＋ Yeni Ekle", command=self.personel_ekle, fg_color="#2fa572", hover_color="#248259", width=100, height=35)
        btn_ekle.pack(side="left", padx=5, pady=12)

        btn_duzenle = ctk.CTkButton(form_card, text="✏️ Düzenle", command=self.personel_duzenle_pencere, fg_color="#d68910", hover_color="#b7770d", width=100, height=35)
        btn_duzenle.pack(side="left", padx=5, pady=12)
        
        btn_365_ac = ctk.CTkButton(form_card, text="🔍 Matrisi Aç", command=self.e_okul_tablosunu_ac, fg_color="#1f6aa5", hover_color="#174d7a", width=110, height=35)
        btn_365_ac.pack(side="left", padx=5, pady=12)

        table_frame = ctk.CTkFrame(self.parent, fg_color="#1f1f1f", corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2a2a2a", foreground="white", fieldbackground="#2a2a2a", rowheight=30, font=('Segoe UI', 10))
        style.configure("Treeview.Heading", background="#333333", foreground="white", font=('Segoe UI', 11, 'bold'))
        style.map("Treeview", background=[('selected', '#1f6aa5')])
        
        self.tree = ttk.Treeview(table_frame, columns=("ID", "Ad Soyad", "Giriş Tarihi", "Kalan İzin (Gün)"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Ad Soyad", text="Ad Soyad")
        self.tree.heading("Giriş Tarihi", text="Giriş Tarihi")
        self.tree.heading("Kalan İzin (Gün)", text="Kalan İzin Gün")
        
        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Ad Soyad", width=300, anchor="w")
        self.tree.column("Giriş Tarihi", width=200, anchor="center")
        self.tree.column("Kalan İzin (Gün)", width=150, anchor="center")
        
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree.bind("<Double-1>", lambda event: self.e_okul_tablosunu_ac())
        
        self.personelleri_listele()

    def get_secilen_personel(self):
        selected_items = self.tree.selection()
        if selected_items:
            vals = self.tree.item(selected_items[0]).get('values')
            if vals: return vals
        
        focused = self.tree.focus()
        if focused:
            vals = self.tree.item(focused).get('values')
            if vals: return vals
                
        children = self.tree.get_children()
        if children:
            vals = self.tree.item(children[0]).get('values')
            if vals: return vals
                
        return None

    def personel_ekle(self):
        ad = self.ent_ad.get().strip()
        tarih = self.cal_giris.get()
        izin_str = self.ent_izin.get().strip()
        
        if not ad:
            messagebox.showwarning("Eksik Bilgi", "Lütfen personelin ad soyad bilgisini girin!")
            return
            
        try:
            izin = float(izin_str) if izin_str else 0.0
        except ValueError:
            messagebox.showerror("Hata", "İzin gün sayısı sayısal bir değer olmalıdır!")
            return
            
        try:
            with baglanti_ac() as conn:
                conn.execute("INSERT INTO personeller (ad_soyad, giris_tarihi, kalan_izin) VALUES (?, ?, ?)", (ad, tarih, izin))
                conn.commit()
            messagebox.showinfo("Başarılı", f"{ad} başarıyla eklendi.")
            self.ent_ad.delete(0, 'end')
            self.ent_izin.delete(0, 'end')
            otomatik_hakedis_guncelle()
            self.personelleri_listele()
        except Exception as e:
            messagebox.showerror("Hata", f"Kayıt eklenirken hata: {e}")

    def personel_duzenle_pencere(self):
        p_vals = self.get_secilen_personel()
        if not p_vals:
            messagebox.showwarning("Seçim Yok", "Lütfen tablodan düzenlemek istediğiniz personele tıklayın!")
            return
            
        p_id, ad, tarih, kalan = p_vals
        
        edit_win = ctk.CTkToplevel(self.parent)
        edit_win.title(f"Personel Düzenle: {ad}")
        edit_win.geometry("420x340")
        edit_win.grab_set()
        
        lbl = ctk.CTkLabel(edit_win, text="Personel Bilgilerini Güncelle", font=ctk.CTkFont(size=16, weight="bold"))
        lbl.pack(pady=15)
        
        ent_ad_edit = ctk.CTkEntry(edit_win, width=280, height=35)
        ent_ad_edit.pack(pady=8)
        ent_ad_edit.insert(0, ad)
        
        cal_edit = ModernDatePicker(edit_win)
        cal_edit.pack(pady=8)
        cal_edit.set_date(tarih)
            
        ent_izin_edit = ctk.CTkEntry(edit_win, width=280, height=35)
        ent_izin_edit.pack(pady=8)
        ent_izin_edit.insert(0, str(kalan))
        
        def kaydet():
            yeni_ad = ent_ad_edit.get().strip()
            yeni_tarih = cal_edit.get()
            yeni_izin_str = ent_izin_edit.get().strip()
            
            try:
                yeni_izin = float(yeni_izin_str) if yeni_izin_str else 0.0
            except ValueError:
                messagebox.showerror("Hata", "İzin gün sayısı sayısal olmalıdır!")
                return
            
            with baglanti_ac() as conn:
                conn.execute("UPDATE personeller SET ad_soyad = ?, giris_tarihi = ?, kalan_izin = ? WHERE id = ?", 
                             (yeni_ad, yeni_tarih, yeni_izin, p_id))
                conn.commit()
            messagebox.showinfo("Başarılı", "Personel güncellendi.")
            edit_win.destroy()
            self.personelleri_listele()
            
        btn_save = ctk.CTkButton(edit_win, text="Değişiklikleri Kaydet", command=kaydet, height=38, fg_color="#2fa572")
        btn_save.pack(pady=20)

    def personelleri_listele(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        with baglanti_ac() as conn:
            personeller = conn.execute("SELECT id, ad_soyad, giris_tarihi, kalan_izin FROM personeller ORDER BY ad_soyad ASC").fetchall()
        
        for p in personeller:
            self.tree.insert("", "end", values=p)

    def e_okul_tablosunu_ac(self):
        p_vals = self.get_secilen_personel()
        if not p_vals:
            messagebox.showwarning("Seçim Yok", "Lütfen tablodan bir personele tıklayarak seçin!")
            return
            
        p_id, ad, tarih, kalan_baslangic = p_vals
        
        win = ctk.CTkToplevel(self.parent)
        win.title(f"{ad} - 365 Günlük İzin Matrisi")
        win.geometry("950x700")
        win.grab_set()
        
        lbl_info = ctk.CTkLabel(win, text=f"{ad} - 2026 Yıllık Matris\n(Pazartesi Başlar, Pazar En Sağdadır | Kırmızı: Gerçek İzinli Günler)", font=ctk.CTkFont(size=13, weight="bold"))
        lbl_info.pack(pady=10)
        
        yil = 2026
        aylar = {1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran", 
                 7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"}
        
        scroll_frame = ctk.CTkScrollableFrame(win, width=900, height=550, fg_color="#1a1a1a")
        scroll_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        for m in range(1, 13):
            month_frame = ctk.CTkFrame(scroll_frame, fg_color="#242424", corner_radius=8)
            month_frame.pack(fill="x", padx=10, pady=8)
            
            lbl_ay = ctk.CTkLabel(month_frame, text=f"{aylar[m]} {yil}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#3498db")
            lbl_ay.grid(row=0, column=0, columnspan=7, sticky="w", padx=10, pady=(8, 4))
            
            hafta_gunleri = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
            for col_idx, g_ad in enumerate(hafta_gunleri):
                lbl_g = ctk.CTkLabel(month_frame, text=g_ad, font=ctk.CTkFont(size=11, weight="bold"), text_color="#aaaaaa", width=105)
                lbl_g.grid(row=1, column=col_idx, padx=2, pady=2)
                
            first_day = datetime(yil, m, 1)
            next_month = datetime(yil + 1, 1, 1) if m == 12 else datetime(yil, m + 1, 1)
            days_in_month = (next_month - first_day).days
            start_col = first_day.weekday()
            
            row_idx = 2
            col_idx = start_col
            
            for day_num in range(1, days_in_month + 1):
                curr_date = datetime(yil, m, day_num)
                tarih_str = curr_date.strftime("%d.%m.%Y")
                tatil_mi, tatil_tipi = tatil_mi_veya_pazar_mi(tarih_str)
                
                def tikla(t_s=tarih_str, t_t=tatil_tipi, btn=None):
                    if t_t == "Pazar (Hafta Tatili)" or t_t == "Resmi Tatil":
                        durum = messagebox.askyesno("Tatil Günü Uyarısı", f"Bu gün '{t_t}' olarak tanımlı. Yine de izin olarak işlemek istiyor musunuz?", parent=win)
                        if not durum: return
                    
                    ToolTip.hide_global()
                    self.gunluk_izin_toggle(p_id, t_s)
                    
                    with baglanti_ac() as conn:
                        is_izinli_simdi = conn.execute("SELECT id FROM gunluk_izinler WHERE personel_id = ? AND tarih = ?", (p_id, t_s)).fetchone() is not None
                    
                    if is_izinli_simdi:
                        btn.configure(text=f"{t_s[:2]}\nİzinli", fg_color="#c0392b", hover_color="#962d22")
                    elif t_t == "Pazar (Hafta Tatili)":
                        btn.configure(text=f"{t_s[:2]}\nPazar", fg_color="#4a235a", hover_color="#5b2c6f")
                    elif t_t == "Resmi Tatil":
                        btn.configure(text=f"{t_s[:2]}\nTatil", fg_color="#b9770e", hover_color="#d68910")
                    else:
                        btn.configure(text=f"{t_s[:2]}\nÇalışma", fg_color="#2a2a2a", hover_color="#3a3a3a")
                    
                    self.personelleri_listele()

                with baglanti_ac() as conn:
                    is_izinli = conn.execute("SELECT id FROM gunluk_izinler WHERE personel_id = ? AND tarih = ?", (p_id, tarih_str)).fetchone() is not None
                
                if is_izinli:
                    btn_text, btn_color, hover_color = f"{day_num:02d}\nİzinli", "#c0392b", "#962d22"
                    tooltip_text = f"Tarih: {tarih_str}\nDurum: Yıllık İzin Kullanıldı"
                elif tatil_tipi == "Pazar (Hafta Tatili)":
                    btn_text, btn_color, hover_color = f"{day_num:02d}\nPazar", "#4a235a", "#5b2c6f"
                    tooltip_text = f"Tarih: {tarih_str}\nDurum: Pazar (Hafta Tatili)"
                elif tatil_tipi == "Resmi Tatil":
                    btn_text, btn_color, hover_color = f"{day_num:02d}\nTatil", "#b9770e", "#d68910"
                    tooltip_text = f"Tarih: {tarih_str}\nDurum: Resmi Tatil ({tatil_tipi})"
                else:
                    btn_text, btn_color, hover_color = f"{day_num:02d}\nÇalışma", "#2a2a2a", "#3a3a3a"
                    tooltip_text = f"Tarih: {tarih_str}\nDurum: Çalışma Günü"
                
                btn_gun = ctk.CTkButton(month_frame, text=btn_text, width=105, height=50, fg_color=btn_color, hover_color=hover_color, font=('Segoe UI', 10, 'bold'))
                btn_gun.configure(command=lambda ts=tarih_str, tt=tatil_tipi, b=btn_gun: tikla(ts, tt, b))
                btn_gun.grid(row=row_idx, column=col_idx, padx=2, pady=2)
                ToolTip(btn_gun, lambda tt=tooltip_text: tt)
                
                col_idx += 1
                if col_idx > 6:
                    col_idx = 0
                    row_idx += 1

    def gunluk_izin_toggle(self, p_id, tarih_str):
        with baglanti_ac() as conn:
            kayit = conn.execute("SELECT id FROM gunluk_izinler WHERE personel_id = ? AND tarih = ?", (p_id, tarih_str)).fetchone()
            if kayit:
                conn.execute("DELETE FROM gunluk_izinler WHERE id = ?", (kayit[0],))
                conn.execute("UPDATE personeller SET kalan_izin = kalan_izin + 1 WHERE id = ?", (p_id,))
            else:
                conn.execute("INSERT INTO gunluk_izinler (personel_id, tarih) VALUES (?, ?)", (p_id, tarih_str))
                conn.execute("UPDATE personeller SET kalan_izin = kalan_izin - 1 WHERE id = ?", (p_id,))
            conn.commit()   