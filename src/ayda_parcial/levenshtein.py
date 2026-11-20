import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class Trace:
    cells: list[tuple[int, int]]
    operations: list[str]


def normalize_char(char: str) -> str:
    decomposed = unicodedata.normalize("NFD", char.lower())
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


def build_matrix(source: str, target: str) -> list[list[int]]:
    source_chars = [normalize_char(char) for char in source]
    target_chars = [normalize_char(char) for char in target]
    m, n = len(source), len(target)

    d = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        d[i][0] = i
    for j in range(n + 1):
        d[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if source_chars[i - 1] == target_chars[j - 1] else 1
            d[i][j] = min(
                d[i - 1][j] + 1,
                d[i][j - 1] + 1,
                d[i - 1][j - 1] + cost,
            )

    return d


def distance(source: str, target: str) -> int:
    return build_matrix(source, target)[-1][-1]


def show_char(char: str) -> str:
    return "␣" if char.isspace() else char


def backtrace(source: str, target: str, matrix: list[list[int]]) -> Trace:
    source_chars = [normalize_char(char) for char in source]
    target_chars = [normalize_char(char) for char in target]
    i, j = len(source), len(target)

    cells = [(i, j)]
    operations: list[str] = []
    while i > 0 or j > 0:
        if (
            i > 0
            and j > 0
            and source_chars[i - 1] == target_chars[j - 1]
            and matrix[i][j] == matrix[i - 1][j - 1]
        ):
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and matrix[i][j] == matrix[i - 1][j - 1] + 1:
            operations.append(
                f"sustituir {show_char(source[i - 1])} → {show_char(target[j - 1])} (posición {i})"
            )
            i -= 1
            j -= 1
        elif i > 0 and matrix[i][j] == matrix[i - 1][j] + 1:
            operations.append(f"eliminar {show_char(source[i - 1])} (posición {i})")
            i -= 1
        else:
            operations.append(f"insertar {show_char(target[j - 1])} (posición {j})")
            j -= 1
        cells.append((i, j))

    operations.reverse()
    cells.reverse()
    return Trace(cells, operations)


def format_matrix(source: str, target: str, matrix: list[list[int]]) -> str:
    columns = "∅" + target
    width = max(3, max(len(str(value)) for row in matrix for value in row) + 1)
    prefix = "     "
    lines = [
        prefix + "".join(f"{j:>{width}}" for j in range(len(columns))),
        prefix + "".join(f"{show_char(char):>{width}}" for char in columns),
        "-" * (len(prefix) + width * len(columns)),
    ]
    for i, row in enumerate(matrix):
        label = "∅" if i == 0 else source[i - 1]
        lines.append(f"{i:>2} {label} " + "".join(f"{value:>{width}}" for value in row))
    return "\n".join(lines)


if __name__ == "__main__":
    source = "programaceón"
    target = "programador"
    example_matrix = build_matrix(source, target)
    print(format_matrix(source, target, example_matrix))
    print("Distancia:", example_matrix[-1][-1])
    print("Operaciones:", backtrace(source, target, example_matrix).operations)
