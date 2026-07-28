# app.py
import streamlit as st
import sqlite3
import pandas as pd

DB_NAME = "ma_signals.db"

# Configurazione della pagina
st.set_page_config(
    page_title="Skyline M&A Signals Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Skyline M&A Signals — Corporate Intelligence")
st.caption("Piattaforma di monitoraggio e identificazione precoce di target societari M&A")

def load_data():
    """Carica le aziende con il rispettivo punteggio aggiornato."""
    conn = sqlite3.connect(DB_NAME)
    query = """
    SELECT 
        c.id,
        c.name AS "Azienda",
        c.vat_number AS "P.IVA",
        c.sector AS "Settore",
        c.region AS "Regione",
        s.total_score AS "Score",
        s.last_updated AS "Ultimo Aggiornamento"
    FROM companies c
    JOIN company_scores s ON c.id = s.company_id
    ORDER BY s.total_score DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def load_company_signals(company_id):
    """Carica la cronologia dei segnali intercettati per un'azienda specifica."""
    conn = sqlite3.connect(DB_NAME)
    query = """
    SELECT 
        signal_type AS "Tipo Segnale",
        detected_at AS "Data Rilevamento"
    FROM raw_signals
    WHERE company_id = ?
    ORDER BY detected_at DESC
    """
    df = pd.read_sql_query(query, conn, params=(company_id,))
    conn.close()
    return df

# Caricamento Dati
try:
    df = load_data()

    # --- METRICHE KPI IN ALTO ---
    col1, col2, col3 = st.columns(3)
    total_companies = len(df)
    hot_targets = len(df[df["Score"] >= 30])
    avg_score = round(df["Score"].mean(), 1) if not df.empty else 0

    col1.metric("Aziende Monitorate", total_companies)
    col2.metric("🔥 Hot Targets (Score >= 30)", hot_targets)
    col3.metric("Punteggio Medio", f"{avg_score} pt")

    st.divider()

    # --- BARRA LATERALE PER I FILTRI ---
    st.sidebar.header("🔍 Filtri di Ricerca")
    min_score = st.sidebar.slider("Punteggio minimo (Score)", 0, 100, 0)
    search_query = st.sidebar.text_input("Cerca Azienda o P.IVA:")

    # Applicazione Filtri
    filtered_df = df[df["Score"] >= min_score]
    if search_query:
        filtered_df = filtered_df[
            filtered_df["Azienda"].str.contains(search_query, case=False, na=False) |
            filtered_df["P.IVA"].str.contains(search_query, case=False, na=False)
        ]

    # --- TABELLA PRINCIPALE ---
    st.subheader("📊 Classifica Target M&A")
    
    # Colonna ID nascosta per la visualizzazione pulita
    display_df = filtered_df.drop(columns=["id"])
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # --- DETTAGLIO E CRONOLOGIA SEGNALI ---
    st.subheader("🔎 Analisi Segnali per Singola Azienda")
    
    if not filtered_df.empty:
        selected_company = st.selectbox(
            "Seleziona un'azienda per esaminarne i segnali storici:",
            options=filtered_df["Azienda"].tolist()
        )
        
        selected_id = filtered_df[filtered_df["Azienda"] == selected_company]["id"].values[0]
        signals_df = load_company_signals(selected_id)
        
        st.write(f"**Cronologia eventi intercettati per:** _{selected_company}_")
        st.table(signals_df)
    else:
        st.info("Nessuna azienda corrisponde ai criteri di filtraggio selezionati.")

except Exception as e:
    st.error(f"Impossibile accedere al database: {e}")