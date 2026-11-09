# main.py
import customtkinter as ctk
from database.db_manager import init_db
from services.leave_logic import otomatik_hakedis_guncelle
from ui.components import ToolTip
from ui.personel_view import PersonelPage
from ui.izin_view import IzinPage
from ui.rapor_view import RaporPage
from config import APP_TITLE, WINDOW_SIZE

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class IzinTakipApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        init_db()
        otomatik_hakedis_guncelle()
        
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.setup_sidebar()
        
        self.main_frame = ctk.CTkFrame(self, fg_color="#242424", corner_radius=12)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        
        self.show_personel_page()

    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color="#1a1a1a")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="İK YÖNETİMİ", font=ctk.CTkFont(size=18, weight="bold"))
        self.logo_label.pack(pady=30, padx=10)
        
        menu_btn_style = {"font": ctk.CTkFont(size=13, weight="bold"), "height": 40, "corner_radius": 8}
        
        ctk.CTkButton(self.sidebar_frame, text="👥 Personel & Matris", command=self.show_personel_page, **menu_btn_style).pack(pady=10, padx=15, fill="x")
        ctk.CTkButton(self.sidebar_frame, text="📅 Toplu İzin Girişi", command=self.show_izin_page, **menu_btn_style).pack(pady=10, padx=15, fill="x")
        ctk.CTkButton(self.sidebar_frame, text="📊 Birim İzin Raporu", command=self.show_rapor_page, **menu_btn_style).pack(pady=10, padx=15, fill="x")

    def clear_main_frame(self):
        ToolTip.hide_global()
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_personel_page(self):
        self.clear_main_frame()
        PersonelPage(self.main_frame)

    def show_izin_page(self):
        self.clear_main_frame()
        IzinPage(self.main_frame)

    def show_rapor_page(self):
        self.clear_main_frame()
        RaporPage(self.main_frame)

if __name__ == "__main__":
    app = IzinTakipApp()
    app.mainloop()