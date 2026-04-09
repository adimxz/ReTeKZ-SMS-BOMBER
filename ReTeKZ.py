from colorama import Fore, Style
from time import sleep
from os import system
from sms import SendSms
import threading

# Servisleri topla (exec yok, direkt çağırma)
servisler_sms = [method for method in dir(SendSms) 
                 if callable(getattr(SendSms, method)) and not method.startswith('__')]

while 1:
    system("cls||clear")
    print(f"""{Fore.LIGHTCYAN_NAME}
██████╗  ███████╗████████╗███████╗██╗  ██╗███████╗
██╔══██╗██╔════╝╚══██╔══╝╚══███╔╝██║ ██╔╝╚══███╔╝
██████╔╝█████╗     ██║     ███╔╝ █████╔╝   ███╔╝ 
██╔══██╗██╔══╝     ██║    ███╔╝  ██╔═██╗  ███╔╝  
██║  ██║███████╗   ██║   ███████╗██║  ██╗███████╗
╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝

    Sms: {len(servisler_sms)}           {Style.RESET_ALL}by {Fore.LIGHTRED_NAME}@ReTeKZ{Style.RESET_ALL}\n  
""")

    try:
        menu = input(f"{Fore.LIGHTMAGENTA_NAME} 1- SMS Gönder (Normal)\n\n 2- SMS Gönder (Turbo)\n\n 3- Çıkış\n\n{Fore.LIGHTYELLOW_NAME} Seçim: ")
        if menu == "":
            continue
        menu = int(menu)
    except ValueError:
        system("cls||clear")
        print(f"{Fore.LIGHTRED_NAME}Hatalı giriş yaptın. Tekrar deneyiniz.{Style.RESET_ALL}")
        sleep(3)
        continue

    if menu == 1:
        system("cls||clear")
        print(f"{Fore.LIGHTYELLOW_NAME}Telefon numarasını başında '+90' olmadan yazınız (Birden çoksa 'enter' tuşuna basınız): {Fore.LIGHTGREEN_NAME}", end="")
        tel_no = input()
        tel_liste = []
        
        if tel_no == "":
            system("cls||clear")
            print(f"{Fore.LIGHTYELLOW_NAME}Telefon numaralarının kayıtlı olduğu dosyanın dizinini yazınız: {Fore.LIGHTGREEN_NAME}", end="")
            dizin = input()
            try:
                with open(dizin, "r", encoding="utf-8") as f:
                    tel_liste = [i.strip() for i in f.read().split("\n") if len(i.strip()) == 10]
            except FileNotFoundError:
                system("cls||clear")
                print(f"{Fore.LIGHTRED_NAME}Hatalı dosya dizini. Tekrar deneyiniz.{Style.RESET_ALL}")
                sleep(3)
                continue
        else:
            if len(tel_no) == 10 and tel_no.isdigit():
                tel_liste.append(tel_no)
            else:
                system("cls||clear")
                print(f"{Fore.LIGHTRED_NAME}Hatalı telefon numarası. Tekrar deneyiniz.{Style.RESET_ALL}")
                sleep(3)
                continue

        system("cls||clear")
        print(f"{Fore.LIGHTYELLOW_NAME}Mail adresi (Bilmiyorsanız 'enter' tuşuna basın): {Fore.LIGHTGREEN_NAME}", end="")
        mail = input()
        if mail and ("@" not in mail or ".com" not in mail):
            system("cls||clear")
            print(f"{Fore.LIGHTRED_NAME}Hatalı mail adresi. Tekrar deneyiniz.{Style.RESET_ALL}")
            sleep(3)
            continue

        system("cls||clear")
        print(f"{Fore.LIGHTYELLOW_NAME}Kaç saniye aralıkla göndermek istiyorsun: {Fore.LIGHTGREEN_NAME}", end="")
        try:
            aralik = int(input())
        except ValueError:
            system("cls||clear")
            print(f"{Fore.LIGHTRED_NAME}Hatalı giriş yaptın. Tekrar deneyiniz.{Style.RESET_ALL}")
            sleep(3)
            continue

        system("cls||clear")
        
        for phone in tel_liste:
            sms = SendSms(phone, mail)
            for method_name in servisler_sms:
                getattr(sms, method_name)()
                sleep(aralik)

        print(f"{Fore.LIGHTRED_NAME}\nMenüye dönmek için 'enter' tuşuna basınız..{Style.RESET_ALL}")
        input()

    elif menu == 2:
        system("cls||clear")
        print(f"{Fore.LIGHTYELLOW_NAME}Telefon numarasını başında '+90' olmadan yazınız: {Fore.LIGHTGREEN_NAME}", end="")
        tel_no = input()
        if len(tel_no) != 10 or not tel_no.isdigit():
            system("cls||clear")
            print(f"{Fore.LIGHTRED_NAME}Hatalı telefon numarası. Tekrar deneyiniz.{Style.RESET_ALL}")
            sleep(3)
            continue

        system("cls||clear")
        print(f"{Fore.LIGHTYELLOW_NAME}Mail adresi (Bilmiyorsanız 'enter' tuşuna basın): {Fore.LIGHTGREEN_NAME}", end="")
        mail = input()
        if mail and ("@" not in mail or ".com" not in mail):
            system("cls||clear")
            print(f"{Fore.LIGHTRED_NAME}Hatalı mail adresi. Tekrar deneyiniz.{Style.RESET_ALL}")
            sleep(3)
            continue

        system("cls||clear")
        send_sms = SendSms(tel_no, mail)
        stop_event = threading.Event()

        def turbo_gonder():
            while not stop_event.is_set():
                threads = []
                for method_name in servisler_sms:
                    t = threading.Thread(target=getattr(send_sms, method_name), daemon=True)
                    threads.append(t)
                    t.start()
                for t in threads:
                    t.join()

        try:
            turbo_gonder()
        except KeyboardInterrupt:
            stop_event.set()
            system("cls||clear")
            print(f"\n{Fore.LIGHTRED_NAME}Ctrl+C tuş kombinasyonu algılandı. Menüye dönülüyor..{Style.RESET_ALL}")
            sleep(2)

    elif menu == 3:
        system("cls||clear")
        print(f"{Fore.LIGHTRED_NAME}Çıkış yapılıyor...{Style.RESET_ALL}")
        break
