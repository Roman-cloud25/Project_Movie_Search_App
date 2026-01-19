import logging
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

error_logger = logging.getLogger("errors")


# обрабатывает ошибки валидации
async def value_error_handler(
        request: Request,
        exc: ValueError
) -> HTMLResponse:
    error_logger.warning(str(exc))

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "error_message": str(exc),
        },
        status_code=400
    )
