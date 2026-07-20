import os


def discover_queries(query_folder):
    """
    Cerca tutti i file .sql nella cartella
    e nelle sottocartelle.
    """

    queries = []

    if not os.path.exists(query_folder):

        raise FileNotFoundError(
            f"Cartella non trovata: {query_folder}"
        )

    for root, _, files in os.walk(query_folder):

        for file in files:

            if file.lower().endswith(".sql"):

                query_name = os.path.splitext(file)[0]

                query_path = os.path.join(
                    root,
                    file
                )

                queries.append(
                    {
                        "name": query_name,
                        "file": query_path
                    }
                )

    queries.sort(
        key=lambda q: q["name"]
    )

    return queries


def show_queries(queries):
    """
    Visualizza la lista numerata.
    """

    print()
    print("=" * 60)
    print("QUERY DISPONIBILI")
    print("=" * 60)

    for index, query in enumerate(
        queries,
        start=1
    ):

        print(
            f"[{index}] "
            f"{query['name']}"
        )

    print("=" * 60)


def parse_selection(selection, total_items):
    """
    Converte:
    1,3,5

    oppure

    1-4

    oppure

    1,3-5,8
    """

    selected = set()

    items = selection.split(",")

    for item in items:

        item = item.strip()

        if "-" in item:

            start, end = item.split("-")

            start = int(start)
            end = int(end)

            for i in range(
                start,
                end + 1
            ):

                if 1 <= i <= total_items:

                    selected.add(i)

        else:

            value = int(item)

            if 1 <= value <= total_items:

                selected.add(value)

    return sorted(selected)


def select_queries(queries):
    """
    Permette all'utente di scegliere
    le query da eseguire.
    """

    if not queries:

        print(
            "Nessuna query trovata."
        )

        return []

    show_queries(queries)

    print()
    print(
        "Selezione:"
    )

    print(
        "ALL -> tutte le query"
    )

    print(
        "1,3,5 -> query specifiche"
    )

    print(
        "1-4 -> intervallo"
    )

    print()

    selection = input(
        "Scelta: "
    ).strip()

    if selection.upper() == "ALL":

        return queries

    try:

        selected_indexes = parse_selection(
            selection,
            len(queries)
        )

        selected_queries = [
            queries[index - 1]
            for index in selected_indexes
        ]

        return selected_queries

    except Exception:

        print(
            "Selezione non valida."
        )

        return []
    
def show_query_details(
    queries
):

    print()
    print("=" * 100)

    for index, query in enumerate(
        queries,
        start=1
    ):

        print(
            f"[{index}] "
            f"{query['name']}"
        )

        print(
            f"     {query['file']}"
        )

    print("=" * 100)