<script setup lang="ts">
import { onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();

const comingSoon = [
  { label: "Pricing", key: "pricing" },
  { label: "Request for quotation", key: "rfq" },
  { label: "Document", key: "document" },
  { label: "AI Assistant", key: "ai" },
  { label: "Support", key: "support" },
];

const accountName = computed(
  () => auth.user?.customer?.name || auth.user?.full_name || "Khách hàng"
);
const accountCode = computed(() => auth.user?.customer?.code || "");

onMounted(() => {
  if (!auth.user) auth.fetchMe();
});

function logout() {
  auth.logout();
  router.push("/login");
}
</script>

<template>
  <div class="app">
    <aside class="side">
      <div class="brand">VNGROW</div>
      <div class="account">
        <b>{{ accountName }}</b>
        <span class="muted">{{ accountCode }}</span>
      </div>
      <nav class="nav">
        <router-link :to="{ name: 'shipments' }" class="nav-link">
          <span>Shipment</span>
        </router-link>
        <a
          v-for="item in comingSoon"
          :key="item.key"
          class="disabled"
          @click.prevent
        >
          <span>{{ item.label }}</span>
          <span class="tag soon">Sắp ra mắt</span>
        </a>
      </nav>
      <div style="margin-top: auto; padding: 12px">
        <button class="ghost small" style="width: 100%" @click="logout">
          Đăng xuất
        </button>
      </div>
    </aside>
    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.nav-link {
  padding: 9px 10px;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.nav-link.router-link-active {
  background: #111;
  color: #fff;
}
.nav-link:hover {
  background: #111;
  color: #fff;
}
.side {
  flex-direction: column;
}
</style>
