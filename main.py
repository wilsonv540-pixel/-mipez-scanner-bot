import time, yfinance as yf, pandas as pd, requests
TOKEN = "8350925513:AAFYKY7nEOahg0cUbIAIeOV16YRvl7pYnyw"
CHAT_ID = None

def send(text):
    global CHAT_ID
    if not CHAT_ID:
        try:
            r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", timeout=10).json()
            if r['result']:
                CHAT_ID = r['result'][-1]['message']['chat']['id']
        except: return
    if CHAT_ID:
        try:
            requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage", params={"chat_id":CHAT_ID,"text":text}, timeout=15)
            print(f"Enviado: {text}")
        except Exception as e:
            print(e)

# Mensaje inicial
send("✅ Mi Pez Scanner Pro CONECTADO! Tu SCANER Supertrend 2.0,8 + RSI14 + MACD M5 activo - ORO, BTC, US30, ETH")

SYMBOLS = {"GC=F":"ORO","BTC-USD":"BTC","ETH-USD":"ETH","^DJI":"US30"}

def get_signal(sym, name):
    try:
        df = yf.download(sym, period="5d", interval="5m", progress=False, auto_adjust=True)
        if len(df) < 50: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # RSI 14
        delta = df['Close'].diff()
        gain = delta.where(delta>0,0).rolling(14).mean()
        loss = -delta.where(delta<0,0).rolling(14).mean()
        rs = gain/loss
        df['RSI'] = 100 - (100/(1+rs))
        # MACD
        ema12 = df['Close'].ewm(span=12).mean()
        ema26 = df['Close'].ewm(span=26).mean()
        df['MACD'] = ema12-ema26
        df['Signal'] = df['MACD'].ewm(span=9).mean()
        df['Hist'] = df['MACD']-df['Signal']
        # Supertrend 2.0,8
        tr = pd.concat([df['High']-df['Low'], (df['High']-df['Close'].shift()).abs(), (df['Low']-df['Close'].shift()).abs()], axis=1).max(axis=1)
        atr = tr.rolling(8).mean()
        hl2 = (df['High']+df['Low'])/2
        upper = hl2 + 2.0*atr
        lower = hl2 - 2.0*atr
        dir = [1]*len(df)
        for i in range(1,len(df)):
            if df['Close'].iloc[i] <= upper.iloc[i-1]: dir[i] = -1
            else: dir[i] = 1
        df['DIR'] = dir
        
        last = df.iloc[-2]
        prev = df.iloc[-3]
        price = float(df['Close'].iloc[-1])
        
        # Tu logica SCANER.txt
        if prev['DIR']==-1 and last['DIR']==1 and last['RSI']>45 and last['Hist']>0:
            return f"🟢 COMPRA {name} {price:.2f} | Supertrend alcista | RSI {last['RSI']:.1f} | MACD ✅ M5"
        if prev['DIR']==1 and last['DIR']==-1 and last['RSI']<55 and last['Hist']<0:
            return f"🔴 VENTA {name} {price:.2f} | Supertrend bajista | RSI {last['RSI']:.1f} | MACD ✅ M5"
        return None
    except Exception as e:
        print(f"Error {name}: {e}")
        return None

while True:
    for sym,name in SYMBOLS.items():
        sig = get_signal(sym,name)
        if sig: send(sig)
    time.sleep(60)
