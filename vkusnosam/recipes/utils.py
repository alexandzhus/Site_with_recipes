
def filter_valid_lines(input_string):
    """
    Фильтрует строки, оставляя только те, которые содержат тире и заканчиваются на точку с запятой.
    :param input_string: Исходная строка
    :return: Список строк, соответствующих условиям
    """
    # Разделяем строку на отдельные строки
    lines = input_string.splitlines()
    # Фильтруем строки
    valid_lines = []
    for line in lines:
        line = line.strip()  # Убираем лишние пробелы
        if '-' in line and line.endswith(';'):  # Проверяем наличие тире и точки с запятой
            valid_lines.append(line)
    return valid_lines