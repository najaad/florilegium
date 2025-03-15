import { createRouter, createWebHistory } from "vue-router";
import HomeView from "./views/HomeView.vue";
import BookshelfView from "./views/BookshelfView.vue";
import ProgressView from "./views/ProgressView.vue";
import AtoZView from "./views/AtoZView.vue";

const routes = [
  { path: "/", component: HomeView },
  { path: "/bookshelf", component: BookshelfView },
  { path: "/progress", component: ProgressView },
  { path: "/atoz", component: AtoZView }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
