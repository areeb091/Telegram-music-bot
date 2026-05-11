import os
import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
import yt_dlp

# --- CREDENTIALS ---
API_ID = 28936791
API_HASH = "ef3a865b0823dff5d3e4cdf6f78f1987"
BOT_TOKEN = "8678473731:AAGhaGeMSVbkGVwrsQbCm6f-0_XVmOkAD0k"
SESSION = "BQG5ilcAGiDWb7lkInPWr1RiXz3OwA7P2RRGV17ButhBp8EwLsFe0_UYxSpWPBKLqsEiIQG8BLZHdInQ69GqvbPD25npSKYnC_w4KoWUBnChBA0cUxrC3uyWa5BBrxbtofZmLAW3NWQFhSwxN4fkYuMjSuw7TPYYCv7vNHKGSSVFDkvTEIVYDMV1hJpqt15YIMxPZZplke-znKbY29A4-nf3M1BRCxcchpUzs4qXSIP2XZz1e4GhrQWyoRK8OYShpHw5FL0liIeR_ERbUZMnFbgxS04NSenSCPe86900iJFJ2BN8eFyMwGG8bXv_BzKVMDqKoA1NaSrml5JPyiARUl_H6FKXZQAAAAHWDBORAA"

# Initialize Bot (For commands)
app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Initialize User Assistant (To join VC)
assistant = Client("assistant_account", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)

# Initialize PyTgCalls with the Assistant
call_py = PyTgCalls(assistant)

async def get_audio_link(query):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "default_search": "ytsearch",
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        if info and info.get('entries'):
            entry = info['entries'][0]
            return entry['url'], entry['title']
    return None, None

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("✨ **Music Bot is ready!**\nUse `/play <song name>` in a group.")

@app.on_message(filters.command("play") & filters.group)
async def play(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Song name likho!")

    query = " ".join(message.command[1:])
    m = await message.reply_text("🔎 Searching...")

    link, title = await get_audio_link(query)
    if not link:
        return await m.edit("❌ Song nahi mila.")

    try:
        await call_py.join_group_call(
            message.chat.id,
            AudioPiped(link)
        )
        await m.edit(f"🎶 **Playing Now:**\n`{title}`")
    except Exception as e:
        await m.edit(f"❌ Error: {e}")

@app.on_message(filters.command("stop") & filters.group)
async def stop(client, message):
    try:
        await call_py.leave_group_call(message.chat.id)
        await message.reply_text("⏹ Stopped.")
    except:
        await message.reply_text("❌ Voice chat me nahi hu.")

async def main():
    await app.start()
    await assistant.start()
    await call_py.start()
    print("✅ Bot and Assistant are Online!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
