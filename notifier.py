# notifier.py
import requests

TELEGRAM_BOT_TOKEN = "8402311708:AAGwciBxWUhvdQm-TJVezIhoo2j224I_7sc"
TELEGRAM_CHAT_ID = "963714464"

def send_telegram_alert(company_name: str, vat_number: str, sector: str, score: int, last_signal: str, details: str = ""):
    """
    Invia un messaggio formattato in HTML sul canale/chat Telegram.
    """
    # Se c'è un dettaglio specifico dell'atto, lo formattiamo in evidenza
    details_block = f"\n📝 <b>Atto/Nota:</b> <i>{details}</i>\n" if details else ""

    message = (
        f"🔥 <b>M&A TARGET CALDO IDENTIFICATO</b> 🔥\n\n"
        f"🏢 <b>Azienda:</b> {company_name}\n"
        f"🆔 <b>P.IVA:</b> <code>{vat_number}</code>\n"
        f"📊 <b>Settore:</b> {sector}\n"
        f"📈 <b>Score Accumulato:</b> {score} / 100\n"
        f"⚡ <b>Ultimo Segnale:</b> {last_signal}\n"
        f"{details_block}\n"
        f"👉 <b>Azione consigliata:</b> Valutare outreach per opportunità straordinaria."
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"✅ Alert Telegram inviato con successo per {company_name}!")
        else:
            print(f"❌ Errore invio Telegram [{response.status_code}]: {response.text}")
    except Exception as e:
        print(f"❌ Errore di connessione durante l'invio su Telegram: {e}")