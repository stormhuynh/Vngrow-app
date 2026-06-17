import { defineStore } from "pinia";
import { ref } from "vue";
import api, { ACCESS_KEY, REFRESH_KEY } from "@/api";
import type { User } from "@/types";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<User | null>(null);
  const loading = ref(false);
  const error = ref("");

  function isAuthenticated() {
    return !!localStorage.getItem(ACCESS_KEY);
  }

  async function login(email: string, password: string) {
    loading.value = true;
    error.value = "";
    try {
      const res = await api.post("/auth/login/", { email, password });
      localStorage.setItem(ACCESS_KEY, res.data.access);
      localStorage.setItem(REFRESH_KEY, res.data.refresh);
      user.value = res.data.user;
      return true;
    } catch (e: any) {
      error.value =
        e?.response?.data?.detail || "Email hoặc mật khẩu không đúng.";
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function fetchMe() {
    if (!isAuthenticated()) return;
    try {
      const res = await api.get("/auth/me/");
      user.value = res.data;
    } catch {
      logout();
    }
  }

  function logout() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
    user.value = null;
  }

  return { user, loading, error, isAuthenticated, login, fetchMe, logout };
});
