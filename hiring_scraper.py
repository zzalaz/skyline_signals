# hiring_scraper.py
import random

def fetch_hiring_signals():
    """
    Simula / scansiona il monitoraggio dei job board e delle pagine "Lavora con noi"
    alla ricerca di ruoli chiave legati a M&A, Ristrutturazione o Espansione.
    """
    print("🔍 Scansione in corso sui Job Board e portali di reclutamento...")

    # Ruoli chiave che incrementano lo score M&A
    key_roles = [
        "Head of M&A and Corporate Development",
        "Chief Financial Officer (CFO)",
        "Plant Manager - Nuova Apertura",
        "HR Restructuring Specialist"
    ]

    # Aziende target simulate / rilevate
    detected_signals = [
        {
            "vat_number": "IT03882910158",  # Lombardia Industriale S.r.l. (già presente!)
            "company_name": "Lombardia Industriale S.r.l.",
            "sector": "Manifatturiero & Metalmeccanica",
            "region": "Lombardia",
            "signal_type": f"HIRING: {random.choice(key_roles)}"
        },
        {
            "vat_number": "IT09876543210",  # Nuova azienda rilevata
            "company_name": "Veneto Pharma Tech S.p.A.",
            "sector": "Pharma & Biotech",
            "region": "Veneto",
            "signal_type": "HIRING: Head of M&A and Corporate Development"
        }
    ]

    print(f"✅ Trovati {len(detected_signals)} segnali di espansione/organigramma.")
    return detected_signals