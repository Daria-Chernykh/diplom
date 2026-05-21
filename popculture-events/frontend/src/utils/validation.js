export function trimValue(value) {
  if (value === null || value === undefined) {
    return "";
  }

  return String(value).trim();
}

export function isEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

export function isUrl(value) {
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:";
  } catch {
    return false;
  }
}

export function hasErrors(errors) {
  return Object.keys(errors).length > 0;
}

export function required(value, message) {
  return trimValue(value) ? "" : message;
}

export function maxLength(value, limit, message) {
  return trimValue(value).length <= limit ? "" : message;
}

export function minLength(value, limit, message) {
  return trimValue(value).length >= limit ? "" : message;
}

export function validateEmailValue(value) {
  if (!trimValue(value)) {
    return "Электронная почта обязательна для заполнения.";
  }

  if (!isEmail(trimValue(value))) {
    return "Введите корректную электронную почту.";
  }

  return "";
}

export function validatePasswordValue(value) {
  if (!value) {
    return "Пароль обязателен для заполнения.";
  }

  if (String(value).length < 6) {
    return "Пароль должен содержать не менее 6 символов.";
  }

  if (String(value).length > 128) {
    return "Пароль не должен превышать 128 символов.";
  }

  return "";
}

export function validateRatingValue(value) {
  if (value === "" || value === null || value === undefined) {
    return "Оценка обязательна для заполнения.";
  }

  const numberValue = Number(value);

  if (!Number.isInteger(numberValue) || numberValue < 0 || numberValue > 5) {
    return "Оценка должна быть целым числом от 0 до 5.";
  }

  return "";
}

export function validateFutureDateTime(value) {
  if (!value) {
    return "Дата и время обязательны для заполнения.";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Дата и время указаны в неверном формате.";
  }

  if (date <= new Date()) {
    return "Дата и время должны быть позже текущего времени.";
  }

  return "";
}

export function getBackendFieldErrors(error) {
  return error?.details || {};
}

export function getFieldError(errors, field) {
  return errors?.[field] || "";
}