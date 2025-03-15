import { createRouter, createWebHistory } from "vue-router";
import Home from "./views/HomeView.vue";
import Bookshelf from "./views/BookshelfView.vue";
import Progress from "./views/ProgressView.vue";
import AtoZ from "./views/AtoZ.vue";

const routes = [
  { path: "/", component: Home },
  { path: "/bookshelf", component: Bookshelf },
  { path: "/progress", component: Progress },
  { path: "/atoz", component: AtoZ }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
