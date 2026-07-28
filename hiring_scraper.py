# hiring_scraper.py
import requests
import xml.etree.ElementTree as ET
import re
import hashlib

# Termini e frasi di notizie generiche/pubbliche da scartare tassativamente
STRICT_EXCLUDE_TERMS = [
    "boccata", "ossigeno", "concorso", "infermieri", "medici", "sanità",
    "scuola", "docenti", "precari", "comune", "regione", "ministero",
    "inps", "bando", "graduatoria", "posti", "assunzioni", "posti di lavoro",
    "via libera", "sindacato", "sindacati", "risorse", "progetto", "piano",
    "accordo", "intesa", "svolta", "crisi", "allarme", "bonus", "decreto",
    "legge", "misure", "fondi", "pnrr", "sciopero", "protesta", "strutture pubbliche"
]

# Indicatori societari ufficiali
CORPORATE_PATTERNS = [
    r'\bS\.p\.A\.\b', r'\bS\.r\.l\.\b', r'\bSpA\b', r'\bSrl\b',
    r'\bGroup\b', r'\bHolding\b', r'\bBanca\b', r'\bBank\b',
    r'\bS\.c\.a\.r\.l\.\b', r'\bSocietà\b', r'\bPharma\b', r'\bTech\b',
    r'\bLogistics\b', r'\bIndustries\b'
]

def extract_strict_company(title):
    """Estrae ed accetta ESCLUSIVAMENTE aziende reali con ragione sociale o ente identificabile."""
    # 1. Rimuove il nome della testata alla fine (" - Il Sole 24 Ore")
    clean = re.sub(r' - [^-]+$', '', title).strip()
    clean = re.sub(r'^[«"“\'’\s:-]+|[»"”\'’\s:-]+$', '', clean).strip()

    # 2. Cerca una ragione sociale esplicita (es. "Banca Popolare S.p.A.", "Barilla Group", "Lombardia Industriale S.r.l.")
    for pattern in CORPORATE_PATTERNS:
        match = re.search(r'([A-Z0-9\s\&\.\'-]{2,35}\s*' + pattern + r')', clean, re.IGNORECASE)
        if match:
            comp = match.group(1).strip(' :,-«»"\'')
            # Pulizia di eventuali verbi/preposizioni in testa
            comp = re.sub(r'^(?:Fusione|Acquisizione|Accordo|Assunzioni|Cerca|Assume|In|Per|Da|Tra|Con)\s+', '', comp, flags=re.IGNORECASE)
            if len(comp) >= 3 and not any(term in comp.lower() for term in STRICT_EXCLUDE_TERMS):
                return comp

    # 3. Se presente i due punti, verifica che prima ci sia una dicitura societaria/ente valida e SENZA parole vietate
    if ":" in clean:
        first_part = clean.split(":")[0].strip()
        if 3 <= len(first_part) <= 35:
            if not any(term in first_part.lower() for term in STRICT_EXCLUDE_TERMS):
                # Deve iniziare con maiuscola e non essere una domanda o frase comune
                if first_part[0].isupper() and not re.search(r'\b(come|perché|quanto|quando|dove|ecco|nuovo|nuove|tutti|tutte|san|via)\b', first_part, re.IGNORECASE):
                    return first_part

    # 4. Cerca soggetti aziendali prima di verbi di azione aziendali (es. "Sviluppo Campania cerca...")
    match_verb = re.search(r'^([A-Z0-9\s\&\.\'-]{3,35})\s+(?:cerca|assume|annuncia|acquisisce|compra|investe|apre|fonda)\b', clean)
    if match_verb:
        cand = match_verb.group(1).strip(' :,-')
        if not any(term in cand.lower() for term in STRICT_EXCLUDE_TERMS):
            return cand

    return None


def fetch_hiring_signals():
    """Scansiona notizie web con query focalizzata su aziende e ragione sociale."""
    print("🔍 Avvio scansione LIVE con query focalizzata su Corporate & M&A...")

    # Query mirata su entità societarie e operazioni M&A/assunzioni strategiche
    rss_url = 'https://news.google.com/rss/search?q=("S.p.A."+OR+"S.r.l."+OR+"SpA"+OR+"Srl"+OR+"Group")+AND+(assunzioni+OR+"M%26A"+OR+fusione+OR+acquisizione+OR+"piano+industriale")&hl=it&gl=IT&ceid=IT:it'
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    detected_signals = []

    try:
        response = requests.get(rss_url, headers=headers, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            items = root.findall(".//item")

            print(f"📡 Analisi di {len(items)} notizie corporate intercettate...")

            for item in items:
                title = item.find("title").text if item.find("title") is not None else ""
                if not title:
                    continue

                # Estrazione e validazione rigorosa
                company_name = extract_strict_company(title)

                if not company_name:
                    continue

                # Generazione ID/P.IVA univoca
                hash_id = hashlib.md5(company_name.lower().encode('utf-8')).hexdigest()[:10].upper()
                vat_number = f"IT{hash_id}"

                # Determinazione del tipo di segnale
                title_upper = title.upper()
                if "CFO" in title_upper or "FINANCE" in title_upper:
                    signal_type = "HIRING: Nomina CFO / Finance"
                elif "M&A" in title_upper or "FUSIONE" in title_upper or "ACQUISIZIONE" in title_upper:
                    signal_type = "M&A: Operazione Straordinaria"
                elif "ASSUNZIONI" in title_upper or "ASSUME" in title_upper:
                    signal_type = "HIRING: Piano Assunzioni"
                else:
                    signal_type = "EXPANSION: Piano Industriale"

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

    print(f"✅ Filtro Strict: estratti {len(detected_signals)} soggetti aziendali reali.")
    return detected_signals