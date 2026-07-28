# main.py
from database import init_db
from engine import add_signal
from notifier import send_telegram_alert
from scraper_gazzetta import fetch_gazzetta_signals

ALERT_THRESHOLD = 30

def process_signal(vat_number: str, company_name: str, sector: str, region: str, signal_type: str, details: str = ""):
    print(f"📡 Elaborazione in corso per '{company_name}' (P.IVA: {vat_number})...")
    
    # 1. Salva nel DB e ricalcola il punteggio
    current_score = add_signal(vat_number, company_name, sector, region, signal_type)
    print(f"📊 Punteggio totale aggiornato: {current_score} / 100")
    
    # 2. Controllo della soglia per la notifica Telegram
    if current_score >= ALERT_THRESHOLD:
        print(f"🚀 SOGLIA SUPERATA ({current_score} >= {ALERT_THRESHOLD})! Invio alert Telegram...")
        send_telegram_alert(
            company_name=company_name,
            vat_number=vat_number,
            sector=sector,
            score=current_score,
            last_signal=signal_type,
            details=details  # Passiamo il dettaglio dinamico dell'atto
        )
    else:
        print(f"⏳ Punteggio sotto la soglia ({current_score} < {ALERT_THRESHOLD}). Nessun alert.\n")

def run_pipeline():
    init_db()
    print("\n--- AVVIO PIPELINE AUTOMATICA SU DATI REALI ---\n")
    
    real_signals = fetch_gazzetta_signals(limit=5)
    
    for sig in real_signals:
        process_signal(
            vat_number=sig["vat_number"],
            company_name=sig["company_name"],
            sector=sig["sector"],
            region=sig["region"],
            signal_type=sig["signal_type"],
            details=sig.get("details", "")
        )

if __name__ == "__main__":
    run_pipeline()