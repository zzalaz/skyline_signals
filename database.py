import sqlite3

DB_NAME = "ma_signals.db"

def init_db():
    # Connessione al file SQLite (se non esiste, verrà creato da zero)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Tabella Anagrafica Aziende
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            vat_number TEXT UNIQUE NOT NULL,
            sector TEXT,
            region TEXT
        )
    ''')
    
    # 2. Tabella Segnali Grezzi Intercettati
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            signal_type TEXT NOT NULL,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    
    # 3. Tabella Punteggio Calcolato
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS company_scores (
            company_id INTEGER PRIMARY KEY,
            total_score INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database SQLite e tabelle creati con successo!")

if __name__ == "__main__":
    init_db()