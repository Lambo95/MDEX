import os

from datetime import datetime

from openpyxl import Workbook

from modules.logger_manager import (
    configure_logger
)

logger = configure_logger()


def calculate_summary(results):

    total_queries = len(results)

    ok_count = sum(
        1
        for r in results
        if r["status"] == "OK"
    )

    ko_count = sum(
        1
        for r in results
        if r["status"] == "KO"
    )

    skipped_count = sum(
        1
        for r in results
        if r["status"] == "SKIPPED"
    )

    total_rows = sum(
        r["rows"]
        for r in results
    )

    total_time = round(
        sum(
            r["elapsed"]
            for r in results
        ),
        2
    )

    return {
        "total_queries": total_queries,
        "ok_count": ok_count,
        "ko_count": ko_count,
        "skipped_count": skipped_count,
        "total_rows": total_rows,
        "total_time": total_time
    }

def generate_report_name():

    return datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

def generate_txt_report(
    config,
    results,
    start_date,
    end_date,
    total_elapsed
):

    report_id = generate_report_name()

    report_folder = config["report_folder"]

    os.makedirs(
        report_folder,
        exist_ok=True
    )

    report_file = os.path.join(
        report_folder,
        f"report_{report_id}.txt"
    )

    summary = calculate_summary(
        results
    )

    with open(
        report_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "MDEX REPORT\n"
        )

        file.write(
            "=" * 80 + "\n"
        )

        file.write(
            f"Database : "
            f"{config['db_type']}\n"
        )

        file.write(
            f"Server   : "
            f"{config['host']}\n"
        )

        file.write(
            f"Periodo  : "
            f"{start_date} -> {end_date}\n\n"
        )

        file.write(
            "-" * 60 + "\n"
        )

        for result in results:

            file.write(
                f"QUERY  : {result['name']}\n"
            )

            file.write(
                f"ESITO  : {result['status']}\n"
            )

            file.write(
                f"RIGHE  : {result['rows']}\n"
            )

            file.write(
                f"TEMPO  : {result['elapsed']} sec\n"
            )

            if result["error"]:

                file.write(
                    f"ERRORE : "
                    f"{result['error']}\n"
                )

            file.write(
                "-" * 60 + "\n"
            )

        file.write("\n")

        file.write(
            f"Totale Query : "
            f"{summary['total_queries']}\n"
        )

        file.write(
            f"OK           : "
            f"{summary['ok_count']}\n"
        )

        file.write(
            f"KO           : "
            f"{summary['ko_count']}\n"
        )

        file.write(
            f"SKIPPED      : "
            f"{summary['skipped_count']}\n"
        )

        file.write(
            f"Totale Righe : "
            f"{summary['total_rows']}\n"
        )

        file.write(
            f"Tempo Totale : "
            f"{total_elapsed} sec\n"
        )

    logger.info(
        f"Report TXT generato: "
        f"{report_file}"
    )

    return report_file

def generate_xlsx_report(
    config,
    results,
    start_date,
    end_date,
    total_elapsed
):

    report_id = generate_report_name()

    report_folder = config["report_folder"]

    os.makedirs(
        report_folder,
        exist_ok=True
    )

    report_file = os.path.join(
        report_folder,
        f"report_{report_id}.xlsx"
    )

    summary = calculate_summary(
        results
    )

    wb = Workbook()

    ws = wb.active

    ws.title = "Summary"

    ws.append(
        [
            "QUERY",
            "ESITO",
            "RIGHE",
            "TEMPO_SEC",
            "ERRORE"
        ]
    )

    for result in results:

        ws.append(
            [
                result["name"],
                result["status"],
                result["rows"],
                result["elapsed"],
                result["error"]
            ]
        )

    ws.append([])
    ws.append(
        [
            "TOTAL_QUERIES",
            summary["total_queries"]
        ]
    )

    ws.append(
        [
            "OK",
            summary["ok_count"]
        ]
    )

    ws.append(
        [
            "KO",
            summary["ko_count"]
        ]
    )

    ws.append(
        [
            "SKIPPED",
            summary["skipped_count"]
        ]
    )

    ws.append(
        [
            "TOTAL_ROWS",
            summary["total_rows"]
        ]
    )

    ws.append(
        [
            "TOTAL_TIME",
            total_elapsed
        ]
    )

    wb.save(
        report_file
    )

    logger.info(
        f"Report XLSX generato: "
        f"{report_file}"
    )

    return report_file

def print_summary(
    results,
    total_elapsed
):

    summary = calculate_summary(
        results
    )

    print()

    print("=" * 70)
    print("REPORT ESECUZIONE")
    print("=" * 70)

    print()

    print(
        f"{'QUERY':30}"
        f"{'RIGHE':12}"
        f"{'TEMPO':12}"
        f"{'ESITO':12}"
    )

    print("-" * 70)

    for result in results:

        print(
            f"{result['name']:<35}"
            f"{result['rows']:>10,d}"
            f"{result['elapsed']:>12.2f} s"
            f"{result['status']:>12}"
        )

    print("-" * 70)

    print(
        f"Query Totali : "
        f"{summary['total_queries']}"
    )

    print(
        f"OK           : "
        f"{summary['ok_count']}"
    )

    print(
        f"KO           : "
        f"{summary['ko_count']}"
    )

    print(
        f"SKIPPED      : "
        f"{summary['skipped_count']}"
    )

    print(
        f"Totale Righe : "
        f"{summary['total_rows']}"
    )

    print(
        f"Tempo Totale : "
        f"{total_elapsed} sec"
    )

    print("=" * 70)

def create_reports(
    config,
    extraction_result,
    start_date,
    end_date
):

    results = extraction_result[
        "results"
    ]

    total_elapsed = extraction_result[
        "total_elapsed"
    ]

    txt_report = generate_txt_report(
        config=config,
        results=results,
        start_date=start_date,
        end_date=end_date,
        total_elapsed=total_elapsed
    )

    xlsx_report = generate_xlsx_report(
        config=config,
        results=results,
        start_date=start_date,
        end_date=end_date,
        total_elapsed=total_elapsed
    )

    print_summary(
        results,
        total_elapsed
    )

    return {
        "txt_report": txt_report,
        "xlsx_report": xlsx_report
    }