import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "../store/AuthContext.jsx";

export function ProtectedRoute({ children, roles = [] }) {
  const location = useLocation();
  const { user, isAuthLoading, isAuthenticated, isBlocked, isLegalAccepted } = useAuth();

  if (isAuthLoading) {
    return <div className="loading-screen">Проверка доступа...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (isBlocked) {
    return <Navigate to="/forbidden" replace />;
  }

  if (!isLegalAccepted && location.pathname !== "/legal-acceptance") {
    return <Navigate to="/legal-acceptance" replace state={{ from: location }} />;
  }

  if (roles.length > 0 && !roles.includes(user.role)) {
    return <Navigate to="/forbidden" replace />;
  }

  return children;
}