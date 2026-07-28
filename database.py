# database.py
import os
import sqlite3
import psycopg2
from urllib.parse import urlparse

# Legge la variabile d'ambiente DATABASE_URL (se presente usa Supabase, altrimenti SQLite locale)
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    """Restituisce una connessione al DB Cloud (Postgres) o Locale (SQLite)."""
    if DATABASE_URL:
        # Connessione a Supabase (PostgreSQL)
        result = urlparse(DATABASE_URL)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port
        return psycopg2.connect(
            dbname=database,
            user=username,
            password=password,
            host=hostname,
            port=port
        ), "postgres"
    else:
        # Fallback su SQLite Locale
        return sqlite3.connect("ma_signals.db"), "sqlite"

def init_db():
    """Inizializza le tabelle del database."""
    conn, db_type = get_connection()
    cursor = conn.cursor()
    
    # Sintassi adattata per entrambi i tipi di DB
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
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_scores (
            company_id INTEGER PRIMARY KEY,
            total_score INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        );
        """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("✅ Database inizializzato con successo!")