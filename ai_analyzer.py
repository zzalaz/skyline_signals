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
    """
    api_key = get_gemini_api_key()
    
    if not api_key:
        return "⚠️ **Errore:** `GEMINI_API_KEY` non trovata nei Secrets. Assicurati che sia scritta in cima al file Secrets su Streamlit Cloud."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        signals_text = "\n".join([f"- [{s['Tipo Segnale']}] Rilevato il: {s['Data Rilevamento']}" for s in signals])

        prompt = f"""
        Sei un Senior M&A Partner & Corporate Intelligence Analyst.
        Analizza i seguenti segnali di mercato intercettati per l'azienda: **{company_name}**.

        CRONOLOGIA SEGNALI INTERCETTATI:
        {signals_text}

        Redigi un Executive Briefing B2B sintetico e formattato in Markdown per un Advisor o Fondo di Private Equity.
        Rispettat tassativamente questa struttura:

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

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"⚠️ Errore durante l'elaborazione del report AI: {e}"