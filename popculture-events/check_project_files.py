from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parent

OUTPUT_FILE = PROJECT_ROOT / "project_files_listing.txt"


EXPECTED_FILES = [
    ".env.example",
    "README.md",

    "backend/.env",
    "backend/requirements.txt",
    "backend/run.py",

    "backend/app/__init__.py",
    "backend/app/config.py",
    "backend/app/extensions.py",
    "backend/app/errors.py",

    "backend/app/common/__init__.py",
    "backend/app/common/validators.py",

    "backend/app/models/__init__.py",
    "backend/app/models/user.py",
    "backend/app/models/event.py",
    "backend/app/models/registration.py",
    "backend/app/models/tag.py",
    "backend/app/models/favorite.py",
    "backend/app/models/review.py",
    "backend/app/models/rating.py",
    "backend/app/models/complaint.py",
    "backend/app/models/notification.py",
    "backend/app/models/file.py",
    "backend/app/models/legal.py",

    "backend/app/auth/__init__.py",
    "backend/app/auth/routes.py",
    "backend/app/auth/schemas.py",
    "backend/app/auth/services.py",
    "backend/app/auth/decorators.py",

    "backend/app/users/__init__.py",
    "backend/app/users/routes.py",
    "backend/app/users/schemas.py",
    "backend/app/users/services.py",

    "backend/app/organizers/__init__.py",
    "backend/app/organizers/routes.py",
    "backend/app/organizers/schemas.py",
    "backend/app/organizers/services.py",

    "backend/app/events/__init__.py",
    "backend/app/events/routes.py",
    "backend/app/events/schemas.py",
    "backend/app/events/services.py",

    "backend/app/registrations/__init__.py",
    "backend/app/registrations/routes.py",
    "backend/app/registrations/schemas.py",
    "backend/app/registrations/services.py",

    "backend/app/favorites/__init__.py",
    "backend/app/favorites/routes.py",
    "backend/app/favorites/schemas.py",
    "backend/app/favorites/services.py",

    "backend/app/reviews/__init__.py",
    "backend/app/reviews/routes.py",
    "backend/app/reviews/schemas.py",
    "backend/app/reviews/services.py",

    "backend/app/complaints/__init__.py",
    "backend/app/complaints/routes.py",
    "backend/app/complaints/schemas.py",
    "backend/app/complaints/services.py",

    "backend/app/notifications/__init__.py",
    "backend/app/notifications/routes.py",
    "backend/app/notifications/schemas.py",
    "backend/app/notifications/services.py",

    "backend/app/files/__init__.py",
    "backend/app/files/routes.py",
    "backend/app/files/schemas.py",
    "backend/app/files/services.py",

    "backend/app/legal/__init__.py",
    "backend/app/legal/routes.py",
    "backend/app/legal/schemas.py",
    "backend/app/legal/services.py",

    "frontend/package.json",
    "frontend/index.html",
    "frontend/vite.config.js",
    "frontend/src/main.jsx",
    "frontend/src/App.jsx",
    "frontend/src/styles.css",

    "frontend/src/api/httpClient.js",
    "frontend/src/api/authApi.js",
    "frontend/src/api/legalApi.js",
    "frontend/src/api/usersApi.js",
    "frontend/src/api/organizersApi.js",
    "frontend/src/api/eventsApi.js",
    "frontend/src/api/favoritesApi.js",
    "frontend/src/api/registrationsApi.js",
    "frontend/src/api/reviewsApi.js",
    "frontend/src/api/complaintsApi.js",
    "frontend/src/api/notificationsApi.js",
    "frontend/src/api/filesApi.js",

    "frontend/src/store/AuthContext.jsx",

    "frontend/src/router/AppRouter.jsx",
    "frontend/src/router/ProtectedRoute.jsx",
    "frontend/src/router/PublicOnlyRoute.jsx",
    "frontend/src/router/LegalRequiredRoute.jsx",

    "frontend/src/layouts/AppLayout.jsx",
    "frontend/src/layouts/AuthLayout.jsx",

    "frontend/src/utils/validation.js",

    "frontend/src/components/ui/Modal.jsx",
    "frontend/src/components/ui/StatusBadge.jsx",
    "frontend/src/components/ui/FieldError.jsx",

    "frontend/src/components/events/EventCard.jsx",

    "frontend/src/components/files/ImageUploader.jsx",

    "frontend/src/components/reviews/ReviewForm.jsx",
    "frontend/src/components/reviews/ReviewCard.jsx",

    "frontend/src/components/complaints/EventComplaintModal.jsx",

    "frontend/src/pages/HomePage.jsx",
    "frontend/src/pages/LoginPage.jsx",
    "frontend/src/pages/RegisterPage.jsx",
    "frontend/src/pages/LegalAcceptancePage.jsx",
    "frontend/src/pages/ForbiddenPage.jsx",

    "frontend/src/pages/EventCreatePage.jsx",
    "frontend/src/pages/EventEditPage.jsx",
    "frontend/src/pages/EventRegistrationPage.jsx",

    "frontend/src/pages/events/EventCatalogPage.jsx",
    "frontend/src/pages/events/EventDetailsPage.jsx",
    "frontend/src/pages/events/EventInternalPage.jsx",
    "frontend/src/pages/events/EventExternalPage.jsx",
    "frontend/src/pages/events/EventWithoutRegistrationPage.jsx",
    "frontend/src/pages/events/EventPastPage.jsx",
    "frontend/src/pages/events/EventPastAdminPage.jsx",

    "frontend/src/pages/user/UserCabinetPage.jsx",
    "frontend/src/pages/user/UserFavoritesPage.jsx",
    "frontend/src/pages/user/UserRegistrationsPage.jsx",
    "frontend/src/pages/user/UserRegistrationArchivePage.jsx",
    "frontend/src/pages/user/UserNotificationsPage.jsx",

    "frontend/src/pages/organizer/OrganizerCabinetPage.jsx",
    "frontend/src/pages/organizer/OrganizerEventsPage.jsx",
    "frontend/src/pages/organizer/OrganizerEventsArchivePage.jsx",
    "frontend/src/pages/organizer/OrganizerNotificationsPage.jsx",
    "frontend/src/pages/organizer/RegisteredParticipantsPage.jsx",

    "frontend/src/pages/organizers/OrganizerPage.jsx",
    "frontend/src/pages/organizers/OrganizersListPage.jsx",

    "frontend/src/pages/admin/AdminCabinetPage.jsx",
    "frontend/src/pages/admin/AdminComplaintsPage.jsx",
    "frontend/src/pages/admin/AdminUsersPage.jsx",
    "frontend/src/pages/admin/AdminOrganizersPage.jsx",
]


IGNORED_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
    "uploads",
    "migrations",
}


TEXT_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".css",
    ".html",
    ".json",
    ".md",
    ".txt",
    ".env",
    ".example",
    ".ini",
    ".cfg",
    ".toml",
    ".yml",
    ".yaml",
    ".sql",
}


def is_ignored_path(path: Path) -> bool:
    for part in path.parts:
        if part in IGNORED_DIR_NAMES:
            return True

    return False


def is_text_file(path: Path) -> bool:
    if path.name == ".env":
        return True

    if path.name == ".env.example":
        return True

    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True

    return False


def read_file_content(path: Path) -> str:
    encodings = ["utf-8", "utf-8-sig", "cp1251"]

    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    return "[Файл не удалось прочитать как текстовый файл.]"


def collect_existing_project_files() -> list[Path]:
    result = []

    for path in PROJECT_ROOT.rglob("*"):
        if path.is_file() and not is_ignored_path(path) and is_text_file(path):
            result.append(path)

    return sorted(result, key=lambda item: item.as_posix().lower())


def write_section_line(output, text: str = "") -> None:
    output.write(f"{text}\n")


def write_file_listing(output, relative_path: str, absolute_path: Path) -> None:
    write_section_line(output)
    write_section_line(output, "=" * 120)
    write_section_line(output, f"ФАЙЛ: {relative_path}")
    write_section_line(output, "=" * 120)
    write_section_line(output)

    content = read_file_content(absolute_path)
    output.write(content)

    if content and not content.endswith("\n"):
        write_section_line(output)

    write_section_line(output)


def main() -> None:
    expected_paths = [PROJECT_ROOT / relative_path for relative_path in EXPECTED_FILES]

    existing_expected_files = []
    missing_expected_files = []

    for relative_path, absolute_path in zip(EXPECTED_FILES, expected_paths):
        if absolute_path.exists() and absolute_path.is_file():
            existing_expected_files.append(relative_path)
        else:
            missing_expected_files.append(relative_path)

    existing_all_files = collect_existing_project_files()

    expected_set = {Path(path).as_posix() for path in EXPECTED_FILES}

    extra_files = []

    for absolute_path in existing_all_files:
        relative_path = absolute_path.relative_to(PROJECT_ROOT).as_posix()

        if relative_path not in expected_set and relative_path != OUTPUT_FILE.name:
            extra_files.append(relative_path)

    with OUTPUT_FILE.open("w", encoding="utf-8") as output:
        write_section_line(output, "ПРОВЕРКА ФАЙЛОВ ПРОЕКТА POPCULTURE EVENTS")
        write_section_line(output, f"Дата проверки: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        write_section_line(output, f"Корень проекта: {PROJECT_ROOT}")
        write_section_line(output)

        write_section_line(output, "ИТОГ")
        write_section_line(output, "-" * 120)
        write_section_line(output, f"Ожидаемых файлов: {len(EXPECTED_FILES)}")
        write_section_line(output, f"Найдено ожидаемых файлов: {len(existing_expected_files)}")
        write_section_line(output, f"Не найдено ожидаемых файлов: {len(missing_expected_files)}")
        write_section_line(output, f"Дополнительных текстовых файлов проекта: {len(extra_files)}")
        write_section_line(output)

        write_section_line(output, "НАЙДЕННЫЕ ОЖИДАЕМЫЕ ФАЙЛЫ")
        write_section_line(output, "-" * 120)

        if existing_expected_files:
            for path in existing_expected_files:
                write_section_line(output, f"[OK] {path}")
        else:
            write_section_line(output, "Ожидаемые файлы не найдены.")

        write_section_line(output)

        write_section_line(output, "ОТСУТСТВУЮЩИЕ ОЖИДАЕМЫЕ ФАЙЛЫ")
        write_section_line(output, "-" * 120)

        if missing_expected_files:
            for path in missing_expected_files:
                write_section_line(output, f"[MISSING] {path}")
        else:
            write_section_line(output, "Все ожидаемые файлы найдены.")

        write_section_line(output)

        write_section_line(output, "ДОПОЛНИТЕЛЬНЫЕ ТЕКСТОВЫЕ ФАЙЛЫ")
        write_section_line(output, "-" * 120)

        if extra_files:
            for path in extra_files:
                write_section_line(output, f"[EXTRA] {path}")
        else:
            write_section_line(output, "Дополнительные текстовые файлы не найдены.")

        write_section_line(output)
        write_section_line(output, "#" * 120)
        write_section_line(output, "ЛИСТИНГ НАЙДЕННЫХ ОЖИДАЕМЫХ ФАЙЛОВ")
        write_section_line(output, "#" * 120)

        for relative_path in existing_expected_files:
            absolute_path = PROJECT_ROOT / relative_path
            write_file_listing(output, relative_path, absolute_path)

        write_section_line(output)
        write_section_line(output, "#" * 120)
        write_section_line(output, "ЛИСТИНГ ДОПОЛНИТЕЛЬНЫХ ТЕКСТОВЫХ ФАЙЛОВ")
        write_section_line(output, "#" * 120)

        for relative_path in extra_files:
            absolute_path = PROJECT_ROOT / relative_path
            write_file_listing(output, relative_path, absolute_path)

    print("Проверка завершена.")
    print(f"Ожидаемых файлов: {len(EXPECTED_FILES)}")
    print(f"Найдено ожидаемых файлов: {len(existing_expected_files)}")
    print(f"Не найдено ожидаемых файлов: {len(missing_expected_files)}")
    print(f"Дополнительных текстовых файлов: {len(extra_files)}")
    print(f"Результат сохранен в файл: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()