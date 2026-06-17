<script setup lang="ts">
import { useRoute } from "vue-router";
const route = useRoute();
</script>

<template>
  <div class="content">
    <div class="head">
      <h1>{{ route.params.module || "Tính năng" }}</h1>
    </div>
    <div class="empty">Module này đang được phát triển — sắp ra mắt.</div>
  </div>
</template>
