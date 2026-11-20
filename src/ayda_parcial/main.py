from collections.abc import Callable

from ayda_parcial.data import read_numbers
from ayda_parcial.floyd_warshall import floyd_warshall, format_report as format_graph_report
from ayda_parcial.graph import EDGES, QUERIES, VERTICES
from ayda_parcial.max_subarray import run_report as format_max_subarray_report
from ayda_parcial.quantiles import run_report as format_quantiles_report
from ayda_parcial.spellchecker import analyze, format_report, select
from ayda_parcial.top_periods import run_report as format_top_periods_report
from ayda_parcial.word_search import (
    MATRIX_FILE,
    WORDS as SEARCH_WORDS,
    find_words,
    format_report as format_word_search_report,
    read_matrix,
)

MENU = """
1. Corrector ortográfico (consigna 1)
2. Floyd-Warshall (consigna 2)
3. Búsqueda de palabras (consigna 3)
4. Mejor periodo de utilidad (consigna 4)
5. Ver datos cargados
6. Salir
"""

CONSIGNA_4_MENU = """
--- Consigna 4: mejor periodo de utilidad ---
4.1 Parte A: Kadane vs Divide y Vencerás
4.2 Parte B: Top-10 periodos no solapados
4.3 Parte C: Percentiles y mediana
4.4 Ejecutar las tres partes
4.5 Volver
"""


def _load_values() -> list[int] | None:
    try:
        return read_numbers()
    except (FileNotFoundError, ValueError) as error:
        print(f"No se pudieron cargar los datos: {error}")
        return None


def _show_report(builder: Callable[[list[int]], str], values: list[int]) -> None:
    try:
        print(builder(values))
    except (ValueError, RuntimeError) as error:
        print(f"No se pudo completar el cálculo: {error}")


def spellchecker_flow() -> None:
    word = input("Palabra a corregir (enter para programaceón): ").strip() or "programaceón"
    candidates = analyze(word)
    print(format_report(word, candidates, select(candidates)))


def floyd_warshall_flow() -> None:
    result = floyd_warshall(VERTICES, EDGES)
    print(format_graph_report(result, EDGES, QUERIES))


def word_search_flow() -> None:
    word = input("Palabra a buscar (enter para las 5 de la consigna): ").strip()
    words = (word,) if word else SEARCH_WORDS
    try:
        matrix = read_matrix()
    except FileNotFoundError:
        print(f"No se encontró el archivo {MATRIX_FILE}.")
        return
    except ValueError as error:
        print(f"La matriz no es válida: {error}.")
        return
    print(format_word_search_report(matrix, find_words(matrix, words)))


def consigna_4_flow() -> None:
    while True:
        print(CONSIGNA_4_MENU)
        option = input("Opción: ").strip()

        if option in ("4.1", "1"):
            values = _load_values()
            if values is not None:
                _show_report(format_max_subarray_report, values)
        elif option in ("4.2", "2"):
            values = _load_values()
            if values is not None:
                _show_report(format_top_periods_report, values)
        elif option in ("4.3", "3"):
            values = _load_values()
            if values is not None:
                _show_report(format_quantiles_report, values)
        elif option in ("4.4", "4"):
            values = _load_values()
            if values is not None:
                for builder in (
                    format_max_subarray_report,
                    format_top_periods_report,
                    format_quantiles_report,
                ):
                    _show_report(builder, values)
                    print()
        elif option in ("4.5", "5", "v", "V"):
            break
        else:
            print("Opción inválida.")


def show_data_flow() -> None:
    values = _load_values()
    if values is None:
        return
    print(f"Datos cargados: {len(values)}")
    print("Primeros valores:", ", ".join(str(value) for value in values[:10]))


def main() -> None:
    while True:
        print(MENU)
        option = input("Opción: ").strip()
        if option == "1":
            spellchecker_flow()
        elif option == "2":
            floyd_warshall_flow()
        elif option == "3":
            word_search_flow()
        elif option == "4":
            consigna_4_flow()
        elif option == "5":
            show_data_flow()
        elif option == "6":
            print("Hasta luego.")
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()
