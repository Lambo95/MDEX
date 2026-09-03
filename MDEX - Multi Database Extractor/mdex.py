from getpass import getpass
from datetime import (
    datetime,
    timedelta
)
import os

from modules.config_manager import (
    load_config,
    save_config,
    show_config
)

from modules.connection_manager import (
    test_connection,
    create_connection
)

from modules.query_discovery import (
    discover_queries,
    show_queries,
    select_queries
)

from modules.extractor import (
    run_extraction
)

from modules.report_manager import (
    create_reports
)

from modules.logger_manager import (
    configure_logger
)

from modules.csv_merger import (
    consolidate_daily_files,
    discover_output_queries    
)

logger = configure_logger()


selected_queries = []

def configure_database(config):

    print()
    print("=" * 30)
    print("CONFIGURAZIONE DATABASE")
    print("=" * 30)

    db_choice = input(
        "Database [1=Oracle, 2=SQL Server]: "
    ).strip()

    if db_choice == "1":

        config["db_type"] = "ORACLE"

        config["host"] = input(
            "Host Oracle: "
        ).strip()

        config["port"] = int(
            input(
                "Porta "
            ).strip()
            or 1521
        )

        config["service_name"] = input(
            "Service Name: "
        ).strip()

        config["user"] = input(
            "Username: "
        ).strip()

    elif db_choice == "2":

        config["db_type"] = "SQLSERVER"

        config["host"] = input(
            "Server SQL: "
        ).strip()

        config["port"] = int(
            input(
                "Porta "
            ).strip()
            or 1433
        )

        config["database"] = input(
            "Database: "
        ).strip()

        config["user"] = input(
            "Username: "
        ).strip()

    config["query_folder"] = input(
        f"Cartella Query [{config['query_folder']}]: "
    ).strip() or config["query_folder"]

    config["output_folder"] = input(
        f"Cartella Output [{config['output_folder']}]: "
    ).strip() or config["output_folder"]

    config["report_folder"] = input(
        f"Cartella Report [{config['report_folder']}]: "
    ).strip() or config["report_folder"]

    output_choice = input(
        "Formato Output [CSV/XLSX]: "
    ).strip().upper()

    if output_choice in ["CSV", "XLSX"]:

        config["output_format"] = (
            output_choice
        )

    save_config(
        config,
        show_message=True
    )

    print()
    print(
        "[OK] Configurazione salvata"
    )

def execute_test(config):

    print()

    password = getpass(
        "Password: "
    )

    config["password"] = password

    result = test_connection(
        config
    )

    print()

    if result["success"]:

        print(
            "[OK] Connessione riuscita"
        )

        print()

        print(
            f"Versione DB : "
            f"{result['version']}"
        )

        print(
            f"Data DB     : "
            f"{result['db_date']}"
        )

    else:

        print(
            "[KO] Connessione fallita"
        )

        print(
            result["error"]
        )

def choose_queries(config):

    global selected_queries

    try:

        queries = discover_queries(
            config["query_folder"]
        )

        selected_queries = (
            select_queries(
                queries
            )
        )

        print()

        print(
            f"Query selezionate: "
            f"{len(selected_queries)}"
        )

    except Exception as ex:

        logger.exception(
            "Errore selezione query"
        )

        print(ex)

def choose_extraction_mode(config):

    print()
    print("Modalità estrazione")
    print()

    print("1 - File unico"
          "(consigliato per query pesanti, inserendo intervallo di tempo ridotto)"
    )

    print(
        "2 - File giornalieri "
        "(consigliato per query leggere)"
    )

    choice = input(
        "Scelta: "
    ).strip()

    if choice == "2":

        config["extraction_mode"] = (
            "DAILY_FILES"
        )

    else:

        config["extraction_mode"] = (
            "SINGLE_FILE"
        )

    save_config(
        config,
        show_message=True
    )

    print()

    print(
        f"Modalità selezionata: "
        f"{config['extraction_mode']}"
    )

def run_batch(config):

    global selected_queries

    if not selected_queries:

        print()
        print("Nessuna query selezionata.")

        return

    start_date = input(
        "Data/Ora inizio (YYYY-MM-DD HH:MM:SS): "
    ).strip()

    end_date = input(
        "Data/Ora fine (YYYY-MM-DD HH:MM:SS): "
    ).strip()

    start_dt = datetime.strptime(
        start_date,
        "%Y-%m-%d %H:%M:%S"
    )

    end_dt = datetime.strptime(
        end_date,
        "%Y-%m-%d %H:%M:%S"
    )

    password = getpass(
        "Password: "
    )

    config["password"] = password

    conn = None

    try:

        logger.info(
            "Avvio batch"
        )

        conn = create_connection(
            config
        )

        mode = (
            config.get(
                "extraction_mode",
                "SINGLE_FILE"
            )
            .strip()
            .upper()
        )

        logger.info(
            f"Modalità estrazione: {mode}"
        )

        if mode == "SINGLE_FILE":

            day_label = (
                start_dt.strftime(
                    "%Y%m%d_%H%M%S"
                )
                + "_"
                + end_dt.strftime(
                    "%Y%m%d_%H%M%S"
                )
            )

            extraction_result = (
                run_extraction(
                    conn=conn,
                    config=config,
                    selected_queries=selected_queries,
                    start_date=start_date,
                    end_date=end_date,
                    day_label=day_label
                )
            )

        else:

            results = []

            total_elapsed = 0

            current_day = start_dt

            while current_day < end_dt:

                next_day = min(
                    current_day +
                    timedelta(days=1),
                    end_dt
                )

                day_label = (
                    current_day.strftime(
                        "%Y%m%d"
                    )
                )

                print()
                print("=" * 30)

                print(
                    f"Elaborazione giorno "
                    f"{day_label}"
                )

                print(
                    "Periodo:"
                )

                print(
                    current_day.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )

                print(
                    next_day.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )

                print("=" * 30)

                daily_result = (
                    run_extraction(
                        conn=conn,
                        config=config,
                        selected_queries=selected_queries,
                        start_date=current_day.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        end_date=next_day.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        day_label=day_label
                    )
                )

                results.extend(
                    daily_result["results"]
                )

                total_elapsed += (
                    daily_result["total_elapsed"]
                )

                current_day = next_day

            extraction_result = {
                "results": results,
                "total_elapsed": round(
                    total_elapsed,
                    2
                )
            }

        report_info = (
            create_reports(
                config=config,
                extraction_result=extraction_result,
                start_date=start_date,
                end_date=end_date
            )
        )

        print()
        print("Report TXT:")
        print(
            report_info[
                "txt_report"
            ]
        )

        print()
        print("Report XLSX:")
        print(
            report_info[
                "xlsx_report"
            ]
        )

    except KeyboardInterrupt:

        logger.warning(
            "Estrazione interrotta dall'utente"
        )

        print()
        print(
            "Interruzione richiesta dall'utente."
        )

    except Exception:

        logger.exception(
            "Errore batch"
        )

    finally:

        if conn:

            conn.close()

            logger.info(
                "Connessione chiusa"
            )

def main():

    logger.info(
        "=" * 60
    )

    logger.info(
        "MDEX AVVIATO"
    )

    logger.info(
        "=" * 60
    )

    config = load_config()

    while True:

        print()
        print("=" * 30)
        print(
            "MDEX - "
            "Multi Database Extractor"
        )
        print("=" * 30)

        print(
            "Database :",
            config["db_type"]
        )

        print(
            "Host     :",
            config["host"]
        )

        print()

        print(
            "1 - Visualizza configurazione"
        )

        print(
            "2 - Configura connessione"
        )

        print(
            "3 - Test connessione"
        )

        print(
            "4 - Elenca query"
        )

        print(
            "5 - Seleziona query"
        )

        print(
            "6 - Modalità estrazione"
        )

        print(
            "7 - Esegui estrazione"
        )

        print(
            "8 - Consolida CSV"
        )

        print(
            "9 - Esci"
        )

        print()

        choice = input(
            "Scelta: "
        ).strip()

        if choice == "1":

            show_config(
                config
            )

        elif choice == "2":

            configure_database(
                config
            )

            config = load_config()

        elif choice == "3":

            execute_test(
                config
            )

        elif choice == "4":

            try:

                queries = (
                    discover_queries(
                        config[
                            "query_folder"
                        ]
                    )
                )

                show_queries(
                    queries
                )

            except Exception as ex:

                print(ex)

        elif choice == "5":

            choose_queries(
                config
            )

        elif choice == "6":

            choose_extraction_mode(
                config
            )

            config = load_config()

        elif choice == "7":

            config = load_config()

            run_batch(
                config
            )

        elif choice == "8":

            if (
                config.get(
                    "output_format",
                    "CSV"
                )
                .strip()
                .upper()
                != "CSV"
            ):

                print()

                print(
                    "Il consolidamento è attualmente "
                    "supportato solo per file CSV."
                )

            else:

                output_queries = (
                    discover_output_queries(
                        config["output_folder"]
                    )
                )

                if not output_queries:

                    print()

                    print(
                        "Nessuna cartella output trovata."
                    )

                else:

                    selected = select_queries(
                        output_queries
                    )

                    for query in selected:

                        files = consolidate_daily_files(
                            query["folder"]
                        )

                        print()

                        print(
                            f"Query: {query['name']}"
                        )

                        if not files:

                            print(
                                "Nessun file da consolidare."
                            )

                        else:

                            print(
                                "File generati:"
                            )

                            for file in files:

                                print(file)

        elif choice == "9":

            logger.info(
                "Uscita applicazione"
            )

            break

        else:

            print()

            print(
                "Scelta non valida."
            )


if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print()

        print(
            "Interruzione richiesta dall'utente."
        )

        logger.info(
            "Applicazione interrotta dall'utente"
        )

    except Exception:

        logger.exception(
            "Errore non gestito"
        )