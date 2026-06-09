<template>
  <div class="docs-page">
    <div class="flex justify-between items-center mb-4">
      <h2>文档管理</h2>
      <div class="flex gap-2">
        <button class="btn btn-primary" @click="openUploadModal">
          <span>📄</span>
          <span>上传文档</span>
        </button>
        <button class="btn btn-secondary" @click="fetchDocuments" :disabled="isLoading">
          <span>🔄</span>
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
        <tbody>
          <tr v-for="document in documents" :key="document.id">
            <td>{{ document.id }}</td>
            <td>{{ document.title }}</td>
            <td>{{ document.file_type.toUpperCase() }}</td>
            <td>
              <span :style="{ color: document.status === 'completed' ? '#10b981' : '#f59e0b' }">
                {{ document.status === 'completed' ? '已完成' : document.status === 'processing' ? '处理中' : document.status }}
              </span>
            </td>
            <td>{{ formatFileSize(document.file_size) }}</td>
            <td>{{ formatDate(document.created_at) }}</td>
            <td>
              <div class="btn-group">
                <button class="btn btn-secondary btn-sm" @click="viewDocument(document)">
                  查看
                </button>
                <button class="btn btn-secondary btn-sm">
                  删除
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="documents.length === 0 && !isLoading">
            <td colspan="7" class="text-center">暂无文档</td>
          </tr>
          <tr v-if="isLoading">
            <td colspan="7" class="text-center">加载中...</td>
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
              <div>
                <strong>文件类型:</strong> {{ selectedDocument?.file_type.toUpperCase() }}
              </div>
              <div>
                <strong>文件大小:</strong> {{ formatFileSize(selectedDocument?.file_size || 0) }}
              </div>
              <div>
                <strong>状态:</strong> 
                <span :style="{ color: selectedDocument?.status === 'completed' ? '#10b981' : '#f59e0b' }">
                  {{ selectedDocument?.status === 'completed' ? '已完成' : selectedDocument?.status === 'processing' ? '处理中' : selectedDocument?.status }}
                </span>
              </div>
              <div>
                <strong>上传时间:</strong> {{ formatDate(selectedDocument?.created_at || '') }}
              </div>
            </div>
          </div>
          
          <div class="document-content">
            <h4>文档内容</h4>
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
      <div class="modal">
        <div class="modal-header">
          <h3>上传文档</h3>
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
                <label for="file-input" class="file-label">
                  <span v-if="!uploadFile">📁 点击选择文件</span>
                  <span v-else class="file-name">{{ uploadFile.name }}</span>
                </label>
              </div>
              <p class="form-hint">支持PDF、Word文档和Markdown文件</p>
            </div>

            <!-- 文档标题 -->
            <div class="form-group mb-4">
              <label class="form-label">文档标题</label>
              <input 
                type="text" 
                v-model="uploadTitle" 
                class="input" 
                placeholder="请输入文档标题（可选，默认使用文件名）"
              >
            </div>

            <!-- 文档分类 -->
            <div class="form-group mb-4">
              <label class="form-label">文档分类</label>
              <input 
                type="text" 
                v-model="uploadCategory" 
                class="input" 
                placeholder="请输入文档分类（可选）"
              >
            </div>

            <!-- 错误信息 -->
            <div v-if="uploadError" class="error-message mb-4">
              {{ uploadError }}
            </div>

            <!-- 提交按钮 -->
            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click="closeUploadModal">
                取消
              </button>
              <button type="submit" class="btn btn-primary" :disabled="uploadLoading">
                <span v-if="uploadLoading">上传中...</span>
                <span v-else>上传文档</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// 文档类型
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

// 文档分块类型
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
    minute: '2-digit',
    second: '2-digit'
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
    } else {
      console.error('获取文档详情失败')
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
    } else {
      console.error('获取文档分块失败')
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
    // 如果没有填写标题，默认使用文件名（不含扩展名）
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

  // 验证文件类型
  if (!validateFileType(uploadFile.value)) {
    uploadError.value = '只支持PDF、Word文档和Markdown文件'
    return
  }

  uploadLoading.value = true
  uploadError.value = ''

  try {
    const formData = new FormData()
    formData.append('file', uploadFile.value)
    if (uploadTitle.value) {
      formData.append('title', uploadTitle.value)
    }
    if (uploadCategory.value) {
      formData.append('category', uploadCategory.value)
    }

    const response = await fetch('http://localhost:8000/api/documents', {
      method: 'POST',
      body: formData
    })

    if (response.ok) {
      const data = await response.json()
      console.log('上传成功:', data)
      closeUploadModal()
      // 刷新文档列表
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

.flex {
  display: flex;
}

.justify-between {
  justify-content: space-between;
}

.items-center {
  align-items: center;
}

.mb-4 {
  margin-bottom: 1rem;
}

.gap-2 {
  gap: 0.5rem;
}

/* 表格样式 */
.table-container {
  overflow-x: auto;
  background-color: #1e293b;
  border-radius: 0.75rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  border: 1px solid #475569;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #475569;
}

.table th {
  background-color: #334155;
  font-weight: 600;
  color: #f8fafc;
}

.table tbody tr {
  transition: all 0.3s ease;
}

.table tbody tr:hover {
  background-color: #334155;
}

.table tbody tr:last-child td {
  border-bottom: none;
}

/* 按钮组 */
.btn-group {
  display: flex;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
}

/* 文本居中 */
.text-center {
  text-align: center;
}

/* 网格布局 */
.grid {
  display: grid;
}

.grid-cols-2 {
  grid-template-columns: repeat(2, 1fr);
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal {
  background-color: #1e293b;
  border-radius: 0.75rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  border: 1px solid #475569;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background-color: #334155;
  border-bottom: 1px solid #475569;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #f8fafc;
}

.modal-close {
  background: none;
  border: none;
  color: #cbd5e1;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background-color: #475569;
  color: #f8fafc;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

/* 文档信息样式 */
.document-info {
  background-color: #334155;
  padding: 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid #475569;
}

.document-info strong {
  color: #6366f1;
  margin-right: 0.5rem;
}

/* 文档内容样式 */
.document-content h4 {
  margin-bottom: 1rem;
  font-size: 1.125rem;
  font-weight: 600;
  color: #f8fafc;
}

.chunks-container {
  background-color: #334155;
  border-radius: 0.5rem;
  border: 1px solid #475569;
  overflow: hidden;
}

.chunk-item {
  border-bottom: 1px solid #475569;
  padding: 1.5rem;
}

.chunk-item:last-child {
  border-bottom: none;
}

.chunk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.chunk-index {
  font-weight: 600;
  color: #6366f1;
  font-size: 0.875rem;
}

.chunk-content {
  color: #e2e8f0;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.no-chunks {
  padding: 2rem;
  text-align: center;
  color: #94a3b8;
  font-style: italic;
}

/* 表单样式 */
.upload-form {
  width: 100%;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #f8fafc;
  font-size: 0.875rem;
}

.form-hint {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #94a3b8;
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
  display: block;
  padding: 1rem;
  background-color: #334155;
  border: 2px dashed #475569;
  border-radius: 0.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #cbd5e1;
  font-size: 0.875rem;
  position: relative;
  z-index: 1;
}

.file-label:hover {
  border-color: #6366f1;
  background-color: rgba(99, 102, 241, 0.1);
  color: #6366f1;
}

.file-name {
  color: #6366f1;
  font-weight: 500;
}

/* 错误信息样式 */
.error-message {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  padding: 0.75rem 1rem;
  border-radius: 0.375rem;
  border: 1px solid rgba(239, 68, 68, 0.3);
  font-size: 0.875rem;
}

/* 表单操作按钮 */
.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .grid-cols-2 {
    grid-template-columns: 1fr;
  }
  
  .modal {
    max-width: 100%;
    max-height: 100vh;
    border-radius: 0;
  }
  
  .modal-body {
    padding: 1rem;
  }
  
  .chunk-item {
    padding: 1rem;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .form-actions button {
    width: 100%;
  }
}
</style>