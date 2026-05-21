import { Navigate } from "react-router-dom";

import { useAuth } from "../store/AuthContext.jsx";

export function PublicOnlyRoute({ children }) {
  const { isAuthLoading, isAuthenticated, isBlocked, isLegalAccepted } = useAuth();

  if (isAuthLoading) {
    return <div className="loading-screen">Загрузка...</div>;
  }

  if (!isAuthenticated) {
    return children;
  }

  if (isBlocked) {
    return <Navigate to="/forbidden" replace />;
  }

  if (!isLegalAccepted) {
    return <Navigate to="/legal-acceptance" replace />;
  }

  return <Navigate to="/" replace />;
}