from math import ceil
from typing import Tuple, List
from local_settings import RESULTS_LIMIT

PER_PAGE = RESULTS_LIMIT


# делит список на страницы
def paginate(
        items: List,
        page: int,
        per_page: int = PER_PAGE
) -> Tuple[List, int]:
    if page < 1:
        page = 1

    total_pages = ceil(len(items) / per_page)

    start = (page - 1) * per_page
    end = start + per_page

    return items[start:end], total_pages
