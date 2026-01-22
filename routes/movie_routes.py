from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from typing import Optional
from pathlib import Path
from services.mongo_logger import log_search_query, get_top_queries, get_last_unique_queries
from services.search_service import (
    search_by_keyword,
    search_by_genre_and_years,
    get_all_genres,
    get_years_range,
    get_movie_details
)
from utils.validators import validate_keyword, validate_year_range
from local_settings import RESULTS_LIMIT

router = APIRouter()
PER_PAGE = RESULTS_LIMIT

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")


# основной роутер главной страницы
@router.get("/")
async def home(
        request: Request,
        keyword: Optional[str] = Query(None),
        genre: Optional[str] = Query(None),
        year_from: Optional[str] = Query(None),
        year_to: Optional[str] = Query(None),
        page: int = Query(1)
):
    try:
        genres = get_all_genres()
        min_yr, max_yr = get_years_range()
    except Exception as e:
        print(f"Критическая ошибка БД: {e}")
        genres, min_yr, max_yr = [], 1900, 2025

    clean_keyword = keyword.strip() if keyword else None
    current_page = int(page) if page else 1
    limit = int(PER_PAGE)

    context = {
        "request": request,
        "genres": genres,
        "min_year": min_yr,
        "max_year": max_yr,
        "keyword": clean_keyword,
        "selected_genre": genre,
        "year_from": year_from,
        "year_to": year_to,
        "page": current_page,
        "films": [],
        "total_pages": 1,
        "popular_stats": [],
        "recent_stats": []
    }

    # статистика MongoDB (try-except защищает от ошибки Unauthorized)
    try:
        context["popular_stats"] = get_top_queries(5)
        context["recent_stats"] = get_last_unique_queries(5)
    except Exception as e:
        print(f"Ошибка MongoDB: {e}")

    # логика поиска
    try:
        # пустой поиск
        if keyword is not None and not keyword.strip() and not (genre or year_from or year_to):
            validate_keyword("")

        # по названию (включая одну букву)
        if clean_keyword:
            validate_keyword(clean_keyword)
            films, total_pages = search_by_keyword(clean_keyword, current_page, limit)
            log_search_query("keyword", {"keyword": clean_keyword}, len(films))

        # по жанру и годам
        elif genre or year_from or year_to:
            y_f = int(year_from) if (year_from and str(year_from).isdigit()) else min_yr
            y_t = int(year_to) if (year_to and str(year_to).isdigit()) else max_yr

            validate_year_range(y_f, y_t, min_yr, max_yr)  #

            films, total_pages = search_by_genre_and_years(genre or "", y_f, y_t, current_page, limit)

            # запись с полной информацией для "Недавнее"
            log_search_query("genre__years_range", {
                "genre": genre or "Все жанры",
                "from": y_f,
                "to": y_t
            }, len(films))

        # главная страница по умолчанию
        else:
            films, total_pages = search_by_keyword("", current_page, limit)

        context.update({"films": films, "total_pages": total_pages})

    except Exception as e:
        context["error_message"] = str(e)

    return templates.TemplateResponse("home.html", context)


# детальная информация о фильме
@router.get("/movie/{title}")
async def movie_details(request: Request, title: str):
    try:
        movie = get_movie_details(title)
        if not movie:
            raise ValueError("Фильм не найден")
        return templates.TemplateResponse("movie_details.html", {"request": request, "movie": movie})
    except Exception as e:
        return templates.TemplateResponse("home.html", {
            "request": request,
            "error_message": f"Ошибка при загрузке фильма: {e}",
            "genres": get_all_genres(),
            "min_year": get_years_range()[0],
            "max_year": get_years_range()[1],
            "films": [],
            "total_pages": 1,
            "popular_stats": [],
            "recent_stats": []
        })
