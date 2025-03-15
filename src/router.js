import { createRouter, createWebHistory } from "vue-router";
import Home from "./views/Home.vue";
import Bookshelf from "./views/Bookshelf.vue";
import Progress from "./views/Progress.vue";
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
