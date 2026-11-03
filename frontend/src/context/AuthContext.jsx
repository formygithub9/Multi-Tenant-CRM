import { createContext, useContext, useEffect, useState } from "react";
import api, {
  clearClientSession,
  refreshAccessToken,
  setClientAccessToken,
} from "../api/client";

const AuthContext = createContext(null);

function readJson(key) {
  try {
    return JSON.parse(localStorage.getItem(key)) || null;
  } catch {
    return null;
  }
}

function clearStoredIdentity() {
  ["companyMobile", "user", "tenant"].forEach((key) =>
    localStorage.removeItem(key),
  );
}

export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(false);
  const [user, setUser] = useState(() => readJson("user"));
  const [tenant, setTenant] = useState(() => readJson("tenant"));
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    function handleSessionExpired() {
      setAccessToken(false);
      setUser(null);
      setTenant(null);
    }

    function handleTokenRefreshed() {
      setAccessToken(true);
    }

    window.addEventListener("crm:session-expired", handleSessionExpired);
    window.addEventListener("crm:token-refreshed", handleTokenRefreshed);

    return () => {
      window.removeEventListener("crm:session-expired", handleSessionExpired);
      window.removeEventListener("crm:token-refreshed", handleTokenRefreshed);
    };
  }, []);

  useEffect(() => {
    let active = true;

    async function initializeSession() {
      // Remove tokens saved by the old localStorage implementation.
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      setClientAccessToken(null);

      try {
        await api.get("/accounts/csrf/");

        const hasSavedIdentity = Boolean(
          localStorage.getItem("companyMobile") && readJson("user"),
        );

        if (hasSavedIdentity) {
          const access = await refreshAccessToken();

          if (active) {
            setAccessToken(Boolean(access));
          }
        } else {
          setClientAccessToken(null);

          if (active) {
            setAccessToken(false);
          }
        }
      } catch {
        clearStoredIdentity();
        setClientAccessToken(null);

        if (active) {
          setAccessToken(false);
          setUser(null);
          setTenant(null);
        }
      } finally {
        if (active) {
          setIsInitializing(false);
        }
      }
    }

    initializeSession();

    return () => {
      active = false;
    };
  }, []);

  function persistSession(result) {
    const access = result?.tokens?.access;
    const loggedInUser = result?.user;
    const loggedInTenant = result?.tenant;

    if (!access || !loggedInTenant?.company_mobile || !loggedInUser) {
      throw new Error(
        "Authentication response is missing user, tenant, or access token data.",
      );
    }

    // Access token stays in memory. Refresh token is set by Django as HttpOnly.
    setClientAccessToken(access);

    localStorage.setItem("companyMobile", loggedInTenant.company_mobile);
    localStorage.setItem("user", JSON.stringify(loggedInUser));
    localStorage.setItem("tenant", JSON.stringify(loggedInTenant));

    setAccessToken(true);
    setUser(loggedInUser);
    setTenant(loggedInTenant);

    return {
      user: loggedInUser,
      tenant: loggedInTenant,
      role: result?.role,
    };
  }

  async function login(credentials) {
    await api.get("/accounts/csrf/");

    const response = await api.post("/accounts/login/", {
      company_mobile: credentials.company_mobile,
      email: credentials.email,
      password: credentials.password,
    });

    return persistSession(response.data?.data);
  }

  async function signup(details) {
    await api.get("/accounts/csrf/");

    const response = await api.post("/accounts/signup/", details);

    return persistSession(response.data?.data);
  }

  async function logout() {
    const companyMobile = localStorage.getItem("companyMobile");

    const logoutRequest = api
      .post(
        "/accounts/logout/",
        {},
        {
          headers: companyMobile
            ? { "X-Company-Mobile": companyMobile }
            : {},
        },
      )
      .catch(() => null);

    clearClientSession();
    setAccessToken(false);
    setUser(null);
    setTenant(null);

    await logoutRequest;
  }

  const value = {
    accessToken: Boolean(accessToken),
    user,
    tenant,
    isInitializing,
    isAuthenticated: Boolean(accessToken),
    login,
    signup,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider.");
  }

  return context;
}