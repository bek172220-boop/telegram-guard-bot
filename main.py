import asyncio
import time
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
import aiohttp

# --- ማስተካከያ ቦታ ---
TOKEN = "7875031829:AAF198JZic6dK8Uk_nKI5x1c-MctayWKYQA"
# የቲክቶክ ኤፒአይ (ይህ ነፃ ኤፒአይ ነው)
TIKTOK_API_URL = "https://www.tikwm.com/api/"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# የተጠቃሚዎችን የጥበቃ ሰአት መመዝገቢያ (Cooldown Dictionary)
# {user_id: next_allowed_time_timestamp}
cooldowns = {}
# የተጠቃሚዎችን የሊንክ መረጃ ጊዜያዊ ማከማቻ
user_data = {}

# የ24 ሰአት ገደብ በሰከንድ (24 * 60 * 60)
COOLDOWN_DURATION = 86400 

def is_on_cooldown(user_id: int) -> tuple[bool, int]:
    """ተጠቃሚው በ24 ሰአት ገደብ ውስጥ መሆኑን ያረጋግጣል"""
    current_time = int(time.time())
    if user_id in cooldowns:
        remaining_time = cooldowns[user_id] - current_time
        if remaining_time > 0:
            return True, remaining_time
    return False, 0

def format_time(seconds: int) -> str:
    """ሰከንድን ወደ ሰአት እና ደቂቃ ይቀይራል"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours} ሰአት ከ {minutes} ደቂቃ"

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 ሰላም! እንኳን ወደ ቲክቶክ ማውረጃ ቦት በደህና መጡ።\n\n"
        "📥 ለመጀመር የቲክቶክ ቪዲዮ ወይም ፎቶ ሊንክ (Link) ይላኩልኝ።\n"
        "⚠️ ማሳሰቢያ፡ ቦቱን መጠቀም የሚችሉት በየ 24 ሰአቱ አንድ ጊዜ ብቻ ነው።"
    )

@dp.message(F.text.contains("tiktok.com"))
async def handle_tiktok_link(message: Message):
    user_id = message.from_user.id
    
    # የ24 ሰአት ገደብ ማረጋገጫ
    on_cooldown, remaining = is_on_cooldown(user_id)
    if on_cooldown:
        await message.reply(f"❌ ይቅርታ! የኔትዎርክ ሰአት ገደብ አልቆበታም። እባክዎ {format_time(remaining)} ይጠብቁ።")
        return

    msg = await message.reply("🔄 መረጃው እየተፈለገ ነው... እባክዎ ይታገሱ...")
    link = message.text.strip()

    # ከቲክቶክ ኤፒአይ መረጃ መውሰድ
    async with aiohttp.ClientSession() as session:
        async with session.get(TIKTOK_API_URL, params={'url': link}) as response:
            if response.status != 200:
                await msg.edit_text("❌ ከቲክቶክ ሰርቨር ጋር መገናኘት አልተቻለም።")
                return
            
            res_json = await response.json()
            if res_json.get('code') != 0:
                await msg.edit_text("❌ ልክ ያልሆነ ሊንክ ነው ወይም ቪዲዮው ተሰርዟል።")
                return
            
            data = res_json['data']
            user_data[user_id] = data # መረጃውን ለጊዜው እናስቀምጠዋለን
            
            # የተጠቃሚ ምርጫ በተኖች (Inline Buttons)
            buttons = []
            
            # ቪዲዮ ከሆነ የቪዲዮ እና ኦዲዮ ምርጫ መስጠት
            if 'images' not in data or data['images'] is None:
                buttons.append([
                    InlineKeyboardButton(text="🎬 ቪዲዮ (Video)", callback_data=f"download_video_{user_id}"),
                    InlineKeyboardButton(text="🎵 ኦዲዮ (Audio)", callback_data=f"download_audio_{user_id}")
                ])
            else:
                # ስላይድ ሾው/ፎቶ ከሆነ የፎቶ ምርጫ መስጠት
                buttons.append([
                    InlineKeyboardButton(text="🖼 ፎቶዎችን አውርድ (Photos)", callback_data=f"download_photos_{user_id}"),
                    InlineKeyboardButton(text="🎵 ኦዲዮ (Audio)", callback_data=f"download_audio_{user_id}")
                ])
                
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            await msg.edit_text("👉 ምን ማውረድ ይፈልጋሉ? ከታች ይምረጡ፡", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("download_"))
async def process_download(callback: CallbackQuery):
    user_id = callback.from_user.id
    action_data = callback.data.split("_")
    action = action_data[1]
    owner_id = int(action_data[2])
    
    if user_id != owner_id:
        await callback.answer("❌ ይህ በተን ለቪዲዮው ባለቤት ብቻ ነው የሚሰራው!", show_alert=True)
        return

    if user_id not in user_data:
        await callback.message.edit_text("❌ መረጃው ጠፍቷል፣ እባክዎ ሊንኩን እንደገና ይላኩ።")
        return

    data = user_data[user_id]
    await callback.message.edit_text("⏳ በመላክ ላይ...")

    try:
        if action == "video":
            video_url = data['play'] # ያለ ወተርማርክ ቪዲዮ
            await bot.send_video(chat_id=user_id, video=video_url, caption="🎬 ቪዲዮዎ በተሳካ ሁኔታ ወርዷል!")
            
        elif action == "audio":
            audio_url = data['music_info']['play'] # ሙዚቃ/ኦዲዮ
            title = data['music_info']['title']
            await bot.send_audio(chat_id=user_id, audio=audio_url, title=title, caption="🎵 ኦዲዮው በተሳካ ሁኔታ ወርዷል!")
            
        elif action == "photos":
            images = data['images'] # የፎቶዎች ሊስት
            for img in images:
                await bot.send_photo(chat_id=user_id, photo=img)
            await bot.send_message(chat_id=user_id, text="🖼 ፎቶዎቹ በሙሉ በተሳካ ሁኔታ ወርደዋል!")

        # ማውረዱ ከተሳካ በኋላ የ 24 ሰአት ገደቡን መጣል
        cooldowns[user_id] = int(time.time()) + COOLDOWN_DURATION
        del user_data[user_id] # ሜሞሪ ለማጽዳት
        await callback.message.delete()

    except Exception as e:
        await callback.message.edit_text("❌ ፋይሉን በመላክ ላይ ስህተት አጋጥሟል።")
        print(f"Error: {e}")

async def main():
    print("🤖 ቦቱ ስራ ጀምሯል...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
