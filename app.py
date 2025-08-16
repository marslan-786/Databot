import os
import json
import logging
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Logging
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8401061463:AAHbV0rmswVP1yvbl90hibgDcOr5sOZxblo"  # replace with your actual bot token

CHANNELS = [
    {"name": "Join Channel 1", "url": "https://t.me/kami_broken5", "id": -1002625530649},
    {"name": "Join Channel 2", "url": "https://t.me/only_possible_world", "id": -1002650289632},
    {"name": "Join Channel 2", "url": "https://t.me/freeonlineearning786z"}
]

# Escape for MarkdownV2
def escape_md(text: str) -> str:
    escape_chars = r"\_*[]()~`>#+-=|{}.!-"
    for ch in escape_chars:
        text = text.replace(ch, "\\" + ch)
    return text

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bot = context.bot
    failed = []

    for channel in CHANNELS:
        if "id" not in channel or not channel["id"]:
            continue
        try:
            member = await bot.get_chat_member(chat_id=channel["id"], user_id=user_id)
            if member.status in ['left', 'kicked']:
                failed.append(channel["name"])
        except Exception as e:
            failed.append(channel["name"])

    if failed:
        keyboard = [
            [InlineKeyboardButton(channel["name"], url=channel["url"])] for channel in CHANNELS
        ]
        keyboard.append([InlineKeyboardButton("✅ I Have Joined", callback_data="verify_join")])

        if os.path.exists("logo.png"):
            try:
                with open("logo.png", "rb") as img:
                    await update.message.reply_photo(
                        photo=img,
                        caption="Welcome to SIM Detail Bot. Please join the required channels below 👇",
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
            except Exception as e:
                logging.error(f"❌ Error loading image: {e}")
                await update.message.reply_text(
                    text="Welcome to SIM Detail Bot. Please join the required channels below 👇",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        else:
            await update.message.reply_text(
                text="Welcome to SIM Detail Bot. Please join the required channels below 👇",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔎 Check Your SIM Detail", callback_data="check_sim")]
        ])

        if os.path.exists("logo.png"):
            try:
                with open("logo.png", "rb") as img:
                    await update.message.reply_photo(
                        photo=img,
                        caption="🔍 SIM Detail Bot\n\nThis bot helps you retrieve SIM owner information using secure API.\n\nOnly for personal and research use.",
                        reply_markup=keyboard
                    )
            except Exception as e:
                logging.error(f"❌ Error loading image: {e}")
                await update.message.reply_text(
                    text="🔍 SIM Detail Bot\n\nThis bot helps you retrieve SIM owner information using secure API.\n\nOnly for personal and research use.",
                    reply_markup=keyboard
                )
        else:
            await update.message.reply_text(
                text="🔍 SIM Detail Bot\n\nThis bot helps you retrieve SIM owner information using secure API.\n\nOnly for personal and research use.",
                reply_markup=keyboard
            )

# Callback after pressing "I Have Joined"
async def verify_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bot = context.bot
    failed = []

    for channel in CHANNELS:
        if "id" not in channel or not channel["id"]:
            continue
        try:
            member = await bot.get_chat_member(chat_id=channel["id"], user_id=user_id)
            if member.status in ['left', 'kicked']:
                failed.append(channel["name"])
        except Exception as e:
            failed.append(channel["name"])

    query = update.callback_query
    if query:
        await query.answer()

        if failed:
            # Prepare a string listing all missing channels
            missing_channels = ", ".join(failed)
            error_message = f"❌ Please First Join This Channel:\n{missing_channels}"
            await query.answer(error_message, show_alert=True)
            return

        # اگر سب چینلز جوائن ہو چکے ہیں تو پچھلا میسج ڈیلیٹ کریں
        try:
            await query.message.delete()
        except Exception as e:
            logging.warning(f"⚠️ Could not delete message: {e}")

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔎 Check Your SIM Detail", callback_data="check_sim")]
        ])

        try:
            if os.path.exists("logo.png") and os.path.getsize("logo.png") > 0:
                with open("logo.png", "rb") as img:
                    await bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=img,
                        caption="🔍 SIM Detail Bot\n\nThis bot helps you retrieve SIM owner information using secure API.\n\nOnly for personal and research use.",
                        reply_markup=keyboard
                    )
            else:
                raise FileNotFoundError("logo.png not found or is empty.")
        except Exception as e:
            logging.error(f"📸 Photo send error: {e}")
            await bot.send_message(
                chat_id=query.message.chat_id,
                text="🔍 SIM Detail Bot\n\nThis bot helps you retrieve SIM owner information using secure API.\n\nOnly for personal and research use.",
                reply_markup=keyboard
            )

# When "Check SIM" button is pressed
async def check_sim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Send a new message instead of editing the old one
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="📱 Please enter the phone number you want to check."
    )

async def generate_image(data: dict, file_path="sim_info.png"):
    from PIL import Image, ImageDraw, ImageFont
    import os

    width, base_height = 600, 500
    bg_path = "logo.png"

    def load_bg(height):
        if os.path.exists(bg_path):
            return Image.open(bg_path).resize((width, height)).convert("RGB")
        else:
            return Image.new("RGB", (width, height), color=(30, 30, 30))

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    title_font = ImageFont.truetype(font_path, size=26)
    brand_font = ImageFont.truetype(font_path, size=52)

    def estimate_box_height(lines, font, padding=20):
        heights = [font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines]
        return sum(heights) + padding * 2 + (len(lines) - 1) * 10

    # حرفوں کی بنیاد پر address تقسیم کرنے والا فنکشن
    def split_address_custom(text):
        # text میں "Address: " پہلے سے موجود ہے
        lines = []

        # پہلی لائن کے لیے: "Address: " کے بعد 10 سے 12 حروف لیں (spaces سمیت)
        prefix = "Address: "
        prefix_len = len(prefix)

        # پورا ٹیکسٹ (Address: + باقی)
        full_text = text

        # پہلی لائن میں prefix شامل کریں، پھر prefix کے بعد 10 سے 12 حروف مزید شامل کریں
        # ہم 12 تک لیں گے، مگر کم از کم 10 بھی ہونا چاہیے

        # prefix کے بعد والے text کو extract کریں:
        after_prefix = full_text[prefix_len:]

        # پہلی لائن میں prefix + 12 characters لیں، اگر متن کم ہو تو جتنا ہو لے لیں
        first_line_chars = min(max(10, 12), len(after_prefix))
        first_line_text = prefix + after_prefix[:first_line_chars]
        lines.append(first_line_text)

        # باقی ٹیکسٹ دوسری لائن کے لیے
        remaining_text = after_prefix[first_line_chars:]

        # دوسری لائن میں زیادہ سے زیادہ 25 حروف لیں
        second_line_chars = min(25, len(remaining_text))
        second_line_text = remaining_text[:second_line_chars]
        lines.append(second_line_text)

        # باقی تیسری لائن کے لیے
        third_line_text = remaining_text[second_line_chars:]
        if third_line_text:
            # اگر تیسری لائن بہت لمبی ہو تو "..." لگائیں
            if len(third_line_text) > 50:
                third_line_text = third_line_text[:47] + "..."
            lines.append(third_line_text)

        return lines

    header_height = 70
    gap = 20

    info_lines = [
        f"Mobile: {data.get('Mobile', 'N/A')}",
        f"Name: {data.get('Name', 'N/A')}",
        f"CNIC: {data.get('CNIC', 'N/A')}",
        f"Network: {data.get('Network', 'N/A')}",
    ]

    full_address = data.get('Address', 'N/A')
    address_text = "Address: " + full_address
    wrapped_address = split_address_custom(address_text)

    info_font = ImageFont.truetype(font_path, size=28)
    address_font = ImageFont.truetype(font_path, size=24)

    content_boxes = [
        (info_lines, estimate_box_height(info_lines, info_font, padding=25)),
        (wrapped_address, estimate_box_height(wrapped_address, address_font, padding=25)),
    ]

    footer_height = brand_font.getbbox("Nothing x Kami")[3] + 40

    total_height = header_height + gap
    for _, h in content_boxes:
        total_height += h + gap
    total_height += footer_height
    height = max(base_height, total_height)

    bg_image = load_bg(height)
    image = bg_image.copy()
    draw = ImageDraw.Draw(image)

    header_box = (20, 15, width - 20, 70)
    draw.rounded_rectangle(header_box, radius=15, fill=(50, 100, 200), outline=(255, 255, 255), width=2)
    draw.text((header_box[0] + 20, header_box[1] + 15), "SIM Information By Kami X Nothing", font=title_font, fill=(255, 255, 255))

    y = header_box[3] + gap

    def draw_info_box(draw, y, lines):
        padding = 25
        radius = 18
        fill = (181, 101, 29)

        max_width = 0
        line_heights = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=info_font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            max_width = max(max_width, w)
            line_heights.append(h)

        total_height = sum(line_heights) + (len(lines) - 1) * 10
        box_width = max_width + 2 * padding
        box_width = min(box_width, width - 50)

        box_height = total_height + 2 * padding

        x1 = (width - box_width) // 2
        y1 = y
        x2 = x1 + box_width
        y2 = y1 + box_height

        draw.rounded_rectangle((x1, y1, x2, y2), radius=radius, fill=fill, outline=(255, 255, 255), width=2)

        y_text = y1 + padding
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=info_font)
            w = bbox[2] - bbox[0]
            draw.text((x1 + (box_width - w) // 2, y_text), line, font=info_font, fill=(255, 255, 255))
            y_text += bbox[3] - bbox[1] + 10

        return y2 + 15

    def draw_address_box(draw, y, lines):
        padding = 25
        radius = 18
        fill = (101, 101, 181)

        max_width = 0
        line_heights = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=address_font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            max_width = max(max_width, w)
            line_heights.append(h)

        total_height = sum(line_heights) + (len(lines) - 1) * 10
        box_width = max_width + 2 * padding
        box_width = min(box_width, width - 50)

        box_height = total_height + 2 * padding

        x1 = (width - box_width) // 2
        y1 = y
        x2 = x1 + box_width
        y2 = y1 + box_height

        draw.rounded_rectangle((x1, y1, x2, y2), radius=radius, fill=fill, outline=(255, 255, 255), width=2)

        y_text = y1 + padding
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=address_font)
            w = bbox[2] - bbox[0]
            draw.text((x1 + (box_width - w) // 2, y_text), line, font=address_font, fill=(255, 255, 255))
            y_text += bbox[3] - bbox[1] + 10

        return y2 + 15

    y = draw_info_box(draw, y, info_lines)
    y = draw_address_box(draw, y, wrapped_address)

    brand_text = "Nothing x Kami"
    bbox = draw.textbbox((0, 0), brand_text, font=brand_font)
    brand_width = bbox[2] - bbox[0]
    brand_height = bbox[3] - bbox[1]
    x = (width - brand_width) // 2
    y_brand = height - brand_height - 20

    for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
        draw.text((x + dx, y_brand + dy), brand_text, font=brand_font, fill=(0, 0, 0))

    draw.text((x, y_brand), brand_text, font=brand_font, fill=(255, 255, 255))

    if os.path.exists(file_path):
        os.remove(file_path)
    image.save(file_path)

# When user enters phone number
from telegram.helpers import escape_markdown
import aiohttp
import logging

keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔎 Check Another Number Detail", callback_data="check_sim")]
        ])

from telegram.helpers import escape_markdown

async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bot = context.bot

    # --- چینلز چیک کریں ---
    failed = []
    for channel in CHANNELS:
        if "id" not in channel or not channel["id"]:
            continue
        try:
            member = await bot.get_chat_member(chat_id=channel["id"], user_id=user_id)
            if member.status in ['left', 'kicked']:
                failed.append(channel["name"])
        except Exception:
            failed.append(channel["name"])

    if failed:
        keyboard = [
            [InlineKeyboardButton(channel["name"], url=channel["url"])] for channel in CHANNELS
        ]
        keyboard.append([InlineKeyboardButton("✅ I Have Joined", callback_data="verify_join")])
        await update.message.reply_text(
            text="❌ You have not joined all required channels. Please join the channels below first.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # --- نمبر پراسیس کریں ---
    phone = update.message.text.strip()
    if phone.startswith("0"):
        phone = phone[1:]

    # --- APIs ---
    image_api = f"https://api.impossible-world.xyz/api/data?phone={phone}"
    text_api = f"https://api.impossible-world.xyz/api/alldata?number={phone}"

    try:
        async with aiohttp.ClientSession() as session:
            # --- image API سے data لو ---
            cnic_from_image = None
            async with session.get(image_api) as resp_img:
                raw_img = await resp_img.text()
                if resp_img.status == 200:
                    try:
                        image_data = json.loads(raw_img)
                        cnic_from_image = image_data.get("CNIC", None)
                        await generate_image(image_data)
                        await update.message.reply_photo(
                            photo=open("sim_info.png", "rb"),
                            caption="🔍 SIM Data Retrieved (Image)"
                        )
                    except Exception:
                        # JSON parse نہ ہوا → اصل response شو
                        await update.message.reply_text(
                            f"❌ Image API invalid response:\n\n{raw_img}"
                        )
                else:
                    await update.message.reply_text(
                        f"❌ Image API failed (status {resp_img.status}):\n\n{raw_img}"
                    )

            # --- text API سے تمام ریکارڈز لو ---
            async with session.get(text_api) as resp_txt:
                raw_txt = await resp_txt.text()
                if resp_txt.status == 200:
                    try:
                        all_records = json.loads(raw_txt)

                        # CNIC override کریں اگر image API کا CNIC ملا ہو
                        if cnic_from_image and isinstance(all_records, list):
                            for record in all_records:
                                record["CNIC"] = cnic_from_image

                        if isinstance(all_records, list) and len(all_records) > 0:
                            text_blocks = []
                            for record in all_records:
                                name = escape_markdown(record.get("Name", "Not Available"), version=2)
                                mobile = escape_markdown(record.get("Mobile", "Not Available"), version=2)
                                cnic = escape_markdown(record.get("CNIC", "Not Available"), version=2)
                                address = escape_markdown(record.get("Address", "Not Available"), version=2)

                                block = (
                                    "━━━━━━━━━━━━━━━\n"
                                    f"👤 *Name:* {name}\n"
                                    f"📱 *Mobile:* {mobile}\n"
                                    f"🆔 *CNIC:* {cnic}\n"
                                    f"🏠 *Address:* {address}\n"
                                    "━━━━━━━━━━━━━━━"
                                )
                                text_blocks.append(block)

                            final_text = "*𝙆𝘼𝙈𝙄 𝙭 𝙉𝙊𝙏𝙃𝙄𝙉𝙂 𝘿𝙖𝙩𝙖𝙗𝙖𝙨𝙚*\n\n" + "\n".join(text_blocks)
                            await update.message.reply_text(
                                final_text,
                                parse_mode="MarkdownV2"
                            )
                        else:
                            await update.message.reply_text("No records found.")
                    except Exception:
                        # JSON parse نہ ہوا → اصل response شو
                        await update.message.reply_text(
                            f"❌ Text API invalid response:\n\n{raw_txt}"
                        )
                else:
                    await update.message.reply_text(
                        f"❌ Text API failed (status {resp_txt.status}):\n\n{raw_txt}"
                    )

    except Exception as e:
        logging.error(f"API error: {e}", exc_info=True)
        await update.message.reply_text(f"⚠️ Error: {e}")


# Run the bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify_join, pattern="^verify_join$"))
    app.add_handler(CallbackQueryHandler(check_sim, pattern="^check_sim$"))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_number))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()