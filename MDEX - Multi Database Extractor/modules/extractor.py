import os
import csv
import time
import traceback
from datetime import datetime

from openpyxl import Workbook

from modules.logger_manager import (
    configure_logger
)

logger = configure_logger()

def get_output_file(
    output_folder,
    query_name,
    output_format,
    extraction_mode,
    day_label=None,
    start_label=None,
    end_label=None
):
    """
    Costruisce il nome del file di output.

    DAILY_FILES
        FILE_IN_20260301.csv

    SINGLE_FILE
        FILE_IN_20260301_20260331.csv
    """

    query_dir = os.path.join(
        output_folder,
        query_name
    )

    os.makedirs(
        query_dir,
        exist_ok=True
    )

    extension = output_format.lower()

    if extraction_mode == "DAILY_FILES":

        filename = (
            f"{query_name}_{day_label}."
            f"{extension}"
        )

    else:

        filename = (
            f"{query_name}_"
            f"{start_label}_"
            f"{end_label}."
            f"{extension}"
        )

    return os.path.join(
        query_dir,
        filename
    )

def read_sql_file(sql_file):
    """
    Legge il contenuto del file SQL.
    """

    with open(
        sql_file,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()

def execute_query(
    conn,
    db_type,
    sql,
    start_date,
    end_date,
    fetch_size
):
    """
    Esegue una query.
    """

    cursor = conn.cursor()

    cursor.arraysize = fetch_size

    try:

        if db_type == "ORACLE":

            cursor.prefetchrows = fetch_size

            cursor.execute(
                sql,
                {
                    "inizio": start_date,
                    "fine": end_date
                }
            )

        else:

            cursor.execute(
                sql,
                (
                    start_date,
                    end_date
                )
            )

        return cursor

    except Exception:

        cursor.close()

        raise

def export_csv(
    cursor,
    output_file,
    fetch_size
):

    total_rows = 0

    columns = [
        col[0]
        for col in cursor.description
    ]

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as csv_file:

        writer = csv.writer(
            csv_file
        )

        writer.writerow(
            columns
        )

        while True:

            rows = cursor.fetchmany(
                fetch_size
            )

            if not rows:
                break

            writer.writerows(
                rows
            )

            total_rows += len(rows)

    return total_rows

def export_xlsx(
    cursor,
    output_file,
    fetch_size
):

    wb = Workbook()

    ws = wb.active

    ws.title = "Data"

    columns = [
        col[0]
        for col in cursor.description
    ]

    ws.append(columns)

    total_rows = 0

    while True:

        rows = cursor.fetchmany(
            fetch_size
        )

        if not rows:
            break

        for row in rows:

            ws.append(
                list(row)
            )

        total_rows += len(rows)

    ws.auto_filter.ref = ws.dimensions

    wb.save(output_file)

    return total_rows

def export_data(
    cursor,
    output_file,
    output_format,
    fetch_size
):
    """
    Esporta i dati nel formato richiesto.

    Formati supportati:
    - CSV
    - XLSX
    """

    output_format = (
        output_format.upper().strip()
    )

    logger.info(
        f"Export file: {output_file}"
    )

    logger.info(
        f"Formato export: {output_format}"
    )

    if output_format == "CSV":

        return export_csv(
            cursor=cursor,
            output_file=output_file,
            fetch_size=fetch_size
        )

    elif output_format == "XLSX":

        return export_xlsx(
            cursor=cursor,
            output_file=output_file,
            fetch_size=fetch_size
        )

    else:

        error_message = (
            f"Formato non supportato: "
            f"{output_format}"
        )

        logger.error(
            error_message
        )

        raise ValueError(
            error_message
        )

def extract_query(
    conn,
    config,
    query,
    start_date,
    end_date,
    day_label
):
    """
    Esegue una singola query e restituisce
    statistiche per il report finale.
    """

    start_time = time.perf_counter()

    output_file = get_output_file(
    output_folder=config["output_folder"],
    query_name=query["name"],
    output_format=config["output_format"],
    extraction_mode=config["extraction_mode"],
    day_label=day_label,
    start_label=datetime.strptime(start_date,"%Y-%m-%d %H:%M:%S").strftime("%Y%m%d_%H%M%S"),
    end_label=datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S").strftime("%Y%m%d_%H%M%S")
    # start_label=start_date[:10].replace("-", ""),
    # end_label=end_date[:10].replace("-", "")
    )


    if os.path.exists(output_file):

        logger.info(
            f"[SKIP] {query['name']} "
            f"-> file già presente "
            f"({output_file})"
        )

        return {
            "name": query["name"],
            "status": "SKIPPED",
            "rows": 0,
            "elapsed": 0,
            "file": output_file,
            "error": ""
        }

    logger.info(
        f"Avvio query {query['name']}"
    )

    cursor = None

    try:

        sql = read_sql_file(
            query["file"]
        )

        cursor = execute_query(
            conn=conn,
            db_type=config["db_type"].upper(),
            sql=sql,
            start_date=start_date,
            end_date=end_date,
            fetch_size=config["fetch_size"]
        )

        rows = export_data(
            cursor=cursor,
            output_file=output_file,
            output_format=config["output_format"],
            fetch_size=config["fetch_size"]
        )

        elapsed = round(
            time.perf_counter() -
            start_time,
            2
        )

        logger.info(
            f"Query {query['name']} "
            f"completata "
            f"Rows={rows} "
            f"Time={elapsed}s"
        )

        return {
            "name": query["name"],
            "status": "OK",
            "rows": rows,
            "elapsed": elapsed,
            "file": output_file,
            "error": ""
        }

    except Exception as ex:

        logger.exception(
            f"Errore query "
            f"{query['name']}"
        )

        if os.path.exists(output_file):

            try:

                os.remove(
                    output_file
                )

            except Exception:
                pass

        elapsed = round(
            time.perf_counter() -
            start_time,
            2
        )

        return {
            "name": query["name"],
            "status": "KO",
            "rows": 0,
            "elapsed": elapsed,
            "file": output_file,
            "error": str(ex)
        }

    finally:

        if cursor:

            cursor.close()

def run_extraction(
    conn,
    config,
    selected_queries,
    start_date,
    end_date,
    day_label
):
    """
    Esegue l'intero batch selezionato.
    """

    results = []

    total_start = time.perf_counter()

    logger.info(
        "=" * 20
    )

    logger.info(
        "INIZIO ESTRAZIONE"
    )

    logger.info(
        "=" * 20
    )

    for query in selected_queries:

        result = extract_query(
            conn=conn,
            config=config,
            query=query,
            start_date=start_date,
            end_date=end_date,
            day_label=day_label
        )

        results.append(
            result
        )

        time.sleep(
            config["sleep_seconds"]
        )

    total_elapsed = round(
        time.perf_counter() -
        total_start,
        2
    )

    logger.info(
        "=" * 20
    )

    logger.info(
        f"FINE ESTRAZIONE "
        f"({total_elapsed}s)"
    )

    logger.info(
        "=" * 20
    )

    return {
        "results": results,
        "total_elapsed": total_elapsed
    }