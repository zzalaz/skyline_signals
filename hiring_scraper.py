# hiring_scraper.py
import requests
import xml.etree.ElementTree as ET
import re
import hashlib

def fetch_hiring_signals():
    """
    Scansiona LIVE il web alla ricerca di notizie reali su assunzioni strategiche,
    nomine di CFO, piani industriali e segnali M&A in Italia.
    """
    print("🔍 Avvio scansione LIVE sul web per segnali di hiring ed espansione...")

    # Query di ricerca live su notizie corporate ed economia in Italia
    rss_url = "https://news.google.com/rss/search?q=assunzioni+CFO+OR+%22M%26A%22+OR+fusione+OR+%22direttore+generale%22+azienda&hl=it&gl=IT&ceid=IT:it"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    detected_signals = []

    try:
        response = requests.get(rss_url, headers=headers, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            items = root.findall(".//item")

            print(f"📡 Intercettate {len(items)} notizie reali dal web.")

            for item in items[:10]:  # Analizziamo i 10 articoli più recenti
                title = item.find("title").text if item.find("title") is not None else ""
                
                if not title:
                    continue

                # Pulizia del titolo (rimuoviamo il nome della testata giornalistica alla fine)
                clean_title = re.sub(r' - [^-]+$', '', title).strip()

                # Generiamo una P.IVA sintetica/ID univoco basato sull'impronta hash del titolo
                hash_id = hashlib.md5(clean_title.encode('utf-8')).hexdigest()[:10].upper()
                vat_number = f"IT{hash_id}"

                # Determinazione del tipo di segnale (max 50 caratteri per il database)
                title_upper = clean_title.upper()
                if "CFO" in title_upper or "FINANCE" in title_upper:
                    signal_type = "HIRING: Nomina CFO / Finance"
                elif "M&A" in title_upper or "FUSIONE" in title_upper or "ACQUISIZIONE" in title_upper:
                    signal_type = "M&A: Operazione Straordinaria"
                elif "ASSUNZIONI" in title_upper or "ASSUME" in title_upper:
                    signal_type = "HIRING: Piano Assunzioni"
                else:
                    signal_type = "EXPANSION: Segnale Corporate"

                # Tagliamo il nome dell'azienda/notizia entro 250 caratteri
                company_name = clean_title[:240]

                detected_signals.append({
                    "vat_number": vat_number,
                    "company_name": company_name,
                    "sector": "Corporate / General",
                    "region": "Italia",
                    "signal_type": signal_type
                })

    except Exception as e:
        print(f"⚠️ Errore durante lo scraping live: {e}")

    print(f"✅ Estratti {len(detected_signals)} segnali reali ed elaborati.")
    return detected_signals