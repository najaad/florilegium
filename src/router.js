import { createRouter, createWebHistory } from "vue-router";
import Home from "./views/HomeView.vue";
import Bookshelf from "./views/BookshelfView.vue";
import Progress from "./views/ProgressView.vue";
import AtoZ from "./views/AtoZView.vue";

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
