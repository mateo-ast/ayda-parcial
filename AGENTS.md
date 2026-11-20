# AGENTS.md

Instrucciones para agentes y colaboradores de este repositorio.

## Contexto

Proyecto entregable para un parcial de la facultad: un único programa que implementa **varios algoritmos** sobre un conjunto de datos, no módulos independientes entre sí. Priorizar claridad y simplicidad sobre abstracciones complejas. El código debe ser legible y fácil de explicar en una evaluación.

## Convenciones generales

- **Idioma del código:** inglés (nombres de variables, funciones, clases, módulos y mensajes internos).
- **Idioma de la interfaz:** español (todo lo que ve el usuario por terminal: menús, prompts, errores y resultados).
- **Sin tests.** No crear archivos ni carpetas de pruebas.
- **Sin comentarios extensos.** Comentar solo lo estrictamente necesario; el código debe explicarse por sí mismo. Nada de docstrings largas ni bloques de documentación redundante.
- **Modularidad clara.** Separar responsabilidades en módulos y funciones pequeñas con un único propósito. Evitar archivos monolíticos y funciones extensas. Cada algoritmo vive en su propio módulo y expone una función principal reutilizable por el programa.

## Python y tipado

- Python moderno con **tipado nativo** (PEP 585 / PEP 604):
  - Usar `list[str]`, `dict[str, int]`, `tuple[int, ...]`, `set[str]`.
  - No usar `List`, `Dict`, `Tuple`, `Set`, `Optional` de `typing`.
  - Usar `str | None` en lugar de `Optional[str]`.
- Anotar tipos en firmas de funciones y variables relevantes.
- Mantener compatibilidad con la versión soportada por el proyecto (definida en `pyproject.toml`).

## Gestión de dependencias y entorno

- Gestor de paquetes y entornos: **uv**.
- El archivo `pyproject.toml` es la fuente de verdad de dependencias y metadatos.
- Usar `uv add <paquete>` para agregar dependencias y `uv run <comando>` para ejecutar dentro del entorno.
- No usar `pip`, `venv`, `requirements.txt` ni otros gestores.
- No versionar el entorno virtual (`.venv/`).

## Interfaz por terminal

- La aplicación se ejecuta por CLI, por ejemplo con `uv run python -m <paquete>`.
- Los textos destinados al usuario van en español.
- Menús y flujos simples, con mensajes claros y manejo básico de errores.
- Separar la lógica de negocio de la capa de presentación/CLI para mantener la modularidad.
- **Cada algoritmo debe poder probarse de forma aislada** mediante un bloque `if __name__ == "__main__":` al final de su módulo, con una llamada de ejemplo. Esto permite ejecutar `uv run python src/<paquete>/<algoritmo>.py` sin levantar el programa completo.

## Datos de entrada

- El programa trabaja con un archivo **`datos.txt`** con aproximadamente **un millón de datos** (números o letras).
- El archivo puede no existir: puede ser necesario **generarlo**. En ese caso, incluir un generador simple (por ejemplo, una función en un módulo de utilidades o un script ejecutable con `uv run`) que escriba `datos.txt` con la cantidad y el tipo de datos requeridos.
- La generación debe ser configurable (cantidad, tipo `number`/`letter`, semilla opcional) y no depender de paquetes externos innecesarios.
- Los algoritmos leen `datos.txt` desde disco; no hardcodear datos de prueba dentro de la lógica.
- No versionar `datos.txt` en el repositorio (se genera localmente).

## Estructura sugerida

```
src/<paquete>/
    __init__.py
    main.py          # punto de entrada / CLI
    data.py          # lectura y generación de datos.txt
    algoritmo_a.py   # un módulo por algoritmo, con if __name__ == "__main__"
    algoritmo_b.py
    ...
pyproject.toml
AGENTS.md
```

Ajustar la estructura según crezca el proyecto, manteniendo módulos pequeños y enfocados.
