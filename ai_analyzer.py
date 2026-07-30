# ai_analyzer.py
import google.generativeai as genai
import streamlit as st
import re

def get_gemini_api_key():
    """Recupera la chiave API da st.secrets gestendo eventuali strutture TOML."""
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    if "passwords" in st.secrets and "GEMINI_API_KEY" in st.secrets["passwords"]:
        return st.secrets["passwords"]["GEMINI_API_KEY"]
    return None

def clean_ai_response(text):
    """Rimuove il monologo interno/ragionamento dell'AI e restituisce solo il report finale."""
    if "Razionale Strategico M&A" in text:
        # Trova l'inizio del primo titolo effettivo del report
        match = re.search(r'(#+.*Razionale Strategico M&A.*)', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        # Fallback split
        parts = text.split("Razionale Strategico M&A", 1)
        return "### 💡 Razionale Strategico M&A" + parts[1]
    return text.strip()

def generate_executive_summary(company_name, signals):
    """
    Genera un Executive Briefing B2B ad alto livello basato sui segnali M&A dell'azienda.
    """
    api_key = get_gemini_api_key()
    
    if not api_key:
        return "⚠️ **Errore:** `GEMINI_API_KEY` non trovata nei Secrets. Assicurati che sia scritta in cima al file Secrets su Streamlit Cloud."

    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        return f"⚠️ Errore di configurazione API Gemini: {e}"

    signals_text = "\n".join([f"- [{s['Tipo Segnale']}] Rilevato il: {s['Data Rilevamento']}" for s in signals])

    prompt = f"""
    Sei un Senior M&A Partner & Corporate Intelligence Analyst.
    Analizza i seguenti segnali di mercato intercettati per l'azienda: **{company_name}**.

    CRONOLOGIA SEGNALI INTERCETTATI:
    {signals_text}

    TASK: Redigi un Executive Briefing B2B per un Advisor o Fondo di Private Equity.
    IMPORTANTE: Restituisci ESCLUSIVAMENTE il report finale. NON includere monologhi interni, note di ragionamento, descrizioni di ruoli o preamboli. Inizia direttamente con la prima intestazione.

    Rispetta tassativamente questa struttura Markdown:

    ### 💡 Razionale Strategico M&A
    (Spiega in 2-3 frasi cosa indicano questi segnali combinati: potenziale acquisizione, cessione di ramo, ristrutturazione o espansione)

    ### 🎯 Opportunità & Rischi
    * **Opportunità:** (Punto chiave)
    * **Rischi:** (Punto chiave da monitorare)

    ### 🚀 Next Steps Raccomandati
    1. (Azione pratica per l'advisor, es. verifica Visura Camerale o contatto M&A)
    2. (Secondo step operativo)

    Tono: Istituzionale, analitico, orientato alle operazioni di Corporate Finance.
    """

    # 1. Recupera la lista dinamica di modelli abilitati da Google per questa API Key
    dynamic_models = []
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                dynamic_models.append(m.name)
    except Exception:
        pass

    # 2. Fallback con identificatori standard
    known_fallbacks = [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-2.0-flash-lite",
        "gemini-1.5-pro",
        "models/gemini-2.0-flash",
        "models/gemini-1.5-flash",
        "models/gemini-1.5-pro"
    ]

    candidate_models = []
    for m_id in dynamic_models + known_fallbacks:
        if m_id not in candidate_models:
            candidate_models.append(m_id)

    # 3. Prova ogni modello finché uno non risponde con successo
    last_error = None
    for model_name in candidate_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response and response.text:
                return clean_ai_response(response.text)
        except Exception as e:
            last_error = e
            continue

    return f"⚠️ Errore durante l'elaborazione del report AI: {last_error}"