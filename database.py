# database.py
import os
import sqlite3
import psycopg2

def get_db_url():
    """Recupera la stringa di connessione sia da os.environ (GitHub Actions) sia da st.secrets (Streamlit Cloud)."""
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")
    try:
        import streamlit as st
        if "DATABASE_URL" in st.secrets:
            return st.secrets["DATABASE_URL"]
    except Exception:
        pass
    return None

DATABASE_URL = get_db_url()

def get_connection():
    """Restituisce una connessione al DB Cloud (Postgres) o Locale (SQLite)."""
    if DATABASE_URL:
        # Passiamo l'URL direttamente con SSL obbligatorio per Supabase
        return psycopg2.connect(DATABASE_URL, sslmode='require'), "postgres"
    else:
        # Fallback su SQLite Locale
        return sqlite3.connect("ma_signals.db"), "sqlite"

def init_db():
    """Inizializza le tabelle del database."""
    conn, db_type = get_connection()
    cursor = conn.cursor()
    
    if db_type == "postgres":
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id SERIAL PRIMARY KEY,
            vat_number VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            sector VARCHAR(100),
            region VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw_signals (
            id SERIAL PRIMARY KEY,
            company_id INTEGER REFERENCES companies(id),
            signal_type VARCHAR(50) NOT NULL,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_scores (
            company_id INTEGER PRIMARY KEY REFERENCES companies(id),
            total_score INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
    else:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vat_number TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            sector TEXT,
            region TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            signal_type TEXT NOT NULL,
            detected_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_scores (
            company_id INTEGER PRIMARY KEY,
            total_score INTEGER DEFAULT 0,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        );
        """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("✅ Database inizializzato con successo!")