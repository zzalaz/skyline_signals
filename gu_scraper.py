# gu_scraper.py
import requests
import xml.etree.ElementTree as ET
import re

# Escludiamo procedure fallimentari o enti pubblici per mantenere solo M&A e Corporate
STRICT_GU_EXCLUDE = [
    "comune", "regione", "ministero", "inps", "fallimento", 
    "liquidazione giudiziale", "procedura concorsuale", "bando"
]

def extract_vat_and_company(text):
    """
    Estrae la P.IVA REALE (11 cifre) e la Ragione Sociale esatta da un testo legale della Gazzetta Ufficiale.
    """
    # 1. Cerca una Partita IVA o Codice Fiscale italiano a 11 cifre
    vat_match = re.search(r'\b(\d{11})\b', text)
    vat_number = f"IT{vat_match.group(1)}" if vat_match else None

    # 2. Estrae la Ragione Sociale formale (S.p.A., S.r.l., SpA, Srl, Group)
    company_pattern = r'\b((?:[A-Z0-9\'-]+\s+){1,5}(?:S\.p\.A\.|S\.r\.l\.|SpA|Srl|Group|Società per Azioni|Società a responsabilità limitata))\b'
    company_match = re.search(company_pattern, text, re.IGNORECASE)
    
    company_name = company_match.group(1).strip() if company_match else None

    return vat_number, company_name

def fetch_gazzetta_official_signals():
    """
    Scansiona gli atti ufficiali di Fusioni, Scissioni e Operazioni Straordinarie dalla Gazzetta Ufficiale.
    """
    print("📜 Avvio scansione atti ufficiali dalla Gazzetta Ufficiale...")
    
    # Query mirata agli atti di Parte II della Gazzetta Ufficiale
    rss_url = 'https://news.google.com/rss/search?q="gazzettaufficiale.it"+AND+("progetto+di+fusione"+OR+"scissione"+OR+"aumento+di+capitale"+OR+"trasferimento+ramo")&hl=it&gl=IT&ceid=IT:it'
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    official_signals = []
    seen_vats = set()

    try:
        response = requests.get(rss_url, headers=headers, timeout=12)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            items = root.findall(".//item")

            for item in items:
                title = item.find("title").text if item.find("title") is not None else ""
                description = item.find("description").text if item.find("description") is not None else ""
                full_text = f"{title} {description}"

                if any(ex in full_text.lower() for ex in STRICT_GU_EXCLUDE):
                    continue

                vat_number, company_name = extract_vat_and_company(full_text)

                # Salviamo il segnale solo se possiede una Partita IVA reale a 11 cifre
                if vat_number and company_name and vat_number not in seen_vats:
                    seen_vats.add(vat_number)

                    text_upper = full_text.upper()
                    if "FUSIONE" in text_upper:
                        signal_type = "OFFICIAL: Progetto di Fusione (G.U.)"
                    elif "SCISSIONE" in text_upper:
                        signal_type = "OFFICIAL: Progetto di Scissione (G.U.)"
                    elif "AUMENTO DI CAPITALE" in text_upper:
                        signal_type = "OFFICIAL: Aumento di Capitale Deliberato (G.U.)"
                    else:
                        signal_type = "OFFICIAL: Trasferimento Ramo d'Azienda (G.U.)"

                    official_signals.append({
                        "vat_number": vat_number,
                        "company_name": company_name,
                        "sector": "Corporate / Legal",
                        "region": "Italia",
                        "signal_type": signal_type
                    })

                if len(official_signals) >= 5:
                    break

    except Exception as e:
        print(f"⚠️ Errore durante lo scraping della Gazzetta Ufficiale: {e}")

    print(f"✅ Gazzetta Ufficiale: estratti {len(official_signals)} atti con P.IVA REALE a 11 cifre.")
    return official_signals