import sqlite3
from datetime import datetime

DB_NAME = "ma_signals.db"

# Tabella dei pesi base per ciascuna tipologia di segnale
SIGNAL_WEIGHTS = {
    "GAZZETTA_ATTO": 35,      # Fusioni, scissioni, aumenti di capitale
    "NEW_PATENT": 25,         # Registrazione di nuovi brevetti o marchi
    "HIRING_SPIKE": 20,       # Impennata di posizioni aperte / recruiting
    "WEBSITE_TRAFFIC": 15     # Aumento rilevante del traffico web
}

def add_signal(vat_number: str, company_name: str, sector: str, region: str, signal_type: str) -> int:
    """
    Registra l'azienda e il segnale intercettato, quindi ricalcola e restituisce il punteggio totale.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Inserisce l'azienda o aggiorna i dati se la P.IVA è già presente (UPSERT)
    cursor.execute('''
        INSERT INTO companies (name, vat_number, sector, region)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(vat_number) DO UPDATE SET 
            name = excluded.name,
            sector = excluded.sector,
            region = excluded.region
    ''', (company_name, vat_number, sector, region))
    
    # Recupera l'ID dell'azienda
    cursor.execute('SELECT id FROM companies WHERE vat_number = ?', (vat_number,))
    company_id = cursor.fetchone()[0]
    
    # 2. Registra il nuovo segnale nella tabella dei segnali grezzi
    cursor.execute('''
        INSERT INTO raw_signals (company_id, signal_type)
        VALUES (?, ?)
    ''', (company_id, signal_type))
    
    conn.commit()
    conn.close()
    
    # 3. Ricalcola e salva il punteggio complessivo aggiornato
    return update_score(company_id)

def update_score(company_id: int) -> int:
    """
    Recupera tutti i segnali dell'azienda e calcola il punteggio ponderato in base al tempo trascorso.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT signal_type, detected_at 
        FROM raw_signals 
        WHERE company_id = ?
    ''', (company_id,))
    signals = cursor.fetchall()
    
    total_score = 0.0
    now = datetime.now()
    
    for sig_type, detected_at_str in signals:
        try:
            detected_at = datetime.strptime(detected_at_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            detected_at = datetime.fromisoformat(detected_at_str)
            
        days_old = (now - detected_at).days
        base_weight = SIGNAL_WEIGHTS.get(sig_type, 10)
        
        # Decadimento temporale: il peso diminuisce gradualmente nell'arco di 60 giorni
        decay_factor = max(0.1, 1.0 - (days_old / 60.0))
        total_score += base_weight * decay_factor
        
    final_score = int(round(total_score))
    
    # Salva o aggiorna il punteggio calcolato
    cursor.execute('''
        INSERT INTO company_scores (company_id, total_score, last_updated)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(company_id) DO UPDATE SET 
            total_score = excluded.total_score,
            last_updated = CURRENT_TIMESTAMP
    ''', (company_id, final_score))
    
    conn.commit()
    conn.close()
    
    return final_score

if __name__ == "__main__":
    # Test di prova direttamente sul file
    test_score = add_signal(
        vat_number="09876543210",
        company_name="Innovazione Industriale S.r.l.",
        sector="Meccatronica",
        region="Emilia-Romagna",
        signal_type="NEW_PATENT"
    )
    print(f"✅ Test engine eseguito! Punteggio azienda: {test_score}")