<template>
  <div class="settings-page">
    <h2>设置</h2>
    <div class="card mt-4">
      <h3>个人设置</h3>
      <div class="mt-3">
        <div class="form-group">
          <label class="form-label" for="setting-username">用户名</label>
          <input type="text" id="setting-username" class="form-control" v-model="settings.username">
        </div>
        <div class="form-group">
          <label class="form-label" for="setting-email">邮箱</label>
          <input type="email" id="setting-email" class="form-control" v-model="settings.email">
        </div>
        <div class="form-group">
          <label class="form-label" for="setting-password">密码</label>
          <input type="password" id="setting-password" class="form-control" v-model="settings.password" placeholder="请输入新密码">
        </div>
        <button class="btn btn-primary mt-3" @click="saveSettings">保存设置</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// 设置类型
interface Settings {
  username: string
  email: string
  password: string
}

const settings = ref<Settings>({
  username: 'user123',
  email: 'user@example.com',
  password: ''
})

const saveSettings = () => {
  // 调用后端API保存设置
  console.log('Settings saved:', settings.value)
}

const fetchSettings = () => {
  // 调用后端API获取设置
  // 目前使用模拟数据
}

onMounted(() => {
  fetchSettings()
})
</script>

<style scoped>
.settings-page {
  padding: 0;
}

.mt-4 {
  margin-top: 1rem;
}

.mt-3 {
  margin-top: 1rem;
}

/* 表单样式 */
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
</style>