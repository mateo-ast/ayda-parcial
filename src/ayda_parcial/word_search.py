import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

MATRIX_FILE = Path("matriz.txt")
WORDS: tuple[str, ...] = ("ARBOL", "HEAPS", "SORTS", "NODOS", "GRAFO")
DIRECTIONS: tuple[tuple[int, int, str], ...] = (
    (-1, 0, "arriba"),
    (1, 0, "abajo"),
    (0, -1, "izquierda"),
    (0, 1, "derecha"),
    (-1, -1, "diagonal superior izquierda"),
    (-1, 1, "diagonal superior derecha"),
    (1, -1, "diagonal inferior izquierda"),
    (1, 1, "diagonal inferior derecha"),
)


@dataclass(frozen=True)
class Match:
    word: str
    start: tuple[int, int]
    end: tuple[int, int]
    direction: str
    cells: tuple[tuple[int, int], ...]


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def read_matrix(path: Path = MATRIX_FILE) -> list[str]:
    with path.open(encoding="utf-8") as file:
        rows = [line.strip() for line in file if line.strip()]
    if not rows:
        raise ValueError("la matriz está vacía")
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("todas las filas deben tener la misma cantidad de columnas")
    return rows


def find_word(matrix: Sequence[str], word: str) -> list[Match]:
    target = normalize(word)
    if not target:
        return []

    grid = [[normalize(char) for char in row] for row in matrix]
    height = len(grid)
    width = len(grid[0]) if height else 0
    length = len(target)
    matches: list[Match] = []

    for row in range(height):
        for col in range(width):
            if grid[row][col] != target[0]:
                continue
            for row_step, col_step, direction in DIRECTIONS:
                cells = tuple(
                    (row + step * row_step, col + step * col_step)
                    for step in range(length)
                )
                if any(
                    not (0 <= cell_row < height and 0 <= cell_col < width)
                    for cell_row, cell_col in cells
                ):
                    continue
                if all(
                    grid[cell_row][cell_col] == target[step]
                    for step, (cell_row, cell_col) in enumerate(cells)
                ):
                    matches.append(Match(word, cells[0], cells[-1], direction, cells))
    return matches


def find_words(matrix: Sequence[str], words: Sequence[str]) -> dict[str, list[Match]]:
    return {word: find_word(matrix, word) for word in words}


def format_cell(cell: tuple[int, int]) -> str:
    return f"({cell[0] + 1}, {cell[1] + 1})"


def format_path(cells: tuple[tuple[int, int], ...]) -> str:
    return " → ".join(format_cell(cell) for cell in cells)


def format_matrix(matrix: Sequence[str]) -> str:
    width = len(matrix[0]) if matrix else 0
    lines = [
        "     " + "".join(f"{col + 1:>4}" for col in range(width)),
        "-" * (5 + 4 * width),
    ]
    for row_index, row in enumerate(matrix):
        lines.append(f"{row_index + 1:>3}  " + "".join(f"{char:>4}" for char in row))
    return "\n".join(lines)


def format_report(matrix: Sequence[str], results: dict[str, list[Match]]) -> str:
    width = len(matrix[0]) if matrix else 0
    lines = [
        "=" * 56,
        "CONSIGNA 3 - BÚSQUEDA DE PALABRAS",
        f"Matriz: {len(matrix)} filas × {width} columnas",
        "Estrategia: desde cada celda se prueban las 8 direcciones en línea recta.",
        "=" * 56,
        "",
        "A) MATRIZ",
        "",
        format_matrix(matrix),
        "",
        "B) PALABRAS ENCONTRADAS",
        "",
    ]
    for word, matches in results.items():
        if not matches:
            lines.append(f"{word}: no encontrada")
            continue
        for match in matches:
            lines.append(
                f"{match.word}: {format_cell(match.start)} → {format_cell(match.end)}, "
                f"{match.direction}"
            )
            lines.append(f"  Camino: {format_path(match.cells)}")
    return "\n".join(lines)


if __name__ == "__main__":
    current_matrix = read_matrix()
    print(format_report(current_matrix, find_words(current_matrix, WORDS)))
