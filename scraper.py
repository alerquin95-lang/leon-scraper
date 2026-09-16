import os, time, threading, requests
from flask import Flask

# Servidor pra Render não derrubar
app = Flask(__name__)
@app.route('/')
def home(): return "Scraper 24/7 OK"
def run_health():
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_health, daemon=True).start()

API_URL = os.getenv("API_URL")
PUSH_SECRET = os.getenv("PUSH_SECRET")

print("Iniciado modo leve 24/7")

# Aqui você coloca a lógica leve de coleta
# sem usar navegador
while True:
    try:
        # exemplo: você vai fazer o push manual ou via requests
        print("Rodando... aguardando dados")
        time.sleep(30)
    except Exception as e:
        print(f"Erro: {e}")
        time.sleep(10)
