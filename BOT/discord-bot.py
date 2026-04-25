#!/usr/bin/env python3
# ReTeKZ Discord SMS Bot
# GitHub: github.com/adimxz/ReTeKZ

import os
from dotenv import load_dotenv

load_dotenv()

import discord
from discord.ext import commands
from time import sleep
from sms import SendSms
import asyncio
import threading
from datetime import datetime
import json

# ============= KONFIGURASYON =============
TOKEN = os.getenv("TOKEN")
PREFIX = "!"
YETKILI_ROLLER = ["Admin", "Moderator", "Owner"]
COOLDOWN_SURESI = 30  # Saniye cinsinden bekleme
MAX_SMS = 100  # Maksimum SMS sayısı
MIN_SMS = 10   # Minimum SMS sayısı
DEFAULT_SMS = 52

# GIF'ler
GIF_LIST = [
    "https://media.tenor.com/SWiGXYOM8eMAAAAC/russia-soviet.gif",
    "https://media.tenor.com/8YQ9Qm4X8ZcAAAAC/bomb-bombing.gif",
    "https://media.tenor.com/2qZxYq8c9fQAAAAC/sms-message.gif"
]

# Kullanıcı cooldown takibi
cooldown_dict = {}

# Bot ayarları
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# Servisleri topla
servisler_sms = []
for attribute in dir(SendSms):
    if callable(getattr(SendSms, attribute)) and not attribute.startswith('__'):
        servisler_sms.append(attribute)

def log_yaz(mesaj):
    """Log kaydı tut"""
    with open("bot_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {mesaj}\n")

@bot.event
async def on_ready():
    print(f"""
╔════════════════════════════════════════╗
║        ReTeKZ DISCORD BOT AKTİF        ║
╠════════════════════════════════════════╣
║  Bot Adı: {bot.user}
║  Servis Sayısı: {len(servisler_sms)}
║  Prefix: {PREFIX}
║  Komutlar: !help, !sms, !info, !stats
╚════════════════════════════════════════╝
    """)
    
    # Bot durumu
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=f"{PREFIX}sms | {len(servisler_sms)} Servis"
        )
    )
    log_yaz("Bot başlatıldı")

def yetki_kontrol(ctx):
    """Yetki kontrolü"""
    for rol in YETKILI_ROLLER:
        if discord.utils.get(ctx.author.roles, name=rol):
            return True
    return ctx.author.guild_permissions.administrator

@bot.command(name="sms")
async def sms_gonder(ctx, telno: str = None, adet: int = DEFAULT_SMS):
    """SMS gönder - Kullanım: !sms 5051234567 [adet]"""
    
    # Telefon kontrolü
    if telno is None:
        embed = discord.Embed(
            title="❌ Hata!",
            description=f"Telefon numarası girmedin!\nKullanım: `{PREFIX}sms 5051234567 52`",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Telefon formatı kontrolü
    telno = telno.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not telno.isdigit() or len(telno) != 10:
        embed = discord.Embed(
            title="❌ Hatalı Numara!",
            description=f"`{telno}` geçerli bir Türkiye numarası değil!\nÖrnek: `5051234567` (10 hane)",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Adet kontrolü
    if adet < MIN_SMS:
        adet = MIN_SMS
    if adet > MAX_SMS:
        adet = MAX_SMS
    
    # Cooldown kontrolü
    user_id = str(ctx.author.id)
    if user_id in cooldown_dict:
        gecen_sure = (datetime.now() - cooldown_dict[user_id]).total_seconds()
        if gecen_sure < COOLDOWN_SURESI:
            kalan = int(COOLDOWN_SURESI - gecen_sure)
            embed = discord.Embed(
                title="⏰ Yavaş Ol!",
                description=f"Lütfen {kalan} saniye bekle ve tekrar dene.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
    
    # Yetki kontrolü (opsiyonel)
    if not yetki_kontrol(ctx):
        embed = discord.Embed(
            title="⚠️ Yetki Yok!",
            description=f"Bu komutu kullanmak için yetkin yok.\nGerekli roller: {', '.join(YETKILI_ROLLER)}",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        return
    
    # SMS gönderme başlıyor
    cooldown_dict[user_id] = datetime.now()
    log_yaz(f"{ctx.author} - {telno} - {adet} adet SMS istedi")
    
    # Başlangıç embed'i
    embed = discord.Embed(
        title="📱 SMS BOMBER AKTİF",
        description=f"""
**Telefon:** `+90{telno}`
**Hedef SMS:** `{adet}`
**Mevcut Servis:** `{len(servisler_sms)}`
**Kullanıcı:** {ctx.author.mention}
        """,
        color=discord.Color.blue()
    )
    embed.set_footer(text="ReTeKZ SMS Bomber | @ReTeKZ")
    embed.set_thumbnail(url=GIF_LIST[0])
    await ctx.send(embed=embed)
    
    # SMS gönderme işlemi
    sms = SendSms(telno, "")
    gonderilen = 0
    hata_sayisi = 0
    
    mesaj = await ctx.send(f"🚀 SMS gönderiliyor... (0/{adet})")
    
    for metod in servisler_sms:
        if gonderilen >= adet:
            break
        try:
            getattr(sms, metod)()
            gonderilen += 1
            hata_sayisi = 0
        except:
            hata_sayisi += 1
            pass
        
        # Her 5 SMS'te bir durum güncelle
        if gonderilen % 5 == 0 or gonderilen == adet:
            await mesaj.edit(content=f"📨 SMS gönderiliyor... ({gonderilen}/{adet})")
        
        await asyncio.sleep(0.5)  # 0.5 saniye bekle
    
    # Sonuç embed'i
    basari_durumu = "✅" if gonderilen > 0 else "❌"
    renk = discord.Color.green() if gonderilen > 0 else discord.Color.red()
    
    embed = discord.Embed(
        title=f"{basari_durumu} SMS Gönderme Tamamlandı!",
        description=f"""
**Telefon:** `+90{telno}`
**Gönderilen:** `{gonderilen}/{adet}`
**Servis Sayısı:** `{len(servisler_sms)}`
**Durum:** {'Başarılı' if gonderilen > 0 else 'Başarısız'}
        """,
        color=renk
    )
    embed.set_footer(text=f"İsteyen: {ctx.author.name} | ReTeKZ")
    embed.set_thumbnail(url=GIF_LIST[1])
    await ctx.send(embed=embed)
    
    log_yaz(f"{ctx.author} - {telno} - {gonderilen}/{adet} SMS gönderildi")

@bot.command(name="help")
async def help_command(ctx):
    """Yardım menüsü"""
    embed = discord.Embed(
        title="📖 ReTeKZ SMS Bot - Yardım Menüsü",
        description="Bu bot ile SMS bombardımanı yapabilirsiniz!",
        color=discord.Color.purple()
    )
    embed.add_field(
        name=f"📱 `{PREFIX}sms`",
        value=f"SMS gönderir.\nKullanım: `{PREFIX}sms 5051234567 52`\n*Adet opsiyonel (min:{MIN_SMS}, max:{MAX_SMS})*",
        inline=False
    )
    embed.add_field(
        name=f"ℹ️ `{PREFIX}info`",
        value="Bot hakkında bilgi gösterir.",
        inline=False
    )
    embed.add_field(
        name=f"📊 `{PREFIX}stats`",
        value="İstatistik gösterir.",
        inline=False
    )
    embed.add_field(
        name=f"❓ `{PREFIX}help`",
        value="Bu menüyü gösterir.",
        inline=False
    )
    embed.add_field(
        name="⚙️ Ayarlar",
        value=f"""
• Maksimum SMS: {MAX_SMS}
• Minimum SMS: {MIN_SMS}
• Cooldown: {COOLDOWN_SURESI} saniye
• Servis Sayısı: {len(servisler_sms)}
        """,
        inline=False
    )
    embed.set_footer(text="ReTeKZ SMS Bomber | @ReTeKZ")
    await ctx.send(embed=embed)

@bot.command(name="info")
async def info_command(ctx):
    """Bot bilgisi"""
    embed = discord.Embed(
        title="🤖 ReTeKZ SMS Bot",
        description="Gelişmiş SMS Bombardıman Botu",
        color=discord.Color.blue()
    )
    embed.add_field(name="👨‍💻 Geliştirici", value="github.com/adimxz", inline=True)
    embed.add_field(name="📦 Servis Sayısı", value=str(len(servisler_sms)), inline=True)
    embed.add_field(name="🕐 Çalışma Süresi", value="Aktif", inline=True)
    embed.add_field(name="⚡ Maksimum SMS", value=str(MAX_SMS), inline=True)
    embed.add_field(name="⏱️ Cooldown", value=f"{COOLDOWN_SURESI} sn", inline=True)
    embed.add_field(name="🔧 Prefix", value=PREFIX, inline=True)
    embed.set_thumbnail(url=GIF_LIST[2])
    await ctx.send(embed=embed)

@bot.command(name="stats")
async def stats_command(ctx):
    """İstatistik göster"""
    total_commands = 0
    try:
        with open("bot_log.txt", "r") as f:
            total_commands = len(f.readlines())
    except:
        pass
    
    embed = discord.Embed(
        title="📊 Bot İstatistikleri",
        color=discord.Color.green()
    )
    embed.add_field(name="📝 Toplam Komut", value=str(total_commands), inline=True)
    embed.add_field(name="🔄 Servis Sayısı", value=str(len(servisler_sms)), inline=True)
    embed.add_field(name="👥 Kullanıcı Sayısı", value=str(len(bot.users)), inline=True)
    embed.add_field(name="💬 Sunucu Sayısı", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="⚙️ Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="🕐 Durum", value="Aktif", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="servisler")
async def servisler_command(ctx):
    """Servis listesi göster"""
    servis_listesi = "\n".join([f"• `{s}`" for s in servisler_sms[:20]])
    if len(servisler_sms) > 20:
        servis_listesi += f"\n... ve {len(servisler_sms) - 20} servis daha"
    
    embed = discord.Embed(
        title="📋 Mevcut Servisler",
        description=servis_listesi,
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Toplam {len(servisler_sms)} servis")
    await ctx.send(embed=embed)

# Bot çalıştır
if __name__ == "__main__":
    if TOKEN == "":
        print("""
╔════════════════════════════════════════╗
║         TOKEN BULUNAMADI!              ║
╠════════════════════════════════════════╣
║  discord-bot.py dosyasını aç ve        ║
║  TOKEN = "" yerine bot tokenini yaz!   ║
╚════════════════════════════════════════╝
        """)
    else:
        bot.run(TOKEN)
