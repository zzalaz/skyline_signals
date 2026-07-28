# ai_analyzer.py
import google.generativeai as genai
import streamlit as st

def generate_executive_summary(company_name, signals):
    """
    Genera un Executive Briefing B2B ad alto livello basato sui segnali M&A dell'azienda.
    """
    api_key = st.secrets.get("GEMINI_API_KEY", None)
    if not api_key:
        return "⚠️ **Errore:** `GEMINI_API_KEY` non configurata nei Secrets di Streamlit."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Formattazione cronologia segnali per l'AI
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