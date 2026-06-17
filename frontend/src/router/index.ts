import { createRouter, createWebHistory } from "vue-router";
import { ACCESS_KEY } from "@/api";
import PortalLayout from "@/layouts/PortalLayout.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      name: "login",
      component: () => import("@/views/Login.vue"),
      meta: { public: true },
    },
    {
      path: "/",
      component: PortalLayout,
      children: [
        {
          path: "",
          redirect: { name: "shipments" },
        },
        {
          path: "shipments",
          name: "shipments",
          component: () => import("@/views/Shipments.vue"),
        },
        {
          path: "coming-soon/:module",
          name: "coming-soon",
          component: () => import("@/views/ComingSoon.vue"),
        },
      ],
    },
  ],
});

router.beforeEach((to) => {
  const authed = !!localStorage.getItem(ACCESS_KEY);
  if (!to.meta.public && !authed) {
    return { name: "login", query: { redirect: to.fullPath } };
  }
  if (to.name === "login" && authed) {
    return { name: "shipments" };
  }
  return true;
});

export default router;
