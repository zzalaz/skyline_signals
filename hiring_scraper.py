# hiring_scraper.py
import requests
import xml.etree.ElementTree as ET
import re
import hashlib

def extract_company_name(title):
    """
    Estrae in modo intelligente il nome dell'azienda o ente dal titolo della notizia.
    """
    # 1. Cerca forme societarie note (S.p.A., S.r.l., Group, ecc.)
    legal_match = re.search(r'([A-Z0-9\s\&\.\'-]+?\b(?:S\.p\.A\.|S\.r\.l\.|SpA|Srl|Group|Holding)\b)', title, re.IGNORECASE)
    if legal_match:
        return legal_match.group(1).strip()

    # 2. Riconosce verbi/azioni chiave e prende il soggetto che precede
    action_verbs = r'\b(si espande|cerca|assume|annuncia|firma|acquisisce|compra|nomina|investe|apre|rilancia|fonda)\b'
    parts = re.split(action_verbs, title, flags=re.IGNORECASE)
    if len(parts) > 1 and len(parts[0].strip()) > 2:
        candidate = parts[0].strip()
        # Pulizia prefissi comuni
        candidate = re.sub(r'^(Fusione|Acquisizione|Accordo|Piani di assunzione per|Nuove assunzioni per|Assunzioni|Piano|Operazione)\s+(per|in|tra|di|con|da)?\s*', '', candidate, flags=re.IGNORECASE)
        if 2 < len(candidate) <= 40:
            return candidate.strip(' :,-')

    # 3. Se presente il carattere due punti (es. "Ospedale di Perugia: assunzioni...")
    if ":" in title:
        first_part = title.split(":")[0].strip()
        first_part = re.sub(r'^(Nuove assunzioni|Assunzioni|Offerta lavoro|Cercasi)\s+(in|per|a|all\'|alla)?\s*', '', first_part, flags=re.IGNORECASE)
        if 2 < len(first_part) <= 40:
            return first_part

    # 4. Fallback: estrae le prime parole significative
    words = title.split()
    clean_words = [w for w in words[:4] if w.lower() not in ["nuove", "assunzioni", "carenza", "organici", "in", "per", "all'", "del", "della", "di"]]
    fallback = " ".join(clean_words) if clean_words else title[:30]
    return fallback[:35].strip(' :,-')


def fetch_hiring_signals():
    """Scansiona LIVE il web ed estrae aziende e segnali puliti."""
    print("🔍 Avvio scansione LIVE con estrazione intelligene dei nomi aziendali...")

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

            print(f"📡 Analisi di {len(items)} articoli di notizie...")

            for item in items[:10]:
                title = item.find("title").text if item.find("title") is not None else ""
                if not title:
                    continue

                clean_title = re.sub(r' - [^-]+$', '', title).strip()

                # Estrazione pulita del nome dell'azienda
                company_name = extract_company_name(clean_title)

                # Generazione P.IVA/ID univoco
                hash_id = hashlib.md5(company_name.lower().encode('utf-8')).hexdigest()[:10].upper()
                vat_number = f"IT{hash_id}"

                # Determinazione del tipo di segnale (max 50 car.)
                title_upper = clean_title.upper()
                if "CFO" in title_upper or "FINANCE" in title_upper:
                    signal_type = "HIRING: Nomina CFO / Finance"
                elif "M&A" in title_upper or "FUSIONE" in title_upper or "ACQUISIZIONE" in title_upper:
                    signal_type = "M&A: Operazione Straordinaria"
                elif "ASSUNZIONI" in title_upper or "ASSUME" in title_upper:
                    signal_type = "HIRING: Piano Assunzioni"
                else:
                    signal_type = "EXPANSION: Segnale Corporate"

                detected_signals.append({
                    "vat_number": vat_number,
                    "company_name": company_name,
                    "sector": "Corporate / General",
                    "region": "Italia",
                    "signal_type": signal_type
                })

    except Exception as e:
        print(f"⚠️ Errore durante lo scraping live: {e}")

    print(f"✅ Estratti {len(detected_signals)} segnali con nomi aziendali puliti.")
    return detected_signals