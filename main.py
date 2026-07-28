# main.py
from engine import add_signal
from hiring_scraper import fetch_hiring_signals
from database import get_connection

def reset_db_data():
    """Cancella i vecchi record con i titoli lunghi per mantenere il DB pulito."""
    try:
        conn, _ = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM raw_signals;")
        cursor.execute("DELETE FROM company_scores;")
        cursor.execute("DELETE FROM companies;")
        conn.commit()
        conn.close()
        print("🧹 Database ripulito con successo dai vecchi record.")
    except Exception as e:
        print(f"⚠️ Nota durante il reset: {e}")

def run_pipeline():
    print("--- AVVIO PIPELINE AUTOMATICA CON ESTRAZIONE PULITA ---")

    # Ripuliamo i vecchi dati errati
    reset_db_data()

    # 1. Estrazione segnali reali dal web
    signals = fetch_hiring_signals()

    if not signals:
        print("⚠️ Nessun nuovo segnale rilevato nell'ultima scansione.")
        return

    # 2. Salvataggio ed elaborazione nel Database Cloud
    for item in signals:
        score = add_signal(
            vat_number=item["vat_number"],
            company_name=item["company_name"],
            sector=item["sector"],
            region=item["region"],
            signal_type=item["signal_type"]
        )
        print(f" -> Azienda: '{item['company_name']}' | Segnale: [{item['signal_type']}] | Score: {score} pt")

    print("\n✅ PIPELINE PULITA COMPLETATA CON SUCCESSO!")

if __name__ == "__main__":
    run_pipeline()