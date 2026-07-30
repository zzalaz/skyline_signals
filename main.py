# main.py
from engine import add_signal
from hiring_scraper import fetch_hiring_signals
from gu_scraper import fetch_gazzetta_official_signals

def run_pipeline():
    print("--- AVVIO PIPELINE DUAL-SOURCE (Gazzetta Ufficiale + Web Intelligence) ---")

    all_signals = []

    # 1. Rilevamento Atti Ufficiali (Dati Legali con P.IVA Reali)
    gu_signals = fetch_gazzetta_official_signals()
    all_signals.extend(gu_signals)

    # 2. Rilevamento Notizie Corporate & Hiring
    hiring_signals = fetch_hiring_signals()
    all_signals.extend(hiring_signals)

    if not all_signals:
        print("⚠️ Nessun nuovo segnale rilevato in questa scansione.")
        return

    # 3. Inserimento e aggiornamento Score su Supabase Cloud
    for item in all_signals:
        score = add_signal(
            vat_number=item["vat_number"],
            company_name=item["company_name"],
            sector=item["sector"],
            region=item["region"],
            signal_type=item["signal_type"]
        )
        print(f" -> [{item['signal_type']}] {item['company_name']} (P.IVA: {item['vat_number']}) | Score: {score} pt")

    print(f"\n✅ PIPELINE COMPLETATA: Elaborati {len(all_signals)} segnali totali.")

if __name__ == "__main__":
    run_pipeline()