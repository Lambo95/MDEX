import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "db_type": "ORACLE",
    "host": "",
    "port": 1521,
    "service_name": "",
    "database": "",
    "user": "",
    "query_folder": "queries",
    "output_folder": "output",
    "report_folder": "reports",
    "sleep_seconds": 5,
    "fetch_size": 1000,
    "output_format": "CSV"
}


def create_folders(config):
    """
    Crea automaticamente tutte le cartelle
    necessarie per il funzionamento di MDEX.
    """

    folders = [
        config["query_folder"],
        config["output_folder"],
        config["report_folder"],
        "logs"
    ]

    for folder in folders:

        os.makedirs(
            folder,
            exist_ok=True
        )

    os.makedirs(
        os.path.join(
            config["query_folder"],
            "oracle"
        ),
        exist_ok=True
    )

    os.makedirs(
        os.path.join(
            config["query_folder"],
            "sqlserver"
        ),
        exist_ok=True
    )


def create_default_config():
    """
    Crea automaticamente config.json
    con i valori di default.
    """

    with open(
        CONFIG_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            DEFAULT_CONFIG,
            file,
            indent=4
        )

    config = DEFAULT_CONFIG.copy()

    create_folders(config)

    return config


def load_config():
    """
    Carica il file config.json.
    Se non esiste viene creato.
    """

    if not os.path.exists(CONFIG_FILE):

        print(
            "[INFO] Configurazione non trovata."
        )

        print(
            "[INFO] Creazione config.json..."
        )

        return create_default_config()

    try:

        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            config = json.load(file)

        create_folders(config)

        return config

    except Exception as ex:

        print(
            "[ERROR] Impossibile leggere config.json"
        )

        print(ex)

        raise


def save_config(config):
    """
    Salva configurazione e ricrea
    le cartelle necessarie.
    """

    try:

        with open(
            CONFIG_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                config,
                file,
                indent=4
            )

        create_folders(config)

        print(
            "[OK] Configurazione salvata."
        )

    except Exception as ex:

        print(
            "[ERROR] Salvataggio configurazione"
        )

        print(ex)

        raise


def show_config(config):
    """
    Visualizza la configurazione corrente.
    """

    print()
    print("=" * 70)
    print("CONFIGURAZIONE ATTUALE")
    print("=" * 70)

    for key, value in config.items():

        print(
            f"{key:<20} : {value}"
        )

    print("=" * 70)


def update_config_value(
    config,
    key,
    value
):
    """
    Aggiorna un parametro della configurazione.
    """

    if key not in config:

        raise KeyError(
            f"Chiave non valida: {key}"
        )

    config[key] = value

    save_config(config)


def reset_config():
    """
    Ripristina configurazione standard.
    """

    save_config(
        DEFAULT_CONFIG.copy()
    )

    return DEFAULT_CONFIG.copy()