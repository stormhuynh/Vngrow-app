<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

const email = ref("khachhang@minhlong.vn");
const password = ref("demo1234");

async function submit() {
  const ok = await auth.login(email.value, password.value);
  if (ok) {
    const redirect = (route.query.redirect as string) || "/shipments";
    router.push(redirect);
  }
}
</script>

<template>
  <div class="login-wrap">
    <form class="login-card" @submit.prevent="submit">
      <div class="brand">VNGROW</div>
      <div>
        <h1>Client Portal</h1>
        <div class="muted">Đăng nhập để quản lý lô hàng của bạn</div>
      </div>
      <div v-if="auth.error" class="error">{{ auth.error }}</div>
      <div class="field">
        <label>Email</label>
        <input class="control" type="email" v-model="email" required />
      </div>
      <div class="field">
        <label>Mật khẩu</label>
        <input class="control" type="password" v-model="password" required />
      </div>
      <button type="submit" :disabled="auth.loading">
        {{ auth.loading ? "Đang đăng nhập..." : "Đăng nhập" }}
      </button>
      <div class="muted">Demo: khachhang@minhlong.vn / demo1234</div>
    </form>
  </div>
</template>
