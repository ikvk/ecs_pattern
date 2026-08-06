from pathlib import Path


def dump_package(package_path, output_file):
    """
    Рекурсивно выгружает все .py файлы из пакета в текстовый файл.
    Аргументы:
        package_path (str или Path): путь к корневой папке пакета.
        output_file (str или Path): путь к выходному .txt файлу.
    """
    package_path = Path(package_path)
    output_file = Path(output_file)

    if not package_path.is_dir():
        raise NotADirectoryError(f"Указанный путь не является папкой: {package_path}")

    py_files = sorted(package_path.rglob("*.py"))

    with output_file.open("w", encoding="utf-8") as out:
        for py_file in py_files:
            out.write(f"### файл: {py_file}\n")
            try:
                out.write(py_file.read_text(encoding="utf-8"))
            except Exception as e:
                out.write(f"# Ошибка чтения файла: {e}\n")
            out.write("\n\n")  # разделитель между файлами


# Пример использования (закомментирован)
dump_package(
    r"C:\kvk\develop\Python\ecs_pattern\examples\snow_day",
    r"C:\kvk\develop\Python\ecs_pattern\_docs\1.txt"
)
