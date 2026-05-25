#!/usr/bin/env python3
"""
Mentor4Trading – Community Gruppen Bot
- Neue Mitglieder begrüßen
- Chat überwachen (Links, Werbung, Bilder, Beleidigungen)
- Auf häufige Fragen automatisch antworten
"""

import requests
import os
import time
import re
from datetime import datetime
import pytz
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
BOT_TOKEN        = os.environ.get("BOT_TOKEN", "")
GROUP_ID         = os.environ.get("GROUP_ID", "")
YOUR_USER_ID     = os.environ.get("YOUR_USER_ID", "")
ANTHROPIC_KEY    = os.environ.get("ANTHROPIC_API_KEY", "")
TIMEZONE         = "Europe/Berlin"
BOT_USERNAME     = "JarvisCommunityBot"
# ─────────────────────────────────────────────

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

BANNED_WORDS = [
    "idiot", "dummkopf", "arschloch", "wichser", "hurensohn",
    "scheiß", "fuck", "asshole", "bastard", "vollidiot",
    "depp", "trottel", "versager", "loser", "wixxer",
    "fuck you", "f*you", "fick dich"
]

AUTO_REPLIES = [
    {
        "keywords": ["indikator", "indicator", "smc entry", "entry finder", "pine script"],
        "reply": (
            "🎯 *SMC Entry Finder V5*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Den Indikator findest du hier:\n"
            "🔗 [mentor4trading.netlify.app/indikator](https://mentor4trading.netlify.app/indikator.html)\n\n"
            "✅ Live Dashboard · Session & Bias\n"
            "✅ Entry Zone Visualisierung\n"
            "✅ Signal Filter mit Alerts\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 Jarvis | @mentor4trading\\_signals"
        )
    },
    {
        "keywords": ["wann signal", "wann kommen", "nächstes signal", "next signal", "wann trade", "signal"],
        "reply": (
            "⏰ *Wann kommen Signale?*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Signale kommen wenn das Setup stimmt –\n"
            "nicht auf Kommando\\! 📊\n\n"
            "🕐 *Trading Zeiten:*\n"
            "• London Session: 08:00 – 12:00\n"
            "• New York Session: 14:30 – 21:00\n\n"
            "Nur A\\+ Setups werden gepostet\\.\n"
            "Kein FOMO, kein Overtrading\\.\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 Jarvis | @mentor4trading\\_signals"
        )
    },
    {
        "keywords": ["wie trade", "wie funktioniert", "smc erklär", "was ist smc", "was ist ict", "wie lerne", "smc", "ict"],
        "reply": (
            "📚 *SMC/ICT Basics*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Alles über SMC & ICT gibt es hier:\n"
            "📱 TikTok: @mentor4trading\n"
            "🎮 Twitch: twitch.tv/mentor4trading\n\n"
            "Kostenlos reinschauen & lernen\\!\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 Jarvis | @mentor4trading\\_signals"
        )
    },
    {
        "keywords": ["orb", "opening range", "opening range breakout"],
        "reply": (
            "📊 *ORB Strategie*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Das komplette ORB Ebook gibt es hier:\n"
            "🔗 [mentor4trading.netlify.app](https://mentor4trading.netlify.app)\n\n"
            "Opening Range Breakout \\+ Retest\n"
            "Alles erklärt mit echten Chart\\-Beispielen\\!\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 Jarvis | @mentor4trading\\_signals"
        )
    },
    {
        "keywords": ["website", "homepage", "seite", "wo finde"],
        "reply": (
            "🌐 *Mentor4Trading Website*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🔗 [mentor4trading.netlify.app](https://mentor4trading.netlify.app)\n\n"
            "📊 Indikator · ORB Ebook · Guides\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 Jarvis | @mentor4trading\\_signals"
        )
    },
    {
        "keywords": ["kanal", "signal kanal", "telegram kanal", "signale kanal"],
        "reply": (
            "📲 *Signal Kanal*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Live Trades direkt auf dein Handy:\n"
            "👉 @mentor4trading\\_signals\n\n"
            "✅ Entry, SL & TP in Echtzeit\n"
            "✅ Täglicher Wirtschaftskalender\n"
            "✅ Weekly Recap jeden Freitag\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 Jarvis | @mentor4trading\\_signals"
        )
    },
    {
        "keywords": ["mnq", "mes", "futures", "micro futures", "instrument", "instrumente", "was wird getradet", "was tradet"],
        "reply": (
            "📈 *Gehandelte Instrumente*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Wir traden hauptsächlich:\n"
            "• *MNQ* – Micro E\\-Mini Nasdaq\n"
            "• *MES* – Micro E\\-Mini S&P 500\n\n"
            "Kleine Margin, volle Bewegung\\!\n"
            "Perfekt für Anfänger & Fortgeschrittene\\.\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 Jarvis | @mentor4trading\\_signals"
        )
    },
    {
        "keywords": ["social", "tiktok", "twitch", "youtube", "stream", "video", "content"],
        "reply": (
            "📱 *Content Plattformen*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "📱 TikTok: @mentor4trading\n"
            "🎮 Twitch: twitch.tv/mentor4trading\n\n"
            "Kostenlos reinschauen & lernen\\!\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 Jarvis | @mentor4trading\\_signals"
        )
    },
]

WELCOME_PUBLIC = (
    "👋 Willkommen {name}\\! Schreib mir einfach wenn du Fragen hast 🤖"
    "🤖 *Jarvis KI:*\n"
    "Schreib einfach @JarvisCommunityBot \\+ deine Frage\\!\n"
    "Ich beantworte alles rund um SMC & Trading\\!\n\n"
    "📲 Signal Kanal: @mentor4trading\\_signals\n"
)

WELCOME_PRIVATE = (
    "👋 *Willkommen in der Mentor4Trading Community, {name}\\!*\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "Schön dass du dabei bist\\! 🎉\n\n"
    "📌 *Regeln:*\n"
    "❌ Keine Links oder Werbung\n"
    "❌ Keine Beleidigungen\n"
    "❌ Keine Bilder/Videos\n"
    "✅ Respektvoller Umgang\n"
    "✅ Trading Fragen jederzeit\n\n"
    "💬 *Wenn du Fragen hast einfach tippen:*\n\n"
    "📊 `Indikator` – Info zum SMC Entry Finder\n"
    "⏰ `Signale` – Wann & wie Signale kommen\n"
    "📈 `Instrumente` – Was wird getradet\n"
    "📚 `SMC` oder `ICT` – Strategie Erklärung\n"
    "🌐 `Website` – Link zur Homepage\n"
    "📱 `Social` – TikTok & Twitch Links\n"
    "📖 `ORB` – ORB Strategie Info\n\n"
    "🤖 *Jarvis KI:*\n"
    "Schreib einfach @JarvisCommunityBot \\+ deine Frage\\!\n"
    "Ich beantworte alles rund um SMC & Trading\\!\n\n"
    "📲 Signal Kanal: @mentor4trading\\_signals\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "🤖 Jarvis | Mentor4Trading"
)


def ask_claude(question, username):
    """Schickt Frage an Claude API und gibt Antwort zurück"""
    try:
        system_prompt = """Du bist Jarvis, der KI-Assistent von Mentor4Trading.
Du hilfst Tradern bei Fragen rund um SMC/ICT Trading, Futures und die Mentor4Trading Community.

Wichtige Infos über Mentor4Trading:
- Gehandelt werden MNQ und MES (Micro E-Mini Futures)
- Strategie: SMC/ICT – CHoCH, BOS, FVG, Liquidity
- Trading Zeiten: London 08:00-12:00, New York 14:30-21:00
- Indikator: SMC Entry Finder V5 – kostenlos auf mentor4trading.netlify.app
- TikTok: @mentor4trading | Twitch: twitch.tv/mentor4trading
- Signal Kanal: @mentor4trading_signals

Antworte immer auf Deutsch, freundlich und kompetent.
Halte Antworten kurz und präzise – maximal 3-4 Sätze.
Beende jede Antwort mit: 🤖 Jarvis | @mentor4trading_signals"""

        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 300,
                "system": system_prompt,
                "messages": [
                    {"role": "user", "content": f"{username} fragt: {question}"}
                ]
            },
            timeout=30
        )
        data = r.json()
        return data["content"][0]["text"]
    except Exception as e:
        print(f"[ERROR] Claude API: {e}")
        return "🤖 Jarvis ist gerade nicht verfügbar – versuch es später nochmal!"


def send_message(chat_id, text, reply_to=None):
    payload = {
        "chat_id":    chat_id,
        "text":       text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    if reply_to:
        payload["reply_to_message_id"] = reply_to
    try:
        requests.post(f"{BASE_URL}/sendMessage", json=payload, timeout=10)
    except Exception as e:
        print(f"[ERROR] sendMessage: {e}")


def delete_message(chat_id, message_id):
    try:
        requests.post(f"{BASE_URL}/deleteMessage", json={
            "chat_id":    chat_id,
            "message_id": message_id
        }, timeout=10)
    except Exception as e:
        print(f"[ERROR] deleteMessage: {e}")


def mute_user(chat_id, user_id):
    try:
        until = int(time.time()) + 3600
        requests.post(f"{BASE_URL}/restrictChatMember", json={
            "chat_id":     chat_id,
            "user_id":     user_id,
            "until_date":  until,
            "permissions": {
                "can_send_messages":         False,
                "can_send_media_messages":   False,
                "can_send_polls":            False,
                "can_send_other_messages":   False,
                "can_add_web_page_previews": False,
                "can_change_info":           False,
                "can_invite_users":          False,
                "can_pin_messages":          False
            }
        }, timeout=10)
    except Exception as e:
        print(f"[ERROR] mute: {e}")


def is_admin(chat_id, user_id):
    try:
        r = requests.get(f"{BASE_URL}/getChatMember", params={
            "chat_id": chat_id,
            "user_id": user_id
        }, timeout=10)
        status = r.json().get("result", {}).get("status", "")
        return status in ("administrator", "creator")
    except:
        return False


def handle_new_members(msg, chat_id):
    new_members = msg.get("new_chat_members", [])
    for member in new_members:
        if member.get("is_bot"):
            continue
        name    = member.get("first_name", "Trader")
        user_id = member.get("id")
        # Kurze öffentliche Begrüßung
        send_message(chat_id, WELCOME_PUBLIC.format(name=name))
        # Ausführliche private Nachricht
        send_message(user_id, WELCOME_PRIVATE.format(name=name))


def has_link(text):
    return bool(re.search(r'(https?://|www\.|t\.me/|@\w+\.(com|de|net|io))', text, re.IGNORECASE))


def has_banned_word(text):
    text_lower = text.lower()
    return any(word in text_lower for word in BANNED_WORDS)


def check_auto_reply(text, chat_id, message_id):
    text_lower = text.lower()
    for item in AUTO_REPLIES:
        if any(kw in text_lower for kw in item["keywords"]):
            send_message(chat_id, item["reply"], reply_to=message_id)
            return True
    return False


def handle_update(update):
    msg = update.get("message", {})
    if not msg:
        return

    # Weitergeleitete Kanal-Nachrichten ignorieren
    if msg.get("forward_from_chat"):
        return
    if msg.get("sender_chat"):
        return

    # Neue Mitglieder begrüßen
    if msg.get("new_chat_members"):
        handle_new_members(msg, msg.get("chat", {}).get("id"))
        return

    chat_id    = str(msg.get("chat", {}).get("id", ""))
    message_id = msg.get("message_id")
    user       = msg.get("from", {})
    user_id    = str(user.get("id", ""))
    username   = user.get("username", user.get("first_name", "User"))
    text       = msg.get("text", "")
    photo      = msg.get("photo")
    video      = msg.get("video")
    document   = msg.get("document")
    sticker    = msg.get("sticker")

    # Bots ignorieren
    if user.get("is_bot"):
        return

    # Admins: nur Auto-Reply
    if is_admin(chat_id, user_id):
        if text:
            check_auto_reply(text, chat_id, message_id)
        return

    # Bilder/Videos/Dateien löschen
    if photo or video or document or sticker:
        delete_message(chat_id, message_id)
        mute_user(chat_id, user_id)
        send_message(chat_id,
            f"🔇 *@{username} wurde stummgeschaltet\\!*\n"
            f"⚠️ Grund: Medien nicht erlaubt\n"
            f"📌 Bitte die Regeln beachten\\!\n"
            f"🤖 Jarvis | Mentor4Trading"
        )
        return

    if text:
        # Bot Erwähnung → Claude antworten lassen
        if f"@{BOT_USERNAME}".lower() in text.lower():
            question = text.lower().replace(f"@{BOT_USERNAME}".lower(), "").strip()
            if question:
                username = user.get("first_name", "Trader")
                answer   = ask_claude(question, username)
                send_message(chat_id, answer, reply_to=message_id)
                return

        if has_link(text):
            delete_message(chat_id, message_id)
            mute_user(chat_id, user_id)
            send_message(chat_id,
                f"🔇 *@{username} wurde stummgeschaltet\\!*\n"
                f"⚠️ Grund: Links & Werbung verboten\n"
                f"📌 Bitte die Regeln beachten\\!\n"
                f"🤖 Jarvis | Mentor4Trading"
            )
            return

        if has_banned_word(text):
            delete_message(chat_id, message_id)
            mute_user(chat_id, user_id)
            send_message(chat_id,
                f"🔇 *@{username} wurde stummgeschaltet\\!*\n"
                f"⚠️ Grund: Beleidigungen nicht toleriert\n"
                f"📌 Respektvoller Umgang bitte\\!\n"
                f"🤖 Jarvis | Mentor4Trading"
            )
            return

        check_auto_reply(text, chat_id, message_id)


def main():
    print(f"[{datetime.now()}] Gruppen Bot startet...")

    if not BOT_TOKEN or not GROUP_ID:
        print("[ERROR] BOT_TOKEN oder GROUP_ID fehlt in .env!")
        return

    offset = 0
    print("[OK] Bot läuft – überwacht die Gruppe...")

    while True:
        try:
            r = requests.get(f"{BASE_URL}/getUpdates", params={
                "offset":  offset,
                "timeout": 5
            }, timeout=10)

            updates = r.json().get("result", [])
            for update in updates:
                offset = update["update_id"] + 1
                handle_update(update)

        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
