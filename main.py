# main.py
from engine import add_signal
from hiring_scraper import fetch_hiring_signals

def run_pipeline():
    print("--- AVVIO PIPELINE AUTOMATICA PRODUCTION ---")

    # NOTA: Il reset del DB è disattivato per consentire l'accumulo dei dati nel tempo
    # e far salire lo score delle aziende ad ogni nuova rilevazione.

    # 1. Estrazione segnali reali dal web
    signals = fetch_hiring_signals()

    if not signals:
        print("⚠️ Nessun nuovo segnale rilevato nell'ultima scansione.")
        return

    # 2. Accumulo segnali e calcolo score nel DB Cloud
    for item in signals:
        score = add_signal(
            vat_number=item["vat_number"],
            company_name=item["company_name"],
            sector=item["sector"],
            region=item["region"],
            signal_type=item["signal_type"]
        )
        print(f" -> [{item['signal_type']}] Azienda: '{item['company_name']}' | Score: {score} pt")

    print("\n✅ PIPELINE REAL-TIME COMPLETATA CON SUCCESSO!")

if __name__ == "__main__":
    run_pipeline()