# проверка корректности диапазона годов
def validate_year_range(
        year_from: int | None,
        year_to: int | None,
        min_year: int,
        max_year: int
) -> None:
    error_msg = f"Пожалуйста, введите года в диапазоне от {min_year} до {max_year}"

    if year_from and not (min_year <= year_from <= max_year):
        raise ValueError(error_msg)

    if year_to and not (min_year <= year_to <= max_year):
        raise ValueError(error_msg)

    if year_from and year_to and year_from > year_to:
        raise ValueError("Год 'ОТ' не может быть больше года 'ДО'")


# проверяет ключевое слово
def validate_keyword(keyword: str):
    if not keyword or len(keyword.strip()) < 1:
        raise ValueError("Пожалуйста, введите название фильма для поиска")
