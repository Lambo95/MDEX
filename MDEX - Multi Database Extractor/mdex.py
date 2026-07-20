from datetime import datetime
from getpass import getpass

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

logger = configure_logger()


selected_queries = []


def configure_database(config):

    print()
    print("=" * 60)
    print("CONFIGURAZIONE DATABASE")
    print("=" * 60)

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

    save_config(config)

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

        print(ex)


def run_batch(config):

    global selected_queries

    if not selected_queries:

        print()

        print(
            "Nessuna query selezionata."
        )

        return

    start_date = input(
        "Data/Ora inizio "
        "(YYYY-MM-DD HH:MM:SS): "
    ).strip()

    end_date = input(
        "Data/Ora fine "
        "(YYYY-MM-DD HH:MM:SS): "
    ).strip()

    password = getpass(
        "Password: "
    )

    config["password"] = password

    test_result = test_connection(
        config
    )

    if not test_result["success"]:

        print()

        print(
            "Test connessione fallito."
        )

        print(
            test_result["error"]
        )

        return

    conn = None

    try:

        logger.info(
            "Avvio batch"
        )

        conn = create_connection(
            config
        )

        day_label = datetime.now(
        ).strftime(
            "%Y%m%d"
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

        report_info = (
            create_reports(
                config=config,
                extraction_result=extraction_result,
                start_date=start_date,
                end_date=end_date
            )
        )

        print()

        print(
            "Report TXT :"
        )

        print(
            report_info[
                "txt_report"
            ]
        )

        print()

        print(
            "Report XLSX :"
        )

        print(
            report_info[
                "xlsx_report"
            ]
        )

    except Exception as ex:

        logger.exception(
            "Errore batch"
        )

        print(ex)

    finally:

        if conn:

            conn.close()

            logger.info(
                "Connessione chiusa"
            )


def main():

    logger.info(
        "=" * 80
    )

    logger.info(
        "MDEX AVVIATO"
    )

    logger.info(
        "=" * 80
    )

    config = load_config()

    while True:

        print()
        print("=" * 60)
        print(
            "MDEX - "
            "Multi Database Extractor"
        )
        print("=" * 60)

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
            "6 - Esegui estrazione"
        )

        print(
            "7 - Esci"
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

            run_batch(
                config
            )

        elif choice == "7":

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

    main()