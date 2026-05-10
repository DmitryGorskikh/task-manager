from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger


def setup_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        logger.error(f"Database error: {exc} | Path: {request.url.path}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Database error occurred"},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error(f"Unhandled error: {exc} | Path: {request.url.path}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
