<template>
  <div class="login-container gradient-bg">
    <div class="login-card">
      <h1 class="login-title">Beauty AI Assistant</h1>
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
      
      <div class="flex gap-2 mt-4">
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

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
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.login-card {
  background-color: #1e293b;
  border-radius: 1rem;
  padding: 2.5rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  border: 1px solid #475569;
  max-width: 450px;
  width: 100%;
  backdrop-filter: blur(10px);
}

.login-title {
  text-align: center;
  margin-bottom: 2rem;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #f8fafc;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  background-color: #0f172a;
  color: #f8fafc;
  border: 1px solid #475569;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: all 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
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
}

.radio-input {
  width: 1rem;
  height: 1rem;
  accent-color: #6366f1;
}

.flex {
  display: flex;
}

.flex-1 {
  flex: 1;
}

.gap-2 {
  gap: 0.5rem;
}

.mt-3 {
  margin-top: 0.75rem;
}

.mt-4 {
  margin-top: 1rem;
}

.error-message {
  color: #ef4444;
  font-size: 0.875rem;
  font-weight: 500;
  background-color: rgba(239, 68, 68, 0.1);
  padding: 0.5rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(239, 68, 68, 0.3);
}
</style>