import os
from flask import Flask
import threading
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "MI PEZ SCANNER BOT - ACTIVO 24/7 - ORO 4124"

def scanner_loop():
    print("MI PEZ INICIADO 24/7")
    while True:
        try:
            # Aquí va tu lógica de scanner
            print("Escaneando...")
            time.sleep(60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

# Iniciar scanner en segundo plano
threading.Thread(target=scanner_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
