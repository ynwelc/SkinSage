<template>
  <div class="login-container">
    <!-- 装饰元素 -->
    <div class="decor-circle decor-1"></div>
    <div class="decor-circle decor-2"></div>

    <div class="login-card">
      <div class="login-header">
        <img src="/beauty-ai-logo.svg?v=2" alt="Beauty AI Logo" class="login-logo">
        <h1 class="login-title">SkinSage</h1>
        <p class="login-subtitle">智能美容咨询助手</p>
      </div>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="form-label" for="username">用户名</label>
          <input type="text" id="username" class="form-control" v-model="loginForm.username" placeholder="请输入用户名" required>
        </div>
        <div class="form-group">
          <label class="form-label" for="password">密码</label>
          <input type="password" id="password" class="form-control" v-model="loginForm.password" placeholder="请输入密码" required>
        </div>
        <div class="form-group">
        <label class="form-label">角色</label>
        <div class="radio-group">
          <label class="radio-item">
            <input type="radio" name="role" value="customer" v-model="loginForm.role" class="radio-input">
            <span>顾客</span>
          </label>
          <label class="radio-item">
            <input type="radio" name="role" value="beautician" v-model="loginForm.role" class="radio-input">
            <span>美容师</span>
          </label>
          <label class="radio-item">
            <input type="radio" name="role" value="manager" v-model="loginForm.role" class="radio-input">
            <span>管理员</span>
          </label>
        </div>
      </div>
      
      <!-- 错误提示 -->
      <div v-if="error" class="error-message mt-3">{{ error }}</div>
      
      <div class="btn-row mt-4">
        <button type="submit" class="btn btn-primary flex-1" :disabled="loading">
          <span v-if="loading">登录中...</span>
          <span v-else>登录</span>
        </button>
        <button type="button" class="btn btn-secondary">注册</button>
      </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import gsap from 'gsap'

const router = useRouter()

const loginForm = ref({
  username: '',
  password: '',
  role: 'customer'
})

const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // 简化登录流程，暂时跳过后端验证
    // 模拟登录成功，保存token和用户信息
    localStorage.setItem('token', 'mock-token-123456')
    localStorage.setItem('user', JSON.stringify({
      id: 1,
      username: loginForm.value.username,
      role: loginForm.value.role,
      name: loginForm.value.username
    }))
    
    // 跳转到主页面
    router.push('/app/qa')
  } catch (err: any) {
    console.error('Login error:', err)
    error.value = '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  nextTick(() => {
    const mm = gsap.matchMedia()
    mm.add('(prefers-reduced-motion: no-preference)', () => {
      gsap.from('.login-card', {
        autoAlpha: 0,
        y: 20,
        duration: 0.8,
        ease: 'power3.out',
        clearProps: 'transform'
      })
      gsap.from('.decor-circle', {
        autoAlpha: 0,
        scale: 0.9,
        duration: 0.8,
        stagger: 0.15,
        ease: 'power3.out',
        delay: 0.2,
        clearProps: 'transform'
      })
      gsap.from('.form-group, .btn-row', {
        autoAlpha: 0,
        y: 10,
        duration: 0.6,
        stagger: 0.08,
        delay: 0.2,
        ease: 'power3.out',
        clearProps: 'transform'
      })
    })
  })
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: linear-gradient(160deg, var(--bg) 0%, var(--surface-alt) 50%, #F3E8E2 100%);
  position: relative;
  overflow: hidden;
}

/* 装饰圆 */
.decor-circle {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
}

.decor-1 {
  width: 400px;
  height: 400px;
  top: -120px;
  right: -80px;
  background: radial-gradient(circle, rgba(196, 136, 122, 0.08) 0%, transparent 70%);
}

.decor-2 {
  width: 300px;
  height: 300px;
  bottom: -80px;
  left: -60px;
  background: radial-gradient(circle, rgba(139, 158, 139, 0.08) 0%, transparent 70%);
}

.login-card {
  background-color: var(--surface);
  border-radius: var(--radius-lg);
  padding: 2.5rem;
  box-shadow: var(--shadow-xl);
  border: 1px solid var(--border-light);
  max-width: 440px;
  width: 100%;
  position: relative;
  z-index: 1;
}

.login-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
}

.login-logo {
  width: 48px;
  height: 48px;
}

.login-title {
  margin-bottom: 0;
  font-family: var(--font-display);
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--primary);
  letter-spacing: -0.01em;
}

.login-subtitle {
  color: var(--text-muted);
  font-size: 0.875rem;
  font-weight: 400;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-label {
  display: block;
  margin-bottom: 0.4rem;
  font-weight: 600;
  color: var(--text);
  font-size: 0.875rem;
}

.form-control {
  width: 100%;
  padding: 0.7rem 0.875rem;
  background-color: var(--surface);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-family: var(--font-body);
  transition: all 0.25s var(--ease);
}

.form-control:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(196, 136, 122, 0.1);
}

.form-control::placeholder {
  color: var(--text-muted);
}

.radio-group {
  display: flex;
  gap: 1.5rem;
  margin-top: 0.5rem;
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 0.875rem;
  transition: color 0.2s;
}

.radio-item:hover {
  color: var(--text);
}

.radio-input {
  width: 1rem;
  height: 1rem;
  accent-color: var(--primary);
}

.btn-row {
  display: flex;
  gap: 0.75rem;
}

.flex-1 {
  flex: 1;
}

.mt-3 {
  margin-top: 0.75rem;
}

.mt-4 {
  margin-top: 1rem;
}

.error-message {
  color: var(--error);
  font-size: 0.875rem;
  font-weight: 500;
  background-color: rgba(196, 112, 112, 0.06);
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(196, 112, 112, 0.15);
}
</style>