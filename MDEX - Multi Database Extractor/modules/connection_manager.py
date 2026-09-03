import oracledb
import pyodbc

from modules.logger_manager import (
    configure_logger
)

logger = configure_logger()

def create_connection(config):
    """
    Factory di connessione.
    """

    db_type = config.get(
        "db_type",
        ""
    ).upper()

    if db_type == "ORACLE":

        return connect_oracle(config)

    elif db_type == "SQLSERVER":

        return connect_sqlserver(config)

    else:

        raise ValueError(
            f"Database non supportato: {db_type}"
        )

def connect_oracle(config):
    """
    Connessione Oracle.
    """

    logger.info(
        "Apertura connessione Oracle"
    )

    dsn = oracledb.makedsn(
        config["host"],
        config["port"],
        service_name=config["service_name"]
    )

    conn = oracledb.connect(
        user=config["user"],
        password=config["password"],
        dsn=dsn
    )

    logger.info(
        "Connessione Oracle OK"
    )

    return conn

def connect_sqlserver(config):
    """
    Connessione SQL Server.
    """

    logger.info(
        "Apertura connessione SQL Server"
    )

    driver = config.get(
        "sql_driver",
        "ODBC Driver 17 for SQL Server"
    )

    conn_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={config['host']},{config['port']};"
        f"DATABASE={config['database']};"
        f"UID={config['user']};"
        f"PWD={config['password']};"
        "TrustServerCertificate=yes;"
    )

    conn = pyodbc.connect(
        conn_string,
        timeout=30
    )

    logger.info(
        "Connessione SQL Server OK"
    )

    return conn

def validate_config(config):
    """
    Verifica che tutti i parametri obbligatori
    siano presenti.
    """

    db_type = config.get(
        "db_type",
        ""
    ).upper()

    required_fields = []

    if db_type == "ORACLE":

        required_fields = [
            "host",
            "port",
            "service_name",
            "user",
            "password"
        ]

    elif db_type == "SQLSERVER":

        required_fields = [
            "host",
            "port",
            "database",
            "user",
            "password"
        ]

    else:

        raise ValueError(
            f"Database non supportato: {db_type}"
        )

    missing = []

    for field in required_fields:

        value = config.get(field)

        if value is None or str(value).strip() == "":

            missing.append(field)

    if missing:

        return {
            "valid": False,
            "missing": missing
        }

    return {
        "valid": True,
        "missing": []
    }

def test_connection(config):

    validation = validate_config(
        config
    )

    if not validation["valid"]:

        return {
            "success": False,
            "error": (
                "Campi mancanti: "
                + ", ".join(
                    validation["missing"]
                )
            )
        }

    conn = None

    try:

        logger.info(
            "Test connessione avviato"
        )

        conn = create_connection(
            config
        )

        info = get_database_info(
            conn,
            config["db_type"].upper()
        )

        logger.info(
            "Test connessione OK"
        )

        return {
            "success": True,
            "version": info["version"],
            "db_date": info["db_date"]
        }

    except Exception as ex:

        logger.exception(
            "Test connessione fallito"
        )

        return {
            "success": False,
            "error": str(ex)
        }

    finally:

        if conn:

            conn.close()

def get_database_info(
    conn,
    db_type
):
    """
    Recupera informazioni principali dal DB.
    """

    cursor = conn.cursor()

    try:

        if db_type == "ORACLE":

            cursor.execute("""
                SELECT
                    banner
                FROM v$version
                WHERE rownum = 1
            """)

            version = cursor.fetchone()[0]

            cursor.execute(
                "SELECT SYSDATE FROM dual"
            )

            db_date = cursor.fetchone()[0]

        else:

            cursor.execute("""
                SELECT @@VERSION
            """)

            version = cursor.fetchone()[0]

            cursor.execute("""
                SELECT GETDATE()
            """)

            db_date = cursor.fetchone()[0]

        return {
            "version": str(version),
            "db_date": str(db_date)
        }

    finally:

        cursor.close()


