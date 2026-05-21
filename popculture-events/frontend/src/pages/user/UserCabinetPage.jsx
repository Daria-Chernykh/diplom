import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  changeCurrentUserPassword,
  getCurrentUserProfile,
  updateCurrentUserProfile
} from "../../api/usersApi.js";
import { uploadUserProfileImage } from "../../api/filesApi.js";
import { ImageUploader } from "../../components/files/ImageUploader.jsx";

export function UserCabinetPage() {
  const [user, setUser] = useState(null);
  const [profileImage, setProfileImage] = useState(null);

  const [profileForm, setProfileForm] = useState({
    full_name: ""
  });

  const [passwordForm, setPasswordForm] = useState({
    current_password: "",
    new_password: ""
  });

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [isSavingPassword, setIsSavingPassword] = useState(false);

  async function loadProfile() {
    setIsLoading(true);
    setError("");

    try {
      const response = await getCurrentUserProfile();
      const loadedUser = response.user;

      setUser(loadedUser);
      setProfileImage(loadedUser.profile_image || null);

      setProfileForm({
        full_name: loadedUser.full_name || ""
      });
    } catch (requestError) {
      setError(requestError.message || "Не удалось загрузить профиль.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadProfile();
  }, []);

  function handleProfileChange(event) {
    const { name, value } = event.target;

    setProfileForm((current) => ({
      ...current,
      [name]: value
    }));
  }

  function handlePasswordChange(event) {
    const { name, value } = event.target;

    setPasswordForm((current) => ({
      ...current,
      [name]: value
    }));
  }

  async function handleProfileSubmit(event) {
    event.preventDefault();

    setIsSavingProfile(true);
    setError("");
    setMessage("");

    try {
      const response = await updateCurrentUserProfile(profileForm);
      const updatedUser = response.user;

      setUser(updatedUser);
      setProfileImage(updatedUser.profile_image || profileImage);
      setMessage(response.message || "Профиль обновлен.");
    } catch (requestError) {
      setError(requestError.message || "Не удалось обновить профиль.");
    } finally {
      setIsSavingProfile(false);
    }
  }

  async function handlePasswordSubmit(event) {
    event.preventDefault();

    setIsSavingPassword(true);
    setError("");
    setMessage("");

    try {
      const response = await changeCurrentUserPassword(passwordForm);

      setPasswordForm({
        current_password: "",
        new_password: ""
      });

      setMessage(response.message || "Пароль изменен.");
    } catch (requestError) {
      setError(requestError.message || "Не удалось изменить пароль.");
    } finally {
      setIsSavingPassword(false);
    }
  }

  if (isLoading) {
    return <div className="loading-screen">Загрузка профиля...</div>;
  }

  if (error && !user) {
    return (
      <main className="page">
        <section className="card">
          <h1>Профиль недоступен</h1>
          <div className="error-box">{error}</div>
        </section>
      </main>
    );
  }

  return (
    <main className="page">
      <section className="title-box">
        <h1>Личный кабинет пользователя</h1>
      </section>

      <section className="main">
        <aside className="sidebar">
          <h2>Разделы</h2>

          <div className="menu">
            <Link className="menu-item active" to="/user">
              <div>Профиль</div>
            </Link>

            <Link className="menu-item" to="/user/registrations">
              <div>Мои регистрации</div>
            </Link>

            <Link className="menu-item" to="/user/favorites">
              <div>Избранное</div>
            </Link>

            <Link className="menu-item" to="/user/notifications">
              <div>Уведомления</div>
            </Link>

            <Link className="menu-item" to="/user/registrations/archive">
              <div>Архив регистраций</div>
            </Link>
          </div>
        </aside>

        <section className="content">
          <div className="section-head">
            <div>
              <h2>Редактирование профиля</h2>
              <p className="muted">Данные пользователя используются для регистрации на мероприятия.</p>
            </div>
          </div>

          {error && <div className="error-box">{error}</div>}
          {message && <div className="success-box">{message}</div>}

          <ImageUploader
            title="Изображение профиля"
            currentFile={profileImage}
            uploadHandler={uploadUserProfileImage}
            onUploaded={(file) => setProfileImage(file)}
            onDeleted={() => setProfileImage(null)}
            buttonText="Загрузить изображение профиля"
          />

          <form className="form" onSubmit={handleProfileSubmit}>
            <section className="form-section">
              <h3>Основные данные</h3>

              <div className="field">
                <label htmlFor="full_name">Имя пользователя</label>
                <input
                  id="full_name"
                  name="full_name"
                  type="text"
                  value={profileForm.full_name}
                  onChange={handleProfileChange}
                  required
                />
              </div>

              <div className="disabled-field">
                <strong>Электронная почта:</strong>
                <br />
                {user.email}
              </div>

              <div className="disabled-field">
                <strong>Роль:</strong>
                <br />
                {user.role === "admin" && "Администратор"}
                {user.role === "organizer" && "Организатор"}
                {user.role === "user" && "Пользователь"}
              </div>
            </section>

            <div className="form-actions">
              <button className="btn btn-primary" type="submit" disabled={isSavingProfile}>
                {isSavingProfile ? "Сохранение..." : "Сохранить профиль"}
              </button>
            </div>
          </form>

          <form className="form" onSubmit={handlePasswordSubmit}>
            <section className="form-section">
              <h3>Изменение пароля</h3>

              <div className="field">
                <label htmlFor="current_password">Текущий пароль</label>
                <input
                  id="current_password"
                  name="current_password"
                  type="password"
                  value={passwordForm.current_password}
                  onChange={handlePasswordChange}
                  required
                />
              </div>

              <div className="field">
                <label htmlFor="new_password">Новый пароль</label>
                <input
                  id="new_password"
                  name="new_password"
                  type="password"
                  value={passwordForm.new_password}
                  onChange={handlePasswordChange}
                  minLength={6}
                  required
                />
              </div>
            </section>

            <div className="form-actions">
              <button className="btn btn-primary" type="submit" disabled={isSavingPassword}>
                {isSavingPassword ? "Сохранение..." : "Изменить пароль"}
              </button>
            </div>
          </form>
        </section>
      </section>
    </main>
  );
}