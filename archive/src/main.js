import { createApp } from "vue";
import App from "./App.vue";
import './assets/main.css';
import router from "./router"; // Import router

const app = createApp(App);
app.use(router); // Register router
app.mount("#app");
