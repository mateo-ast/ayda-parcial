from dataclasses import dataclass

from ayda_parcial.levenshtein import Trace, backtrace, build_matrix, format_matrix

DICTIONARY = [
    "programación",
    "programador",
    "programaciónes",
    "programaciónal",
    "programación web",
    "probabilístico",
]
MAX_DISTANCE = 3


@dataclass(frozen=True)
class Candidate:
    word: str
    matrix: list[list[int]]
    dist: int
    trace: Trace


def analyze(word: str, dictionary: list[str] = DICTIONARY) -> list[Candidate]:
    candidates: list[Candidate] = []
    for candidate in dictionary:
        matrix = build_matrix(word, candidate)
        candidates.append(
            Candidate(candidate, matrix, matrix[-1][-1], backtrace(word, candidate, matrix))
        )
    return candidates


def select(
    candidates: list[Candidate], max_distance: int = MAX_DISTANCE
) -> list[Candidate]:
    return sorted(
        (candidate for candidate in candidates if candidate.dist <= max_distance),
        key=lambda candidate: candidate.dist,  # estable: conserva el orden del diccionario
    )


def suggest(
    word: str,
    dictionary: list[str] = DICTIONARY,
    max_distance: int = MAX_DISTANCE,
    limit: int | None = None,
) -> list[tuple[str, int]]:
    selected = select(analyze(word, dictionary), max_distance)
    if limit is not None:
        selected = selected[:limit]
    return [(candidate.word, candidate.dist) for candidate in selected]


def format_path(cells: list[tuple[int, int]]) -> str:
    items = [f"({i},{j})" for i, j in cells]
    chunks = [" → ".join(items[start : start + 8]) for start in range(0, len(items), 8)]
    lines = [
        "  " + chunk + (" →" if index < len(chunks) - 1 else "")
        for index, chunk in enumerate(chunks)
    ]
    return "Camino de la última celda a la primera:\n" + "\n".join(lines)


def format_operations(operations: list[str]) -> str:
    lines = ["Operaciones en orden:"]
    lines += [f"  {index}. {operation}" for index, operation in enumerate(operations, start=1)]
    return "\n".join(lines) if operations else "Operaciones en orden: ninguna"


def format_matrices(word: str, candidates: list[Candidate]) -> str:
    lines = ["A) MATRICES COMPLETAS Y DISTANCIAS", ""]
    for candidate in candidates:
        lines.append(f"{candidate.word} (distancia = {candidate.dist})")
        lines.append(format_matrix(word, candidate.word, candidate.matrix))
        lines.append(format_path(list(reversed(candidate.trace.cells))))
        lines.append(format_operations(candidate.trace.operations))
        lines.append("")
    return "\n".join(lines)


def format_selection(selected: list[Candidate]) -> str:
    lines = ["B/C) SELECCIÓN CON DISTANCIA ≤ 3, ORDENADA POR DISTANCIA", ""]
    lines += [
        f"{index}. {candidate.word} (distancia = {candidate.dist})"
        for index, candidate in enumerate(selected, start=1)
    ]
    return "\n".join(lines)


def format_suggestions(selected: list[Candidate]) -> str:
    lines = ["D) SALIDA DEL CORRECTOR", "", "¿Quisiste decir?"]
    lines += [
        f"{index}. {candidate.word} (distancia = {candidate.dist})"
        for index, candidate in enumerate(selected, start=1)
    ]
    return "\n".join(lines)


def format_report(
    word: str, candidates: list[Candidate], selected: list[Candidate]
) -> str:
    return "\n".join(
        [
            "=" * 52,
            "CONSIGNA 1 - CORRECTOR ORTOGRÁFICO",
            f"Palabra ingresada: {word}",
            "Las tildes se comparan sin diferenciarlas (ó = o).",
            "En las matrices: i = fila (palabra ingresada), j = columna (candidato).",
            "=" * 52,
            "",
            format_matrices(word, candidates),
            format_selection(selected),
            "",
            format_suggestions(selected),
        ]
    )


if __name__ == "__main__":
    word = "programaceón"
    candidates = analyze(word)
    print(format_report(word, candidates, select(candidates)))
