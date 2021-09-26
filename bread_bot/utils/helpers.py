import re

from bread_bot.main.settings import DEFAULT_SENSITIVE_KEY_WORDS_PATTERN


def chunks(chunked_list, n: int):
    """
    Chunk коллекций на размер N
    """
    for i in range(0, len(chunked_list), n):
        yield chunked_list[i:i + n]


def mask_string(
        source_string: str,
        additional_mask_keys: tuple = tuple(),
        additional_mask_values: tuple = tuple()
) -> str:
    """
    Маскирование уязвимых данных по ключам в строке.

    :param source_string: Оригинал строки
    :param additional_mask_keys: Дополнительные ключи данных
    :param additional_mask_values: Дополнительные данные
    :return: Строка со скрытыми уязвимыми данными
    """
    # Подготовка паттерна поиска
    mask_keys = DEFAULT_SENSITIVE_KEY_WORDS_PATTERN

    if additional_mask_keys:
        mask_keys += '|' + '|'.join(
            map(lambda x: f'\\b{x}\\b', additional_mask_keys,)
        )
    mask_regex = rf'\\?[\"|\']?({mask_keys})' \
                 r'\\?[\"|\']?[:|=]\s?\\?[\"|\']?(.+?)\\?[\\|\"|\'|,]\}?'
    # Поиск подходящих ключ-значений
    groups = re.findall(mask_regex, source_string, re.IGNORECASE)

    if not groups and not additional_mask_values:
        return source_string
    # Коллекционирование уязвимых данных в паттерн из уникального набора
    sensitive_data_set = '|'.join(
        (f'\\b{v}\\b' for k, v in set(groups))
    )
    if additional_mask_values:
        sensitive_data_set += '|' + '|'.join(
            map(
                lambda x: f'\\b{x}\\b',
                additional_mask_values,
            )
        )
    # Маскирование
    result = re.sub(
        sensitive_data_set,
        repl='***',
        string=source_string,
    )

    return result
