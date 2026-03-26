from flask import Flask, request
import sqlite3
import datetime

app = Flask(__name__)
db_path = "parcels.db"

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

create_db()

@app.route('/deliveries')
def deliveries():
    token = request.args.get('token')
    today = datetime.date.today().isoformat()
    if token != today:
        return "<h1 style='color:red;text-align:center;margin-top:100px;direction:rtl;'>❌ الكود منتهي الصلاحية<br>اطلب QR جديد من المكتب</h1>"

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT id, client_name, address, delivery_date, content, status FROM parcels WHERE status = 'pending' ORDER BY id DESC")
    parcels = c.fetchall()
    conn.close()

    html = """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تمكين - تسليم البريد</title>
        <style>
            body {font-family: Arial, sans-serif; background: #001f3f; color: #ffffff; margin:0; padding:20px;}
            h1 {color:#d32f2f; text-align:center;}
            .card {background:#002b5c; margin:20px 0; padding:25px; border-radius:18px; box-shadow:0 6px 20px rgba(0,0,0,0.5);}
            input, button {width:100%; padding:14px; margin:10px 0; border-radius:10px; font-size:17px; direction:rtl;}
            button {background:#d32f2f; color:white; border:none; font-weight:bold; cursor:pointer; height:52px;}
            button:hover {background:#b71c1c;}
        </style>
    </head>
    <body>
        <h1>🚚 تمكين للتأمين - تسليم البريد</h1>
    """
    for p in parcels:
        pid, name, addr, ddate, content, status = p
        html += f"""
        <div class="card">
            <h2>{name}</h2>
            <p><strong>العنوان:</strong> {addr}</p>
            <p><strong>تاريخ التسليم:</strong> {ddate}</p>
            <p><strong>المحتوى:</strong> {content[:150]}{'...' if len(content)>150 else ''}</p>
        """
        if status == 'pending':
            html += f"""
            <form action="/confirm/{pid}" method="post" enctype="multipart/form-data">
                <input type="text" name="recipient" placeholder="اسم المستلم" required>
                <input type="text" name="signature_name" placeholder="اسم الموقّع" required>
                <label style="color:#a0d8ff;">📸 صورة التوقيع أو البريد:</label>
                <input type="file" name="photo" accept="image/*" required>
                <button type="submit">✅ تأكيد التسليم</button>
            </form>
            """
        else:
            html += '<p style="color:#4ade80;text-align:center;font-size:20px;">✅ تم التسليم</p>'
        html += "</div>"
    html += "</body></html>"
    return html

@app.route('/confirm/<int:pid>', methods=['POST'])
def confirm(pid):
    recipient = request.form.get('recipient')
    signature_name = request.form.get('signature_name')
    photo_file = request.files.get('photo')
    photo_blob = photo_file.read() if photo_file else None
    confirm_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""UPDATE parcels SET recipient_name=?, signature_name=?, status='completed', 
                 photo=?, confirm_date=? WHERE id=?""",
              (recipient, signature_name, photo_blob, confirm_date, pid))
    conn.commit()
    conn.close()

    return f"""
    <h1 style="color:#4ade80;text-align:center;margin-top:80px;direction:rtl;">✅ تم تأكيد التسليم بنجاح</h1>
    <a href="/deliveries?token={datetime.date.today().isoformat()}" style="display:block;margin:40px auto;width:300px;padding:18px;background:#d32f2f;color:white;text-align:center;border-radius:12px;text-decoration:none;font-size:18px;">العودة إلى قائمة البريد</a>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)