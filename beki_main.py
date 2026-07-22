import asyncio
from pyrogram import Client, filters

# ===== የአንተ መረጃዎች =====
API_ID = 37468042
API_HASH = "49635e8940adec0c1661229e9ad56a81"
MY_ADMIN_ID = 6391190160

app = Client("my_guard_account", api_id=API_ID, api_hash=API_HASH)

pending_users = {}

AUTO_REPLY_TEXT = (
    "ሰላም! 👋\n\n"
    "ወደ Bereket አካውንት እንኳን ደህና መጡ።\n"
    "እባክዎን ከእኔ ጋር ለመነጋገር የመጡበትን **ዋና ምክንያት/ሀሳብ** እዚህ ይጻፉ።\n\n"
    "መልእክትዎ ሲደርሰኝ አይቼ ከተስማማሁ ውይይቱን እጀምራለሁ።"
)

@app.on_message(filters.private & ~filters.me & ~filters.bot)
async def handle_incoming(client, message):
    user_id = message.from_user.id
    
    if pending_users.get(user_id) == "APPROVED":
        return

    if user_id not in pending_users:
        pending_users[user_id] = "WAITING_FOR_REASON"
        await message.reply_text(AUTO_REPLY_TEXT)
        return

    if pending_users.get(user_id) == "WAITING_FOR_REASON":
        reason = message.text
        pending_users[user_id] = "PENDING_APPROVAL"
        
        user_info = (
            f"👤 **አዲስ ሰው መነጋገር ይፈልጋል!**\n\n"
            f"• **ስም:** {message.from_user.first_name}\n"
            f"• **Username:** @{message.from_user.username}\n"
            f"• **ID:** `{user_id}`\n\n"
            f"📝 **የመጣበት ምክንያት:**\n{reason}\n\n"
            f"-----------------------------------\n"
            f"👉 **ለመፍቀድ ይላኩ:** `/ok {user_id}`\n"
            f"👉 **ለማገድ ይላኩ:** `/no {user_id}`"
        )
        
        await client.send_message("me", user_info)
        await message.reply_text("አመሰግናለሁ! የቀረበው ሀሳብ ተልኳል። ምላሽ እስኪያገኝ ድረስ ይቆዩ።")

@app.on_message(filters.me & filters.command(["ok", "no"]))
async def handle_approval(client, message):
    try:
        command = message.command[0]
        target_user_id = int(message.command[1])

        if command == "ok":
            pending_users[target_user_id] = "APPROVED"
            await message.reply_text(f"✅ ለ `{target_user_id}` ፈቅደሃል። አሁን ማውራት ትችላላችሁ።")
            await client.send_message(target_user_id, "ሀሳብዎ ተቀባይነት አግኝቷል! አሁን መነጋገር ይችላሉ።")
        
        elif command == "no":
            pending_users[target_user_id] = "DENIED"
            await message.reply_text(f"❌ ለ `{target_user_id}` ውድቅ ተደርጓል።")
            await client.send_message(target_user_id, "ይቅርታ፣ በአሁኑ ወቅት ጥያቄዎን መቀበል አልተቻለም።")
            
    except Exception as e:
        await message.reply_text("⚠️ እባክዎን ትክክለኛ ቅርጽ ይጠቀሙ! (ምሳሌ፡ `/ok 12345678`)")

print("🤖 ቦቱ በስኬት ስራ ጀምሯል!")
app.run()
