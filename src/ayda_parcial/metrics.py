from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from time import perf_counter


@dataclass
class Metrics:
    comparisons: int = 0
    swaps: int = 0
    writes: int = 0
    elapsed_ms: float = 0.0


@contextmanager
def timer(metrics: Metrics) -> Iterator[None]:
    start = perf_counter()
    yield
    metrics.elapsed_ms = (perf_counter() - start) * 1000


def format_int(value: int) -> str:
    return f"{value:,}"


def format_float(value: float, decimals: int = 1) -> str:
    return f"{value:,.{decimals}f}"


def format_bytes(size: int) -> str:
    return f"{size / (1024 * 1024):,.1f} MB"


def format_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    widths = [
        max([len(headers[index])] + [len(row[index]) for row in rows])
        for index in range(len(headers))
    ]

    def render(cells: Sequence[str]) -> str:
        return "  ".join(f"{cell:>{width}}" for cell, width in zip(cells, widths))

    header = render(headers)
    return "\n".join([header, "-" * len(header), *(render(row) for row in rows)])
