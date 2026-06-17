import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE || "http://localhost:8000";

const api = axios.create({
  baseURL: `${baseURL}/api`,
});

export const ACCESS_KEY = "vngrow_access";
export const REFRESH_KEY = "vngrow_refresh";

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(ACCESS_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let isRefreshing = false;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (
      error.response &&
      error.response.status === 401 &&
      !original._retry &&
      localStorage.getItem(REFRESH_KEY)
    ) {
      original._retry = true;
      if (!isRefreshing) {
        isRefreshing = true;
        try {
          const refresh = localStorage.getItem(REFRESH_KEY);
          const res = await axios.post(`${baseURL}/api/auth/refresh/`, {
            refresh,
          });
          localStorage.setItem(ACCESS_KEY, res.data.access);
          isRefreshing = false;
        } catch (refreshError) {
          isRefreshing = false;
          localStorage.removeItem(ACCESS_KEY);
          localStorage.removeItem(REFRESH_KEY);
          window.location.href = "/login";
          return Promise.reject(refreshError);
        }
      }
      original.headers.Authorization = `Bearer ${localStorage.getItem(
        ACCESS_KEY
      )}`;
      return api(original);
    }
    return Promise.reject(error);
  }
);

export const fileBase = baseURL;
export default api;
