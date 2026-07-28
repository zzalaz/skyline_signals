# app.py
import streamlit as st
import pandas as pd
from database import init_db, get_connection

# Configurazione della pagina
st.set_page_config(
    page_title="Skyline M&A Signals — Portal",
    page_icon="📈",
    layout="wide"
)

# --- SISTEMA DI AUTENTICAZIONE ---
def check_password():
    """Restituisce True se l'utente ha inserito credenziali valide."""
    def password_entered():
        user = st.session_state["username"]
        pwd = st.session_state["password"]
        
        if "passwords" in st.secrets and user in st.secrets["passwords"]:
            if pwd == st.secrets["passwords"][user]:
                st.session_state["password_correct"] = True
                del st.session_state["password"]
                del st.session_state["username"]
                return
        st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    # Schermata di Login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 🔒 Accesso Riservato — Skyline M&A Signals")
        st.caption("Inserisci le tue credenziali per accedere al terminale di Corporate Intelligence.")
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Accedi alla Dashboard", on_click=password_entered)

        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("⚠️ Username o Password non validi.")

    return False

if not check_password():
    st.stop()

# --- LOGOUT BARRA LATERALE ---
st.sidebar.markdown("### 👤 Sessione Attiva")
if st.sidebar.button("Disconnetti (Logout)"):
    st.session_state["password_correct"] = False
    st.rerun()

# --- INIZIALIZZAZIONE DATABASE ---
init_db()

st.title("📈 Skyline M&A Signals — Corporate Intelligence")
st.caption("Piattaforma di monitoraggio e identificazione precoce di target societari M&A")

def load_data():
    """Carica le aziende con il rispettivo punteggio aggiornato dal DB."""
    conn, _ = get_connection()
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
    ORDER BY s.total_score DESC, s.last_updated DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def load_company_signals(company_id):
    """Carica la cronologia dei segnali intercettati per un'azienda specifica."""
    conn, db_type = get_connection()
    placeholder = "%s" if db_type == "postgres" else "?"
    query = f"""
    SELECT 
        signal_type AS "Tipo Segnale",
        detected_at AS "Data Rilevamento"
    FROM raw_signals
    WHERE company_id = {placeholder}
    ORDER BY detected_at DESC
    """
    df = pd.read_sql_query(query, conn, params=(int(company_id),))
    conn.close()
    return df

# Caricamento Dati
try:
    df = load_data()

    # --- METRICHE KPI IN ALTO ---
    col1, col2, col3 = st.columns(3)
    total_companies = len(df)
    hot_targets = len(df[df["Score"] >= 30]) if not df.empty else 0
    avg_score = round(df["Score"].mean(), 1) if not df.empty else 0

    col1.metric("Aziende Monitorate", total_companies)
    col2.metric("🔥 Hot Targets (Score >= 30)", hot_targets)
    col3.metric("Punteggio Medio", f"{avg_score} pt")

    st.divider()

    if df.empty:
        st.info("ℹ️ Il database cloud è attivo e pronto, ma non contiene ancora segnali salvati.")
    else:
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

        # --- INTESTAZIONE TABELLA + PULSANTE EXPORT ---
        col_title, col_download = st.columns([3, 1])
        with col_title:
            st.subheader("📊 Classifica Target M&A")
        with col_download:
            csv_data = filtered_df.drop(columns=["id"]).to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Esporta Report CSV",
                data=csv_data,
                file_name="Skyline_MA_Targets_Report.csv",
                mime="text/csv",
                use_container_width=True
            )

        # --- TABELLA PRINCIPALE ---
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
            
            selected_id = int(filtered_df[filtered_df["Azienda"] == selected_company]["id"].values[0])
            signals_df = load_company_signals(selected_id)
            
            st.write(f"**Cronologia eventi intercettati per:** _{selected_company}_")
            st.table(signals_df)

except Exception as e:
    st.error(f"Errore durante la lettura del database: {e}")