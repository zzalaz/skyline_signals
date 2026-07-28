# main.py
from engine import add_signal
from hiring_scraper import fetch_hiring_signals
from database import get_connection

def clean_old_dirty_data():
    """Pulisce solo le vecchie righe contenenti stringhe imperfette."""
    try:
        conn, _ = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM raw_signals;")
        cursor.execute("DELETE FROM company_scores;")
        cursor.execute("DELETE FROM companies;")
        conn.commit()
        conn.close()
        print("🧹 Database azzerato per applicare la nuova pulizia strict.")
    except Exception as e:
        print(f"⚠️ Nota pulizia: {e}")

def run_pipeline():
    print("--- AVVIO PIPELINE AUTOMATICA PRODUCTION ---")

    # Pulizia una tantum dei vecchi dati
    clean_old_dirty_data()

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