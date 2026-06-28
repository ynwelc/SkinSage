# Beauty Fonted

A Vue 3 + TypeScript + Vite SPA scaffold with a clean layout, routing, and a lightweight store. This project is suitable for UI dashboards, admin panels, and design-system experiments.

## Demo Video
<video src="./demo-video/demo.webm" controls width="100%"></video>

## Tech stack (high level)
- Vue 3 (with script setup SFCs)
- TypeScript
- Vite
- Vue Router 4
- Pinia
- Axios
- Marked

## Quick start
1) Install dependencies
   ```bash
   npm install
   ```
2) Run in development
   ```bash
   npm run dev
   ```
3) Build for production
   ```bash
   npm run build
   ```
4) Preview production build
   ```bash
   npm run preview
   ```
5) Run tests
   ```bash
   npm run test
   ```

## Project structure
- Root: package.json, README.md, index.html, vite.config.ts, tsconfig.json, etc.
- public/: static assets (e.g. beauty-ai-logo.svg)
- src/: application source code
  - main.ts: app entry
  - App.vue: root component
  - router/index.ts: app routes
  - store/index.ts: Pinia store
  - views/: page-level components (LoginPage.vue, DocsPage.vue, QA.vue, AnalyticsPage.vue, HistoryPage.vue, KnowledgePage.vue, etc.)
  - components/: reusable UI components (e.g. HelloWorld.vue)
  - assets/: fonts, images, styles
- style.css: global styles
- dist/: built assets after a production build
- PRD.md / prd_htmls/: documented requirements and HTML prototypes
- 后端.md: backend notes (Chinese)

## Scripts and usage
- dev: Start Vite dev server
- build: Type-check + Vite build
- preview: Serve production build locally
- test: Run Vitest tests

## Documentation and notes
- PRD.md contains product requirements
- 后端.md contains backend notes (Chinese)
- The repository includes a minimal README to get you started; extend it as needed.
