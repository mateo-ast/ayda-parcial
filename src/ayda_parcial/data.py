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
