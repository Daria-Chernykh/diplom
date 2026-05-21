import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { FieldError } from "../components/ui/FieldError.jsx";
import { useAuth } from "../store/AuthContext.jsx";
import {
  getBackendFieldErrors,
  hasErrors,
  validateEmailValue,
  validatePasswordValue
} from "../utils/validation.js";

export function RegisterPage() {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    role: "user",
    organization_name: "",
    organization_description: "",
    user_agreement_accepted: false,
    privacy_policy_acknowledged: false,
    personal_data_consent_given: false
  });

  const [fieldErrors, setFieldErrors] = useState({});
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  function validateForm() {
    const errors = {};

    if (!form.full_name.trim()) {
      errors.full_name = "Имя пользователя обязательно для заполнения.";
    }

    const emailError = validateEmailValue(form.email);
    const passwordError = validatePasswordValue(form.password);

    if (emailError) {
      errors.email = emailError;
    }

    if (passwordError) {
      errors.password = passwordError;
    }

    if (form.role === "organizer" && !form.organization_name.trim()) {
      errors.organization_name = "Название организации обязательно для организатора.";
    }

    if (!form.user_agreement_accepted) {
      errors.user_agreement_accepted = "Необходимо принять Пользовательское соглашение.";
    }

    if (!form.privacy_policy_acknowledged) {
      errors.privacy_policy_acknowledged = "Необходимо подтвердить ознакомление с Политикой обработки персональных данных.";
    }

    if (!form.personal_data_consent_given) {
      errors.personal_data_consent_given = "Необходимо отдельно дать согласие на обработку персональных данных.";
    }

    setFieldErrors(errors);

    return !hasErrors(errors);
  }

  function handleChange(event) {
    const { name, value, type, checked } = event.target;

    setForm((current) => ({
      ...current,
      [name]: type === "checkbox" ? checked : value
    }));

    setFieldErrors((current) => ({
      ...current,
      [name]: ""
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (!validateForm()) {
      setError("Проверьте заполнение формы.");
      return;
    }

    setIsSubmitting(true);
    setError("");

    try {
      await register({
        full_name: form.full_name,
        email: form.email,
        password: form.password,
        role: form.role,
        organization_name: form.organization_name,
        organization_description: form.organization_description,
        user_agreement_accepted: form.user_agreement_accepted,
        privacy_policy_acknowledged: form.privacy_policy_acknowledged,
        personal_data_consent_given: form.personal_data_consent_given
      });

      navigate("/legal-acceptance", { replace: true });
    } catch (requestError) {
      setFieldErrors(getBackendFieldErrors(requestError));
      setError(requestError.message || "Не удалось выполнить регистрацию.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="auth-card">
      <div>
        <h1>Регистрация</h1>
        <p className="muted">Создайте учетную запись пользователя или организатора.</p>
      </div>

      {error && <div className="error-box">{error}</div>}

      <form className="form" onSubmit={handleSubmit} noValidate>
        <div className="field">
          <label htmlFor="full_name">Имя пользователя</label>
          <input
            className={fieldErrors.full_name ? "invalid" : ""}
            id="full_name"
            name="full_name"
            type="text"
            value={form.full_name}
            onChange={handleChange}
          />
          <FieldError message={fieldErrors.full_name} />
        </div>

        <div className="field">
          <label htmlFor="email">Электронная почта</label>
          <input
            className={fieldErrors.email ? "invalid" : ""}
            id="email"
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
          />
          <FieldError message={fieldErrors.email} />
        </div>

        <div className="field">
          <label htmlFor="password">Пароль</label>
          <input
            className={fieldErrors.password ? "invalid" : ""}
            id="password"
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
          />
          <FieldError message={fieldErrors.password} />
        </div>

        <div>
          <label className="field-label">Тип учетной записи</label>

          <div className="choice-group">
            <label className="choice-label">
              <input
                type="radio"
                name="role"
                value="user"
                checked={form.role === "user"}
                onChange={handleChange}
              />
              Пользователь
            </label>

            <label className="choice-label">
              <input
                type="radio"
                name="role"
                value="organizer"
                checked={form.role === "organizer"}
                onChange={handleChange}
              />
              Организатор
            </label>
          </div>
        </div>

        {form.role === "organizer" && (
          <>
            <div className="field">
              <label htmlFor="organization_name">Название организации</label>
              <input
                className={fieldErrors.organization_name ? "invalid" : ""}
                id="organization_name"
                name="organization_name"
                type="text"
                value={form.organization_name}
                onChange={handleChange}
              />
              <FieldError message={fieldErrors.organization_name} />
            </div>

            <div className="field">
              <label htmlFor="organization_description">Описание организации</label>
              <textarea
                id="organization_description"
                name="organization_description"
                value={form.organization_description}
                onChange={handleChange}
              />
            </div>
          </>
        )}

        <div className="legal-check-group">
          <label className="legal-check">
            <input
              type="checkbox"
              name="user_agreement_accepted"
              checked={form.user_agreement_accepted}
              onChange={handleChange}
            />
            <span>
              Я принимаю <Link to="/legal-documents">Пользовательское соглашение</Link>.
            </span>
          </label>
          <FieldError message={fieldErrors.user_agreement_accepted} />

          <label className="legal-check">
            <input
              type="checkbox"
              name="privacy_policy_acknowledged"
              checked={form.privacy_policy_acknowledged}
              onChange={handleChange}
            />
            <span>
              Я ознакомлен с <Link to="/legal-documents">Политикой обработки персональных данных</Link>.
            </span>
          </label>
          <FieldError message={fieldErrors.privacy_policy_acknowledged} />

          <label className="legal-check">
            <input
              type="checkbox"
              name="personal_data_consent_given"
              checked={form.personal_data_consent_given}
              onChange={handleChange}
            />
            <span>
              Я даю отдельное согласие на обработку персональных данных.
            </span>
          </label>
          <FieldError message={fieldErrors.personal_data_consent_given} />
        </div>

        <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Регистрация..." : "Зарегистрироваться"}
        </button>
      </form>

      <div className="auth-links">
        <span>Уже есть учетная запись?</span>
        <Link to="/login">Войти</Link>
      </div>
    </section>
  );
}
