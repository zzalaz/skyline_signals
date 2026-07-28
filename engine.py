# engine.py
from database import get_connection, init_db

def add_signal(vat_number, company_name, sector, region, signal_type):
    """Aggiunge un segnale al database centralizzato, creando l'azienda se non esiste, e aggiorna lo score."""
    # 1. Assicuriamo che le tabelle esistano nel database corrente
    init_db()
    
    conn, db_type = get_connection()
    cursor = conn.cursor()
    
    ph = "%s" if db_type == "postgres" else "?"

    try:
        # 2. Inserisci o aggiorna l'azienda
        if db_type == "postgres":
            cursor.execute(f"""
            INSERT INTO companies (vat_number, name, sector, region)
            VALUES ({ph}, {ph}, {ph}, {ph})
            ON CONFLICT (vat_number) DO UPDATE 
            SET name = EXCLUDED.name, sector = EXCLUDED.sector, region = EXCLUDED.region
            RETURNING id;
            """, (vat_number, company_name, sector, region))
            company_id = cursor.fetchone()[0]
        else:
            cursor.execute(f"""
            INSERT OR IGNORE INTO companies (vat_number, name, sector, region)
            VALUES ({ph}, {ph}, {ph}, {ph});
            """, (vat_number, company_name, sector, region))
            cursor.execute(f"SELECT id FROM companies WHERE vat_number = {ph};", (vat_number,))
            company_id = cursor.fetchone()[0]

        # 3. Registra il nuovo segnale grezzo
        cursor.execute(f"""
        INSERT INTO raw_signals (company_id, signal_type)
        VALUES ({ph}, {ph});
        """, (company_id, signal_type))

        # 4. Calcola e aggiorna il punteggio di M&A Target
        score_delta = 20 if "Gazzetta" in signal_type or "Liquidazione" in signal_type else 10

        if db_type == "postgres":
            cursor.execute(f"""
            INSERT INTO company_scores (company_id, total_score, last_updated)
            VALUES ({ph}, {ph}, CURRENT_TIMESTAMP)
            ON CONFLICT (company_id) DO UPDATE 
            SET total_score = company_scores.total_score + {ph}, last_updated = CURRENT_TIMESTAMP
            RETURNING total_score;
            """, (company_id, score_delta, score_delta))
            new_score = cursor.fetchone()[0]
        else:
            cursor.execute(f"""
            INSERT INTO company_scores (company_id, total_score, last_updated)
            VALUES ({ph}, {ph}, CURRENT_TIMESTAMP)
            ON CONFLICT(company_id) DO UPDATE 
            SET total_score = total_score + {ph}, last_updated = CURRENT_TIMESTAMP;
            """, (company_id, score_delta, score_delta))
            cursor.execute(f"SELECT total_score FROM company_scores WHERE company_id = {ph};", (company_id,))
            new_score = cursor.fetchone()[0]

        conn.commit()
        return new_score

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()