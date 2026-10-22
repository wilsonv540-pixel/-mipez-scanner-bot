import os, time, threading, requests, yfinance as yf
import pandas as pd
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "7730244122") # Tu chat ID
SYMBOL = "GC=F"  # Oro

def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
        print(f"Telegram: {text[:50]}")
    except Exception as e:
        print(f"Error telegram: {e}")

def supertrend(df, period=8, multiplier=2.0):
    hl2 = (df['High'] + df['Low']) / 2
    atr = (df['High'] - df['Low']).rolling(period).mean()
    upper = hl2 + multiplier * atr
    lower = hl2 - multiplier * atr
    st = pd.Series(0, index=df.index)
    direction = pd.Series(1, index=df.index)
    for i in range(1, len(df)):
        if df['Close'][i] > upper[i-1]: direction[i]=1
        elif df['Close'][i] < lower[i-1]: direction[i]=-1
        else: direction[i]=direction[i-1]
        st[i] = lower[i] if direction[i]==1 else upper[i]
    return st, direction

def check_signal():
    try:
        data = yf.download(SYMBOL, period="1d", interval="5m", progress=False)
        if len(data) < 50: return
        data.columns = [c[0] if isinstance(c, tuple) else c for c in data.columns]
        close = data['Close']
        # RSI
        delta = close.diff()
        gain = delta.where(delta>0,0).rolling(14).mean()
        loss = (-delta.where(delta<0,0)).rolling(14).mean()
        rsi = 100 - (100/(1+gain/loss))
        # Supertrend
        _, direction = supertrend(data)
        price = float(close.iloc[-1])
        rsi_val = float(rsi.iloc[-1])
        st_dir = int(direction.iloc[-1])
        
        print(f"Oro {price:.2f} | RSI {rsi_val:.1f} | ST {st_dir}")
        
        # SEÑAL COMPRA: ST alcista + RSI >50
        if st_dir == 1 and rsi_val > 52 and rsi_val < 70:
            send_telegram(f"🐟 *MI PEZ SEÑAL ORO - COMPRA*\nPrecio: {price:.2f}\nRSI: {rsi_val:.1f}\nSupertrend: COMPRA\n_5m confirmada_")
            time.sleep(900) # Esperar 15min para no spamear
        elif st_dir == -1 and rsi_val < 48:
            send_telegram(f"🐟 *MI PEZ SEÑAL ORO - VENTA*\nPrecio: {price:.2f}\nRSI: {rsi_val:.1f}\nSupertrend: VENTA")
            time.sleep(900)
    except Exception as e:
        print(f"Error scanner: {e}")

def scanner_loop():
    send_telegram("🐟 *MI PEZ SCANNER 24/7 INICIADO*\n✅ Render: ACTIVO\n✅ UptimeRobot: Cuidando\n✅ Oro: Monitoreando 5m\n\n¡Ya no se apaga mi pez!")
    while True:
        check_signal()
        time.sleep(60)

threading.Thread(target=scanner_loop, daemon=True).start()

@app.route('/')
def home():
    return "MI PEZ BOT 24/7 - ARRIBA 100% - ORO ACTIVO"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
