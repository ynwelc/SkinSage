<template>
  <div class="main-app">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="container navbar-content">
        <div class="logo">
          <img src="/beauty-ai-logo.svg?v=2" alt="Beauty AI Logo" class="ai-beauty-logo">
          <span class="logo-text">SkinSage</span>
        </div>
        <div class="nav-menu">
          <router-link to="/app/qa" class="nav-item" :class="{ active: currentRoute === 'qa' }" @click="changePage('qa')">问答</router-link>
          <router-link to="/app/history" class="nav-item" :class="{ active: currentRoute === 'history' }" @click="changePage('history')">对话历史</router-link>
          <router-link to="/app/docs" class="nav-item" :class="{ active: currentRoute === 'docs' }" @click="changePage('docs')">文档管理</router-link>
          <router-link to="/app/knowledge" class="nav-item" :class="{ active: currentRoute === 'knowledge' }" @click="changePage('knowledge')">知识库</router-link>
          <router-link to="/app/analytics" class="nav-item" :class="{ active: currentRoute === 'analytics' }" @click="changePage('analytics')">统计分析</router-link>
        </div>
        <div class="header-right">
          <div class="user-dropdown-container">
            <div class="user-avatar" @click="toggleUserMenu">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 1.25rem; height: 1.25rem;"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            </div>
            
            <div v-if="isUserMenuOpen" class="user-dropdown-menu" @click.stop>
              <div class="user-info">
                <div class="user-name">美容系统用户</div>
              </div>
              <div class="dropdown-divider"></div>
              <button class="dropdown-item text-error" @click="logout">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="dropdown-icon"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
                退出登录
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主内容区域 -->
    <div class="main-app-content">
      <!-- 侧边栏 -->
      <aside class="sidebar" :class="{ 'collapsed': isCollapsed }">
        <router-link to="/app/qa" class="sidebar-item" :class="{ active: currentRoute === 'qa' }" @click="changePage('qa')">
          <svg class="sidebar-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
          <span v-show="!isCollapsed">智能问答</span>
        </router-link>
        <router-link to="/app/history" class="sidebar-item" :class="{ active: currentRoute === 'history' }" @click="changePage('history')">
          <svg class="sidebar-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
          <span v-show="!isCollapsed">对话历史</span>
        </router-link>
        <router-link to="/app/docs" class="sidebar-item" :class="{ active: currentRoute === 'docs' }" @click="changePage('docs')">
          <svg class="sidebar-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
          <span v-show="!isCollapsed">文档管理</span>
        </router-link>
        <router-link to="/app/knowledge" class="sidebar-item" :class="{ active: currentRoute === 'knowledge' }" @click="changePage('knowledge')">
          <svg class="sidebar-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
          <span v-show="!isCollapsed">知识库管理</span>
        </router-link>
        <router-link to="/app/analytics" class="sidebar-item" :class="{ active: currentRoute === 'analytics' }" @click="changePage('analytics')">
          <svg class="sidebar-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
          <span v-show="!isCollapsed">统计分析</span>
        </router-link>
        <router-link to="/app/settings" class="sidebar-item" :class="{ active: currentRoute === 'settings' }" @click="changePage('settings')">
          <svg class="sidebar-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
          <span v-show="!isCollapsed">设置</span>
        </router-link>
        
        <div class="sidebar-spacer"></div>
        <button class="sidebar-toggle-btn" @click="toggleSidebar">
          <svg v-if="!isCollapsed" class="sidebar-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
          <svg v-else class="sidebar-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
          <span v-show="!isCollapsed">收起侧边栏</span>
        </button>
      </aside>

      <!-- 内容区域 -->
      <main class="main-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import gsap from 'gsap'

const route = useRoute()
const router = useRouter()
const currentRoute = ref('qa')
const isCollapsed = ref(false)
const isUserMenuOpen = ref(false)

const toggleUserMenu = (e: Event) => {
  e.stopPropagation()
  isUserMenuOpen.value = !isUserMenuOpen.value
}

const closeUserMenu = () => {
  isUserMenuOpen.value = false
}

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/')
}

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

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

onMounted(() => {
  nextTick(() => {
    const mm = gsap.matchMedia()
    mm.add('(prefers-reduced-motion: no-preference)', () => {
      gsap.from('.sidebar-item', {
        autoAlpha: 0,
        x: -8,
        duration: 0.6,
        stagger: 0.04,
        ease: 'power3.out',
        clearProps: 'all'
      })
      gsap.from('.nav-item', {
        autoAlpha: 0,
        y: -5,
        duration: 0.6,
        stagger: 0.04,
        ease: 'power3.out',
        delay: 0.1,
        clearProps: 'all'
      })
    })
  })
  document.addEventListener('click', closeUserMenu)
})

onUnmounted(() => {
  document.removeEventListener('click', closeUserMenu)
})
</script>

<style scoped>
/* 主应用布局 */
.main-app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--bg);
  color: var(--text);
}

/* 导航栏 */
.navbar {
  background-color: var(--surface);
  padding: 0;
  border-bottom: 1px solid var(--border-light);
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 1px 8px rgba(196, 136, 122, 0.06);
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1.5rem;
  height: 60px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-text {
  font-family: var(--font-display);
  font-size: 1.35rem;
  font-weight: 600;
  color: var(--primary);
  letter-spacing: -0.01em;
}

.ai-beauty-logo {
  width: 28px;
  height: 28px;
  transition: all 0.3s var(--ease);
}

.ai-beauty-logo:hover {
  transform: scale(1.08);
}

.nav-menu {
  display: flex;
  gap: 0.25rem;
  align-items: center;
}

.nav-item {
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.25s var(--ease);
  padding: 0.5rem 1rem;
  border-radius: var(--radius-sm);
  margin: 0 0.125rem;
  font-size: 0.9rem;
  position: relative;
}

.nav-item:hover {
  color: var(--primary);
  background-color: rgba(196, 136, 122, 0.06);
}

.nav-item.active {
  color: var(--primary-dark);
  font-weight: 600;
  background-color: transparent;
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0.75rem;
  right: 0.75rem;
  height: 2px;
  background: linear-gradient(90deg, var(--primary), var(--primary-light), var(--accent));
  border-radius: 1px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: #fff;
  cursor: pointer;
  transition: all 0.25s var(--ease);
  font-size: 0.85rem;
}

.user-avatar:hover {
  transform: scale(1.06);
  box-shadow: 0 3px 10px rgba(196, 136, 122, 0.25);
}

.user-dropdown-container {
  position: relative;
}

.user-dropdown-menu {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  width: 160px;
  background-color: var(--surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  padding: 0.5rem;
  z-index: 1000;
  animation: fadeInDown 0.2s var(--ease);
}

@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.user-info {
  padding: 0.5rem 0.75rem;
}

.user-name {
  font-weight: 600;
  color: var(--text);
  font-size: 0.9rem;
}

.dropdown-divider {
  height: 1px;
  background-color: var(--border-light);
  margin: 0.25rem 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  text-align: left;
  padding: 0.5rem 0.75rem;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.85rem;
  color: var(--text);
  transition: all 0.2s var(--ease);
}

.dropdown-item:hover {
  background-color: rgba(196, 136, 122, 0.08);
}

.dropdown-item.text-error {
  color: var(--error);
}
.dropdown-item.text-error:hover {
  background-color: rgba(196, 112, 112, 0.08);
}

.dropdown-icon {
  width: 1rem;
  height: 1rem;
}

/* 主内容区域 */
.main-app-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 侧边栏 */
.sidebar {
  width: 190px;
  background-color: var(--surface);
  border-right: 1px solid var(--border-light);
  padding: 1.25rem 0.75rem;
  height: calc(100vh - 60px);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  transition: width 0.35s cubic-bezier(0.2, 0, 0, 1), padding 0.35s cubic-bezier(0.2, 0, 0, 1);
}

.sidebar.collapsed {
  width: 64px;
  padding: 1.25rem 0.5rem;
}

.sidebar-spacer {
  flex: 1;
}

.sidebar-toggle-btn {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.75rem 0.6rem;
  color: var(--text-secondary);
  background: transparent;
  border: none;
  width: 100%;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.25s var(--ease);
  font-weight: 500;
  font-size: 0.85rem;
  white-space: nowrap;
  font-family: var(--font-body);
  margin-top: auto;
  flex-shrink: 0;
}

.sidebar-toggle-btn:hover {
  background-color: rgba(196, 136, 122, 0.08);
  color: var(--primary);
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.75rem 1rem;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: var(--radius-sm);
  transition: all 0.25s var(--ease);
  margin-bottom: 0.25rem;
  font-weight: 500;
  font-size: 0.9rem;
  white-space: nowrap;
  flex-shrink: 0;
}

.sidebar-icon-svg {
  width: 1.15rem;
  height: 1.15rem;
  stroke: currentColor;
  opacity: 0.8;
  transition: all 0.25s var(--ease);
}

.sidebar-item:hover .sidebar-icon-svg {
  opacity: 1;
  transform: scale(1.05);
}

.sidebar-item.active .sidebar-icon-svg {
  opacity: 1;
}

.sidebar-item:hover {
  background-color: rgba(196, 136, 122, 0.06);
  color: var(--primary);
}

.sidebar-item.active {
  background-color: rgba(196, 136, 122, 0.1);
  color: var(--primary-dark);
  font-weight: 600;
}

/* 内容区域 */
.main-content {
  margin-left: 0;
  padding: 1.5rem;
  min-height: calc(100vh - 60px);
  flex: 1;
  overflow-y: auto;
  background-color: var(--bg);
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
    box-shadow: 4px 0 20px rgba(196, 136, 122, 0.12);
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