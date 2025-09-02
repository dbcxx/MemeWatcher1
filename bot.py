from telethon import TelegramClient, events
import asyncio, os

# ==== CONFIG from environment variable  ====
api_id = int(os.getenv("API_ID"))          # <- Get from https://my.telegram.org
api_hash = os.getenv("API_HASH")          # long string
phone = os.getenv("PHONE")        # <- Your Telegram phone number
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")      # e.g. "elonmuskcoin" (without @)

# ==== FILE STORAGE ====
KEYWORD_FILE = "keywords.txt"

def load_keywords():
    if not os.path.exists(KEYWORD_FILE):
        return []
    with open(KEYWORD_FILE, "r") as f:
        return [line.strip().lower() for line in f if line.strip()]

def save_keywords(words):
    with open(KEYWORD_FILE, "w") as f:
        f.write("\n".join(words))

keywords = load_keywords()

# ==== TELEGRAM CLIENT ====
client = TelegramClient("session_name", api_id, api_hash)

# ---- 1. CHANNEL WATCHER ----
@client.on(events.NewMessage(chats=TARGET_CHANNEL))
async def channel_handler(event):
    global keywords
    message = event.message.message.lower()
    keywords = load_keywords()
    if any(word in message for word in keywords):
        await client.send_message("me", f"⚡ Keyword Alert!\n\n{event.message.message}")

# ---- 2. COMMANDS VIA SAVED MESSAGES ----
@client.on(events.NewMessage(chats="me"))
async def command_handler(event):
    global keywords
    text = event.raw_text.strip().lower()
    if text.startswith("+"):
        word = text[1:].strip()
        if word and word not in keywords:
            keywords.append(word)
            save_keywords(keywords)
            await event.respond(f"✅ Added new keyword: {word}")
    elif text.startswith("-"):
        word = text[1:].strip()
        if word in keywords:
            keywords.remove(word)
            save_keywords(keywords)
            await event.respond(f"❌ Removed keyword: {word}")
    elif text == "!list":
        if keywords:
            await event.respond("📋 Current keywords:\n" + "\n".join(keywords))
        else:
            await event.respond("📋 No keywords set.")

# ---- MAIN ----
async def main():
    print("Starting keyword watcher...")
    await client.start(phone)
    await client.run_until_disconnected()

if name == "main":
    asyncio.run(main())