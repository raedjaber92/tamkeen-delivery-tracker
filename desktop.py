import customtkinter as ctk
from tkinter import messagebox, Toplevel, Label
import tkinter as tk
from PIL import Image, ImageTk
import qrcode
from io import BytesIO
import sqlite3
import datetime
import threading

# ====================== إعدادات ======================
WEB_BASE_URL = "https://YOUR-RENDER-URL.onrender.com"   # ← غيّرها بعد ما تنشر على Render
db_path = "parcels.db"

# ====================== قاعدة البيانات ======================
def create_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS parcels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT,
        recipient_name TEXT,
        address TEXT,
        delivery_date TEXT,
        content TEXT,
        signature_name TEXT,
        status TEXT DEFAULT 'pending',
        photo BLOB,
        confirm_date TEXT
    )''')
    conn.commit()
    conn.close()

def update_old_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try: c.execute("ALTER TABLE parcels ADD COLUMN recipient_name TEXT"); except: pass
    try: c.execute("ALTER TABLE parcels ADD COLUMN signature_name TEXT"); except: pass
    conn.commit()
    conn.close()

create_db()
update_old_db()

# ====================== التطبيق الديسكتوب ======================
class DeliveryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("تمكين للتأمين - نظام تتبع البريد")
        self.geometry("1350x820")
        ctk.set_appearance_mode("dark")

        self.tab_view = ctk.CTkTabview(self, fg_color="#001f3f")
        self.tab_view.pack(fill="both", expand=True, padx=25, pady=25)

        self.tab_view.add("إضافة بريد جديد")
        self.tab_view.add("قائمة البريد")
        self.tab_view.add("توليد QR يومي")

        self.setup_add_tab()
        self.setup_list_tab()
        self.setup_qr_tab()

    # (باقي الدوال كاملة زي النسخة السابقة - setup_add_tab, setup_list_tab, setup_qr_tab, add_parcel, load_parcels, show_photo, filter_list, generate_daily_qr)
    # ... للاختصار، استخدم نفس الدوال من الرد السابق (اللي كان شغال بدون أخطاء) وغيّر فقط سطر generate_daily_qr كالتالي:

    def generate_daily_qr(self):
        if WEB_BASE_URL == "https://YOUR-RENDER-URL.onrender.com":
            messagebox.showerror("خطأ", "غيّر WEB_BASE_URL بالرابط الحقيقي بعد النشر على Render")
            return
        try:
            today_token = datetime.date.today().isoformat()
            qr_url = f"{WEB_BASE_URL}/deliveries?token={today_token}"

            qr = qrcode.QRCode(version=1, box_size=11, border=5)
            qr.add_data(qr_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#001f3f", back_color="#ffffff")

            bio = BytesIO()
            img.save(bio, "PNG")
            bio.seek(0)
            pil_img = Image.open(bio).resize((310, 310))
            tk_img = ImageTk.PhotoImage(pil_img)

            self.qr_label.configure(image=tk_img, text="✅ QR جاهز\nافتحه على هاتف الموظف")
            self.qr_label.image = tk_img

            messagebox.showinfo("تمكين", f"QR كود اليوم جاهز\nالرابط: {qr_url}")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

# ... (انسخ باقي الدوال من الكود السابق: setup_add_tab, setup_list_tab, setup_qr_tab, add_parcel, clear_add_form, load_parcels, show_photo, filter_list)

if __name__ == "__main__":
    app_instance = DeliveryApp()
    app_instance.mainloop()