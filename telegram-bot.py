#!/usr/bin/env python3
# ReTeKZ Telegram SMS Bot
# GitHub: github.com/adimxz/ReTeKZ

import requests
from time import sleep
from sms import SendSms
import threading
from datetime import datetime
import json
import os

# ============= KONFIGURASYON =============
TOKEN = ""  # Bot tokenini buraya yaz (BotFather'dan al)
OWNER_ID = ""  # Sahibin Telegram ID'si (opsiyonel)
PREFIX = "/"
MAX_SMS = 100  # Maksimum SMS
MIN_SMS = 10   # Minimum SMS
DEFAULT_SMS = 52
DEFAULT_DELAY = 0  # Varsayılan bekleme (saniye)

# Renk kodları (terminal için)
R = "\033[91m"
G = "\033[92m"
Y = "\033[93m"
B = "\033[94m"
C = "\033[96m"
W = "\033[0m"

# Kullanıcı işlemleri takibi
user_sessions = {}
cooldown_users = {}

# Log dosyası
LOG_FILE = "telegram_bot_log.txt"

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
║         TELEGRAM SMS BOT v2.0 | @ReTeKZ                      ║
╚══════════════════════════════════════════════════════════════╝{W}
    """)

def bot_api(method, params=None):
    """Telegram API isteği gönder"""
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    try:
        if params:
            r = requests.get(url, params=params, timeout=10)
        else:
            r = requests.get(url, timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception as e:
        log_yaz(f"API Hatası: {e}")
        return None

def send_message(chat_id, text, parse_mode=None):
    """Mesaj gönder"""
    params = {"chat_id": chat_id, "text": text}
    if parse_mode:
        params["parse_mode"] = parse_mode
    return bot_api("sendMessage", params)

def send_typing(chat_id):
    """Yazıyor durumu göster"""
    bot_api("sendChatAction", {"chat_id": chat_id, "action": "typing"})

def get_updates(offset=None):
    """Güncellemeleri al"""
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    return bot_api("getUpdates", params)

# Servisleri topla
servisler_sms = []
for attribute in dir(SendSms):
    if callable(getattr(SendSms, attribute)) and not attribute.startswith('__'):
        servisler_sms.append(attribute)

def sms_gonderme(chat_id, telno, adet, delay):
    """SMS gönderme işlemi (thread'de çalışır)"""
    try:
        send_message(chat_id, f"📱 **SMS Gönderimi Başladı!**\n\n📞 Numara: `+90{telno}`\n🎯 Hedef: `{adet}`\n⏱️ Aralık: `{delay}` saniye\n🔄 Servis: `{len(servisler_sms)}`\n\n⏳ İşlem devam ediyor...", parse_mode="Markdown")
        
        sms = SendSms(telno, "")
        gonderilen = 0
        
        for metod in servisler_sms:
            if gonderilen >= adet:
                break
            try:
                getattr(sms, metod)()
                gonderilen += 1
            except:
                pass
            
            if delay > 0:
                sleep(delay)
        
        # Sonuç mesajı
        if gonderilen > 0:
            send_message(chat_id, f"✅ **SMS Gönderimi Tamamlandı!**\n\n📞 Numara: `+90{telno}`\n✅ Gönderilen: `{gonderilen}/{adet}`\n📡 Servis: `{len(servisler_sms)}`", parse_mode="Markdown")
        else:
            send_message(chat_id, f"❌ **HATA!**\n\n📞 Numara: `+90{telno}`\n❌ SMS gönderilemedi!\n\nSebep: API hatası veya servisler çalışmıyor.", parse_mode="Markdown")
        
        log_yaz(f"SMS tamamlandı: {telno} - {gonderilen}/{adet} - Kullanıcı: {chat_id}")
        
    except Exception as e:
        send_message(chat_id, f"❌ **Beklenmeyen Hata!**\n\n{str(e)}")
        log_yaz(f"Hata: {e}")

def main():
    print_banner()
    
    # Token kontrolü
    if TOKEN == "":
        print(f"{R}[!] HATA: Token bulunamadı!{W}")
        print(f"{Y}[*] telegram-bot.py dosyasını aç ve TOKEN = \"\" yerine tokenini yaz{W}")
        print(f"{Y}[*] BotFather'dan yeni bot alabilirsin: @BotFather{W}")
        return
    
    print(f"{G}[+] Bot başlatılıyor...{W}")
    print(f"{C}[+] Token: {TOKEN[:15]}...{W}")
    print(f"{C}[+] Servis Sayısı: {len(servisler_sms)}{W}")
    print(f"{C}[+] Prefix: {PREFIX}{W}")
    print(f"{C}[+] Maksimum SMS: {MAX_SMS}{W}")
    print(f"{G}[+] Bot aktif!{W}\n")
    
    log_yaz("Telegram bot başlatıldı")
    
    last_update_id = 0
    
    while True:
        try:
            updates = get_updates(last_update_id + 1 if last_update_id else None)
            
            if updates and updates.get("ok"):
                for update in updates.get("result", []):
                    last_update_id = update.get("update_id")
                    message = update.get("message")
                    
                    if not message:
                        continue
                    
                    chat_id = message.get("chat", {}).get("id")
                    text = message.get("text", "")
                    user_id = message.get("from", {}).get("id")
                    username = message.get("from", {}).get("username", "bilinmiyor")
                    
                    if not text:
                        continue
                    
                    log_yaz(f"Mesaj geldi: {username} ({user_id}) - {text[:50]}")
                    
                    # Komutları işle
                    if text.startswith(PREFIX):
                        komut = text[len(PREFIX):].strip().lower()
                        
                        # START komutu
                        if komut == "start":
                            welcome_text = f"""
**🤖 ReTeKZ SMS Bot'a Hoş Geldin!**

📱 Bu bot ile SMS bombardımanı yapabilirsin.

**📖 Komutlar:**
`{PREFIX}sms <numara> <adet> <aralık>` - SMS gönder
`{PREFIX}info` - Bot bilgisi
`{PREFIX}servisler` - Servis listesi
`{PREFIX}help` - Yardım menüsü

**📱 Örnek:** `{PREFIX}sms 5051234567 52 0`

**⚠️ Kurallar:**
• Maksimum SMS: {MAX_SMS}
• Minimum SMS: {MIN_SMS}
• İzinsiz kullanım yasaktır!

**👨‍💻 Geliştirici:** @ReTeKZ
**🔗 GitHub:** github.com/adimxz/ReTeKZ
"""
                            send_message(chat_id, welcome_text, parse_mode="Markdown")
                        
                        # HELP komutu
                        elif komut == "help" or komut == "yardim":
                            help_text = f"""
**📖 ReTeKZ SMS Bot - Yardım Menüsü**

**🔧 Komutlar:**

`{PREFIX}sms <numara> <adet> <aralık>` - SMS gönder
`{PREFIX}info` - Bot bilgisi göster
`{PREFIX}servisler` - Servis listesi göster
`{PREFIX}help` - Bu menüyü göster

**📱 Kullanım Örnekleri:**

• `{PREFIX}sms 5051234567` - (varsayılan: {DEFAULT_SMS} SMS, 0 sn)
• `{PREFIX}sms 5051234567 30` - (30 SMS, 0 sn)
• `{PREFIX}sms 5051234567 50 2` - (50 SMS, 2 sn aralık)

**⚠️ Kurallar:**
• Numara 10 haneli olmalı (5XXXXXXXXX)
• Maksimum SMS: {MAX_SMS}
• Minimum SMS: {MIN_SMS}
• Aralık maksimum: 10 saniye

**📊 İstatistik:**
• Toplam Servis: {len(servisler_sms)}
• Maksimum SMS: {MAX_SMS}

**👨‍💻 Geliştirici:** @ReTeKZ
"""
                            send_message(chat_id, help_text, parse_mode="Markdown")
                        
                        # INFO komutu
                        elif komut == "info":
                            # Toplam kullanıcı sayısını al
                            info_text = f"""
**🤖 ReTeKZ SMS Bot v2.0**

**📊 Bot Bilgileri:**

• **Servis Sayısı:** {len(servisler_sms)}
• **Maksimum SMS:** {MAX_SMS}
• **Minimum SMS:** {MIN_SMS}
• **Varsayılan SMS:** {DEFAULT_SMS}
• **Prefix:** `{PREFIX}`

**👨‍💻 Geliştirici:** @ReTeKZ
**🔗 GitHub:** github.com/adimxz/ReTeKZ

**📖 Komutlar için:** `{PREFIX}help`
"""
                            send_message(chat_id, info_text, parse_mode="Markdown")
                        
                        # SERVISLER komutu
                        elif komut == "servisler":
                            servis_list = "\n".join([f"• `{s}`" for s in servisler_sms[:20]])
                            if len(servisler_sms) > 20:
                                servis_list += f"\n\n... ve {len(servisler_sms) - 20} servis daha"
                            
                            servis_text = f"**📋 Mevcut Servisler ({len(servisler_sms)})**\n\n{servis_list}"
                            send_message(chat_id, servis_text, parse_mode="Markdown")
                        
                        # SMS komutu
                        elif komut.startswith("sms"):
                            send_typing(chat_id)
                            
                            parts = komut.split()
                            
                            if len(parts) < 2:
                                send_message(chat_id, f"❌ **Hatalı Kullanım!**\n\n📖 Doğru kullanım:\n`{PREFIX}sms <numara> <adet> <aralık>`\n\nÖrnek: `{PREFIX}sms 5051234567 52 0`", parse_mode="Markdown")
                                continue
                            
                            telno = parts[1].replace(" ", "").replace("-", "")
                            
                            # Telefon kontrolü
                            if not telno.isdigit() or len(telno) != 10:
                                send_message(chat_id, f"❌ **Hatalı Numara!**\n\n`{telno}` geçerli bir Türkiye numarası değil!\n\n📱 Örnek: `5051234567` (10 hane)", parse_mode="Markdown")
                                continue
                            
                            # Adet kontrolü
                            adet = DEFAULT_SMS
                            if len(parts) >= 3:
                                try:
                                    adet = int(parts[2])
                                    if adet > MAX_SMS:
                                        adet = MAX_SMS
                                        send_message(chat_id, f"⚠️ Maksimum SMS sınırı ({MAX_SMS}) aşıldı, {MAX_SMS} olarak ayarlandı.")
                                    if adet < MIN_SMS:
                                        adet = MIN_SMS
                                        send_message(chat_id, f"⚠️ Minimum SMS sınırı ({MIN_SMS}) altında, {MIN_SMS} olarak ayarlandı.")
                                except:
                                    send_message(chat_id, f"❌ **Hatalı Adet!**\n\nSayısal bir değer girmelisin.\nÖrnek: `{PREFIX}sms {telno} 52 0`", parse_mode="Markdown")
                                    continue
                            
                            # Aralık kontrolü
                            delay = DEFAULT_DELAY
                            if len(parts) >= 4:
                                try:
                                    delay = int(parts[3])
                                    if delay > 10:
                                        delay = 10
                                        send_message(chat_id, f"⚠️ Maksimum aralık 10 saniye, 10 olarak ayarlandı.")
                                    if delay < 0:
                                        delay = 0
                                except:
                                    send_message(chat_id, f"❌ **Hatalı Aralık!**\n\nSayısal bir değer girmelisin.\nÖrnek: `{PREFIX}sms {telno} {adet} 0`", parse_mode="Markdown")
                                    continue
                            
                            # Cooldown kontrolü
                            if user_id in cooldown_users:
                                gecen = (datetime.now().timestamp() - cooldown_users[user_id])
                                if gecen < 30:  # 30 saniye cooldown
                                    kalan = int(30 - gecen)
                                    send_message(chat_id, f"⏰ **Yavaş Ol!**\n\nLütfen {kalan} saniye bekle ve tekrar dene.", parse_mode="Markdown")
                                    continue
                            
                            # SMS göndermeyi başlat
                            cooldown_users[user_id] = datetime.now().timestamp()
                            
                            send_message(chat_id, f"✅ **SMS Gönderimi Başlatılıyor!**\n\n📞 Numara: `+90{telno}`\n🎯 Hedef: `{adet}` SMS\n⏱️ Aralık: `{delay}` saniye\n\n⏳ Lütfen bekleyin...", parse_mode="Markdown")
                            
                            # Thread'de gönder
                            thread = threading.Thread(target=sms_gonderme, args=(chat_id, telno, adet, delay))
                            thread.daemon = True
                            thread.start()
                        
                        # Bilinmeyen komut
                        else:
                            send_message(chat_id, f"❌ **Bilinmeyen Komut!**\n\n📖 Komut listesi için: `{PREFIX}help`", parse_mode="Markdown")
                    
                    else:
                        # Komut olmayan mesajlar
                        send_message(chat_id, f"❓ **Ne demek istedin?**\n\nKomut kullanmak için `{PREFIX}` ile başlayan bir mesaj gönder.\n\n📖 Yardım: `{PREFIX}help`", parse_mode="Markdown")
            
            sleep(1)
            
        except Exception as e:
            log_yaz(f"Döngü hatası: {e}")
            sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{R}[!] Bot durduruldu.{W}")
        log_yaz("Bot durduruldu")
