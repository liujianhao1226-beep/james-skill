# James Skill Collection

This repository contains custom skills for Claude Code / OpenClaw agents, covering development, testing, DevOps, productivity, and more.

## Skills (85 total)

### 🧪 Testing & QA
- `doc-based-testcase-generator` — 从 PRD/接口文档生成结构化测试用例表格
- `prd-to-xmind-testcases` — 从 PRD 生成可导入 XMind 的测试用例思维导图
- `test-driven-development` — TDD 工作流
- `systematic-debugging` — 系统化调试方法论
- `generate-tests` — 生成单元测试和集成测试

### 🔍 Code Review & Analysis
- `code-review` — 代码质量、安全和最佳实践审查
- `deep-research` — 深度研究模式
- `receiving-code-review` / `requesting-code-review` — 审查协作

### 🛠️ Development
- `debug` — 调试与根因分析
- `refactor` — 重构（可读性、可维护性、性能）
- `generate-docs` — 生成文档、注释、README
- `codex-orchestrator` — Codex 编码 agent 编排
- `subagent-driven-development` — 子 agent 开发模式

### 🎨 Frontend & Design
- `frontend-design` — 前端界面设计
- `web-design-guidelines` — Web UI 设计规范审查
- `canvas-design` — 设计类海报/艺术作品
- `algorithmic-art` — 生成式算法艺术
- `interaction-design` — 交互动效与微交互
- `brand-guidelines` — Anthropic 品牌色彩/字体
- `theme-factory` — 幻灯片/文档主题套用

### 📄 Documents & Content
- `docx` — Word 文档读写
- `pdf` — PDF 处理
- `pptx` — PowerPoint 演示文稿
- `xlsx` — Excel 表格处理
- `copywriting` — 营销文案撰写
- `content-strategy` — 内容策略规划
- `internal-comms` — 内部通讯写作
- `doc-coauthoring` — 协同撰写文档工作流

### 🤖 AI & Agents
- `mcp-builder` — 构建 MCP (Model Context Protocol) 服务器
- `claude-api` — Claude API / SDK 开发指南
- `openclaw` — OpenClaw 框架操作手册
- `agent-reach` — Agent 工具配置（Twitter、Reddit、GitHub 等）
- `agent-browser` — 浏览器自动化
- `superpowers` — Superpowers agentic 开发方法论
- `using-superpowers` — Superpowers 使用指南
- `codex-orchestrator` — Codex agent 编排

### 🌐 Web & Data
- `webapp-testing` — Web 应用测试（Playwright）
- `web-artifacts-builder` — 复杂 Web 界面 artifact 构建
- `web-reader` / `search-skill` — 网页读取与搜索
- `ai-daily-news` — AI 每日新闻抓取
- `technews` — 科技新闻聚合
- `miniflux-news` — Miniflux RSS 阅读
- `weather` — 天气查询

### 📊 Productivity & Workflow
- `brainstorming` — 头脑风暴引导
- `workflow-patterns` — Conductor TDD 工作流
- `context-driven-development` — 上下文驱动开发
- `finishing-a-development-branch` — 分支完成与合并流程
- `executing-plans` — 执行计划管理
- `writing-plans` — 写作计划
- `verification-before-completion` — 完成前验证

### 🧠 Memory & Knowledge
- `memory-system-v2` — 语义记忆系统
- `skill-from-github` — 从 GitHub 提取 skill
- `skill-from-masters` — 向高手学习 skill
- `skill-from-notebook` — 从笔记提取 skill
- `find-skills` — 发现和安装新 skill
- `use-findskill` — 使用 find-skills 工具

### 📈 Marketing & SEO
- `marketing-ideas` — 营销创意（139 种方法）
- `marketing-psychology` — 营销心理学（70+ 心理模型）
- `programmatic-seo` — 规模化 SEO 页面构建
- `seo-audit` — SEO 健康检查
- `pollinations` — AI 图像生成

### 🔧 Tools & Infrastructure
- `comfyui-runner` — ComfyUI 实例管理
- `mcp-builder` — MCP 服务器构建
- `python-design-patterns` — Python 设计模式
- `async-python-patterns` — Python 异步编程
- `python-project-structure` — Python 项目结构
- `typescript-advanced-types` — TypeScript 高级类型
- `react-best-practices` — React/Next.js 性能优化
- `composition-patterns` — React 组合模式
- `error-handling-patterns` — 错误处理模式
- `prompt-engineering-patterns` — 提示工程模式
- `llm-evaluation` — LLM 应用评估策略
- `rag-implementation` — RAG 系统实现
- `giphy` — GIF 发送
- `slack-gif-creator` — Slack GIF 制作
- `weather` — 天气

### 📁 Cloud & Platform
- `feishu-doc` — 飞书文档读写
- `feishu-drive` — 飞书云存储
- `feishu-perm` — 飞书权限管理
- `feishu-wiki` — 飞书知识库

## Installation

### For Claude Code
Copy skill folders to `~/.claude/skills/`:
```bash
cp -r <skill-name> ~/.claude/skills/
```

### For OpenClaw
Skills are stored in `~/.openclaw/skills/` (auto-discovered):
```bash
~/.openclaw/skills/<skill-name>/
```

## Usage

Each skill activates based on description triggers. In Claude Code or OpenClaw, simply describe what you need and the appropriate skill will activate automatically.

---

Generated with [Claude Code](https://claude.com/claude-code) & [OpenClaw](https://github.com/openclaw/openclaw)
