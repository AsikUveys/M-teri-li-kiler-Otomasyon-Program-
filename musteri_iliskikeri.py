import json
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
def add_customer(data):
    name = input("Müşteri adı ve soyadı: ")
    email = input("Mail adresi: ")

    # Telefon numarası doğrulama
    while True:
        phone = input("Telefon numarası (11 haneli): ")
        if phone.isdigit() and len(phone) == 11:
            break
        else:
            print("Hatalı giriş! Telefon numarası 11 rakamdan oluşmalı.")
    
    data[name] = { "Email": email, "Telefon": phone, "Siparişler": []}
    print(f"{name} eklendi!")

# Sipariş ekleme
def add_order(data):
    name = input("Müşteri adı: ")
    if name in data:
        order = input("Sipariş bilgisi: ")
        order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Tarih ve saat bilgisi
        data[name]["Siparişler"].append({"Sipariş": order, "Tarih": order_date})
        print(f"{order} siparişi {name} için eklendi ({order_date})!")
        updated = True
    else:
        print("Müşteri bulunamadı!")
    if updated:
        save_data(data)
        print("Veriler güncellendi ve kaydedildi.")

# Müşteri düzenleme
def edit_customer(data):
    updated = False
    name = input("Düzenlemek istediğiniz müşteri adı: ")
    if name in data:
        print(f"Mevcut ad: {name}")
        new_name = input("Yeni ad ve soyad (boş bırakılırsa değiştirilmez): ")
        if new_name:
            data[new_name] = data.pop(name)
            name = new_name
            print("Ad başarıyla güncellendi.")
        else:
            print("Ad değişmedi.")

        print(f"Mevcut e-posta: {data[name]['Email']}")
        new_email = input("Yeni e-posta adresi (boş bırakılırsa değiştirilmez): ")
        if new_email:
            if "@" in new_email and "." in new_email:
                data[name]["Email"] = new_email
                print("E-posta adresi güncellendi.")
            else:
                print("Geçerli bir e-posta adresi girin.")
        else:
            print("E-posta adresi değişmedi.")

        print(f"Mevcut telefon numarası: {data[name]['Telefon']}")
        new_phone = input("Yeni telefon numarası (boş bırakılırsa değiştirilmez): ")
        if new_phone:
            if new_phone.isdigit() and len(new_phone) == 11:
                data[name]["Telefon"] = new_phone
                print("Telefon numarası güncellendi.")
            else:
                print("Hatalı giriş! Telefon numarası 11 rakamdan oluşmalı.")
        else:
            print("Telefon numarası değişmedi.")

        # Siparişleri düzenleme
        print("Mevcut siparişler:")
        for idx, order in enumerate(data[name]["Siparişler"], 1):
            print(f"{idx}. {order['Sipariş']} ({order['Tarih']})")
        choice = input("Sipariş eklemek için 'E', silmek için 'S' yazın (ya da boş bırakın): ")
        if choice.lower() == "e":
            new_order = input("Yeni sipariş bilgisi: ")
            order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data[name]["Siparişler"].append({"Sipariş": new_order, "Tarih": order_date})
            print("Sipariş eklendi.")
        elif choice.lower() == "s":
            try:
                order_index = int(input("Silmek istediğiniz sipariş numarası: ")) - 1
                if 0 <= order_index < len(data[name]["Siparişler"]):
                    removed_order = data[name]["Siparişler"].pop(order_index)
                    print(f"{removed_order['Sipariş']} siparişi silindi.")
                else:
                    print("Geçersiz sipariş numarası!")
            except ValueError:
                print("Geçersiz giriş!")
    else:
        print("Müşteri bulunamadı!")

# Müşteri silme
def delete_customer(data):
    name = input("Silmek istediğiniz müşteri adı: ")
    if name in data:
        del data[name]
        print(f"{name} başarıyla silindi!")
    else:
        print("Müşteri bulunamadı!")

# Belirli tarih aralığındaki siparişleri listeleme
def list_orders_by_date(data):
    start_date = input("Başlangıç tarihi (YYYY-MM-DD): ")
    end_date = input("Bitiş tarihi (YYYY-MM-DD): ")
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        print("Hatalı tarih formatı!")
        return

    print("\nBelirtilen tarih aralığındaki siparişler:")
    for name, info in data.items():
        for order in info["Siparişler"]:
            order_date = datetime.strptime(order["Tarih"], "%Y-%m-%d %H:%M:%S")
            if start_date <= order_date <= end_date:
                print(f"Müşteri: {name}, Sipariş: {order['Sipariş']}, Tarih: {order['Tarih']}")

# E-posta gönderme
def send_email(data):
    name = input("E-posta göndermek istediğiniz müşteri adı: ")
    additional_note = input("Müşteriye eklemek istediğiniz bir not var mı? (Boş bırakabilirsiniz): ")
    
    if name in data:
        email_address = data[name]["Email"]
        phone_number = data[name]["Telefon"]
        
        # Siparişler ve tarihlerini hazırlama
        orders = "\n".join([f"- {order['Sipariş']} ({order['Tarih']})" for order in data[name]["Siparişler"]])
        
        # E-posta içeriği
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

        # E-posta oluşturma
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = email_address
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # SMTP sunucusu üzerinden gönderim
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, email_address, msg.as_string())
                print(f"E-posta başarıyla {name} adlı müşteriye gönderildi.")
        except Exception as e:
            print("E-posta gönderim hatası:", e)
    else:
        print("Müşteri bulunamadı!")



# Müşteri bilgilerini görüntüleme
def view_customers(data):
    for name, info in data.items():
        print(f"Müşteri: {name}")
        print(f"Email: {info['Email']}")
        print(f"Telefon: {info['Telefon']}")
        print("Siparişler:")
        for order in info["Siparişler"]:
            print(f"  - {order['Sipariş']} ({order['Tarih']})")

# Menü
def menu():
    data = load_data()
    while True:
        print("\n1. Müşteri Ekle")
        print("2. Sipariş Ekle")
        print("3. Müşteri Bilgilerini Görüntüle")
        print("4. Müşteri Bilgilerini Düzenle")
        print("5. Müşteri Sil")
        print("6. Belirli Tarih Aralığında Siparişleri Listele")
        print("7. E-posta Gönder")
        print("8. Çıkış")
        choice = input("Seçim yapın: ")
        if choice == "1":
            add_customer(data)
        elif choice == "2":
            add_order(data)
        elif choice == "3":
            view_customers(data)
        elif choice == "4":
            edit_customer(data)
        elif choice == "5":
            delete_customer(data)
        elif choice == "6":
            list_orders_by_date(data)
        elif choice == "7":
            send_email(data)
        elif choice == "8":
            save_data(data)
            print("Programdan çıkıldı.")
            break
        else:
            print("Geçersiz seçim!")

menu()
