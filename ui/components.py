# ui/components.py
import customtkinter as ctk
from datetime import datetime
from tkcalendar import Calendar

class ToolTip:
    active_tooltip = None

    def __init__(self, widget, text_func):
        self.widget = widget
        self.text_func = text_func
        self.tipwindow = None
        self.widget.bind("<Enter>", self.show_tip, add="+")
        self.widget.bind("<Leave>", self.hide_tip, add="+")
        self.widget.bind("<Button-1>", self.hide_tip, add="+")

    def show_tip(self, event=None):
        ToolTip.hide_global()
        text = self.text_func()
        if not text:
            return
        try:
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        except:
            return
            
        self.tipwindow = tw = ctk.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = ctk.CTkLabel(tw, text=text, fg_color="#1f1f1f", text_color="#ffffff", corner_radius=6, padx=10, pady=6, font=('Segoe UI', 11))
        label.pack()
        ToolTip.active_tooltip = self

    def hide_tip(self, event=None):
        if self.tipwindow:
            try:
                self.tipwindow.destroy()
            except:
                pass
            self.tipwindow = None
        if ToolTip.active_tooltip == self:
            ToolTip.active_tooltip = None

    @classmethod
    def hide_global(cls):
        if cls.active_tooltip and cls.active_tooltip.tipwindow:
            try:
                cls.active_tooltip.tipwindow.destroy()
            except:
                pass
            cls.active_tooltip.tipwindow = None
            cls.active_tooltip = None

class ModernDatePicker(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.selected_date_str = datetime.now().strftime("%d.%m.%Y")
        
        self.btn = ctk.CTkButton(self, text=f"📅 {self.selected_date_str}", command=self.open_calendar, width=150, height=35, fg_color="#1f6aa5", hover_color="#174d7a", font=('Segoe UI', 12, 'bold'))
        self.btn.pack(side="left")

    def open_calendar(self):
        top = ctk.CTkToplevel(self)
        top.title("Tarih Seç")
        top.geometry("320x350")
        top.grab_set()
        
        cal = Calendar(top, selectmode='day', year=datetime.now().year, month=datetime.now().month, day=datetime.now().day, locale='tr_TR', background='#1f6aa5', foreground='white', headersbackground='#333333')
        cal.pack(pady=15, padx=15, fill="both", expand=True)
        
        def set_date():
            d = cal.selection_get()
            self.selected_date_str = d.strftime("%d.%m.%Y")
            self.btn.configure(text=f"📅 {self.selected_date_str}")
            top.destroy()
            
        btn_ok = ctk.CTkButton(top, text="Seçimi Onayla", command=set_date, fg_color="#2fa572", height=35)
        btn_ok.pack(pady=10, padx=15, fill="x")

    def get(self):
        return self.selected_date_str

    def set_date(self, date_obj_or_str):
        if isinstance(date_obj_or_str, str):
            self.selected_date_str = date_obj_or_str
        else:
            self.selected_date_str = date_obj_or_str.strftime("%d.%m.%Y")
        self.btn.configure(text=f"📅 {self.selected_date_str}")