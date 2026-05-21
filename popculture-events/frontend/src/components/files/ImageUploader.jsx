import { useRef, useState } from "react";

import { buildFileUrl, deleteFile } from "../../api/filesApi.js";

export function ImageUploader({
  title,
  currentFile,
  uploadHandler,
  onUploaded,
  onDeleted,
  buttonText = "Загрузить изображение"
}) {
  const inputRef = useRef(null);

  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  function handleFileChange(event) {
    const file = event.target.files?.[0];

    setError("");
    setMessage("");

    if (!file) {
      setSelectedFile(null);
      setPreviewUrl("");
      return;
    }

    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      setError("Можно загружать только изображения JPEG, PNG или WEBP.");
      setSelectedFile(null);
      setPreviewUrl("");
      return;
    }

    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
  }

  async function handleUpload() {
    if (!selectedFile) {
      setError("Выберите изображение.");
      return;
    }

    setIsUploading(true);
    setError("");
    setMessage("");

    try {
      const response = await uploadHandler(selectedFile);
      setMessage(response.message || "Изображение загружено.");
      setSelectedFile(null);
      setPreviewUrl("");

      if (inputRef.current) {
        inputRef.current.value = "";
      }

      onUploaded(response.file);
    } catch (requestError) {
      setError(requestError.message || "Не удалось загрузить изображение.");
    } finally {
      setIsUploading(false);
    }
  }

  async function handleDelete() {
    if (!currentFile?.id) {
      return;
    }

    setIsUploading(true);
    setError("");
    setMessage("");

    try {
      await deleteFile(currentFile.id);
      setMessage("Изображение удалено.");
      onDeleted();
    } catch (requestError) {
      setError(requestError.message || "Не удалось удалить изображение.");
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <section className="image-uploader">
      <h3>{title}</h3>

      {currentFile && (
        <div className="image-preview-box">
          <img src={buildFileUrl(currentFile.file_url)} alt={currentFile.original_filename} />
        </div>
      )}

      {!currentFile && !previewUrl && (
        <div className="image-placeholder">
          Изображение не загружено
        </div>
      )}

      {previewUrl && (
        <div className="image-preview-box">
          <img src={previewUrl} alt="Предпросмотр" />
        </div>
      )}

      <div className="field">
        <label htmlFor={`image-uploader-${title}`}>Файл изображения</label>
        <input
          id={`image-uploader-${title}`}
          ref={inputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleFileChange}
          disabled={isUploading}
        />
        <span className="field-hint">Поддерживаются JPEG, PNG и WEBP. Размер проверяется на сервере.</span>
      </div>

      {error && <div className="error-box">{error}</div>}
      {message && <div className="success-box">{message}</div>}

      <div className="actions-row">
        <button
          className="btn btn-primary"
          type="button"
          onClick={handleUpload}
          disabled={isUploading || !selectedFile}
        >
          {isUploading ? "Загрузка..." : buttonText}
        </button>

        {currentFile && (
          <button
            className="btn btn-danger"
            type="button"
            onClick={handleDelete}
            disabled={isUploading}
          >
            Удалить изображение
          </button>
        )}
      </div>
    </section>
  );
}