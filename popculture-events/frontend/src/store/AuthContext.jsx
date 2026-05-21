import { createContext, useContext, useEffect, useMemo, useState } from "react";

import {
  acceptLegalDocuments,
  getCurrentAuthUser,
  loginUser,
  logoutUser,
  refreshAccessToken,
  registerUser
} from "../api/authApi.js";

import {
  getAccessToken,
  getRefreshToken,
  removeAuthTokens,
  setAuthTokens
} from "../api/httpClient.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isAuthLoading, setIsAuthLoading] = useState(true);

  const isAuthenticated = Boolean(user);
  const isBlocked = Boolean(user?.is_blocked);
  const isLegalAccepted = Boolean(user?.legal_documents_accepted);

  async function loadCurrentUser() {
    const accessToken = getAccessToken();

    if (!accessToken) {
      setUser(null);
      setIsAuthLoading(false);
      return;
    }

    setIsAuthLoading(true);

    try {
      const response = await getCurrentAuthUser();
      setUser(response.user);
    } catch (error) {
      try {
        const refreshToken = getRefreshToken();

        if (!refreshToken) {
          throw error;
        }

        const refreshResponse = await refreshAccessToken(refreshToken);

        setAuthTokens(refreshResponse.access_token, refreshResponse.refresh_token);
        setUser(refreshResponse.user);
      } catch {
        removeAuthTokens();
        setUser(null);
      }
    } finally {
      setIsAuthLoading(false);
    }
  }

  useEffect(() => {
    loadCurrentUser();
  }, []);

  async function login(payload) {
    const response = await loginUser(payload);

    setAuthTokens(response.access_token, response.refresh_token);
    setUser(response.user);

    return response;
  }

  async function register(payload) {
    const response = await registerUser(payload);

    setAuthTokens(response.access_token, response.refresh_token);
    setUser(response.user);

    return response;
  }

  async function logout() {
    try {
      await logoutUser();
    } finally {
      removeAuthTokens();
      setUser(null);
    }
  }

  async function acceptDocuments(payload) {
    const response = await acceptLegalDocuments(payload);

    setUser(response.user);

    return response;
  }

  function updateUser(nextUser) {
    setUser(nextUser);
  }

  const value = useMemo(
    () => ({
      user,
      isAuthLoading,
      isAuthenticated,
      isBlocked,
      isLegalAccepted,
      login,
      register,
      logout,
      acceptDocuments,
      reloadUser: loadCurrentUser,
      updateUser
    }),
    [user, isAuthLoading, isAuthenticated, isBlocked, isLegalAccepted]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth должен использоваться внутри AuthProvider.");
  }

  return context;
}