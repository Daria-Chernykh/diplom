from app.models import File


def file_to_dict(file: File) -> dict:
    return {
        "id": file.id,
        "uploader_id": file.uploader_id,
        "entity_type": file.entity_type,
        "entity_id": file.entity_id,
        "file_path": file.file_path,
        "file_url": f"/api/files/view/{file.file_path}",
        "original_filename": file.original_filename,
        "mime_type": file.mime_type,
    }