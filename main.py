import os, time, threading, requests, yfinance as yf
import pandas as pd
import numpy as np
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

SYMBOLS = {
    "GC=F": "ORO 🥇 XAUUSD",
    "BTC-USD": "BTC ₿",
    "ETH-USD": "ETH Ξ",
    "YM=F": "US30 🇺🇸"
}

last_signal = {}

def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=10)
        print(f"TG ENVIADO: {text[:50]}")
    except Exception as e:
        print(f"Error TG: {e}")

def supertrend_real(df, period=8, multiplier=2.0):
    # ATR real como TradingView
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    
    hl2 = (df['High'] + df['Low']) / 2
    upper = hl2 + multiplier * atr
    lower = hl2 - multiplier * atr
    
    st = pd.Series(0, index=df.index)
    dir = pd.Series(1, index=df.index)
    
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > upper.iloc[i-1]:
            dir.iloc[i] = 1
        elif df['Close'].iloc[i] < lower.iloc[i-1]:
            dir.iloc[i] = -1
        else:
            dir.iloc[i] = dir.iloc[i-1]
            if dir.iloc[i] == 1 and lower.iloc[i] < lower.iloc[i-1]:
                lower.iloc[i] = lower.iloc[i-1]
            if dir.iloc[i] == -1 and upper.iloc[i] > upper.iloc[i-1]:
                upper.iloc[i] = upper.iloc[i-1]
    
    return dir, upper, lower

def check_market(symbol, name):
    try:
        data = yf.download(symbol, period="2d", interval="5m", progress=False, auto_adjust=True)
        if len(data) < 60:
            print(f"{name} pocos datos")
            return False
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        
        dir, upper, lower = supertrend_real(data, 8, 2.0)
        price = float(data['Close'].iloc[-1])
        prev_dir = int(dir.iloc[-2])
        curr_dir = int(dir.iloc[-1])
        
        print(f"{name} {price} ST prev:{prev_dir} curr:{curr_dir}")
        
        # DETECTA CAMBIO IGUAL QUE TU FOTO
        if prev_dir != curr_dir:
            if curr_dir == 1:
                send_telegram(f"🐟 COMPRA {name}\n💰 {price:.2f}\n📈 Supertrend 2.0,8 acaba de girar a COMPRA\n⏰ M5 - igual que tu TradingView")
                return True
            else:
                send_telegram(f"🐟 VENTA {name}\n💰 {price:.2f}\n📉 Supertrend 2.0,8 acaba de girar a VENTA\n⏰ M5 - igual que tu TradingView")
                return True
        
        # Guarda estado
        last_signal[name] = curr_dir
        return False
    except Exception as e:
        print(f"Error {name}: {e}")
        return False

def scanner_loop():
    send_telegram("🐟 MI PEZ BOT ARREGLADO 24/7\n✅ Ahora es IGUAL a tu TradingView\n✅ Solo Supertrend 8,2.0 - sin filtros\n✅ Te avisará en cada giro COMPRA/VENTA\n\nProbando ORO, BTC, ETH, US30 cada 1 min")
    while True:
        for sym, name in SYMBOLS.items():
            check_market(sym, name)
            time.sleep(10)
        time.sleep(60)

threading.Thread(target=scanner_loop, daemon=True).start()

@app.route('/')
def home():
    return "MI PEZ BOT IGUAL TRADINGVIEW - ACTIVO"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
