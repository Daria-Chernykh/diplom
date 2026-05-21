import os
import shutil
import uuid
from pathlib import Path

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Event, EventReview, File, User


class FileError(Exception):
    def __init__(self, message: str, status_code: int = 400, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


ENTITY_FOLDERS = {
    "event": "events",
    "review": "reviews",
    "user_profile": "profiles",
    "organizer_profile": "organizers",
}


SINGLE_FILE_ENTITY_TYPES = {
    "event",
    "user_profile",
    "organizer_profile",
}


def get_upload_root() -> Path:
    configured_folder = current_app.config.get("UPLOAD_FOLDER")

    upload_root = Path(configured_folder)

    if not upload_root.is_absolute():
        upload_root = Path(current_app.root_path).parent / upload_root

    upload_root.mkdir(parents=True, exist_ok=True)

    return upload_root


def get_entity_folder(entity_type: str, entity_id: int) -> Path:
    if entity_type not in ENTITY_FOLDERS:
        raise FileError(
            "Недопустимый тип сущности для загрузки файла.",
            status_code=400,
            details={"entity_type": "Недопустимый тип сущности."},
        )

    folder = get_upload_root() / ENTITY_FOLDERS[entity_type] / str(entity_id)
    folder.mkdir(parents=True, exist_ok=True)

    return folder


def validate_image_file(file: FileStorage) -> None:
    if file is None or not file.filename:
        raise FileError(
            "Файл не передан.",
            status_code=400,
            details={"file": "Выберите файл для загрузки."},
        )

    if file.mimetype not in ALLOWED_IMAGE_MIME_TYPES:
        raise FileError(
            "Можно загружать только изображения JPEG, PNG или WEBP.",
            status_code=400,
            details={"file": "Разрешенные форматы: JPEG, PNG, WEBP."},
        )

    max_size_mb = current_app.config.get("MAX_UPLOAD_SIZE_MB", 5)
    max_size_bytes = max_size_mb * 1024 * 1024

    stream = file.stream
    stream.seek(0, os.SEEK_END)
    file_size = stream.tell()
    stream.seek(0)

    if file_size > max_size_bytes:
        raise FileError(
            f"Размер файла не должен превышать {max_size_mb} МБ.",
            status_code=400,
            details={"file": f"Максимальный размер файла — {max_size_mb} МБ."},
        )


def validate_entity_exists(entity_type: str, entity_id: int) -> None:
    if entity_type == "event":
        exists = Event.query.filter(Event.id == entity_id).first() is not None
    elif entity_type == "review":
        exists = EventReview.query.filter(EventReview.id == entity_id).first() is not None
    elif entity_type in {"user_profile", "organizer_profile"}:
        exists = User.query.filter(User.id == entity_id).first() is not None
    else:
        exists = False

    if not exists:
        raise FileError(
            "Сущность для привязки файла не найдена.",
            status_code=404,
        )


def get_entity_files(entity_type: str, entity_id: int) -> list[File]:
    return (
        File.query.filter(File.entity_type == entity_type)
        .filter(File.entity_id == entity_id)
        .order_by(File.id.asc())
        .all()
    )


def get_entity_single_file(entity_type: str, entity_id: int) -> File | None:
    return (
        File.query.filter(File.entity_type == entity_type)
        .filter(File.entity_id == entity_id)
        .order_by(File.id.desc())
        .first()
    )


def remove_file_from_disk(file: File) -> None:
    upload_root = get_upload_root()
    absolute_path = upload_root / file.file_path

    if absolute_path.exists():
        absolute_path.unlink()

    parent = absolute_path.parent

    if parent.exists() and not any(parent.iterdir()):
        parent.rmdir()


def delete_file_record(file: File, commit: bool = True) -> None:
    remove_file_from_disk(file)
    db.session.delete(file)

    if commit:
        db.session.commit()


def delete_entity_files(entity_type: str, entity_id: int, commit: bool = True) -> None:
    files = get_entity_files(entity_type, entity_id)

    for file in files:
        delete_file_record(file, commit=False)

    folder = get_upload_root() / ENTITY_FOLDERS.get(entity_type, "") / str(entity_id)

    if folder.exists():
        shutil.rmtree(folder, ignore_errors=True)

    if commit:
        db.session.commit()


def save_image_file(
    uploader: User,
    entity_type: str,
    entity_id: int,
    file: FileStorage,
    replace_existing: bool = False,
    commit: bool = True,
) -> File:
    validate_entity_exists(entity_type, entity_id)
    validate_image_file(file)

    if entity_type in SINGLE_FILE_ENTITY_TYPES:
        replace_existing = True

    if replace_existing:
        delete_entity_files(entity_type, entity_id, commit=False)

    entity_folder = get_entity_folder(entity_type, entity_id)

    original_filename = secure_filename(file.filename)
    extension = os.path.splitext(original_filename)[1].lower()

    if not extension:
        extension = ".jpg"

    stored_filename = f"{uuid.uuid4().hex}{extension}"
    absolute_path = entity_folder / stored_filename

    file.save(absolute_path)

    relative_path = (
        Path(ENTITY_FOLDERS[entity_type]) / str(entity_id) / stored_filename
    ).as_posix()

    file_record = File(
        uploader_id=uploader.id,
        entity_type=entity_type,
        entity_id=entity_id,
        file_path=relative_path,
        original_filename=original_filename,
        mime_type=file.mimetype,
    )

    db.session.add(file_record)

    if commit:
        db.session.commit()

    return file_record


def save_review_photos(
    uploader: User,
    review: EventReview,
    files: list[FileStorage],
    commit: bool = True,
) -> list[File]:
    max_review_photos = current_app.config.get("MAX_REVIEW_PHOTOS", 5)

    existing_count = (
        File.query.filter(File.entity_type == "review")
        .filter(File.entity_id == review.id)
        .count()
    )

    valid_files = [file for file in files if file and file.filename]

    if existing_count + len(valid_files) > max_review_photos:
        raise FileError(
            f"К отзыву можно прикрепить не более {max_review_photos} фотографий.",
            status_code=400,
            details={"photos": f"Максимальное количество файлов — {max_review_photos}."},
        )

    saved_files = []

    for file in valid_files:
        saved_files.append(
            save_image_file(
                uploader=uploader,
                entity_type="review",
                entity_id=review.id,
                file=file,
                replace_existing=False,
                commit=False,
            )
        )

    if commit:
        db.session.commit()

    return saved_files


def get_file_by_id_or_404(file_id: int) -> File:
    file = File.query.filter(File.id == file_id).first()

    if file is None:
        raise FileError("Файл не найден.", status_code=404)

    return file


def can_user_manage_file(user: User, file: File) -> bool:
    if user.role == "admin":
        return True

    if file.uploader_id == user.id:
        return True

    if file.entity_type == "event":
        event = Event.query.filter(Event.id == file.entity_id).first()
        return event is not None and event.organizer_id == user.id

    if file.entity_type == "review":
        review = EventReview.query.filter(EventReview.id == file.entity_id).first()
        return review is not None and review.user_id == user.id

    if file.entity_type in {"user_profile", "organizer_profile"}:
        return file.entity_id == user.id

    return False


def delete_file_by_user(user: User, file_id: int) -> None:
    file = get_file_by_id_or_404(file_id)

    if not can_user_manage_file(user, file):
        raise FileError("Нет доступа к удалению файла.", status_code=403)

    delete_file_record(file, commit=True)


def get_event_for_file_upload(user: User, event_id: int) -> Event:
    event = Event.query.filter(Event.id == event_id).first()

    if event is None:
        raise FileError("Мероприятие не найдено.", status_code=404)

    if user.role != "admin" and event.organizer_id != user.id:
        raise FileError("Нет доступа к загрузке изображения мероприятия.", status_code=403)

    return event


def save_event_image(user: User, event_id: int, file: FileStorage) -> File:
    get_event_for_file_upload(user, event_id)

    return save_image_file(
        uploader=user,
        entity_type="event",
        entity_id=event_id,
        file=file,
        replace_existing=True,
        commit=True,
    )


def save_user_profile_image(user: User, file: FileStorage) -> File:
    return save_image_file(
        uploader=user,
        entity_type="user_profile",
        entity_id=user.id,
        file=file,
        replace_existing=True,
        commit=True,
    )


def save_organizer_profile_image(user: User, file: FileStorage) -> File:
    if user.role not in {"organizer", "admin"}:
        raise FileError(
            "Изображение организатора доступно только организатору.",
            status_code=403,
        )

    return save_image_file(
        uploader=user,
        entity_type="organizer_profile",
        entity_id=user.id,
        file=file,
        replace_existing=True,
        commit=True,
    )