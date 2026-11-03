import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

let currentAccessToken = null;
let refreshPromise = null;

const publicPaths = [
  "/accounts/csrf/",
  "/accounts/login/",
  "/accounts/signup/",
  "/accounts/token/refresh/",
  "/accounts/logout/",
];

function getCookie(name) {
  const prefix = `${name}=`;
  const cookie = document.cookie
    .split(";")
    .map((item) => item.trim())
    .find((item) => item.startsWith(prefix));

  return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : null;
}

export function setClientAccessToken(token) {
  currentAccessToken = token || null;
}

export function clearClientSession() {
  currentAccessToken = null;

  ["accessToken", "refreshToken", "companyMobile", "user", "tenant"].forEach(
    (key) => localStorage.removeItem(key),
  );

  window.dispatchEvent(new Event("crm:session-expired"));
}

api.interceptors.request.use((config) => {
  const requestUrl = String(config.url || "");
  const isPublicRequest = publicPaths.some((path) =>
    requestUrl.includes(path),
  );
  const companyMobile = localStorage.getItem("companyMobile");
  const method = String(config.method || "get").toUpperCase();

  config.headers = config.headers || {};

  if (currentAccessToken && !isPublicRequest) {
    config.headers.Authorization = `Bearer ${currentAccessToken}`;
  } else {
    delete config.headers.Authorization;
  }

  if (
    companyMobile &&
    !requestUrl.includes("/accounts/login/") &&
    !requestUrl.includes("/accounts/signup/")
  ) {
    config.headers["X-Company-Mobile"] = companyMobile;
  }

  if (!["GET", "HEAD", "OPTIONS", "TRACE"].includes(method)) {
    const csrfToken = getCookie("csrftoken");

    if (csrfToken) {
      config.headers["X-CSRFToken"] = csrfToken;
    }
  }

  return config;
});

export function refreshAccessToken() {
  if (!refreshPromise) {
    refreshPromise = api
      .post("/accounts/token/refresh/", {}, { _skipAuthRefresh: true })
      .then((response) => {
        const access = response.data?.access;

        if (!access) {
          throw new Error("Refresh endpoint did not return an access token.");
        }

        setClientAccessToken(access);
        window.dispatchEvent(new Event("crm:token-refreshed"));

        return access;
      })
      .catch((error) => {
        clearClientSession();
        throw error;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }

  return refreshPromise;
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (!originalRequest || error.response?.status !== 401) {
      return Promise.reject(error);
    }

    const requestUrl = String(originalRequest.url || "");
    const isPublicRequest = publicPaths.some((path) =>
      requestUrl.includes(path),
    );

    if (isPublicRequest || originalRequest._skipAuthRefresh) {
      return Promise.reject(error);
    }

    if (originalRequest._retry) {
      clearClientSession();
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      const access = await refreshAccessToken();

      originalRequest.headers = originalRequest.headers || {};
      originalRequest.headers.Authorization = `Bearer ${access}`;

      return api(originalRequest);
    } catch (refreshError) {
      return Promise.reject(refreshError);
    }
  },
);

export default api;