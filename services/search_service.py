from math import ceil
from typing import List, Tuple, Dict, Optional
from db.mysql_connector import get_mysql_connection
from utils.decorators import log_execution


# поиск фильмов по ключевому слову в названии
@log_execution
def search_by_keyword(keyword: str, page: int, limit: int) -> Tuple[List[Dict], int]:
    safe_limit = int(limit)
    safe_page = int(page)
    safe_offset = (safe_page - 1) * safe_limit

    clean_keyword = str(keyword).strip().lower()
    like_pattern = f"%{clean_keyword}%"

    connection = get_mysql_connection()
    try:
        with connection.cursor() as cursor:

            count_sql = "SELECT COUNT(*) AS total FROM film WHERE LOWER(title) LIKE %s"
            cursor.execute(count_sql, (like_pattern,))

            total_results = cursor.fetchone()["total"]
            total_pages = ceil(total_results / safe_limit) if total_results > 0 else 1

            select_sql = """
                SELECT title, description, release_year, rental_rate as rating 
                FROM film 
                WHERE LOWER(title) LIKE %s
                LIMIT %s OFFSET %s
            """
            cursor.execute(select_sql, (like_pattern, safe_limit, safe_offset))

            return cursor.fetchall(), total_pages
    finally:
        connection.close()


# поиск фильмов по названию
@log_execution
def search_by_keyword(keyword: str, page: int, limit: int) -> Tuple[List[Dict], int]:
    safe_limit = int(limit)
    safe_page = int(page)
    safe_offset = (safe_page - 1) * safe_limit

    clean_keyword = str(keyword).strip().lower()
    like_pattern = f"{clean_keyword}%"

    connection = get_mysql_connection()
    try:
        with connection.cursor() as cursor:

            count_sql = "SELECT COUNT(*) AS total FROM film WHERE LOWER(title) LIKE %s"
            cursor.execute(count_sql, (like_pattern,))

            total_results = cursor.fetchone()["total"]
            total_pages = ceil(total_results / safe_limit) if total_results > 0 else 1

            select_sql = """
                SELECT f.title, f.description, f.release_year, f.rental_rate as rating, 
                       c.name AS genre 
                FROM film f
                LEFT JOIN film_category fc ON f.film_id = fc.film_id
                LEFT JOIN category c ON fc.category_id = c.category_id
                WHERE LOWER(f.title) LIKE %s
                LIMIT %s OFFSET %s
            """
            cursor.execute(select_sql, (like_pattern, safe_limit, safe_offset))

            return cursor.fetchall(), total_pages
    finally:
        connection.close()


# фильтрация по жанру и годам
@log_execution
def search_by_genre_and_years(genre: str, year_from: int, year_to: int, page: int, limit: int):
    safe_limit = int(limit)
    safe_offset = (int(page) - 1) * safe_limit
    connection = get_mysql_connection()

    try:
        with connection.cursor() as cursor:
            count_query = """
                SELECT COUNT(*) AS total FROM film f
                JOIN film_category fc ON f.film_id = fc.film_id
                JOIN category c ON fc.category_id = c.category_id
                WHERE (%s = '' OR c.name = %s) AND f.release_year BETWEEN %s AND %s
            """
            cursor.execute(count_query, (genre, genre, int(year_from), int(year_to)))
            total_results = cursor.fetchone()["total"]
            total_pages = ceil(total_results / safe_limit) if total_results > 0 else 1

            query = """
                SELECT f.title, f.description, f.release_year, c.name AS genre
                FROM film f
                JOIN film_category fc ON f.film_id = fc.film_id
                JOIN category c ON fc.category_id = c.category_id
                WHERE (%s = '' OR c.name = %s) AND f.release_year BETWEEN %s AND %s
                ORDER BY f.release_year ASC, f.title ASC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (genre, genre, int(year_from), int(year_to), safe_limit, safe_offset))
            return cursor.fetchall(), total_pages
    finally:
        connection.close()


# список жанров
@log_execution
def get_all_genres() -> List[str]:
    query = "SELECT name FROM category ORDER BY name;"
    connection = get_mysql_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            return [row["name"] for row in result]
    finally:
        connection.close()


# минимальный и максимальный год
@log_execution
def get_years_range() -> Tuple[int, int]:
    query = "SELECT MIN(release_year) AS min_year, MAX(release_year) AS max_year FROM film;"
    connection = get_mysql_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
            return int(result["min_year"]), int(result["max_year"])
    finally:
        connection.close()


# подробная информация о конкретном фильме для детальной страницы
@log_execution
def get_movie_details(title: str) -> Optional[Dict]:
    connection = get_mysql_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT f.title, f.description, f.release_year, c.name AS genre,
                       f.rating, f.length, f.special_features
                FROM film f
                JOIN film_category fc ON f.film_id = fc.film_id
                JOIN category c ON fc.category_id = c.category_id
                WHERE f.title = %s
            """
            cursor.execute(query, (title,))
            return cursor.fetchone()
    finally:
        connection.close()
