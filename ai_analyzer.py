# ai_analyzer.py
import google.generativeai as genai
import streamlit as st

def get_gemini_api_key():
    """Recupera la chiave API da st.secrets gestendo eventuali strutture TOML."""
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    if "passwords" in st.secrets and "GEMINI_API_KEY" in st.secrets["passwords"]:
        return st.secrets["passwords"]["GEMINI_API_KEY"]
    return None

def generate_executive_summary(company_name, signals):
    """
    Genera un Executive Briefing B2B ad alto livello basato sui segnali M&A dell'azienda.
    Utilizza un loop di fallback dinamico per selezionare il modello Gemini attivo.
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

    Redigi un Executive Briefing B2B sintetico e formattato in Markdown per un Advisor o Fondo di Private Equity.
    Rispetta tassativamente questa struttura:

    ### 💡 Razionale Strategico M&A
    (Spiega in 2-3 frasi cosa indicano questi segnali combinati: potenziale acquisizione, cessione di ramo, ristrutturazione o espansione)

    ### 🎯 Opportunità & Rischi
    * **Opportunità:** (Punto chiave)
    * **Rischi:** (Punto chiave da monitorare)

    ### 🚀 Next Steps Raccomandati
    1. (Azione pratica per l'advisor, es. verifica Visura Camerale o contatto M&A)
    2. (Secondo step operativo)

    Mantieni un tono istituzionale, sintetico e rigoroso.
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

    # Combina le liste evitando duplicati
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
                return response.text
        except Exception as e:
            last_error = e
            continue

    return f"⚠️ Errore durante l'elaborazione del report AI: {last_error}"