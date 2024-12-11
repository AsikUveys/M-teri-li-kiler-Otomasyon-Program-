import json
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

DATA_FILE = "customers.json"

# Veri dosyasını yükle
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# Veri dosyasını kaydet
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Müşteri ekleme
def add_customer_gui(data):
    name = simpledialog.askstring("Müşteri Ekle", "Müşteri adı ve soyadı:")
    email = simpledialog.askstring("Müşteri Ekle", "E-posta adresi:")
    phone = simpledialog.askstring("Müşteri Ekle", "Telefon numarası (11 haneli):")

    if not name or not email or not phone:
        messagebox.showerror("Hata", "Tüm alanları doldurun!")
        return

    if not phone.isdigit() or len(phone) != 11:
        messagebox.showerror("Hata", "Telefon numarası 11 haneli olmalı!")
        return

    data[name] = {"Email": email, "Telefon": phone, "Siparişler": []}
    save_data(data)
    messagebox.showinfo("Başarılı", f"{name} başarıyla eklendi!")

# Müşteri düzenleme
def edit_customer_gui(data):
    name = simpledialog.askstring("Müşteri Düzenle", "Düzenlemek istediğiniz müşteri adı:")
    if name not in data:
        messagebox.showerror("Hata", "Müşteri bulunamadı!")
        return

    new_name = simpledialog.askstring("Müşteri Düzenle", "Yeni müşteri adı (boş bırakılırsa değiştirilmez):")
    if new_name:
        data[new_name] = data.pop(name)
        name = new_name

    new_email = simpledialog.askstring("Müşteri Düzenle", "Yeni e-posta adresi (boş bırakılırsa değiştirilmez):")
    if new_email:
        data[name]["Email"] = new_email

    new_phone = simpledialog.askstring("Müşteri Düzenle", "Yeni telefon numarası (boş bırakılırsa değiştirilmez):")
    if new_phone and new_phone.isdigit() and len(new_phone) == 11:
        data[name]["Telefon"] = new_phone

    save_data(data)
    messagebox.showinfo("Başarılı", f"{name} başarıyla güncellendi!")

# Müşteri silme
def delete_customer_gui(data):
    name = simpledialog.askstring("Müşteri Sil", "Silmek istediğiniz müşteri adı:")
    if name not in data:
        messagebox.showerror("Hata", "Müşteri bulunamadı!")
        return

    confirm = messagebox.askyesno("Onay", f"{name} adlı müşteri silinecek. Emin misiniz?")
    if confirm:
        del data[name]
        save_data(data)
        messagebox.showinfo("Başarılı", f"{name} başarıyla silindi!")

# Müşteri bilgilerini görüntüleme
def view_customers_gui(data):
    customers_window = tk.Toplevel()
    customers_window.title("Müşteri Listesi")

    text = tk.Text(customers_window, wrap=tk.WORD, width=80, height=25, font=("Arial", 12))
    text.pack(padx=10, pady=10)

    for name, info in data.items():
        text.insert(tk.END, f"Müşteri: {name}\n")
        text.insert(tk.END, f"  E-posta: {info['Email']}\n")
        text.insert(tk.END, f"  Telefon: {info['Telefon']}\n")
        text.insert(tk.END, "  Siparişler:\n")
        for order in info["Siparişler"]:
            text.insert(tk.END, f"    - {order['Sipariş']} ({order['Tarih']})\n")
        text.insert(tk.END, "\n")

    text.configure(state=tk.DISABLED)

# Sipariş ekleme
def add_order_gui(data):
    name = simpledialog.askstring("Sipariş Ekle", "Sipariş eklemek istediğiniz müşteri adı:")
    if name not in data:
        messagebox.showerror("Hata", "Müşteri bulunamadı!")
        return

    order = simpledialog.askstring("Sipariş Ekle", "Sipariş bilgisi:")
    if not order:
        messagebox.showerror("Hata", "Sipariş bilgisi boş bırakılamaz!")
        return

    order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data[name]["Siparişler"].append({"Sipariş": order, "Tarih": order_date})
    save_data(data)
    messagebox.showinfo("Başarılı", f"{order} siparişi {name} için eklendi!")

# E-posta gönderme
def send_email_gui(data):
    name = simpledialog.askstring("E-posta Gönder", "E-posta göndermek istediğiniz müşteri adı:")
    if name not in data:
        messagebox.showerror("Hata", "Müşteri bulunamadı!")
        return

    additional_note = simpledialog.askstring("E-posta Gönder", "Eklemek istediğiniz bir not (isteğe bağlı):")

    email_address = data[name]["Email"]
    orders = "\n".join([f"- {order['Sipariş']} ({order['Tarih']})" for order in data[name]["Siparişler"]])

    body = f"""
    Merhaba {name},

    Siparişleriniz:
    {orders}

    {additional_note if additional_note else ''}

    Teşekkürler!
    """
    subject = "Siparişiniz Hakkında Bilgilendirme"

    sender_email = "your_email@gmail.com"
    sender_password = "your_password"

    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = email_address
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email_address, msg.as_string())
        messagebox.showinfo("Başarılı", f"E-posta başarıyla {name} adlı müşteriye gönderildi.")
    except Exception as e:
        messagebox.showerror("Hata", f"E-posta gönderim hatası: {e}")

# Ana menü arayüzü
def main_menu():
    data = load_data()

    root = tk.Tk()
    root.title("Müşteri Yönetim Sistemi")
    root.geometry("400x500")
    root.configure(bg="#f4f4f4")

    style = ttk.Style()
    style.configure("TButton", font=("Arial", 12), padding=5)

    ttk.Label(root, text="Müşteri Yönetim Sistemi", font=("Arial", 16), background="#f4f4f4").pack(pady=20)

    ttk.Button(root, text="Müşteri Ekle", command=lambda: add_customer_gui(data), width=30).pack(pady=10)
    ttk.Button(root, text="Sipariş Ekle", command=lambda: add_order_gui(data), width=30).pack(pady=10)
    ttk.Button(root, text="Müşterileri Görüntüle", command=lambda: view_customers_gui(data), width=30).pack(pady=10)
    ttk.Button(root, text="Müşteri Bilgilerini Düzenle", command=lambda: edit_customer_gui(data), width=30).pack(pady=10)
    ttk.Button(root, text="Müşteri Sil", command=lambda: delete_customer_gui(data), width=30).pack(pady=10)
    ttk.Button(root, text="E-posta Gönder", command=lambda: send_email_gui(data), width=30).pack(pady=10)
    ttk.Button(root, text="Çıkış", command=root.destroy, width=30).pack(pady=20)

    root.protocol("WM_DELETE_WINDOW", root.destroy)  # Pencereyi kapatırken güvenli kapanış
    root.mainloop()


# Programı başlat
main_menu()
