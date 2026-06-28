<template>
  <div class="docs-page">
    <div class="page-header flex justify-between items-center mb-4">
      <h2 class="page-title">文档管理</h2>
      <div class="flex gap-2">
        <button class="btn btn-primary" @click="openUploadModal">
          <span>✧</span>
          <span>上传文档</span>
        </button>
        <button class="btn btn-secondary" @click="fetchDocuments" :disabled="isLoading">
          <span>↻</span>
          <span>{{ isLoading ? '刷新中...' : '刷新' }}</span>
        </button>
      </div>
    </div>
    
    <div class="table-container">
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>标题</th>
            <th>类型</th>
            <th>状态</th>
            <th>大小</th>
            <th>上传时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody class="table-body">
          <tr v-for="document in documents" :key="document.id" class="table-row">
            <td class="text-muted">#{{ document.id }}</td>
            <td class="font-medium">{{ document.title }}</td>
            <td><span class="badge-type">{{ document.file_type.toUpperCase() }}</span></td>
            <td>
              <span class="status-indicator" :class="'status-' + document.status">
                {{ document.status === 'completed' ? '已完成' : document.status === 'processing' ? '处理中' : document.status }}
              </span>
            </td>
            <td class="text-muted">{{ formatFileSize(document.file_size) }}</td>
            <td class="text-muted">{{ formatDate(document.created_at) }}</td>
            <td>
              <div class="btn-group">
                <button class="btn btn-secondary btn-sm" @click="viewDocument(document)">
                  查看
                </button>
                <button class="btn btn-danger btn-sm">
                  删除
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="documents.length === 0 && !isLoading">
            <td colspan="7" class="text-center empty-state">暂无文档</td>
          </tr>
          <tr v-if="isLoading">
            <td colspan="7" class="text-center empty-state">加载中...</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 文档查看模态框 -->
    <div v-if="isViewModalOpen" class="modal-overlay" @click.self="isViewModalOpen = false">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ selectedDocument?.title }}</h3>
          <button class="modal-close" @click="isViewModalOpen = false">
            <span>×</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="document-info mb-4">
            <div class="grid grid-cols-2 gap-4">
              <div class="info-item">
                <span class="info-label">文件类型</span>
                <span class="info-value">{{ selectedDocument?.file_type.toUpperCase() }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">文件大小</span>
                <span class="info-value">{{ formatFileSize(selectedDocument?.file_size || 0) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">状态</span>
                <span class="status-indicator" :class="'status-' + selectedDocument?.status">
                  {{ selectedDocument?.status === 'completed' ? '已完成' : selectedDocument?.status === 'processing' ? '处理中' : selectedDocument?.status }}
                </span>
              </div>
              <div class="info-item">
                <span class="info-label">上传时间</span>
                <span class="info-value">{{ formatDate(selectedDocument?.created_at || '') }}</span>
              </div>
            </div>
          </div>
          
          <div class="document-content">
            <h4 class="section-title">文档内容解析</h4>
            <div class="chunks-container">
              <div v-for="chunk in documentChunks" :key="chunk.id" class="chunk-item">
                <div class="chunk-header">
                  <span class="chunk-index">分块 {{ chunk.chunk_index + 1 }}</span>
                </div>
                <div class="chunk-content">
                  {{ chunk.chunk_content }}
                </div>
              </div>
              <div v-if="documentChunks.length === 0" class="no-chunks">
                暂无文档内容
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 文档上传模态框 -->
    <div v-if="isUploadModalOpen" class="modal-overlay" @click.self="closeUploadModal">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h3>上传知识文档</h3>
          <button class="modal-close" @click="closeUploadModal">
            <span>×</span>
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="uploadDocument" class="upload-form">
            <!-- 文件选择 -->
            <div class="form-group mb-4">
              <label class="form-label">选择文件</label>
              <div class="file-input-container">
                <input 
                  type="file" 
                  id="file-input" 
                  class="file-input" 
                  accept=".pdf,.docx,.doc,.md,.markdown" 
                  @change="handleFileChange"
                >
                <label for="file-input" class="file-label" :class="{ 'has-file': uploadFile }">
                  <div class="upload-icon">📄</div>
                  <span v-if="!uploadFile">点击或拖拽选择文件</span>
                  <span v-else class="file-name">{{ uploadFile.name }}</span>
                </label>
              </div>
              <p class="form-hint">支持 PDF、Word 和 Markdown 格式文档</p>
            </div>

            <!-- 文档标题 -->
            <div class="form-group mb-4">
              <label class="form-label">文档标题</label>
              <input 
                type="text" 
                v-model="uploadTitle" 
                class="input" 
                placeholder="可选，默认使用文件名"
              >
            </div>

            <!-- 文档分类 -->
            <div class="form-group mb-4">
              <label class="form-label">文档分类</label>
              <input 
                type="text" 
                v-model="uploadCategory" 
                class="input" 
                placeholder="如：面部护理、仪器操作等（可选）"
              >
            </div>

            <!-- 错误信息 -->
            <div v-if="uploadError" class="error-message mb-4">
              {{ uploadError }}
            </div>

            <!-- 提交按钮 -->
            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click="closeUploadModal">取消</button>
              <button type="submit" class="btn btn-primary" :disabled="uploadLoading">
                <span v-if="uploadLoading">上传中...</span>
                <span v-else>确认上传</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import gsap from 'gsap'

// ... [原有接口定义保持不变] ...
interface Document {
  id: number
  title: string
  filename: string
  file_size: number
  file_type: string
  status: string
  created_by: number
  created_at: string
}

interface DocumentChunk {
  id: number
  document_id: number
  chunk_content: string
  chunk_index: number
  created_at: string
}

const documents = ref<Document[]>([])
const selectedDocument = ref<Document | null>(null)
const documentChunks = ref<DocumentChunk[]>([])
const isViewModalOpen = ref(false)
const isLoading = ref(false)

// 动画函数
const animateTableRows = () => {
  nextTick(() => {
    const mm = gsap.matchMedia()
    mm.add('(prefers-reduced-motion: no-preference)', () => {
      gsap.from('.file-item', {
        autoAlpha: 0,
        y: 10,
        duration: 0.6,
        stagger: 0.05,
        ease: 'power3.out',
        clearProps: 'all'
      })
    })
  })
}

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// 格式化日期
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取文档列表
const fetchDocuments = async () => {
  isLoading.value = true
  try {
    const response = await fetch('http://localhost:8000/api/documents')
    if (response.ok) {
      const data = await response.json()
      documents.value = data
      animateTableRows()
    } else {
      console.error('获取文档列表失败')
    }
  } catch (error) {
    console.error('获取文档列表出错:', error)
  } finally {
    isLoading.value = false
  }
}

// 获取文档详情
const fetchDocumentDetails = async (documentId: number) => {
  try {
    const response = await fetch(`http://localhost:8000/api/documents/${documentId}`)
    if (response.ok) {
      const data = await response.json()
      selectedDocument.value = data
    }
  } catch (error) {
    console.error('获取文档详情出错:', error)
  }
}

// 获取文档分块
const fetchDocumentChunks = async (documentId: number) => {
  try {
    const response = await fetch(`http://localhost:8000/api/documents/${documentId}/chunks`)
    if (response.ok) {
      const data = await response.json()
      documentChunks.value = data
    }
  } catch (error) {
    console.error('获取文档分块出错:', error)
  }
}

// 查看文档
const viewDocument = async (document: Document) => {
  selectedDocument.value = document
  await fetchDocumentChunks(document.id)
  isViewModalOpen.value = true
  
  nextTick(() => {
    gsap.from('.modal', {
      autoAlpha: 0,
      y: 20,
      scale: 0.98,
      duration: 0.4,
      ease: 'power2.out'
    })
  })
}

// 文档上传功能
const isUploadModalOpen = ref(false)
const uploadFile = ref<File | null>(null)
const uploadTitle = ref('')
const uploadCategory = ref('')
const uploadLoading = ref(false)
const uploadError = ref('')

// 打开上传模态框
const openUploadModal = () => {
  isUploadModalOpen.value = true
  uploadFile.value = null
  uploadTitle.value = ''
  uploadCategory.value = ''
  uploadError.value = ''
  
  nextTick(() => {
    gsap.from('.modal', {
      autoAlpha: 0,
      y: 20,
      scale: 0.98,
      duration: 0.4,
      ease: 'power2.out'
    })
  })
}

// 关闭上传模态框
const closeUploadModal = () => {
  isUploadModalOpen.value = false
}

// 选择文件
const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    uploadFile.value = target.files[0]
    if (!uploadTitle.value) {
      const filename = target.files[0].name
      uploadTitle.value = filename.substring(0, filename.lastIndexOf('.'))
    }
  }
}

// 验证文件类型
const validateFileType = (file: File): boolean => {
  const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword', 'text/markdown']
  const allowedExtensions = ['.pdf', '.docx', '.doc', '.md', '.markdown']
  const fileType = file.type
  const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))
  return allowedTypes.includes(fileType) || allowedExtensions.includes(fileExtension)
}

// 上传文档
const uploadDocument = async () => {
  if (!uploadFile.value) {
    uploadError.value = '请选择要上传的文件'
    return
  }

  if (!validateFileType(uploadFile.value)) {
    uploadError.value = '只支持PDF、Word文档和Markdown文件'
    return
  }

  uploadLoading.value = true
  uploadError.value = ''

  try {
    const formData = new FormData()
    formData.append('file', uploadFile.value)
    if (uploadTitle.value) formData.append('title', uploadTitle.value)
    if (uploadCategory.value) formData.append('category', uploadCategory.value)

    const response = await fetch('http://localhost:8000/api/documents', {
      method: 'POST',
      body: formData
    })

    if (response.ok) {
      closeUploadModal()
      fetchDocuments()
    } else {
      const errorData = await response.json()
      uploadError.value = errorData.msg || '上传失败'
    }
  } catch (error) {
    console.error('上传出错:', error)
    uploadError.value = '上传过程中发生错误'
  } finally {
    uploadLoading.value = false
  }
}

onMounted(() => {
  fetchDocuments()
})
</script>

<style scoped>
.docs-page {
  padding: 0;
}

.page-title {
  font-family: var(--font-display);
  font-size: 1.5rem;
  color: var(--text);
  font-weight: 600;
  margin: 0;
}

.flex { display: flex; }
.justify-between { justify-content: space-between; }
.items-center { align-items: center; }
.mb-4 { margin-bottom: 1.5rem; }
.gap-2 { gap: 0.75rem; }
.gap-4 { gap: 1rem; }

/* 表格样式 */
.table-container {
  overflow-x: auto;
  background-color: var(--surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 1rem 1.5rem;
  text-align: left;
  border-bottom: 1px solid var(--border-light);
  font-size: 0.9rem;
}

.table th {
  background-color: var(--surface-alt);
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.85rem;
  letter-spacing: 0.02em;
}

.table tbody tr {
  transition: background-color 0.2s var(--ease);
}

.table tbody tr:hover {
  background-color: var(--bg);
}

.table tbody tr:last-child td {
  border-bottom: none;
}

.text-muted { color: var(--text-muted); }
.font-medium { font-weight: 500; color: var(--text); }
.text-center { text-align: center; }

/* 状态标签 */
.badge-type {
  background-color: var(--bg);
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-family: var(--font-mono);
  color: var(--text-secondary);
  border: 1px solid var(--border);
}

.status-indicator {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.6rem;
  border-radius: var(--radius-pill);
  font-size: 0.75rem;
  font-weight: 500;
}

.status-completed {
  background-color: rgba(107, 158, 107, 0.1);
  color: var(--success);
}

.status-processing {
  background-color: rgba(212, 165, 74, 0.1);
  color: var(--warning);
}

.status-failed {
  background-color: rgba(196, 112, 112, 0.1);
  color: var(--error);
}

.empty-state {
  padding: 3rem;
  color: var(--text-muted);
  font-style: italic;
}

/* 按钮组 */
.btn-group {
  display: flex;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.4rem 0.8rem;
  font-size: 0.8rem;
}

.btn-danger {
  background-color: var(--surface);
  color: var(--error);
  border: 1px solid var(--border);
}

.btn-danger:hover {
  background-color: rgba(196, 112, 112, 0.05);
  border-color: var(--error);
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: rgba(61, 54, 50, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal {
  background-color: var(--surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  border: 1px solid var(--border-light);
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-sm {
  max-width: 500px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background-color: var(--surface-alt);
  border-bottom: 1px solid var(--border-light);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-family: var(--font-display);
  font-weight: 600;
  color: var(--primary-dark);
}

.modal-close {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  transition: all 0.2s var(--ease);
}

.modal-close:hover {
  background-color: var(--bg);
  color: var(--text);
}

.modal-body {
  padding: 2rem;
  overflow-y: auto;
  flex: 1;
}

/* 文档信息样式 */
.document-info {
  background-color: var(--surface-alt);
  padding: 1.25rem 1.5rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
}

.grid { display: grid; }
.grid-cols-2 { grid-template-columns: repeat(2, 1fr); }

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.info-value {
  font-size: 0.9rem;
  color: var(--text);
  font-weight: 500;
}

/* 文档内容样式 */
.section-title {
  margin-bottom: 1rem;
  font-size: 1.1rem;
  font-family: var(--font-display);
  font-weight: 600;
  color: var(--text);
  margin-top: 1.5rem;
}

.chunks-container {
  background-color: var(--bg);
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  overflow: hidden;
}

.chunk-item {
  border-bottom: 1px solid var(--border);
  padding: 1.25rem 1.5rem;
  background-color: var(--surface);
}

.chunk-item:last-child { border-bottom: none; }

.chunk-header {
  margin-bottom: 0.75rem;
}

.chunk-index {
  font-weight: 500;
  color: var(--primary);
  font-size: 0.85rem;
  background-color: rgba(196, 136, 122, 0.08);
  padding: 0.2rem 0.6rem;
  border-radius: var(--radius-sm);
}

.chunk-content {
  color: var(--text);
  line-height: 1.6;
  font-size: 0.9rem;
  white-space: pre-wrap;
}

.no-chunks {
  padding: 3rem;
  text-align: center;
  color: var(--text-muted);
  font-style: italic;
}

/* 表单样式 */
.upload-form { width: 100%; }
.form-group { margin-bottom: 1.5rem; }
.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text);
  font-size: 0.9rem;
}
.form-hint {
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: var(--text-muted);
}

/* 文件输入样式 */
.file-input-container {
  position: relative;
  margin-bottom: 0.5rem;
}

.file-input {
  position: absolute;
  opacity: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
  z-index: 2;
}

.file-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 2rem 1rem;
  background-color: var(--bg);
  border: 2px dashed var(--border);
  border-radius: var(--radius-md);
  text-align: center;
  cursor: pointer;
  transition: all 0.2s var(--ease);
  color: var(--text-secondary);
  font-size: 0.9rem;
  position: relative;
  z-index: 1;
}

.upload-icon {
  font-size: 2rem;
  opacity: 0.5;
  transition: transform 0.2s;
}

.file-label:hover {
  border-color: var(--primary-light);
  background-color: rgba(196, 136, 122, 0.02);
  color: var(--primary);
}

.file-label:hover .upload-icon {
  transform: translateY(-2px);
  opacity: 0.8;
}

.file-label.has-file {
  border-style: solid;
  border-color: var(--primary-light);
  background-color: var(--surface);
}

.file-name {
  color: var(--primary-dark);
  font-weight: 500;
}

/* 错误信息 */
.error-message {
  background-color: rgba(196, 112, 112, 0.06);
  color: var(--error);
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(196, 112, 112, 0.15);
  font-size: 0.875rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-light);
}

@media (max-width: 768px) {
  .grid-cols-2 { grid-template-columns: 1fr; }
  .modal { max-height: 100vh; border-radius: 0; }
  .modal-body { padding: 1.5rem; }
  .chunk-item { padding: 1rem; }
  .form-actions { flex-direction: column; }
  .form-actions button { width: 100%; }
}
</style>