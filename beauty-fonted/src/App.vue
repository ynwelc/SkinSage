<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
/* ── Global utility styles ── */

/* 渐变背景 */
.gradient-bg {
  background: linear-gradient(135deg, var(--bg) 0%, var(--surface-alt) 100%);
}

.gradient-primary {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
}

.gradient-accent {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 50%, var(--accent) 100%);
}

/* 容器 */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* 卡片样式 */
.card {
  background-color: var(--surface);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-light);
  transition: all 0.25s var(--ease);
}

.card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-1px);
}

/* 按钮样式 */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.625rem 1.25rem;
  border-radius: var(--radius-sm);
  font-weight: 600;
  text-decoration: none;
  transition: all 0.25s var(--ease);
  border: 1px solid transparent;
  cursor: pointer;
  font-size: 0.875rem;
  gap: 0.5rem;
  font-family: var(--font-body);
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: #fff;
  border: none;
}

.btn-primary:hover {
  box-shadow: 0 4px 14px rgba(196, 136, 122, 0.35);
  transform: translateY(-1px);
}

.btn-secondary {
  background-color: var(--surface);
  color: var(--text);
  border: 1px solid var(--border);
}

.btn-secondary:hover {
  background-color: var(--surface-alt);
  border-color: var(--primary-light);
}

/* 输入框样式 */
.input {
  width: 100%;
  padding: 0.75rem;
  background-color: var(--surface);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-family: var(--font-body);
  transition: all 0.25s var(--ease);
}

.input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(196, 136, 122, 0.12);
}

.input::placeholder {
  color: var(--text-muted);
}

/* 隐藏类 */
.hidden {
  display: none;
}
</style>
