# hiring_scraper.py
import requests
import xml.etree.ElementTree as ET
import re
import hashlib

# Lista di termini generici o notizie pubbliche da scartare se scambiati per aziende
NOISE_BLACKLIST = [
    "sanità", "strutture pubbliche", "pubblica amministrazione", "ospedale",
    "regione", "comune", "ministero", "sindacati", "in carenza", "via libera",
    "firmati", "contratti", "nuove assunzioni", "piano assunzioni"
]

def clean_and_extract_company(title):
    """Estrae e pulisce rigorosamente il nome dell'azienda o ente dal titolo."""
    # 1. Rimuove virgolette, parentesi e caratteri speciali iniziali/finali
    clean = re.sub(r'^[«"“\'’\s:-]+|[»"”\'’\s:-]+$', '', title).strip()
    
    # 2. Corregge prefissi spezzati tipo "ll'ospedale" o "all'Azienda"
    clean = re.sub(r'^(?:[lLlhH][\'’]|all[\'’]|dall[\'’]|nell[\'’])\s*', '', clean).strip()

    # 3. Riconosce forme societarie ufficiali (S.p.A., S.r.l., SpA, Srl, Group, Holding)
    m = re.search(r'([A-Z0-9\s\&\.\'-]+?\b(?:S\.p\.A\.|S\.r\.l\.|SpA|Srl|Group|Holding)\b)', clean, re.IGNORECASE)
    if m:
        return m.group(1).strip()

    # 4. Gestisce titoli con azioni o due punti (es. "Sviluppo Campania: approvato...")
    if ":" in clean:
        candidate = clean.split(":")[0].strip()
        candidate = re.sub(r',.*$', '', candidate).strip() # Rimuove incisi dopo la virgola
        if len(candidate) >= 3 and not any(word in candidate.lower() for word in NOISE_BLACKLIST):
            return candidate

    # 5. Cerca il soggetto principale prima dei verbi di azione
    match_verb = re.search(r'^(.*?)\s+(?:cerca|assume|annuncia|acquisisce|compra|investe|apre|firma|si espande)\b', clean, re.IGNORECASE)
    if match_verb:
        candidate = match_verb.group(1).strip()
        candidate = re.sub(r'^(?:Fusione|Acquisizione|Intesa|Accordo)\s+', '', candidate, flags=re.IGNORECASE)
        candidate = re.sub(r',.*$', '', candidate).strip()
        if len(candidate) >= 3 and not any(word in candidate.lower() for word in NOISE_BLACKLIST):
            return candidate

    # 6. Fallback pulito: prende le prime parole significative
    words = clean.split()
    clean_words = []
    for w in words[:4]:
        w_clean = re.sub(r'[^\w\s]', '', w)
        if w_clean.lower() not in ["nuove", "assunzioni", "carenza", "organici", "in", "per", "del", "della", "di", "con", "tra"]:
            clean_words.append(w)
        else:
            break
            
    fallback = " ".join(clean_words).strip(' :,-«»"\'')
    if len(fallback) >= 3 and not any(word in fallback.lower() for word in NOISE_BLACKLIST):
        return fallback

    return None


def fetch_hiring_signals():
    """Scansiona LIVE il web ed applica la validazione strict per entità societarie."""
    print("🔍 Avvio scansione LIVE con Filtro di Qualificazione Entity...")

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

            for item in items:
                title = item.find("title").text if item.find("title") is not None else ""
                if not title:
                    continue

                # Rimuove nome testata giornalistica
                clean_title = re.sub(r' - [^-]+$', '', title).strip()

                # Estrazione e validazione rigorosa del nome azienda
                company_name = clean_and_extract_company(clean_title)

                # Scarta se non ha passato i controlli di qualità
                if not company_name or len(company_name) < 3:
                    continue
                if any(noise in company_name.lower() for noise in NOISE_BLACKLIST):
                    continue

                # Generazione P.IVA/ID univoco
                hash_id = hashlib.md5(company_name.lower().encode('utf-8')).hexdigest()[:10].upper()
                vat_number = f"IT{hash_id}"

                # Determinazione segnale
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

                if len(detected_signals) >= 10:
                    break

    except Exception as e:
        print(f"⚠️ Errore durante lo scraping live: {e}")

    print(f"✅ Filtro applicato: estratti {len(detected_signals)} soggetti societari validi.")
    return detected_signals