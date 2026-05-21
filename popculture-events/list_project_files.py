from __future__ import annotations

from datetime import datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = ROOT_DIR / "project_clean_listing.txt"

IGNORED_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
    ".vite",
    "coverage",
    "htmlcov",
    "uploads",
    "instance",
    "logs",
}

IGNORED_FILES = {
    ".env",
    "project_files_listing.txt",
    "project_clean_listing.txt",
    "list_project_files.py",
}

IGNORED_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".log",
    ".tmp",
    ".temp",
    ".cache",
    ".db",
    ".sqlite",
    ".sqlite3",
}

TEXT_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".json",
    ".html",
    ".css",
    ".txt",
    ".md",
    ".env.example",
    ".gitignore",
    ".drawio",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".cfg",
    ".bat",
    ".cmd",
    ".ps1",
    ".sql",
    ".xml",
    ".csv",
}


def is_ignored_path(path: Path) -> bool:
    relative_parts = path.relative_to(ROOT_DIR).parts

    for part in relative_parts:
        if part in IGNORED_DIRS:
            return True

    if path.name in IGNORED_FILES:
        return True

    if path.suffix.lower() in IGNORED_EXTENSIONS:
        return True

    return False


def is_text_file(path: Path) -> bool:
    if path.name in {".env.example", ".gitignore"}:
        return True

    return path.suffix.lower() in TEXT_EXTENSIONS


def get_file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def get_all_project_files() -> list[Path]:
    result = []

    for path in ROOT_DIR.rglob("*"):
        if path.is_file() and not is_ignored_path(path):
            result.append(path)

    return sorted(result, key=lambda item: str(item.relative_to(ROOT_DIR)).lower())


def read_text_file(path: Path) -> str:
    encodings = ["utf-8", "utf-8-sig", "cp1251"]

    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except OSError as error:
            return f"Не удалось прочитать файл: {error}"

    return "Файл не является текстовым или использует неподдерживаемую кодировку."


def write_header(output, files: list[Path]) -> None:
    output.write("ЛИСТИНГ ФАЙЛОВ ПРОЕКТА POPCULTURE EVENTS\n")
    output.write("=" * 120)
    output.write("\n")
    output.write(f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
    output.write(f"Корень проекта: {ROOT_DIR}\n")
    output.write(f"Файл результата: {OUTPUT_FILE}\n")
    output.write(f"Количество файлов: {len(files)}\n")
    output.write("\n")

    output.write("ИСКЛЮЧЕННЫЕ СЛУЖЕБНЫЕ ПАПКИ\n")
    output.write("-" * 120)
    output.write("\n")
    for directory in sorted(IGNORED_DIRS):
        output.write(f"{directory}\n")

    output.write("\n")
    output.write("ИСКЛЮЧЕННЫЕ СЛУЖЕБНЫЕ ФАЙЛЫ\n")
    output.write("-" * 120)
    output.write("\n")
    for file_name in sorted(IGNORED_FILES):
        output.write(f"{file_name}\n")

    output.write("\n")


def write_file_tree(output, files: list[Path]) -> None:
    output.write("СПИСОК ФАЙЛОВ\n")
    output.write("=" * 120)
    output.write("\n")

    for index, path in enumerate(files, start=1):
        relative_path = path.relative_to(ROOT_DIR)
        size = get_file_size(path)
        output.write(f"{index:03}. {relative_path} ({size} байт)\n")

    output.write("\n")


def write_file_contents(output, files: list[Path]) -> None:
    output.write("СОДЕРЖИМОЕ ТЕКСТОВЫХ ФАЙЛОВ\n")
    output.write("=" * 120)
    output.write("\n\n")

    for path in files:
        relative_path = path.relative_to(ROOT_DIR)
        size = get_file_size(path)

        output.write("=" * 120)
        output.write("\n")
        output.write(f"ФАЙЛ: {relative_path}\n")
        output.write(f"РАЗМЕР: {size} байт\n")
        output.write("=" * 120)
        output.write("\n\n")

        if is_text_file(path):
            output.write(read_text_file(path))
        else:
            output.write("Содержимое не выведено: файл не относится к текстовым файлам проекта.")

        output.write("\n\n")


def main() -> None:
    files = get_all_project_files()

    with OUTPUT_FILE.open("w", encoding="utf-8") as output:
        write_header(output, files)
        write_file_tree(output, files)
        write_file_contents(output, files)

    print("Листинг проекта сформирован.")
    print(f"Файлов включено: {len(files)}")
    print(f"Результат сохранен в файл: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()