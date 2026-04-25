#!/usr/bin/env python3
# ReTeKZ Discord Selfbot
# ⚠️ UYARI: Selfbot kullanımı Discord ToS'a aykırıdır!
# GitHub: github.com/adimxz/ReTeKZ

import requests
from time import sleep
from sms import SendSms
import random
import string
from datetime import datetime
import json
import os

# ============= KONFIGURASYON =============
TOKEN = ""  # Discord token'in (selfbot)
CHAT_ID = ""  # Sohbet ID'si (string veya int)
PREFIX = "."
MAX_SMS = 75  # Maksimum SMS
MIN_SMS = 10  # Minimum SMS
DEFAULT_SMS = 55
COOLDOWN = 60  # Saniye cinsinden cooldown
SLEEP_TIME = 0  # SMS aralığı (saniye)

# Renk kodları (terminal için)
R = "\033[91m"
G = "\033[92m"
Y = "\033[93m"
B = "\033[94m"
C = "\033[96m"
W = "\033[0m"

# Bot durumu
STATUS_MESSAGES = [
    "ReTeKZ Selfbot",
    f"{PREFIX}sms 5051234567",
    f"{len([m for m in dir(SendSms) if callable(getattr(SendSms, m)) and not m.startswith('__')])} Servis"
]

# Log dosyası
LOG_FILE = "selfbot_log.txt"

def log_yaz(mesaj):
    """Log kaydı tut"""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {mesaj}\n")
    except:
        pass

def print_banner():
    """Banner göster"""
    print(f"""{C}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ██████╗ ███████╗████████╗███████╗██╗  ██╗███████╗         ║
║   ██╔══██╗██╔════╝╚══██╔══╝╚══███╔╝██║ ██╔╝╚══███╔╝         ║
║   ██████╔╝█████╗     ██║     ███╔╝ █████╔╝   ███╔╝          ║
║   ██╔══██╗██╔══╝     ██║    ███╔╝  ██╔═██╗  ███╔╝           ║
║   ██║  ██║███████╗   ██║   ███████╗██║  ██╗███████╗         ║
║   ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝         ║
║                                                              ║
║         DISCORD SELFBOT v2.0 | @ReTeKZ                       ║
║         ⚠️  KULLANIM RISKLI - DİKKAT!  ⚠️                    ║
╚══════════════════════════════════════════════════════════════╝{W}
    """)

def get_headers(token=None, content_type="application/json"):
    """Header oluştur"""
    headers = {
        "Content-Type": content_type,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    if token:
        headers["Authorization"] = token
    return headers

def send_message(token, channel_id, text):
    """Mesaj gönder"""
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    headers = get_headers(token)
    payload = {"content": text, "nonce": "", "tts": False}
    
    try:
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code == 200:
            return True
        else:
            log_yaz(f"Mesaj gönderilemedi: {r.status_code} - {r.text}")
            return False
    except Exception as e:
        log_yaz(f"Hata: {e}")
        return False

def edit_message(token, channel_id, message_id, text):
    """Mesaj düzenle"""
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}"
    headers = get_headers(token)
    payload = {"content": text}
    
    try:
        r = requests.patch(url, headers=headers, json=payload)
        return r.status_code == 200
    except:
        return False

def get_messages(token, channel_id, limit=50):
    """Son mesajları al"""
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit={limit}"
    headers = get_headers(token)
    
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return r.json()
        return []
    except:
        return []

def update_status(token):
    """Bot durumunu güncelle"""
    url = "https://discord.com/api/v9/users/@me/settings"
    headers = get_headers(token)
    status = random.choice(STATUS_MESSAGES)
    payload = {"custom_status": {"text": status}}
    
    try:
        requests.patch(url, headers=headers, json=payload)
    except:
        pass

# Servisleri topla
servisler_sms = []
for attribute in dir(SendSms):
    if callable(getattr(SendSms, attribute)) and not attribute.startswith('__'):
        servisler_sms.append(attribute)

# Cooldown takibi
cooldown_users = {}
processed_messages = set()

def main():
    print_banner()
    
    # Token kontrolü
    if TOKEN == "":
        print(f"{R}[!] HATA: Token bulunamadı!{W}")
        print(f"{Y}[*] discord-selfbot.py dosyasını aç ve TOKEN = \"\" yerine tokenini yaz{W}")
        return
    
    if CHAT_ID == "":
        print(f"{R}[!] HATA: Chat ID bulunamadı!{W}")
        print(f"{Y}[*] CHAT_ID = \"\" yerine sohbet ID'sini yaz{W}")
        return
    
    print(f"{G}[+] Selfbot başlatılıyor...{W}")
    print(f"{C}[+] Token: {TOKEN[:20]}...{W}")
    print(f"{C}[+] Chat ID: {CHAT_ID}{W}")
    print(f"{C}[+] Servis Sayısı: {len(servisler_sms)}{W}")
    print(f"{C}[+] Prefix: {PREFIX}{W}")
    print(f"{G}[+] Selfbot aktif!{W}\n")
    
    log_yaz("Selfbot başlatıldı")
    
    last_message_id = None
    status_update_time = 0
    
    while True:
        try:
            # Her 5 dakikada bir durum güncelle
            if status_update_time == 0 or (datetime.now().timestamp() - status_update_time) > 300:
                update_status(TOKEN)
                status_update_time = datetime.now().timestamp()
            
            messages = get_messages(TOKEN, CHAT_ID, limit=10)
            
            if not messages:
                sleep(1)
                continue
            
            for msg in messages:
                msg_id = msg["id"]
                content = msg.get("content", "")
                author_id = msg["author"]["id"]
                
                # Kendi mesajımızı kontrol etme
                if msg_id in processed_messages:
                    continue
                
                # Selfbot kontrolü (kendi mesajlarımızı işleme)
                if author_id == msg["author"].get("id") and msg.get("webhook_id") is None:
                    # Kendi mesajıysa işleme
                    processed_messages.add(msg_id)
                    continue
                
                # Komut kontrolü
                if content.startswith(PREFIX):
                    komut = content[len(PREFIX):].strip().lower()
                    
                    # SMS komutu
                    if komut.startswith("sms"):
                        parts = komut.split()
                        if len(parts) >= 2:
                            telno = parts[1].replace(" ", "").replace("-", "")
                            
                            # Adet kontrolü
                            sms_adet = DEFAULT_SMS
                            if len(parts) >= 3:
                                try:
                                    sms_adet = int(parts[2])
                                    if sms_adet > MAX_SMS:
                                        sms_adet = MAX_SMS
                                    if sms_adet < MIN_SMS:
                                        sms_adet = MIN_SMS
                                except:
                                    pass
                            
                            # Telefon formatı kontrolü
                            if telno.isdigit() and len(telno) == 10:
                                # Cooldown kontrolü
                                if author_id in cooldown_users:
                                    gecen = (datetime.now().timestamp() - cooldown_users[author_id])
                                    if gecen < COOLDOWN:
                                        kalan = int(COOLDOWN - gecen)
                                        send_message(TOKEN, CHAT_ID, f"⏰ {author_id} lütfen {kalan} saniye bekle!")
                                        processed_messages.add(msg_id)
                                        continue
                                
                                cooldown_users[author_id] = datetime.now().timestamp()
                                log_yaz(f"SMS başlatıldı: {telno} - {sms_adet} adet - Kullanıcı: {author_id}")
                                
                                # Başlangıç mesajı
                                baslangic_msg = f"📱 **ReTeKZ SMS Bomber**\n📞 Numara: `+90{telno}`\n🎯 Hedef: `{sms_adet}`\n🔄 Servis: `{len(servisler_sms)}`\n⏳ Durum: **Başlatılıyor...**\n<@{author_id}>"
                                
                                send_message(TOKEN, CHAT_ID, baslangic_msg)
                                
                                # SMS gönder
                                sms = SendSms(telno, "")
                                gonderilen = 0
                                
                                for metod in servisler_sms:
                                    if gonderilen >= sms_adet:
                                        break
                                    try:
                                        getattr(sms, metod)()
                                        gonderilen += 1
                                    except:
                                        pass
                                    
                                    if SLEEP_TIME > 0:
                                        sleep(SLEEP_TIME)
                                
                                # Sonuç mesajı
                                if gonderilen > 0:
                                    sonuc_msg = f"✅ **SMS Gönderimi Tamamlandı!**\n📞 Numara: `+90{telno}`\n✅ Gönderilen: `{gonderilen}/{sms_adet}`\n📡 Servis: `{len(servisler_sms)}`\n<@{author_id}>"
                                else:
                                    sonuc_msg = f"❌ **HATA!**\n📞 Numara: `+90{telno}`\n❌ SMS gönderilemedi!\n<@{author_id}>"
                                
                                send_message(TOKEN, CHAT_ID, sonuc_msg)
                                log_yaz(f"SMS tamamlandı: {telno} - {gonderilen}/{sms_adet}")
                                
                            else:
                                send_message(TOKEN, CHAT_ID, f"❌ Hatalı numara: `{telno}`\nÖrnek: `{PREFIX}sms 5051234567 55`\n<@{author_id}>")
                        else:
                            send_message(TOKEN, CHAT_ID, f"📖 Kullanım: `{PREFIX}sms <numara> <adet>`\nÖrnek: `{PREFIX}sms 5051234567 55`\n<@{author_id}>")
                    
                    # Help komutu
                    elif komut == "help" or komut == "yardim":
                        help_text = f"""
**📖 ReTeKZ Selfbot Komutları**

`{PREFIX}sms <numara> <adet>` - SMS gönder
`{PREFIX}info` - Bot bilgisi
`{PREFIX}servisler` - Servis listesi
`{PREFIX}ping` - Ping kontrolü
`{PREFIX}status` - Durum değiştir
`{PREFIX}help` - Bu menü

**📱 Örnek:** `{PREFIX}sms 5051234567 55`
**⚠️ Maksimum SMS:** {MAX_SMS}
**⏱️ Cooldown:** {COOLDOWN} saniye

<@{author_id}>
"""
                        send_message(TOKEN, CHAT_ID, help_text)
                    
                    # Info komutu
                    elif komut == "info":
                        info_text = f"""
**🤖 ReTeKZ Selfbot v2.0**

👨‍💻 **Geliştirici:** github.com/adimxz
📦 **Servis Sayısı:** {len(servisler_sms)}
⚡ **Maksimum SMS:** {MAX_SMS}
⏱️ **Cooldown:** {COOLDOWN} saniye
🔧 **Prefix:** {PREFIX}

⚠️ **UYARI:** Selfbot kullanımı risklidir!

<@{author_id}>
"""
                        send_message(TOKEN, CHAT_ID, info_text)
                    
                    # Servisler komutu
                    elif komut == "servisler":
                        servis_list = "\n".join([f"• `{s}`" for s in servisler_sms[:15]])
                        if len(servisler_sms) > 15:
                            servis_list += f"\n... ve {len(servisler_sms) - 15} servis daha"
                        
                        servis_text = f"**📋 Mevcut Servisler ({len(servisler_sms)})**\n\n{servis_list}\n\n<@{author_id}>"
                        send_message(TOKEN, CHAT_ID, servis_text)
                    
                    # Ping komutu
                    elif komut == "ping":
                        send_message(TOKEN, CHAT_ID, f"🏓 Pong! <@{author_id}>")
                    
                    # Status komutu
                    elif komut.startswith("status"):
                        new_status = komut[6:].strip()
                        if new_status:
                            url = "https://discord.com/api/v9/users/@me/settings"
                            headers = get_headers(TOKEN)
                            payload = {"custom_status": {"text": new_status}}
                            try:
                                requests.patch(url, headers=headers, json=payload)
                                send_message(TOKEN, CHAT_ID, f"✅ Durum değiştirildi: `{new_status}`\n<@{author_id}>")
                            except:
                                send_message(TOKEN, CHAT_ID, f"❌ Durum değiştirilemedi!\n<@{author_id}>")
                        else:
                            send_message(TOKEN, CHAT_ID, f"📖 Kullanım: `{PREFIX}status <mesaj>`\n<@{author_id}>")
                
                processed_messages.add(msg_id)
                
                # Çok fazla mesaj birikmesin
                if len(processed_messages) > 1000:
                    processed_messages.clear()
            
            sleep(1)
            
        except Exception as e:
            log_yaz(f"Hata: {e}")
            sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{R}[!] Selfbot durduruldu.{W}")
        log_yaz("Selfbot durduruldu")
