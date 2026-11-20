from pathlib import Path

from ayda_parcial.data import DATA_FILE, generate_data, read_data
from ayda_parcial.floyd_warshall import floyd_warshall, format_report as format_graph_report
from ayda_parcial.graph import EDGES, QUERIES, VERTICES
from ayda_parcial.spellchecker import analyze, format_report, select

MENU = """
1. Corrector ortográfico (consigna 1)
2. Floyd-Warshall (consigna 2)
3. Generar datos
4. Ver datos cargados
5. Salir
"""


def spellchecker_flow() -> None:
    word = input("Palabra a corregir (enter para programaceón): ").strip() or "programaceón"
    candidates = analyze(word)
    print(format_report(word, candidates, select(candidates)))


def floyd_warshall_flow() -> None:
    result = floyd_warshall(VERTICES, EDGES)
    print(format_graph_report(result, EDGES, QUERIES))


def generate_data_flow() -> None:
    raw_count = input("Cantidad de datos (enter para 1000000): ").strip()
    kind = input("Tipo (number/letter) [number]: ").strip() or "number"
    try:
        count = int(raw_count) if raw_count else 1_000_000
        generate_data(Path(DATA_FILE), count, kind)
    except ValueError:
        print("La cantidad debe ser un número entero y el tipo number o letter.")
        return
    print(f"Archivo {DATA_FILE} generado con {count} datos.")


def show_data_flow() -> None:
    try:
        data = read_data()
    except FileNotFoundError:
        print("No existe el archivo de datos. Generalo primero.")
        return
    print(f"Datos cargados: {len(data)}")
    print("Primeros valores:", ", ".join(data[:10]))


def main() -> None:
    while True:
        print(MENU)
        option = input("Opción: ").strip()
        if option == "1":
            spellchecker_flow()
        elif option == "2":
            floyd_warshall_flow()
        elif option == "3":
            generate_data_flow()
        elif option == "4":
            show_data_flow()
        elif option == "5":
            print("Hasta luego.")
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()
