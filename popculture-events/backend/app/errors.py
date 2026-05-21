from http import HTTPStatus

from flask import Flask, jsonify
from flask_jwt_extended.exceptions import JWTExtendedException
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException


def _error_response(status_code: int, message: str, details: dict | None = None):
    payload = {
        "success": False,
        "error": {
            "code": status_code,
            "message": message,
        },
    }

    if details is not None:
        payload["error"]["details"] = details

    response = jsonify(payload)
    response.status_code = status_code

    return response


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        status_code = error.code or HTTPStatus.INTERNAL_SERVER_ERROR
        message = error.description or HTTPStatus(status_code).phrase

        return _error_response(status_code, message)

    @app.errorhandler(JWTExtendedException)
    def handle_jwt_exception(error: JWTExtendedException):
        return _error_response(
            HTTPStatus.UNAUTHORIZED,
            str(error),
        )

    @app.errorhandler(SQLAlchemyError)
    def handle_database_exception(error: SQLAlchemyError):
        app.logger.exception(error)

        return _error_response(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "Ошибка при работе с базой данных.",
        )

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error: Exception):
        app.logger.exception(error)

        return _error_response(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "Внутренняя ошибка сервера.",
        )