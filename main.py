# main.py
from engine import add_signal
from hiring_scraper import fetch_hiring_signals

def run_pipeline():
    print("--- AVVIO PIPELINE AUTOMATICA MULTI-FONTE ---")

    # ---------------------------------------------------------
    # FONTE 1: Gazzetta Ufficiale (Atti e Fusioni/Scissioni)
    # ---------------------------------------------------------
    print("\n[FONTE 1] Scansione Gazzetta Ufficiale...")
    gazzetta_signals = [
        {
            "vat_number": "IT03882910158",
            "company_name": "Lombardia Industriale S.r.l.",
            "sector": "Manifatturiero & Metalmeccanica",
            "region": "Lombardia",
            "signal_type": "GAZZETTA_ATTO"
        },
        {
            "vat_number": "IT01928470362",
            "company_name": "Emilia Logistics S.p.A.",
            "sector": "Trasporti & Logistica",
            "region": "Emilia-Romagna",
            "signal_type": "GAZZETTA_ATTO"
        }
    ]

    for item in gazzetta_signals:
        score = add_signal(
            vat_number=item["vat_number"],
            company_name=item["company_name"],
            sector=item["sector"],
            region=item["region"],
            signal_type=item["signal_type"]
        )
        print(f" -> {item['company_name']}: Nuovo Score = {score} pt")

    # ---------------------------------------------------------
    # FONTE 2: Hiring & Expansion Signals
    # ---------------------------------------------------------
    print("\n[FONTE 2] Scansione Job Posting & Espansione...")
    hiring_signals = fetch_hiring_signals()

    for item in hiring_signals:
        score = add_signal(
            vat_number=item["vat_number"],
            company_name=item["company_name"],
            sector=item["sector"],
            region=item["region"],
            signal_type=item["signal_type"]
        )
        print(f" -> {item['company_name']}: Nuovo Score = {score} pt")

    print("\n✅ PIPELINE MULTI-FONTE COMPLETATA CON SUCCESSO!")

if __name__ == "__main__":
    run_pipeline()