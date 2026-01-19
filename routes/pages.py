from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from typing import Optional
from pathlib import Path
from services.mongo_logger import log_search_query, get_top_queries, get_last_unique_queries
from services.search_service import search_by_keyword, search_by_genre_and_years, get_all_genres, get_years_range
from utils.validators import validate_keyword, validate_year_range
from local_settings import RESULTS_LIMIT

router = APIRouter()
PER_PAGE = RESULTS_LIMIT

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@router.get("/")
async def home(
        request: Request,
        keyword: Optional[str] = Query(None),
        genre: Optional[str] = Query(None),
        year_from: Optional[str] = Query(None),
        year_to: Optional[str] = Query(None),
        page: int = Query(1)
):
    genres = get_all_genres()
    min_yr, max_yr = get_years_range()

    # статистика из MongoDB (Популярные и Недавние)
    try:
        popular_stats = get_top_queries(5)
        recent_stats = get_last_unique_queries(5)
    except Exception:
        popular_stats, recent_stats = [], []

    # контекст для передачи в HTML-шаблон
    context = {
        "request": request,
        "genres": genres,
        "min_year": min_yr,
        "max_year": max_yr,
        "popular_stats": popular_stats,
        "recent_stats": recent_stats,
        "keyword": keyword,
        "selected_genre": genre,
        "year_from": year_from,
        "year_to": year_to,
        "page": page
    }

    # поиск
    try:
        if keyword:
            validate_keyword(keyword)
            films, total_pages = search_by_keyword(keyword, page, PER_PAGE)
            log_search_query("keyword", {"keyword": keyword}, len(films))
        elif genre or year_from or year_to:
            y_f = int(year_from) if year_from and year_from.isdigit() else min_yr
            y_t = int(year_to) if year_to and year_to.isdigit() else max_yr
            validate_year_range(y_f, y_t, min_yr, max_yr)
            films, total_pages = search_by_genre_and_years(genre or "", y_f, y_t, page, PER_PAGE)
            log_search_query("genre__years_range", {"genre": genre, "from": y_f, "to": y_t}, len(films))
        else:
            films, total_pages = search_by_keyword("", page, PER_PAGE)

        context.update({"films": films, "total_pages": total_pages})
        return templates.TemplateResponse("home.html", context)

    except ValueError as e:
        context.update({"error_message": str(e), "films": [], "total_pages": 1})
        return templates.TemplateResponse("home.html", context)
