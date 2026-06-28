<template>
  <div class="settings-page">
    <div class="page-header mb-4">
      <h2 class="page-title">系统设置</h2>
      <p class="page-subtitle text-muted">管理您的偏好和系统配置</p>
    </div>

    <div class="settings-grid">
      <!-- 个人资料设置 -->
      <div class="card settings-card profile-settings">
        <h3 class="section-title">个人资料</h3>
        
        <div class="profile-info mb-4">
          <div class="profile-avatar">U</div>
          <div class="profile-details">
            <div class="profile-name">{{ currentUser.name }}</div>
            <div class="profile-role badge-type">{{ getRoleName(currentUser.role) }}</div>
          </div>
          <button class="btn btn-secondary btn-sm ml-auto">更换头像</button>
        </div>
        
        <form @submit.prevent="saveProfile">
          <div class="form-group">
            <label class="form-label">用户名</label>
            <input type="text" class="input" v-model="profileForm.username" disabled>
            <p class="form-hint">登录使用的用户名不可修改</p>
          </div>
          <div class="form-group">
            <label class="form-label">显示名称</label>
            <input type="text" class="input" v-model="profileForm.name">
          </div>
          <div class="form-group">
            <label class="form-label">当前密码</label>
            <input type="password" class="input" v-model="profileForm.currentPassword" placeholder="修改密码时需提供当前密码">
          </div>
          <div class="form-group">
            <label class="form-label">新密码</label>
            <input type="password" class="input" v-model="profileForm.newPassword" placeholder="留空则不修改密码">
          </div>
          <div class="form-actions mt-4">
            <button type="submit" class="btn btn-primary" :disabled="isSaving">
              {{ isSaving ? '保存中...' : '保存更改' }}
            </button>
          </div>
        </form>
      </div>

      <!-- 系统偏好设置 -->
      <div class="card settings-card preference-settings">
        <h3 class="section-title">系统偏好</h3>
        
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-name">桌面通知</div>
            <div class="setting-desc">收到新消息或处理完成时发送桌面通知</div>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="preferences.notifications">
            <span class="slider round"></span>
          </label>
        </div>
        
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-name">自动滚动</div>
            <div class="setting-desc">问答时自动滚动到最新消息</div>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="preferences.autoScroll">
            <span class="slider round"></span>
          </label>
        </div>
        
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-name">显示引用文档</div>
            <div class="setting-desc">在回答下方自动显示引用来源</div>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="preferences.showReferences">
            <span class="slider round"></span>
          </label>
        </div>
        
        <div class="setting-item border-none">
          <div class="setting-info">
            <div class="setting-name">回答语言风格</div>
            <div class="setting-desc">调整AI回答的语气和专业程度</div>
          </div>
          <select class="input select-input mt-2 w-full" v-model="preferences.responseStyle">
            <option value="professional">专业严谨</option>
            <option value="friendly">亲切随和</option>
            <option value="concise">简明扼要</option>
          </select>
        </div>
        
        <div class="form-actions mt-4 pt-4 border-t">
          <button class="btn btn-danger-outline" @click="logout">退出登录</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import gsap from 'gsap'

const router = useRouter()

// 用户信息
const currentUser = ref({
  id: 1,
  username: 'customer_1',
  name: 'customer_1',
  role: 'customer'
})

// 表单数据
const profileForm = ref({
  username: '',
  name: '',
  currentPassword: '',
  newPassword: ''
})

// 偏好设置
const preferences = ref({
  notifications: true,
  autoScroll: true,
  showReferences: true,
  responseStyle: 'professional'
})

const isSaving = ref(false)

const getRoleName = (role: string) => {
  switch (role) {
    case 'customer': return '顾客'
    case 'beautician': return '美容师'
    case 'manager': return '管理员'
    default: return '用户'
  }
}

const loadUserData = () => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      const user = JSON.parse(userStr)
      currentUser.value = user
      profileForm.value.username = user.username
      profileForm.value.name = user.name || user.username
    } catch (e) {
      console.error('解析用户信息失败', e)
    }
  }
}

const saveProfile = () => {
  isSaving.value = true
  
  // 模拟保存请求
  setTimeout(() => {
    currentUser.value.name = profileForm.value.name
    
    // 更新本地存储
    const userStr = localStorage.getItem('user')
    if (userStr) {
      const user = JSON.parse(userStr)
      user.name = profileForm.value.name
      localStorage.setItem('user', JSON.stringify(user))
    }
    
    // 清空密码框
    profileForm.value.currentPassword = ''
    profileForm.value.newPassword = ''
    
    isSaving.value = false
    
    // 简单的成功提示，实际项目应使用toast组件
    alert('保存成功')
  }, 800)
}

// 退出登录
const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/')
}

onMounted(() => {
  loadUserData()
  
  nextTick(() => {
    const mm = gsap.matchMedia()
    mm.add('(prefers-reduced-motion: no-preference)', () => {
      gsap.from('.settings-card', {
        autoAlpha: 0,
        y: 10,
        duration: 0.7,
        stagger: 0.1,
        ease: 'power3.out',
        clearProps: 'transform'
      })
    })
  })
})
</script>

<style scoped>
.settings-page {
  padding: 0;
  max-width: 1000px;
  margin: 0 auto;
}

.page-title {
  font-family: var(--font-display);
  font-size: 1.5rem;
  color: var(--text);
  font-weight: 600;
  margin: 0 0 0.25rem 0;
}

.page-subtitle {
  font-size: 0.9rem;
  margin: 0;
}

.mb-4 { margin-bottom: 1.5rem; }
.mt-4 { margin-top: 1.5rem; }
.mt-2 { margin-top: 0.5rem; }
.ml-auto { margin-left: auto; }
.pt-4 { padding-top: 1rem; }
.w-full { width: 100%; }
.border-t { border-top: 1px solid var(--border-light); }
.text-muted { color: var(--text-muted); }

.settings-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.settings-card {
  padding: 2rem;
  align-self: flex-start;
}

.section-title {
  font-size: 1.1rem;
  color: var(--text);
  margin: 0 0 1.5rem 0;
  font-weight: 600;
  font-family: var(--font-display);
}

/* 个人资料信息 */
.profile-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-light);
}

.profile-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 600;
  font-family: var(--font-display);
}

.profile-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 0.25rem;
}

.badge-type {
  background-color: rgba(196, 136, 122, 0.1);
  padding: 0.2rem 0.6rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  color: var(--primary-dark);
  font-weight: 500;
  display: inline-block;
}

/* 表单样式 */
.form-group {
  margin-bottom: 1.25rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text);
  font-size: 0.9rem;
}

.form-hint {
  margin-top: 0.4rem;
  font-size: 0.8rem;
  color: var(--text-muted);
}

.input:disabled {
  background-color: var(--surface-alt);
  color: var(--text-muted);
  cursor: not-allowed;
}

/* 偏好设置项 */
.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid var(--border-light);
}

.setting-item.border-none {
  border-bottom: none;
  flex-direction: column;
  align-items: flex-start;
}

.setting-name {
  font-weight: 500;
  color: var(--text);
  font-size: 0.95rem;
  margin-bottom: 0.25rem;
}

.setting-desc {
  font-size: 0.8rem;
  color: var(--text-muted);
}

/* 开关组件 */
.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--border);
  transition: .3s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .3s;
}

input:checked + .slider {
  background-color: var(--primary);
}

input:focus + .slider {
  box-shadow: 0 0 1px var(--primary);
}

input:checked + .slider:before {
  transform: translateX(20px);
}

.slider.round {
  border-radius: 24px;
}

.slider.round:before {
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.select-input {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%238A7F79%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem top 50%;
  background-size: 0.65rem auto;
}

.btn-sm {
  padding: 0.4rem 0.8rem;
  font-size: 0.8rem;
}

.btn-danger-outline {
  background-color: transparent;
  color: var(--error);
  border: 1px solid var(--error);
  width: 100%;
}

.btn-danger-outline:hover {
  background-color: rgba(196, 112, 112, 0.05);
  border-color: var(--error);
}

@media (max-width: 900px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
}
</style>