export function Modal({
  title,
  children,
  actions,
  onClose
}) {
  return (
    <div className="modal-backdrop" role="presentation">
      <section className="modal" role="dialog" aria-modal="true">
        <div className="modal-head">
          <h2>{title}</h2>

          <button
            className="modal-close"
            type="button"
            onClick={onClose}
            aria-label="Закрыть окно"
          >
            ×
          </button>
        </div>

        <div className="modal-body">
          {children}
        </div>

        {actions && (
          <div className="modal-actions">
            {actions}
          </div>
        )}
      </section>
    </div>
  );
}