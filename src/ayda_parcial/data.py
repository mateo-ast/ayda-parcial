import argparse
import random
from pathlib import Path

DATA_FILE = Path("datos.txt")


def read_numbers(path: Path = DATA_FILE) -> list[int]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo {path}") from None

    tokens = text.split()
    if not tokens:
        raise ValueError(f"El archivo {path} está vacío")

    values: list[int] = []
    for token in tokens:
        try:
            values.append(int(token))
        except ValueError:
            raise ValueError(
                f"El archivo {path} contiene un valor que no es entero: {token}"
            ) from None
    return values


def generate_numbers(
    count: int,
    data_type: str = "number",
    seed: int | None = None,
    path: Path = DATA_FILE,
) -> None:
    rng = random.Random(seed)
    if data_type == "number":
        values = [str(rng.randint(-1_000_000, 1_000_000)) for _ in range(count)]
    elif data_type == "letter":
        values = [rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(count)]
    else:
        raise ValueError("tipo no válido: usa 'number' o 'letter'")
    path.write_text(" ".join(values), encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genera el archivo datos.txt.")
    parser.add_argument(
        "-n", "--count", type=int, default=1_000_000, help="cantidad de datos"
    )
    parser.add_argument(
        "-t", "--type", choices=("number", "letter"), default="number",
        help="tipo de datos",
    )
    parser.add_argument("-s", "--seed", type=int, default=None, help="semilla opcional")
    parser.add_argument(
        "-o", "--output", type=Path, default=DATA_FILE, help="archivo de salida"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    generate_numbers(args.count, args.type, args.seed, args.output)
    print(f"Generados {args.count} datos en {args.output}")
