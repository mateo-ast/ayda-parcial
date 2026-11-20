# Cómo generar el ejecutable `.exe` en Windows

El proyecto se ejecuta con `uv run python -m ayda_parcial`. PyInstaller ya está
configurado en el repositorio, así que el `.exe` se construye **en la PC con
Windows**: PyInstaller no compila de forma cruzada, por eso no se genera en Linux.

## Requisitos en la PC con Windows

- Python 3.10 o superior (si no está: `uv python install 3.12`).
- **uv** instalado. En PowerShell:

  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

- Una copia de este proyecto (clonar o copiar la carpeta).

## Pasos

1. Abrir PowerShell dentro de la carpeta del proyecto.

2. Crear el entorno e instalar dependencias (el grupo `dev` incluye PyInstaller):

   ```powershell
   uv sync
   ```

   Si por alguna razón no instala PyInstaller, forzar el grupo:

   ```powershell
   uv sync --group dev
   ```

3. Generar `datos.txt` (no está versionado, se crea localmente). Para la
   consigna 4 hay que usar números:

   ```powershell
   uv run python -m ayda_parcial.data --count 1000000 --type number --seed 42
   ```

   Opciones disponibles: `--count`/`-n` (cantidad), `--type`/`-t`
   (`number` o `letter`), `--seed`/`-s` (semilla opcional) y `--output`/`-o`
   (archivo de salida, por defecto `datos.txt`).

4. Verificar que el programa funciona antes de compilar (opcional):

   ```powershell
   uv run python -m ayda_parcial
   ```

5. Compilar con el archivo de configuración incluido (`ayda-parcial.spec`):

   ```powershell
   uv run pyinstaller ayda-parcial.spec --noconfirm --clean
   ```

   El resultado queda en `dist\ayda-parcial.exe` (un único archivo, consola
   visible). Si se prefiere sin el `.spec`, el comando equivalente es:

   ```powershell
   uv run pyinstaller --onefile --console --name ayda-parcial --paths src src\ayda_parcial\__main__.py
   ```

6. Armar la carpeta de entrega. Copiar estos tres archivos **en la misma
   carpeta**:

   ```text
   ayda-parcial.exe
   datos.txt
   matriz.txt
   ```

   El programa lee `datos.txt` y `matriz.txt` desde la carpeta en la que se
   ejecuta. Si se abre el `.exe` con doble clic desde el Explorador, esa carpeta
   es la que contiene al `.exe`; si se abre desde PowerShell, primero crear la
   carpeta con `cd` y después ejecutar `.\ayda-parcial.exe`.

7. Ejecutar: doble clic en `ayda-parcial.exe` o `.\ayda-parcial.exe` desde
   PowerShell ubicado en esa carpeta.

## Solución de problemas

- **"No se encontró el archivo datos.txt" o "No se encontró el archivo
  matriz.txt"**: los archivos deben estar junto al `.exe` y hay que ejecutar
  desde esa carpeta (ver paso 6).
- **El antivirus bloquea el `.exe`**: los ejecutables de un solo archivo creados
  por PyInstaller tienen firma desconocida. Permitir la ejecución o compilar en
  modo carpeta quitando `a.binaries` y `a.datas` de `EXE(...)` y agregando un
  bloque `COLLECT(...)` (el resultado sería `dist\ayda-parcial\ayda-parcial.exe`).
- **Cambiar el nombre del ejecutable**: editar `name="ayda-parcial"` en
  `ayda-parcial.spec` y volver a compilar con `--clean`.
- **Recompilar desde cero**: agregar `--clean` al comando de PyInstaller.
- **El `.exe` no sirve en otra arquitectura**: PyInstaller incluye el intérprete
  de Python usado al compilar; hay que generarlo en la misma versión de Windows
  y arquitectura (x64) en la que se va a ejecutar.
