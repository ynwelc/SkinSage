<template>
  <div class="main-app">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="container navbar-content">
        <div class="logo">
          <img src="/beauty-ai-logo.svg" alt="Beauty AI Logo" class="ai-beauty-logo">
          Beauty AI Assistant
        </div>
        <div class="nav-menu">
          <router-link to="/app/qa" class="nav-item" :class="{ active: currentRoute === 'qa' }" @click="changePage('qa')">问答</router-link>
          <router-link to="/app/history" class="nav-item" :class="{ active: currentRoute === 'history' }" @click="changePage('history')">对话历史</router-link>
          <router-link to="/app/docs" class="nav-item" :class="{ active: currentRoute === 'docs' }" @click="changePage('docs')">文档管理</router-link>
          <router-link to="/app/knowledge" class="nav-item" :class="{ active: currentRoute === 'knowledge' }" @click="changePage('knowledge')">知识库</router-link>
          <router-link to="/app/analytics" class="nav-item" :class="{ active: currentRoute === 'analytics' }" @click="changePage('analytics')">统计分析</router-link>
        </div>
        <div class="flex gap-3 items-center">
          <div class="user-avatar">U</div>
        </div>
      </div>
    </nav>

    <!-- 主内容区域 -->
    <div class="main-app-content">
      <!-- 侧边栏 -->
      <aside class="sidebar">
        <router-link to="/app/qa" class="sidebar-item" :class="{ active: currentRoute === 'qa' }" @click="changePage('qa')">
          <span>💬</span>
          <span>智能问答</span>
        </router-link>
        <router-link to="/app/history" class="sidebar-item" :class="{ active: currentRoute === 'history' }" @click="changePage('history')">
          <span>📚</span>
          <span>对话历史</span>
        </router-link>
        <router-link to="/app/docs" class="sidebar-item" :class="{ active: currentRoute === 'docs' }" @click="changePage('docs')">
          <span>📄</span>
          <span>文档管理</span>
        </router-link>
        <router-link to="/app/knowledge" class="sidebar-item" :class="{ active: currentRoute === 'knowledge' }" @click="changePage('knowledge')">
          <span>🧠</span>
          <span>知识库管理</span>
        </router-link>
        <router-link to="/app/analytics" class="sidebar-item" :class="{ active: currentRoute === 'analytics' }" @click="changePage('analytics')">
          <span>📊</span>
          <span>统计分析</span>
        </router-link>
        <router-link to="/app/settings" class="sidebar-item" :class="{ active: currentRoute === 'settings' }" @click="changePage('settings')">
          <span>⚙️</span>
          <span>设置</span>
        </router-link>
      </aside>

      <!-- 内容区域 -->
      <main class="main-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentRoute = ref('qa')

// 监听路由变化
watch(() => route.path, (newPath) => {
  const pathParts = newPath.split('/')
  if (pathParts.length > 2 && pathParts[2]) {
    currentRoute.value = pathParts[2]
  }
}, { immediate: true })

const changePage = (page: string) => {
  currentRoute.value = page
}
</script>

<style scoped>
/* 主应用布局 */
.main-app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #0f172a;
  color: #e2e8f0;
}

/* 导航栏 */
.navbar {
  background-color: #1e293b;
  padding: 0.75rem 0;
  border-bottom: 1px solid #334155;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.logo {
  font-size: 1.25rem;
  font-weight: 700;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.ai-beauty-logo {
  width: 28px;
  height: 28px;
  stroke: #6366f1;
  stroke-width: 2;
  transition: all 0.3s ease;
}

.ai-beauty-logo:hover {
  transform: scale(1.1);
  stroke: #818cf8;
}

.nav-menu {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.nav-item {
  color: #cbd5e1;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  margin: 0 0.25rem;
}

.nav-item:hover {
  color: #6366f1;
  background-color: rgba(99, 102, 241, 0.1);
}

.nav-item.active {
  color: #ffffff;
  background-color: #6366f1;
  font-weight: 600;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #6366f1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.user-avatar:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.3);
}

/* 主内容区域 */
.main-app-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 侧边栏 */
.sidebar {
  width: 160px;
  background-color: #1e293b;
  border-right: 1px solid #334155;
  padding: 1.5rem 0;
  height: calc(100vh - 60px);
  overflow-y: auto;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.25rem;
  color: #cbd5e1;
  text-decoration: none;
  border-radius: 0.5rem;
  transition: all 0.2s ease;
  margin-bottom: 0.25rem;
  font-weight: 500;
  font-size: 0.875rem;
}

.sidebar-item:hover {
  background-color: rgba(99, 102, 241, 0.1);
  color: #6366f1;
}

.sidebar-item.active {
  background-color: #6366f1;
  color: #ffffff;
  border-radius: 0.5rem;
  margin: 0 0.5rem 0.25rem 0.5rem;
  font-weight: 600;
}

/* 内容区域 */
.main-content {
  margin-left: 0;
  padding: 1.5rem;
  min-height: calc(100vh - 60px);
  flex: 1;
  overflow-y: auto;
  background-color: #111827;
}

/* 响应式布局 - 移动端 */
@media (max-width: 768px) {
  .nav-menu {
    display: none;
  }

  .sidebar {
    transform: translateX(-100%);
    z-index: 999;
    position: fixed;
    top: 60px;
    left: 0;
    width: 100%;
    max-width: 240px;
  }

  .sidebar.open {
    transform: translateX(0);
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.3);
  }

  .main-content {
    margin-left: 0;
    padding: 1rem;
  }

  .navbar-content {
    padding: 0 1rem;
  }
}

/* 工具类 */
.flex {
  display: flex;
}

.items-center {
  align-items: center;
}

.justify-between {
  justify-content: space-between;
}

.gap-3 {
  gap: 0.75rem;
}
</style>