from math import ceil
from typing import List, Tuple, Dict
from db.mysql_connector import get_mysql_connection
from utils.decorators import log_execution


# поиск фильмов по ключевому слову в названии и описании
@log_execution
def search_by_keyword(keyword: str, page: int, limit: int) -> Tuple[List[Dict], int]:
    offset = (page - 1) * limit
    connection = get_mysql_connection()
    like_pattern = f"%{keyword}%"

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM film WHERE title LIKE %s OR description LIKE %s",
                           (like_pattern, like_pattern))
            total_results = cursor.fetchone()["total"]
            total_pages = ceil(total_results / limit) if total_results > 0 else 1

            query = """
                SELECT f.title, f.description, f.release_year, c.name AS genre
                FROM film f
                JOIN film_category fc ON f.film_id = fc.film_id
                JOIN category c ON fc.category_id = c.category_id
                WHERE f.title LIKE %s OR f.description LIKE %s
                ORDER BY f.title ASC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (like_pattern, like_pattern, limit, offset))
            return cursor.fetchall(), total_pages
    finally:
        connection.close()


# фильтрация фильмов по жанру и диапазону лет выпуска
@log_execution
def search_by_genre_and_years(genre: str, year_from: int, year_to: int, page: int, limit: int):
    offset = (page - 1) * limit
    connection = get_mysql_connection()

    try:
        with connection.cursor() as cursor:

            count_query = """
                SELECT COUNT(*) AS total FROM film f
                JOIN film_category fc ON f.film_id = fc.film_id
                JOIN category c ON fc.category_id = c.category_id
                WHERE (%s = '' OR c.name = %s) AND f.release_year BETWEEN %s AND %s
            """
            cursor.execute(count_query, (genre, genre, year_from, year_to))
            total_results = cursor.fetchone()["total"]
            total_pages = ceil(total_results / limit) if total_results > 0 else 1

            query = """
                SELECT f.title, f.description, f.release_year, c.name AS genre
                FROM film f
                JOIN film_category fc ON f.film_id = fc.film_id
                JOIN category c ON fc.category_id = c.category_id
                WHERE (%s = '' OR c.name = %s) AND f.release_year BETWEEN %s AND %s
                ORDER BY f.release_year ASC, f.title ASC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (genre, genre, year_from, year_to, limit, offset))
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
            return result["min_year"], result["max_year"]
    finally:
        connection.close()
