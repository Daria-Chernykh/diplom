import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <main className="page">
      <section className="card">
        <h1>Страница не найдена</h1>
        <p className="muted">Запрошенная страница отсутствует.</p>
        <div className="form-actions">
          <Link className="btn btn-primary" to="/">
            На главную
          </Link>
        </div>
      </section>
    </main>
  );
}