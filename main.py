import os
import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8407271613:AAGuND6tnLQUHMhH2MqdglNiB6oGk-o60xY"  # Railway پر env variable set کریں

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Build Your Project", callback_data="build")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Welcome! Click below to build your Python script into EXE.", reply_markup=reply_markup)

# Button handler
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "build":
        await query.edit_message_text("📄 Please send me your Python script file (.py).")

# File upload handler
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    file = await update.message.document.get_file()
    file_path = f"{user.id}.py"
    await file.download_to_drive(file_path)

    await update.message.reply_text("⚙️ Building your EXE... Please wait ⏳")

    exe_name = f"{user.id}.exe"

    try:
        # Run PyInstaller with MinGW-w64 (cross-compilation)
        subprocess.run([
            "pyinstaller",
            "--onefile",
            "--distpath", "dist",
            "--workpath", "build",
            "--specpath", "build",
            "--name", exe_name,
            file_path
        ], check=True)

        exe_path = os.path.join("dist", exe_name)

        if os.path.exists(exe_path):
            await update.message.reply_document(document=open(exe_path, "rb"))
        else:
            await update.message.reply_text("❌ Failed to build the EXE file.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")
    finally:
        # Cleanup
        for folder in ["build", "dist"]:
            if os.path.exists(folder):
                subprocess.run(["rm", "-rf", folder])
        spec_file = os.path.splitext(file_path)[0] + ".spec"
        if os.path.exists(spec_file):
            os.remove(spec_file)
        if os.path.exists(file_path):
            os.remove(file_path)

# Main function
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.Document.FileExtension("py"), handle_file))
    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()