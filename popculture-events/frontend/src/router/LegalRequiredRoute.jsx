import { Navigate } from "react-router-dom";

import { useAuth } from "../store/AuthContext.jsx";

export function LegalRequiredRoute({ children }) {
  const { isAuthLoading, isAuthenticated, isBlocked, isLegalAccepted } = useAuth();

  if (isAuthLoading) {
    return <div className="loading-screen">Проверка доступа...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (isBlocked) {
    return <Navigate to="/forbidden" replace />;
  }

  if (isLegalAccepted) {
    return <Navigate to="/" replace />;
  }

  return children;
}