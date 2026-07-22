import asyncio
from telethon import TelegramClient, events

# 1. Python Asyncio Event Loop Fix (ለ Render ሰርቨር ተስማሚ ለማድረግ)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# 2. የቴሌግራም API መረጃዎችህ
api_id = 20779777
api_hash = 'ed5f0e388147d4e339ffca9e504c5a9b'

# Telegram Client ማስነሳት
client = TelegramClient('my_guard_account', api_id, api_hash, loop=loop)

# 3. አዲሱ የመልእክት ፅሁፍ
RESPONSE_TEXT = """ሰላም! 👋

ወደ Beki  አካውንት እንኳን ደህና መጡ።
እባክዎን ከእኔ ጋር ለመነጋገር የመጡበትን ዋና ምክንያት/ሀሳብ እዚህ ይጻፉ።

መልእክትዎ ሲደርሰኝ አሳውቄ ነግረዎታለው ።"""

@client.on(events.NewMessage(incoming=True))
async def handle_new_message(event):
    # ግሩፕ ወይም ቻናል ከሆነ ምንም አይልካም (ለግል መልእክት ብቻ)
    if not event.is_private:
        return

    sender = await event.get_sender()
    
    # የላከው ሰው ከስልክህ ኮንታክት (Contact) ውጪ ከሆነ ብቻ መልእክት ይልካል
    if sender and not getattr(sender, 'contact', False):
        await event.reply(RESPONSE_TEXT)

print("Bot is running...")
client.start()
client.run_until_disconnected()

