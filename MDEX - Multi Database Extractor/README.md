# MDEX v1.1

Multi Database Extractor

Tool Python per l'esecuzione automatizzata di query SQL ed esportazione risultati in CSV o XLSX.

Database supportati:

- Oracle
- Microsoft SQL Server

---

Nuova release di MDEX (Multi Database Extractor) con importanti miglioramenti alla gestione delle estrazioni, della configurazione e della reportistica.

## Nuove funzionalità

### Naming avanzato dei file

La modalità SINGLE_FILE include ora anche l'orario nel nome del file.

Questo evita conflitti e skip involontari durante l'esecuzione di più estrazioni nello stesso giorno.

### Consolidamento CSV

Nuova funzione:

8 - Consolida CSV

Permette di unire automaticamente i file CSV appartenenti alla stessa query e allo stesso giorno.

### Resume automatico

Se un file di output esiste già, MDEX non riesegue la query e registra lo stato:

SKIPPED

Funzionalità utile per riprendere estrazioni interrotte.

## Miglioramenti

- Gestione configurazione più robusta.
- Aggiornamento automatico dei nuovi parametri di configurazione.
- Migliore gestione dei nomi file.
- Miglioramenti ai report TXT e XLSX.
- Ottimizzazione del logging.
- Rimozione della connessione di test ridondante prima dell'esecuzione batch.
- Migliore gestione delle query di grandi dimensioni.

### MDEX è un tool sviluppato per automatizzare estrazioni massive multi-database, supportare scenari di recovery tramite SKIP automatico e semplificare la produzione di dataset CSV/XLSX e report operativi.

## Autore

Lambo


