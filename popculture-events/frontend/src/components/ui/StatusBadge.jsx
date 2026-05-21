export function StatusBadge({ type = "primary", children }) {
  return (
    <span className={`status ${type}`}>
      {children}
    </span>
  );
}