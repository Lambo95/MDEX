import csv
import os
import re

def discover_output_queries(
    output_folder
):
    """
    Scopre tutte le query
    presenti nella cartella output.
    """

    queries = []

    if not os.path.exists(
        output_folder
    ):
        return queries

    for name in os.listdir(
        output_folder
    ):

        full_path = os.path.join(
            output_folder,
            name
        )

        if os.path.isdir(
            full_path
        ):

            queries.append(
                {
                    "name": name,
                    "folder": full_path
                }
            )

    queries.sort(
        key=lambda q: q["name"]
    )

    return queries


def merge_csv_files(
    source_files,
    output_file
):
    """
    Unisce più CSV aventi
    la stessa struttura.
    """

    first_file = True

    total_rows = 0

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as outfile:

        writer = csv.writer(outfile)

        for file in source_files:

            with open(
                file,
                "r",
                encoding="utf-8-sig"
            ) as infile:

                reader = csv.reader(
                    infile
                )

                header = next(
                    reader,
                    None
                )

                if header is None:
                    continue

                if first_file:

                    writer.writerow(
                        header
                    )

                    first_file = False

                for row in reader:

                    writer.writerow(
                        row
                    )

                    total_rows += 1

    return total_rows


def group_files_by_day(
    query_folder
):

    if not os.path.exists(
        query_folder
    ):
        return {}
    
    groups = {}

    pattern = re.compile(
        r"(.*)_(\d{8})_\d{6}_\d{8}_\d{6}\.csv"
    )

    for file in os.listdir(
        query_folder
    ):

        match = pattern.match(
            file
        )

        if not match:
            continue

        query_name = match.group(1)

        day = match.group(2)

        key = (
            query_name,
            day
        )

        groups.setdefault(
            key,
            []
        ).append(
            os.path.join(
                query_folder,
                file
            )
        )

    return groups


def consolidate_daily_files(
    query_folder
):

    groups = group_files_by_day(
        query_folder
    )

    generated_files = []

    for (
        query_name,
        day
    ), files in groups.items():

        files.sort()

        output_file = os.path.join(
            query_folder,
            f"{query_name}_{day}.csv"
        )

        merge_csv_files(
            files,
            output_file
        )

        generated_files.append(
            output_file
        )

    return generated_files