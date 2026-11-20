from collections.abc import Sequence

from ayda_parcial.metrics import format_int


def block_sums(values: Sequence[int], width: int) -> tuple[list[int], int]:
    size = max(1, (len(values) + width - 1) // width)
    sums: list[int] = []
    for start in range(0, len(values), size):
        block = values[start : start + size]
        sums.append(round(sum(block) * size / len(block)))
    return sums, size


def signed_bars(
    values: Sequence[int], marks: Sequence[str] | None = None, height: int = 9
) -> tuple[list[str], int, int]:
    high = max(0, max(values))
    low = min(0, min(values))
    zero_row = round(high / (high - low) * (height - 1)) if high > low else height // 2
    grid = [[" "] * len(values) for _ in range(height)]

    for column, value in enumerate(values):
        grid[zero_row][column] = "─"
        target = (
            round((high - value) / (high - low) * (height - 1))
            if high > low
            else zero_row
        )
        char = marks[column] if marks else "▒"
        if target < zero_row:
            for row in range(target, zero_row):
                grid[row][column] = char
        elif target > zero_row:
            for row in range(zero_row + 1, target + 1):
                grid[row][column] = char

    top = f"+{format_int(high)}" if high else ""
    bottom = f"-{format_int(-low)}" if low else ""
    gutter = max(1, len(top), len(bottom))
    lines: list[str] = []
    for index, row in enumerate(grid):
        if index == zero_row:
            label = "0"
        elif index == 0:
            label = top
        elif index == height - 1:
            label = bottom
        else:
            label = ""
        edge = "┤" if index in (0, height - 1) else "┼" if index == zero_row else "│"
        lines.append(f"{label:>{gutter}}{edge}{''.join(row)}")

    return lines, gutter, zero_row
