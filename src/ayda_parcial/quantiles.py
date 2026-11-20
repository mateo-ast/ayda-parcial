import math
import random
from collections.abc import Callable, Sequence

from ayda_parcial.chart import signed_bars
from ayda_parcial.data import read_numbers
from ayda_parcial.metrics import (
    Metrics,
    count_label,
    format_bytes,
    format_float,
    format_int,
    format_table,
    percentage,
    sign_counts,
    timer,
)

Selector = Callable[[list[int], int, random.Random, Metrics], int]


def merge_sort(values: Sequence[int]) -> tuple[list[int], Metrics]:
    metrics = Metrics()
    with timer(metrics):
        source = list(values)
        n = len(source)
        auxiliary = [0] * n
        width = 1

        while width < n:
            for left in range(0, n, 2 * width):
                middle = min(left + width, n)
                right = min(left + 2 * width, n)
                first, second, target = left, middle, left

                while first < middle and second < right:
                    metrics.comparisons += 1
                    if source[first] <= source[second]:
                        auxiliary[target] = source[first]
                        first += 1
                    else:
                        auxiliary[target] = source[second]
                        second += 1
                    target += 1
                    metrics.writes += 1

                while first < middle:
                    auxiliary[target] = source[first]
                    first += 1
                    target += 1
                    metrics.writes += 1

                while second < right:
                    auxiliary[target] = source[second]
                    second += 1
                    target += 1
                    metrics.writes += 1

            source, auxiliary = auxiliary, source
            width *= 2

    return source, metrics


def _select_lomuto(
    values: list[int], target: int, rng: random.Random, metrics: Metrics
) -> int:
    low, high = 0, len(values) - 1

    while low < high:
        pivot_index = rng.randrange(low, high + 1)
        values[pivot_index], values[high] = values[high], values[pivot_index]
        metrics.swaps += 1
        pivot = values[high]
        store = low

        for index in range(low, high):
            metrics.comparisons += 1
            if values[index] <= pivot:
                if index != store:
                    values[index], values[store] = values[store], values[index]
                    metrics.swaps += 1
                store += 1

        values[store], values[high] = values[high], values[store]
        metrics.swaps += 1

        if target == store:
            break
        if target < store:
            high = store - 1
        else:
            low = store + 1

    return values[target]


def _select_hoare(
    values: list[int], target: int, rng: random.Random, metrics: Metrics
) -> int:
    low, high = 0, len(values) - 1

    while low < high:
        pivot = values[rng.randrange(low, high)]
        first, second = low, high

        while True:
            while values[first] < pivot:
                metrics.comparisons += 1
                first += 1
            while values[second] > pivot:
                metrics.comparisons += 1
                second -= 1
            metrics.comparisons += 1

            if first >= second:
                break

            values[first], values[second] = values[second], values[first]
            metrics.swaps += 1
            first += 1
            second -= 1

        if target <= second:
            high = second
        else:
            low = second + 1

    return values[target]


def _rank_index(n: int, percentile: int) -> int:
    return max(0, min(n - 1, math.ceil(percentile / 100 * n) - 1))


def _median(working: list[int], select: Selector, rng: random.Random, metrics: Metrics) -> int | float:
    n = len(working)
    if n % 2:
        return select(working, n // 2, rng, metrics)
    low = select(working, n // 2 - 1, rng, metrics)
    high = select(working, n // 2, rng, metrics)
    return (low + high) / 2 if low != high else low


def _median_from_sorted(sorted_values: Sequence[int]) -> int | float:
    n = len(sorted_values)
    if n % 2:
        return sorted_values[n // 2]
    low = sorted_values[n // 2 - 1]
    high = sorted_values[n // 2]
    return (low + high) / 2 if low != high else low


def _quantiles_with_selector(
    values: Sequence[int], select: Selector, seed: int
) -> tuple[dict[str, int | float], Metrics]:
    working = list(values)
    rng = random.Random(seed)
    metrics = Metrics()

    with timer(metrics):
        n = len(working)
        quantiles = {
            "p50": _median(working, select, rng, metrics),
            "p90": select(working, _rank_index(n, 90), rng, metrics),
            "p95": select(working, _rank_index(n, 95), rng, metrics),
        }

    return quantiles, metrics


def quantiles_lomuto(
    values: Sequence[int], seed: int = 0
) -> tuple[dict[str, int | float], Metrics]:
    return _quantiles_with_selector(values, _select_lomuto, seed)


def quantiles_hoare(
    values: Sequence[int], seed: int = 0
) -> tuple[dict[str, int | float], Metrics]:
    return _quantiles_with_selector(values, _select_hoare, seed)


def quantiles_merge_sort(
    values: Sequence[int],
) -> tuple[dict[str, int | float], list[int], Metrics]:
    sorted_values, metrics = merge_sort(values)
    n = len(sorted_values)
    quantiles = {
        "p50": _median_from_sorted(sorted_values),
        "p90": sorted_values[_rank_index(n, 90)],
        "p95": sorted_values[_rank_index(n, 95)],
    }
    return quantiles, sorted_values, metrics


def count_leq(sorted_values: Sequence[int], threshold: int) -> int:
    low, high = 0, len(sorted_values)
    while low < high:
        middle = (low + high) // 2
        if sorted_values[middle] <= threshold:
            low = middle + 1
        else:
            high = middle
    return low


def _format_quantile(value: int | float) -> str:
    if isinstance(value, float):
        return format_float(value)
    return format_int(value)


def _validation_lines(
    sorted_values: Sequence[int],
    merge_quantiles: dict[str, int | float],
    lomuto_quantiles: dict[str, int | float],
    hoare_quantiles: dict[str, int | float],
) -> list[str]:
    n = len(sorted_values)
    lines: list[str] = []

    for percentile in (90, 95):
        key = f"p{percentile}"
        index = _rank_index(n, percentile)
        expected = sorted_values[index]
        threshold = int(merge_quantiles[key])
        lines.append(
            f"{key}: ordenado[{format_int(index)}] = {format_int(expected)}; "
            f"Merge Sort = {format_int(threshold)}; "
            f"Lomuto = {_format_quantile(lomuto_quantiles[key])}; "
            f"Hoare = {_format_quantile(hoare_quantiles[key])}"
        )
        lines.append(
            f"  elementos ≤ umbral: {format_int(count_leq(sorted_values, threshold))} "
            f"(esperado ≥ {format_int(index + 1)})"
        )
        lines.append(
            f"  elementos < umbral: {format_int(count_leq(sorted_values, threshold - 1))} "
            f"(esperado ≤ {format_int(index)})"
        )

    expected_median = _median_from_sorted(sorted_values)
    lines.append(
        f"p50: {_format_quantile(expected_median)} "
        f"({'promedio de las dos centrales, n par' if n % 2 == 0 else 'valor central, n impar'})"
    )
    if n % 2 == 0:
        lines.append(
            f"  ordenado[{format_int(n // 2 - 1)}] = {format_int(sorted_values[n // 2 - 1])}, "
            f"ordenado[{format_int(n // 2)}] = {format_int(sorted_values[n // 2])}"
        )

    lines.append(
        "Coincidencia de los tres enfoques: "
        + (
            "sí"
            if merge_quantiles == lomuto_quantiles == hoare_quantiles
            else "no (revisar arriba)"
        )
    )
    return lines


def format_distribution_chart(
    values: Sequence[int],
    quantiles: dict[str, int | float],
    width: int = 64,
    height: int = 9,
) -> str:
    low, high = min(values), max(values)
    span = max(abs(low), abs(high), 1)
    size = max(1, math.ceil(span / max(1, width // 2)))
    ranges: list[tuple[int, int]] = []
    if low < 0:
        ranges.extend(
            (start, min(-1, start + size - 1)) for start in range(low, 0, size)
        )
    negative_bins = len(ranges)
    zero_index = len(ranges) if low <= 0 <= high else None
    if zero_index is not None:
        ranges.append((0, 0))
    positive_base = len(ranges)
    ranges.extend(
        (start, min(high, start + size - 1)) for start in range(1, high + 1, size)
    )

    def bin_of(value: int) -> int:
        if value < 0:
            return min(negative_bins - 1, (value - low) // size)
        if value == 0 and zero_index is not None:
            return zero_index
        if value == 0:
            return min(positive_base, len(ranges) - 1)
        return min(len(ranges) - 1, positive_base + (value - 1) // size)

    counts = [0] * len(ranges)
    for value in values:
        counts[bin_of(value)] += 1

    columns: list[int] = []
    marks: list[str] = []
    for index, (start, end) in enumerate(ranges):
        if start < 0:
            columns.append(-counts[index])
            marks.append("▒")
        elif start == 0 == end:
            columns.append(0)
            marks.append("0")
        else:
            columns.append(counts[index])
            marks.append("█")

    lines, gutter, zero_row = signed_bars(columns, marks, height)
    if zero_index is not None:
        position = gutter + 1 + zero_index
        lines[zero_row] = (
            lines[zero_row][:position] + "0" + lines[zero_row][position + 1 :]
        )

    markers = ["·"] * len(ranges)
    if zero_index is not None:
        markers[zero_index] = "0"
    for key, char in (("p50", "M"), ("p90", "9"), ("p95", "5")):
        markers[bin_of(int(quantiles[key]))] = char
    lines.append(" " * (gutter + 1) + "".join(markers))

    negatives, zeros, positives = sign_counts(values)
    quantile_text = ", ".join(
        f"{char} = {key} {_format_quantile(quantiles[key])}"
        for key, char in (("p50", "M"), ("p90", "9"), ("p95", "5"))
    )

    return "\n".join(
        [
            f"Cada columna resume {count_label(size, 'valor', 'valores')} de utilidad diaria.",
            "▒ = negativos   █ = positivos   0 = ceros   ─ = separación   M/9/5 = cuantiles.",
            "La altura es la cantidad de días; los ceros se ubican sobre la línea cero.",
            "",
            *lines,
            "",
            f"Rango diario: mín {format_int(low)}, máx {format_int(high)}.",
            f"Marcadores: {quantile_text}; 0 = valor cero.",
            f"Días: {count_label(positives, 'positivo', 'positivos')} "
            f"({percentage(positives, len(values))}%), "
            f"{count_label(zeros, 'cero', 'ceros')}, "
            f"{count_label(negatives, 'negativo', 'negativos')} "
            f"({percentage(negatives, len(values))}%).",
        ]
    )


def run_report(values: Sequence[int], seed: int = 0) -> str:
    n = len(values)
    distinct = len(set(values))
    merge_quantiles, sorted_values, merge_metrics = quantiles_merge_sort(values)
    lomuto_quantiles, lomuto_metrics = quantiles_lomuto(values, seed)
    hoare_quantiles, hoare_metrics = quantiles_hoare(values, seed)

    rows = [
        (
            "Merge Sort",
            format_float(merge_metrics.elapsed_ms),
            format_int(merge_metrics.comparisons),
            "0",
            format_int(merge_metrics.writes),
            f"O(n) ({format_bytes(n * 8)})",
            _format_quantile(merge_quantiles["p50"]),
            _format_quantile(merge_quantiles["p90"]),
            _format_quantile(merge_quantiles["p95"]),
        ),
        (
            "QuickSelect Lomuto",
            format_float(lomuto_metrics.elapsed_ms),
            format_int(lomuto_metrics.comparisons),
            format_int(lomuto_metrics.swaps),
            "0",
            "O(1)",
            _format_quantile(lomuto_quantiles["p50"]),
            _format_quantile(lomuto_quantiles["p90"]),
            _format_quantile(lomuto_quantiles["p95"]),
        ),
        (
            "QuickSelect Hoare",
            format_float(hoare_metrics.elapsed_ms),
            format_int(hoare_metrics.comparisons),
            format_int(hoare_metrics.swaps),
            "0",
            "O(1)",
            _format_quantile(hoare_quantiles["p50"]),
            _format_quantile(hoare_quantiles["p90"]),
            _format_quantile(hoare_quantiles["p95"]),
        ),
    ]

    return "\n".join(
        [
            "=" * 118,
            "CONSIGNA 4 - PARTE C: PERCENTILES Y MEDIANA DE LA UTILIDAD DIARIA",
            "=" * 118,
            f"Días analizados (n): {format_int(n)}   Semilla del pivote: {seed}",
            f"Valores distintos: {format_int(distinct)} de {format_int(n)} días",
            "Convención: p90 y p95 por rango más cercano; p50 = promedio de las dos",
            "posiciones centrales si n es par, y el valor central si n es impar.",
            "* QuickSelect trabaja in-place sobre una copia; la copia no se cuenta como memoria del algoritmo.",
            "",
            "A) TIEMPO, OPERACIONES Y MEMORIA",
            "",
            format_table(
                (
                    "Método",
                    "Tiempo (ms)",
                    "Comparaciones",
                    "Swaps",
                    "Escrituras",
                    "Memoria adic.",
                    "p50",
                    "p90",
                    "p95",
                ),
                rows,
            ),
            "",
            "B) VALIDACIÓN SOBRE EL ARREGLO ORDENADO",
            "",
            *_validation_lines(
                sorted_values, merge_quantiles, lomuto_quantiles, hoare_quantiles
            ),
            "",
            "C) DISTRIBUCIÓN Y CUANTILES",
            "",
            format_distribution_chart(values, merge_quantiles),
            "",
            "D) CONCLUSIONES",
            "",
            "QuickSelect obtiene un solo cuantil en O(n) esperado, mientras Merge Sort",
            "paga O(n log n) porque ordena todo el arreglo; por eso suele ser preferible.",
            "Con pivote fijo y entrada ordenada, cualquier QuickSelect cae en O(n²);",
            "aquí se usa pivote aleatorio con semilla para evitar ese caso.",
            f"Con {format_int(distinct)} valores distintos, los repetidos perjudican a Lomuto:",
            "deja todos los iguales de un lado y puede degradarse a O(n²), mientras",
            "Hoare reparte mejor los bloques de iguales.",
            "Si se piden muchos cuantiles, ordenar una sola vez puede convenir más.",
        ]
    )


if __name__ == "__main__":
    try:
        current_values = read_numbers()
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
    else:
        print(run_report(current_values))
