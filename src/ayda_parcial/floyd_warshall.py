from collections.abc import Sequence
from dataclasses import dataclass

Edge = tuple[str, str, int]
Matrix = dict[str, dict[str, float]]

INF = float("inf")


@dataclass(frozen=True)
class FloydWarshallResult:
    vertices: tuple[str, ...]
    distances: Matrix
    next_hop: dict[str, dict[str, str | None]]

    def has_negative_cycle(self) -> bool:
        return any(self.distances[vertex][vertex] < 0 for vertex in self.vertices)

    def path(self, source: str, target: str) -> tuple[str, ...] | None:
        if source not in self.distances or target not in self.distances:
            raise ValueError(f"Vértice desconocido: {source} o {target}")
        if source == target:
            return (source,)

        route = [source]
        while source != target:
            following = self.next_hop[source][target]
            if following is None:
                return None
            source = following
            route.append(source)
            if len(route) > len(self.vertices):
                return None
        return tuple(route)


def floyd_warshall(vertices: Sequence[str], edges: Sequence[Edge]) -> FloydWarshallResult:
    names = tuple(vertices)
    distances: Matrix = {
        origin: {dest: 0 if origin == dest else INF for dest in names}
        for origin in names
    }
    next_hop: dict[str, dict[str, str | None]] = {
        origin: {dest: None for dest in names} for origin in names
    }

    for origin, dest, weight in edges:
        if origin not in distances or dest not in distances:
            raise ValueError(f"Arco con vértice desconocido: {origin} -> {dest}")
        if weight < distances[origin][dest]:
            distances[origin][dest] = weight
            next_hop[origin][dest] = dest

    for via in names:
        for origin in names:
            to_via = distances[origin][via]
            if to_via == INF:
                continue
            for dest in names:
                candidate = to_via + distances[via][dest]
                if candidate < distances[origin][dest]:
                    distances[origin][dest] = candidate
                    next_hop[origin][dest] = next_hop[origin][via]

    return FloydWarshallResult(names, distances, next_hop)


def is_stable(result: FloydWarshallResult, edges: Sequence[Edge]) -> bool:
    return all(
        result.distances[origin][dest] <= result.distances[origin][source] + weight
        for source, dest, weight in edges
        for origin in result.vertices
    )


def _format_table(
    result: FloydWarshallResult, title: str, values: dict[str, dict[str, str]]
) -> str:
    width = max(3, max(len(value) for row in values.values() for value in row.values()))
    lines = [
        title,
        "     " + "".join(f"{vertex:>{width}}" for vertex in result.vertices),
        "-" * (5 + width * len(result.vertices)),
    ]
    for origin in result.vertices:
        cells = "".join(f"{values[origin][dest]:>{width}}" for dest in result.vertices)
        lines.append(f"{origin:>3}  {cells}")
    return "\n".join(lines)


def format_distances(result: FloydWarshallResult) -> str:
    values = {
        origin: {
            dest: "∞" if distance == INF else str(distance)
            for dest, distance in row.items()
        }
        for origin, row in result.distances.items()
    }
    return _format_table(result, "MATRIZ FINAL DE DISTANCIAS", values)


def format_next_hop(result: FloydWarshallResult) -> str:
    values = {
        origin: {dest: following or "–" for dest, following in row.items()}
        for origin, row in result.next_hop.items()
    }
    return _format_table(result, "MATRIZ DE RECONSTRUCCIÓN (próximo vértice)", values)


def format_report(
    result: FloydWarshallResult,
    edges: Sequence[Edge],
    queries: Sequence[tuple[str, str]],
) -> str:
    lines = [
        "=" * 56,
        "CONSIGNA 2 - FLOYD-WARSHALL",
        f"Vértices ({len(result.vertices)}): {', '.join(result.vertices)}",
        "=" * 56,
        "",
        "A) DISTANCIAS Y CAMINOS MÍNIMOS",
        "",
    ]
    for source, target in queries:
        route = result.path(source, target)
        lines.append(f"{source} → {target}: distancia {result.distances[source][target]}")
        lines.append(f"  Camino: {' → '.join(route) if route else 'No alcanzable'}")

    lines += ["", "B) CICLO NEGATIVO", ""]
    if result.has_negative_cycle():
        lines.append("Existe un ciclo negativo (hay un valor negativo en la diagonal).")
    else:
        lines.append("No existe ciclo negativo (toda la diagonal es 0).")
    lines.append(
        "Relajación de todos los arcos estable: " + ("sí" if is_stable(result, edges) else "no")
    )

    lines += [
        "",
        format_distances(result),
        "",
        format_next_hop(result),
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    from ayda_parcial.graph import EDGES, QUERIES, VERTICES

    print(format_report(floyd_warshall(VERTICES, EDGES), EDGES, QUERIES))
