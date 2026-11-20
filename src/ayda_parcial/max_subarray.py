from collections.abc import Sequence
from dataclasses import dataclass
from math import log2

from ayda_parcial.data import read_numbers
from ayda_parcial.metrics import (
    Metrics,
    format_float,
    format_int,
    format_table,
    timer,
)

BLOCKS = "▁▂▃▄▅▆▇█"


@dataclass(frozen=True)
class Period:
    start: int
    end: int
    total: int


NEGATIVE = -(1 << 60)


def _prefer(candidate: Period, current: Period, metrics: Metrics) -> bool:
    metrics.comparisons += 1
    if candidate.total != current.total:
        return candidate.total > current.total
    if candidate.start != current.start:
        return candidate.start < current.start
    return candidate.end < current.end


def kadane(values: Sequence[int]) -> tuple[Period, Metrics]:
    if not values:
        raise ValueError("el arreglo está vacío")

    metrics = Metrics()
    with timer(metrics):
        current = values[0]
        current_start = 0
        best = Period(0, 0, values[0])

        for index in range(1, len(values)):
            metrics.comparisons += 1
            if current < 0:
                current = values[index]
                current_start = index
            else:
                current += values[index]

            candidate = Period(current_start, index, current)
            if _prefer(candidate, best, metrics):
                best = candidate

    return best, metrics


def _solve(values: Sequence[int], low: int, high: int, metrics: Metrics) -> Period:
    if high - low == 1:
        return Period(low, low, values[low])

    middle = (low + high) // 2
    left = _solve(values, low, middle, metrics)
    right = _solve(values, middle, high, metrics)

    running = 0
    best_left = NEGATIVE
    start = middle - 1
    for index in range(middle - 1, low - 1, -1):
        running += values[index]
        metrics.comparisons += 1
        if running >= best_left:
            best_left = running
            start = index

    running = 0
    best_right = NEGATIVE
    end = middle
    for index in range(middle, high):
        running += values[index]
        metrics.comparisons += 1
        if running > best_right:
            best_right = running
            end = index

    crossing = Period(start, end, best_left + best_right)
    best = left
    if _prefer(right, best, metrics):
        best = right
    if _prefer(crossing, best, metrics):
        best = crossing
    return best


def divide_and_conquer(values: Sequence[int]) -> tuple[Period, Metrics]:
    if not values:
        raise ValueError("el arreglo está vacío")

    metrics = Metrics()
    with timer(metrics):
        result = _solve(values, 0, len(values), metrics)
    return result, metrics


def format_ascii(values: Sequence[int], period: Period, width: int = 100) -> str:
    size = max(1, (len(values) + width - 1) // width)
    buckets = [
        sum(values[start : start + size]) / len(values[start : start + size])
        for start in range(0, len(values), size)
    ]
    minimum = min(buckets)
    maximum = max(buckets)
    span = maximum - minimum or 1

    sparkline = "".join(
        BLOCKS[min(len(BLOCKS) - 1, int((value - minimum) / span * (len(BLOCKS) - 1) + 0.5))]
        for value in buckets
    )

    markers = ["·"] * len(buckets)
    first = period.start // size
    last = min(len(buckets) - 1, period.end // size)
    if first == last:
        markers[first] = "#"
    else:
        markers[first] = "["
        markers[last] = "]"
        for index in range(first + 1, last):
            markers[index] = "#"
    markline = "".join(markers)

    return "\n".join(
        [
            f"Cada carácter resume {format_int(size):>7} días (promedio de utilidad).",
            f"Utilidad:  {sparkline}",
            f"Periodo:   {markline}",
            f"El tramo marcado cubre los buckets {first} a {last}.",
        ]
    )


def run_report(values: Sequence[int]) -> str:
    kadane_period, kadane_metrics = kadane(values)
    dc_period, dc_metrics = divide_and_conquer(values)
    n = len(values)
    theoretical = max(1, n * log2(n)) if n > 1 else 1

    rows = [
        (
            "Kadane",
            "O(n)",
            format_float(kadane_metrics.elapsed_ms),
            format_int(kadane_metrics.comparisons),
            format_int(kadane_period.total),
            format_int(kadane_period.start),
            format_int(kadane_period.end),
        ),
        (
            "Divide y Vencerás",
            "O(n log n)",
            format_float(dc_metrics.elapsed_ms),
            format_int(dc_metrics.comparisons),
            format_int(dc_period.total),
            format_int(dc_period.start),
            format_int(dc_period.end),
        ),
    ]

    same_total = kadane_period.total == dc_period.total
    same_range = (
        kadane_period.start == dc_period.start and kadane_period.end == dc_period.end
    )

    return "\n".join(
        [
            "=" * 72,
            "CONSIGNA 4 - PARTE A: MEJOR PERIODO DE UTILIDAD",
            "=" * 72,
            f"Días analizados (n): {format_int(n)}",
            "Índices de inicio y fin: base 0, ambos inclusive.",
            "",
            "A) MEDICIONES Y CONTRASTE TEÓRICO",
            "",
            format_table(
                (
                    "Algoritmo",
                    "Cota",
                    "Tiempo (ms)",
                    "Comparaciones",
                    "Suma máx.",
                    "Inicio",
                    "Fin",
                ),
                rows,
            ),
            "",
            f"Referencia teórica: n = {format_int(n)}, n·log2(n) ≈ {format_int(int(theoretical))}.",
            f"Kadane realiza ≈ 2n comparaciones; Divide y Vencerás ≈ c·n·log2(n).",
            f"Relación empírica de tiempo (DyV / Kadane): "
            f"{format_float(dc_metrics.elapsed_ms / kadane_metrics.elapsed_ms, 2)}×."
            if kadane_metrics.elapsed_ms
            else "Relación empírica de tiempo: no disponible.",
            "",
            "B) RESULTADO Y VALIDACIÓN",
            "",
            f"Valor máximo de utilidad: {format_int(kadane_period.total)}",
            f"Inicio: {format_int(kadane_period.start)}   Fin: {format_int(kadane_period.end)}",
            f"Longitud del periodo: {format_int(kadane_period.end - kadane_period.start + 1)} días",
            f"Sumas coincidentes entre ambos algoritmos: {'sí' if same_total else 'no'}",
            f"Índices coincidentes: {'sí' if same_range else 'no (puede haber empates)'}",
            "",
            "C) REPRESENTACIÓN GRÁFICA SIMPLE",
            "",
            format_ascii(values, kadane_period),
        ]
    )


if __name__ == "__main__":
    try:
        current_values = read_numbers()
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
    else:
        print(run_report(current_values))
