<template>
  <aside :class="['sidebar', { collapsed: isCollapsed }]">
    <button class="toggle-btn" @click="toggleSidebar">
      {{ isCollapsed ? '➡' : '⬅' }}
    </button>
    <nav v-show="!isCollapsed">
      <ul>
        <li><router-link to="/">🖤 Home</router-link></li>
        <li><router-link to="/bookshelf">🧡 Bookshelf</router-link></li>
        <li><router-link to="/progress">🤎 Reading Progress</router-link></li>
        <li><router-link to="/atoz">💜 A-to-Z Challenge</router-link></li>
      </ul>
    </nav>
  </aside>
</template>

<script>
export default {
  name: "SidebarNavigation",
  data() {
    return {
      isCollapsed: false
    };
  },
  methods: {
    toggleSidebar() {
      this.isCollapsed = !this.isCollapsed;
    }
  }
};
</script>

<style scoped>
.sidebar {
  width: 250px;
  height: 100vh;
  background-color: var(--green-dark);
  color: white;
  padding: 20px;
  position: fixed;
  left: 0;
  top: 0;
  transition: width 0.3s ease-in-out;
}

.sidebar.collapsed {
  width: 60px;
}

.toggle-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  margin-bottom: 10px;
}

nav ul {
  list-style: none;
  padding: 0;
}

nav ul li {
  margin: 20px 0;
}

nav ul li a {
  color: white;
  text-decoration: none;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
}

nav ul li a:hover {
  color: var(--purple-light);
}
</style>
