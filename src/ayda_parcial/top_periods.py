from array import array
from collections.abc import Sequence

from ayda_parcial.data import read_numbers
from ayda_parcial.max_subarray import Period
from ayda_parcial.metrics import (
    Metrics,
    format_bytes,
    format_float,
    format_int,
    format_table,
    timer,
)

NEGATIVE = -(1 << 60)


def _reconstruct(
    dp: list[array], prefix: list[int], k: int, n: int
) -> list[Period]:
    periods: list[Period] = []
    j, i = k, n

    while j > 0:
        if dp[j][i] == dp[j][i - 1]:
            i -= 1
            continue

        best_score = NEGATIVE
        best_start = -1
        for start in range(j - 1, i):
            previous = dp[j - 1][start]
            if previous <= NEGATIVE // 2:
                continue
            score = previous - prefix[start]
            if score > best_score:
                best_score = score
                best_start = start

        if best_start < 0:
            raise RuntimeError("no se pudo reconstruir el periodo óptimo")

        periods.append(Period(best_start, i - 1, prefix[i] - prefix[best_start]))
        j -= 1
        i = best_start

    periods.reverse()
    return periods


def select_top_periods(values: Sequence[int], k: int = 10) -> tuple[list[Period], Metrics]:
    n = len(values)
    if k <= 0:
        return [], Metrics()
    if n < k:
        raise ValueError("se necesitan al menos k valores para formar k periodos")

    metrics = Metrics()
    with timer(metrics):
        prefix = [0] * (n + 1)
        running = 0
        for index, value in enumerate(values):
            running += value
            prefix[index + 1] = running

        dp: list[array] = [array("q", [NEGATIVE]) * (n + 1) for _ in range(k + 1)]
        for index in range(n + 1):
            dp[0][index] = 0

        for j in range(1, k + 1):
            current = dp[j]
            previous = dp[j - 1]
            best_start_score = NEGATIVE

            for i in range(j, n + 1):
                last_start = i - 1
                previous_value = previous[last_start]
                if previous_value > NEGATIVE // 2:
                    score = previous_value - prefix[last_start]
                    metrics.comparisons += 1
                    if score > best_start_score:
                        best_start_score = score

                metrics.comparisons += 1
                candidate = prefix[i] + best_start_score
                skip = current[i - 1]
                if candidate > skip:
                    current[i] = candidate
                else:
                    current[i] = skip

        periods = _reconstruct(dp, prefix, k, n)

    return periods, metrics


def run_report(values: Sequence[int], k: int = 10) -> str:
    periods, metrics = select_top_periods(values, k)
    n = len(values)
    total = sum(period.total for period in periods)
    memory_bytes = (k + 1) * (n + 1) * 8 + (n + 1) * 8

    rows = [
        (
            format_int(index),
            format_int(period.start),
            format_int(period.end),
            format_int(period.total),
            format_int(period.end - period.start + 1),
        )
        for index, period in enumerate(periods, start=1)
    ]

    return "\n".join(
        [
            "=" * 72,
            "CONSIGNA 4 - PARTE B: TOP-10 PERIODOS NO SOLAPADOS",
            "=" * 72,
            f"Días analizados (n): {format_int(n)}   Períodos pedidos (k): {k}",
            "Índices de inicio y fin: base 0, ambos inclusive.",
            "Los periodos se listan en orden cronológico, no por suma.",
            "",
            "A) CRITERIO Y ESTRUCTURA DE DATOS",
            "",
            "Criterio: exactamente k periodos no vacíos y disjuntos que maximizan",
            "la suma total de utilidades (r_i < l_(i+1) entre periodos consecutivos).",
            "Si no hay suficientes tramos positivos, el óptimo forzado puede incluir",
            "periodos de suma negativa o tramos adyacentes.",
            "",
            "Estructura: sumas prefijas + tabla DP por capas guardada en array('q').",
            "Recurrencia: dp[j][i] = max(dp[j][i-1], S[i] + max_{l<i}(dp[j-1][l] - S[l])).",
            "El máximo interno se mantiene acumulado, por lo que cada capa es O(n).",
            "",
            "B) COSTO Y MEDICIONES",
            "",
            f"Tiempo: {format_float(metrics.elapsed_ms)} ms",
            f"Comparaciones relevantes: {format_int(metrics.comparisons)}",
            f"Memoria adicional estimada: {format_bytes(memory_bytes)} (DP + sumas prefijas)",
            "Cota teórica: O(n·k) tiempo y O(n·k) memoria.",
            "Alternativa con heap + división incremental: más rápida en la práctica,",
            "pero greedy no garantiza el óptimo global; se eligió el DP exacto.",
            "",
            "C) PERIODOS SELECCIONADOS",
            "",
            format_table(("#", "Inicio", "Fin", "Suma", "Días"), rows),
            "",
            f"Utilidad total de los {k} periodos: {format_int(total)}",
            f"Suma directa de los valores del arreglo: {format_int(sum(values))}",
        ]
    )


if __name__ == "__main__":
    try:
        current_values = read_numbers()
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
    else:
        print(run_report(current_values, 10))
