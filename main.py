import os
from flask import Flask
import threading
import time
import requests

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

@app.route('/')
def home():
    return "MI PEZ BOT 24/7 - ACTIVO - ORO 4124"

def send_telegram(msg):
    if BOT_TOKEN and CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
        except: pass

def scanner():
    send_telegram("🐟 MI PEZ BOT 24/7 INICIADO - Render ACTIVO")
    while True:
        try:
            print("Mi pez escaneando...")
            # Aquí va tu lógica de Supertrend + RSI
            time.sleep(60)
        except Exception as e:
            print(e)
            time.sleep(10)

threading.Thread(target=scanner, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
