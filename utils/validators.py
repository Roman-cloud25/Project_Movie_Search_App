# проверка корректности диапазона годов
def validate_year_range(
        year_from: int | None,
        year_to: int | None,
        min_year: int,
        max_year: int
) -> None:
    if year_from and not (min_year <= year_from <= max_year):
        raise ValueError("Invalid start year")

    if year_to and not (min_year <= year_to <= max_year):
        raise ValueError("Invalid end year")

    if year_from and year_to and year_from > year_to:
        raise ValueError("Start year cannot be greater than end year")


# проверяет ключевое слово
def validate_keyword(keyword: str):
    if not keyword or len(keyword.strip()) < 2:
        raise ValueError("Keyword is too short")
