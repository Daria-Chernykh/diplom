import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { FieldError } from "../components/ui/FieldError.jsx";
import { getActualLegalDocuments } from "../api/legalApi.js";
import { useAuth } from "../store/AuthContext.jsx";

function getDocumentLabel(type) {
  if (type === "user_agreement") {
    return "Пользовательское соглашение";
  }

  if (type === "privacy_policy") {
    return "Политика обработки персональных данных";
  }

  if (type === "personal_data_consent") {
    return "Согласие на обработку персональных данных";
  }

  return type;
}

export function LegalAcceptancePage({ readonly = false }) {
  const navigate = useNavigate();
  const { user, acceptDocuments } = useAuth();

  const [documents, setDocuments] = useState([]);
  const [confirmations, setConfirmations] = useState({
    user_agreement_accepted: false,
    privacy_policy_acknowledged: false,
    personal_data_consent_given: false
  });
  const [fieldErrors, setFieldErrors] = useState({});
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function loadDocuments() {
    setIsLoading(true);
    setError("");

    try {
      const response = await getActualLegalDocuments();
      setDocuments(response.documents || []);
    } catch (requestError) {
      setError(requestError.message || "Не удалось загрузить правовые документы.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  function handleConfirmationChange(event) {
    const { name, checked } = event.target;

    setConfirmations((current) => ({
      ...current,
      [name]: checked
    }));

    setFieldErrors((current) => ({
      ...current,
      [name]: ""
    }));
  }

  function validateConfirmations() {
    const errors = {};

    if (!confirmations.user_agreement_accepted) {
      errors.user_agreement_accepted = "Необходимо принять Пользовательское соглашение.";
    }

    if (!confirmations.privacy_policy_acknowledged) {
      errors.privacy_policy_acknowledged = "Необходимо подтвердить ознакомление с Политикой обработки персональных данных.";
    }

    if (!confirmations.personal_data_consent_given) {
      errors.personal_data_consent_given = "Необходимо отдельно дать согласие на обработку персональных данных.";
    }

    setFieldErrors(errors);

    return Object.keys(errors).length === 0;
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (!validateConfirmations()) {
      setError("Для продолжения необходимо выполнить все правовые подтверждения.");
      return;
    }

    setIsSubmitting(true);
    setError("");
    setMessage("");

    try {
      const response = await acceptDocuments(confirmations);

      setMessage(response.message || "Правовые документы приняты.");
      navigate("/", { replace: true });
    } catch (requestError) {
      setError(requestError.message || "Не удалось принять правовые документы.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="page">
      <section className="title-box">
        <h1>Правовые документы</h1>
      </section>

      <section className="content single-content">
        {isLoading && <div className="loading-screen">Загрузка документов...</div>}

        {error && <div className="error-box">{error}</div>}
        {message && <div className="success-box">{message}</div>}

        {!isLoading && (
          <>
            {!readonly && user && !user.legal_documents_accepted && (
              <div className="note">
                Для продолжения работы необходимо выполнить отдельные подтверждения по актуальным правовым документам.
              </div>
            )}

            <div className="legal-documents-list">
              {documents.map((document) => (
                <article className="legal-document-card" key={document.id}>
                  <h2>{getDocumentLabel(document.document_type)}</h2>

                  <p className="muted">
                    Версия документа: {document.version}
                  </p>

                  <a
                    className="btn btn-outline"
                    href={`http://localhost:5000${document.download_url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Открыть документ
                  </a>
                </article>
              ))}
            </div>

            {!readonly && (
              <form className="form" onSubmit={handleSubmit} noValidate>
                <div className="legal-check-group">
                  <label className="legal-check">
                    <input
                      type="checkbox"
                      name="user_agreement_accepted"
                      checked={confirmations.user_agreement_accepted}
                      onChange={handleConfirmationChange}
                    />
                    <span>Я принимаю Пользовательское соглашение.</span>
                  </label>
                  <FieldError message={fieldErrors.user_agreement_accepted} />

                  <label className="legal-check">
                    <input
                      type="checkbox"
                      name="privacy_policy_acknowledged"
                      checked={confirmations.privacy_policy_acknowledged}
                      onChange={handleConfirmationChange}
                    />
                    <span>Я ознакомлен с Политикой обработки персональных данных.</span>
                  </label>
                  <FieldError message={fieldErrors.privacy_policy_acknowledged} />

                  <label className="legal-check">
                    <input
                      type="checkbox"
                      name="personal_data_consent_given"
                      checked={confirmations.personal_data_consent_given}
                      onChange={handleConfirmationChange}
                    />
                    <span>Я даю отдельное согласие на обработку персональных данных.</span>
                  </label>
                  <FieldError message={fieldErrors.personal_data_consent_given} />
                </div>

                <div className="form-actions">
                  <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
                    {isSubmitting ? "Сохранение..." : "Принять документы"}
                  </button>
                </div>
              </form>
            )}

            {readonly && (
              <div className="form-actions">
                <Link className="btn btn-outline" to="/">
                  На главную
                </Link>
              </div>
            )}
          </>
        )}
      </section>
    </main>
  );
}
