# Beauty Fonted

一个基于 Vue 3 + TypeScript + Vite 的 SPA 脚手架，提供干净的布局、路由和轻量级状态管理。适合用于 UI 仪表盘、后台管理面板或设计系统实验。

## 技术栈（高水平）
- Vue 3（使用 script setup SFC）
- TypeScript
- Vite
- Vue Router 4
- Pinia
- Axios
- Marked

## 快速开始
1) 安装依赖
   ```bash
   npm install
   ```
2) 开发模式运行
   ```bash
   npm run dev
   ```
3) 生产构建
   ```bash
   npm run build
   ```
4) 预览生产构建
   ```bash
   npm run preview
   ```
5) 运行测试
   ```bash
   npm run test
   ```

## 项目结构
- 根目录：package.json, README.md, index.html, vite.config.ts, tsconfig.json 等
- public/：静态资源（例如 beauty-ai-logo.svg）
- src/：应用源代码
  - main.ts：应用入口
  - App.vue：根组件
  - router/index.ts：应用路由
  - store/index.ts：Pinia 状态管理
  - views/：页面级组件（LoginPage.vue, DocsPage.vue, QA.vue, AnalyticsPage.vue, HistoryPage.vue, KnowledgePage.vue 等）
  - components/：可复用 UI 组件（例如 HelloWorld.vue）
  - assets/：字体、图片、样式
- style.css：全局样式
- dist/：生产构建后的资源
- PRD.md / prd_htmls/：需求文档和 HTML 原型
- 后端.md：后端笔记（中文）

## 脚本和用法
- dev：启动 Vite 开发服务器
- build：类型检查 + Vite 构建
- preview：在本地提供生产构建服务
- test：运行 Vitest 测试

## 文档和备注
- PRD.md 包含产品需求
- 后端.md 包含后端笔记（中文）
- 该仓库包含一个最小化的 README 以帮助您入门；根据需要扩展它。