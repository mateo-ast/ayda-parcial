import random
from pathlib import Path

DATA_FILE = Path("datos.txt")


def generate_data(
    path: Path = DATA_FILE,
    count: int = 1_000_000,
    kind: str = "number",
    seed: int | None = None,
) -> None:
    if kind not in ("number", "letter"):
        raise ValueError("kind must be 'number' or 'letter'")
    rng = random.Random(seed)
    if kind == "number":
        values = (str(rng.randint(0, 9_999_999)) for _ in range(count))
    else:
        values = (rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(count))
    with path.open("w", encoding="utf-8") as file:
        file.write("\n".join(values))


def read_data(path: Path = DATA_FILE) -> list[str]:
    with path.open(encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def ensure_data(
    path: Path = DATA_FILE,
    count: int = 1_000_000,
    kind: str = "number",
    seed: int | None = None,
) -> list[str]:
    if not path.exists():
        generate_data(path, count, kind, seed)
    return read_data(path)
