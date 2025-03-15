<template>
  <aside class="sidebar">
    <nav>
      <ul>
        <li>
          <router-link to="/">🏠 Home</router-link>
        </li>
        <li>
          <router-link to="/bookshelf">📚 Bookshelf</router-link>
        </li>
        <li>
          <router-link to="/progress">📖 Reading Progress</router-link>
        </li>
        <li>
          <router-link to="/atoz">🔠 A-to-Z Challenge</router-link>
        </li>
      </ul>
    </nav>
  </aside>
</template>

<script>
export default {
  name: "SidebarNavigation"
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
  display: flex;
  flex-direction: column;
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
