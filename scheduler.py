# scheduler.py
import schedule
import time
from datetime import datetime
from main import run_pipeline

def scheduled_job():
    print(f"\n⏰ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Avvio scansione programmata...")
    try:
        run_pipeline()
        print("✅ Scansione completata con successo.")
    except Exception as e:
        print(f"❌ Errore durante l'esecuzione della pipeline: {e}")

if __name__ == "__main__":
    print("🤖 --- SKYLINE AUTOMATION BOT AVVIATO ---")
    print("⚙️  Il sistema eseguirà la pipeline automaticamente ogni giorno alle 08:00.")
    print("💡 (Premi CTRL+C nel terminale per arrestare lo scheduler)\n")

    # 1. Esegue subito una prima scansione all'avvio
    scheduled_job()

    # 2. Programma l'esecuzione automatica ogni giorno alle 08:00
    schedule.every().day.at("08:00").do(scheduled_job)

    # In alternativa, per testarlo subito ogni 10 minuti puoi usare:
    # schedule.every(10).minutes.do(scheduled_job)

    # Loop infinito per mantenere attivo il processo
    while True:
        schedule.run_pending()
        time.sleep(30) # Controlla ogni 30 secondi se c'è un task in attesa