from collections.abc import Sequence
from dataclasses import dataclass
from math import log2

from ayda_parcial.chart import block_sums, signed_bars
from ayda_parcial.data import read_numbers
from ayda_parcial.metrics import (
    Metrics,
    count_label,
    format_float,
    format_int,
    format_table,
    percentage,
    sign_counts,
    timer,
)


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


def format_chart(
    values: Sequence[int], period: Period, width: int = 64, height: int = 9
) -> str:
    sums, size = block_sums(values, width)
    first = min(len(sums) - 1, period.start // size)
    last = min(len(sums) - 1, period.end // size)
    marks = ["█" if first <= index <= last else "▒" for index in range(len(sums))]
    lines, gutter, _ = signed_bars(sums, marks, height)

    brackets = ["·"] * len(sums)
    if first == last:
        brackets[first] = "#"
    else:
        brackets[first] = "["
        brackets[last] = "]"
        for index in range(first + 1, last):
            brackets[index] = "="
    lines.append(" " * (gutter + 1) + "".join(brackets))
    lines.append(
        " " * (gutter + 1 + first)
        + f"días {format_int(period.start)} a {format_int(period.end)}"
    )

    negatives, zeros, positives = sign_counts(values)
    inside_negatives, inside_zeros, inside_positives = sign_counts(
        values[period.start : period.end + 1]
    )
    negative_blocks = sum(1 for value in sums if value < 0)

    return "\n".join(
        [
            f"Cada columna resume {count_label(size, 'día', 'días')} (suma neta del bloque).",
            "█ = dentro del periodo   ▒ = resto   ─ = línea cero.",
            "El resaltado usa bloques completos; los días exactos se indican abajo.",
            "",
            *lines,
            "",
            f"Bloques: mín {format_int(min(sums))}, máx {format_int(max(sums))}, "
            f"negativos {negative_blocks}/{len(sums)}.",
            f"Días: {count_label(positives, 'positivo', 'positivos')} "
            f"({percentage(positives, len(values))}%), "
            f"{count_label(zeros, 'cero', 'ceros')}, "
            f"{count_label(negatives, 'negativo', 'negativos')} "
            f"({percentage(negatives, len(values))}%).",
            f"Dentro del periodo: {count_label(inside_positives, 'positivo', 'positivos')}, "
            f"{count_label(inside_zeros, 'cero', 'ceros')}, "
            f"{count_label(inside_negatives, 'negativo', 'negativos')}; "
            f"total {format_int(period.total)}.",
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
            "C) REPRESENTACIÓN GRÁFICA",
            "",
            format_chart(values, kadane_period),
        ]
    )


if __name__ == "__main__":
    try:
        current_values = read_numbers()
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
    else:
        print(run_report(current_values))
