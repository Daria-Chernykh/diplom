import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { FieldError } from "../components/ui/FieldError.jsx";
import { useAuth } from "../store/AuthContext.jsx";
import {
  getBackendFieldErrors,
  hasErrors,
  validateEmailValue
} from "../utils/validation.js";

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [form, setForm] = useState({
    email: "",
    password: ""
  });

  const [fieldErrors, setFieldErrors] = useState({});
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  function validateForm() {
    const errors = {};

    const emailError = validateEmailValue(form.email);

    if (emailError) {
      errors.email = emailError;
    }

    if (!form.password) {
      errors.password = "Пароль обязателен для заполнения.";
    }

    setFieldErrors(errors);

    return !hasErrors(errors);
  }

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((current) => ({
      ...current,
      [name]: value
    }));

    setFieldErrors((current) => ({
      ...current,
      [name]: ""
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setError("");

    try {
      const response = await login(form);

      if (!response.user.legal_documents_accepted) {
        navigate("/legal-acceptance", { replace: true });
        return;
      }

      const fallbackPath = response.user.role === "admin"
        ? "/admin"
        : response.user.role === "organizer"
          ? "/organizer"
          : "/user";

      const from = location.state?.from?.pathname || fallbackPath;

      navigate(from, { replace: true });
    } catch (requestError) {
      setFieldErrors(getBackendFieldErrors(requestError));
      setError(requestError.message || "Не удалось выполнить вход.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="auth-card">
      <div>
        <h1>Вход</h1>
        <p className="muted">
          Войдите в учетную запись для регистрации на мероприятия и работы с личным кабинетом.
        </p>
      </div>

      {error && <div className="error-box">{error}</div>}

      <form className="form" onSubmit={handleSubmit} noValidate>
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

        <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Вход..." : "Войти"}
        </button>
      </form>

      <div className="auth-links">
        <span>Нет учетной записи?</span>
        <Link to="/register">Зарегистрироваться</Link>
      </div>
    </section>
  );
}