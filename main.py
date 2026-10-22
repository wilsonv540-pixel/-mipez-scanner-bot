import os, time, threading, requests, yfinance as yf
import pandas as pd
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

SYMBOLS = {
    "GC=F": "ORO 🥇",
    "BTC-USD": "BTC ₿",
    "ETH-USD": "ETH Ξ",
    "YM=F": "US30 🇺🇸"
}

def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(f"Error TG: {e}")

def supertrend(df, period=8, multiplier=2.0):
    hl2 = (df['High'] + df['Low']) / 2
    atr = (df['High'] - df['Low']).rolling(period).mean()
    upper = hl2 + multiplier * atr
    lower = hl2 - multiplier * atr
    direction = pd.Series(1, index=df.index)
    for i in range(1, len(df)):
        if df['Close'][i] > upper[i-1]: direction[i]=1
        elif df['Close'][i] < lower[i-1]: direction[i]=-1
        else: direction[i]=direction[i-1]
    return direction

def check_market(symbol, name):
    try:
        data = yf.download(symbol, period="1d", interval="5m", progress=False)
        if len(data) < 50: return
        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
        
        close = data['Close']
        # RSI
        delta = close.diff()
        gain = delta.where(delta>0,0).rolling(14).mean()
        loss = (-delta.where(delta<0,0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100/(1+rs))
        # MACD
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        # Supertrend
        st_dir = supertrend(data)

        price = float(close.iloc[-1])
        rsi_val = float(rsi.iloc[-1])
        macd_val = float(macd.iloc[-1])
        sig_val = float(signal.iloc[-1])
        st_val = int(st_dir.iloc[-1])
        
        print(f"{name} {price:.2f} RSI:{rsi_val:.1f} ST:{st_val}")

        # SEÑAL PRO: ST + RSI + MACD alineados
        buy = st_val == 1 and rsi_val > 52 and rsi_val < 75 and macd_val > sig_val
        sell = st_val == -1 and rsi_val < 48 and macd_val < sig_val

        if buy:
            send_telegram(f"🐟 *MI PEZ COMPRA - {name}*\n💰 Precio: `{price:.2f}`\n📊 RSI: {rsi_val:.1f} | MACD: ALCISTA\n✅ Supertrend 2.0,8: COMPRA\n⏰ M5 Confirmada")
            return True
        if sell:
            send_telegram(f"🐟 *MI PEZ VENTA - {name}*\n💰 Precio: `{price:.2f}`\n📊 RSI: {rsi_val:.1f} | MACD: BAJISTA\n🔻 Supertrend 2.0,8: VENTA\n⏰ M5 Confirmada")
            return True
    except Exception as e:
        print(f"Error {name}: {e}")
    return False

def scanner_loop():
    send_telegram("🐟 *MI PEZ SCANNER PRO 24/7 INICIADO*\n✅ Render: ACTIVO\n✅ UptimeRobot: 100% Cuidando\n✅ Mercados: ORO, BTC, ETH, US30\n✅ Estrategia: Supertrend 2.0,8 + RSI14 + MACD M5\n\n¡Ya no se apaga mi pez! Señales cada M5")
    while True:
        for sym, name in SYMBOLS.items():
            triggered = check_market(sym, name)
            if triggered:
                time.sleep(300) # 5 min cooldown por señal
            time.sleep(20) # 20 seg entre mercados
        time.sleep(60) # Vuelta completa cada 1 min

threading.Thread(target=scanner_loop, daemon=True).start()

@app.route('/')
def home():
    return "MI PEZ SCANNER PRO 24/7 - ORO,BTC,ETH,US30 - ACTIVO"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
