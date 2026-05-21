from flask import Flask

from app.extensions import db


def register_commands(app: Flask) -> None:
    @app.cli.command("db-check")
    def db_check() -> None:
        with app.app_context():
            db.session.execute(db.text("SELECT 1"))
            print("Подключение к базе данных выполнено успешно.")