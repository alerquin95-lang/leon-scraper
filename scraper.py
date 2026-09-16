
import os, time, re, json, requests
from playwright.sync_api import sync_playwright

LEON_USER = os.getenv("LEON_USER")
LEON_PASS = os.getenv("LEON_PASS")
API_URL = os.getenv("API_URL", "https://bacbo-api-fixa.onrender.com/push")
PUSH_SECRET = os.getenv("PUSH_SECRET", "leonbet2026")

# URL da mesa Bac Bo - você pode trocar
BACBO_URL = os.getenv("BACBO_URL", "https://leon.bet/pt/live-casino")

def push_api(result, player_sum, banker_sum):
    try:
        r = requests.post(API_URL, json={
            "secret": PUSH_SECRET,
            "result": result, # player / banker / tie
            "player_sum": player_sum,
            "banker_sum": banker_sum
        }, timeout=10)
        print(f"PUSH {result} {player_sum} x {banker_sum} -> {r.status_code} {r.text}")
        return r.ok
    except Exception as e:
        print(f"Erro push: {e}")
        return False

def run():
    print("Iniciando scraper 24/7...")
    if not LEON_USER or not LEON_PASS:
        print("FALTA LEON_USER e LEON_PASS nas Environment Variables!")
        time.sleep(999999)
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context(user_agent="Mozilla/5.0")
        page = context.new_page()
        
        print("Indo pra Leonbet login...")
        page.goto(BACBO_URL, timeout=60000)
        time.sleep(5)

        # TENTA LOGIN - os seletores mudam, você ajusta se precisar
        try:
            # Procura botão Entrar/Login
            if page.locator("text=Entrar").count() > 0:
                page.locator("text=Entrar").first.click()
                time.sleep(2)
            # campos comuns
            page.fill('input[name="username"], input[type="email"]', LEON_USER)
            page.fill('input[name="password"], input[type="password"]', LEON_PASS)
            page.keyboard.press("Enter")
            time.sleep(8)
            print("Login enviado...")
        except Exception as e:
            print(f"Login manual pode ser necessário, continuando... {e}")

        # Vai pra mesa Bac Bo - Evolution Gaming
        # Você deve estar logado e ir na mesa manualmente se o auto falhar
        # Deixe o navegador aberto, ele vai tentar achar o histórico
        
        last_signature = None
        print("Monitorando mesa Bac Bo...")

        while True:
            try:
                # Tenta achar resultados no DOM da Evolution
                # Bac Bo geralmente tem .bacbo-result ou .history-item
                # Vamos procurar texto tipo "Player 7 - Banker 5"
                
                # Pega todo texto da pagina e tenta extrair último resultado
                content = page.content()
                
                # Heurística: procura padrões no histórico da Evolution
                # Exemplos que aparecem: Player wins, Banker wins, Tie
                # E somas: 2 dados = soma de 2 a 12
                
                # Tenta achar via JS dentro de iframes
                result_data = page.evaluate("""
                () => {
                    // Procura em iframes da Evolution
                    let texts = [];
                    function scan(doc) {
                        try {
                            texts.push(doc.body.innerText.slice(-5000));
                            let iframes = doc.querySelectorAll('iframe');
                            iframes.forEach(f => {
                                try { scan(f.contentDocument); } catch(e) {}
                            });
                        } catch(e) {}
                    }
                    scan(document);
                    return texts.join(' \n ');
                }
                """)

                # Exemplo de parse simples - VOCÊ VAI AJUSTAR COM O QUE VER NO LOG
                # Procura último "Player 8 Banker 9" etc
                # Por enquanto loga pra você ver o formato
                print(f"Scan: {result_data[-500:]}")

                # TODO: Ajuste esse regex quando ver o log no Render
                # m = re.search(r'Player.*?(\d+).*?Banker.*?(\d+).*?(Player|Banker|Tie)', result_data, re.I)
                
                time.sleep(5)

            except Exception as e:
                print(f"Erro loop: {e}")
                time.sleep(10)
                # tenta recarregar se cair
                try:
                    page.reload()
                    time.sleep(10)
                except:
                    pass

if __name__ == "__main__":
    run()
