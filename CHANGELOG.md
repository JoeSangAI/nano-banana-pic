# Changelog

All notable changes to this project will be documented in this file.

## [v1.4.0] - 2026-04-28

### 🚀 新特性
- **默认模型升级**：全面切换至 `gpt-image-2-all`，出图质量更稳定，中文文字渲染效果更好
- **垫图生成支持**：新增 `generate_gpt_image_edit()`，通过 DeerAPI `/v1/images/edits` 端点实现 image-to-image，支持单张主图 + 多张附加参考图
- **视觉总监策略升级**：Prompt 构建从"结构化公式"改为"意图翻译 + 关键约束"，提案从线框图思维改为情绪板思维，充分激发模型审美能力

### 📖 文档更新
- **README 全面重写**：以 `gpt-image-2-all` 为主模型重新描述能力，去掉过时的 4K/超长比例误导，明确标注各模型真实支持范围
- **DeerAPI 推荐**：文档中明确推荐 DeerAPI 作为首选 API 提供商，国内直连、稳定、一个 Key 通用多模型
- **新增模型对比表**：清晰对比 `gpt-image-2-all` 与 `gemini-3.1-flash-image-preview` 的能力差异，帮助用户按需选择

### ⚠️ 已知限制
- `gpt-image-2-all` 原生仅支持 1024×1024 / 1536×1024 / 1024×1536 三种尺寸，不支持 1:4 / 21:9 等超长比例
- `gpt-image-2-all` 的 2K/4K 为 DeerAPI 扩展映射，实际输出由模型端决定，如需真 4K 请切换至 Gemini
- `replace_text.py` 仍依赖 Google genai SDK，建议配置 `GEMINI_BASE_URL` 指向 DeerAPI 以保证兼容性

## [v1.3.0] - 2026-04-23

### 🚀 新特性
- **多模型支持**：新增 `gpt-image-2` 模型（OpenAI Images API），与 Gemini 并行可选
- **默认模型切换**：默认从 Gemini 切换为 `gpt-image-2`，出图质量更稳定
- **模型配置化**：引入 `MODEL_CONFIGS` 统一配置不同提供商的模型参数（endpoint、分辨率策略等）
- **GPT Image 尺寸映射**：新增 `GPT_IMAGE_SIZES` 映射表，将 `--resolution` + `--aspect-ratio` 自动转换为 OpenAI 支持的 `size` 参数

### ⚠️ 已知限制
- `gpt-image-2` 暂不支持参考图片（`--input-image` / 垫图），使用时会自动忽略该参数并提示
- GPT Image 的 4K/2K 方形请求会被重映射，实际输出尺寸与请求值可能不完全一致

## [v1.2.0] - 2026-04-05

### 🚀 新特性
- **DeerAPI 全面重构**：切换至 DeerAPI REST API，支持 `gemini-3.1-flash-image-preview` 模型
- **超多比例支持**：新增 `1:4`、`1:8`、`21:9` 等超长比例，适配手机壁纸、电影级宽屏等场景
- **4K 分辨率支持**：正式支持 4K（≈4096px）输出
- **自动压缩参考图**：参考图超过 500KB 时自动压缩，避免 API 上传失败
- **多图生图（一次多张）**：新增 `--number N` 参数，一次生成 N 张图片
- **输出路径重构**：默认输出至 `/Users/Joe_1/Desktop/AI output/pic/`，支持 `GEMINI_OUTPUT_DIR` 环境变量配置
- **DeerAPI 配置化**：支持 `DEER_BASE_URL`（默认 `https://api.deerapi.com`）和 `DEER_API_VERSION` 自定义

### 🎨 风格与模板
- **海报 Prompt 模板** (`poster_templates.py`): 内置混沌风格（Chaos Style）排版规则，中文字清晰、层级分明、留白充足
- **信息图模式** (`--style infographic`): 专用于高密度信息布局、Bento Grid、数据可视化

## [v1.1.0] - 2026-03-24

### 🚀 新特性
- **海报文字无损替换工作流**: 新增 `extract_text.py` 和 `replace_text.py`。支持一键提取生成图片中的所有文字，用户在 Markdown 文件中修改后，再次运行即可自动把图片中的文字替换掉。
- **智能 Diff 重绘**: 采用了"新老文本对比指令生成"技术，自动找到原始图片中需要修改的确切文案，并指挥大模型精准替换，无需任何画图基础。
- **强制多语言渲染约束**: 底层提示词全面加强。无论原图是中文还是其他语言，都能强制 AI 放弃"乱写"或"翻译成英文"的毛病，保证完美手写中文。

### 🛠 重构与优化
- **超清替换保护**: 文字替换流程默认开启最高 4K 分辨率生成，并且加入底层级提示词锁定原图画质，杜绝背景变糊。
- **YAML 解析器升级**: 自带简易 YAML 解析器增强了鲁棒性，现在可以完美兼容处理包含 `\n` 或英文双引号的提取文本，杜绝崩溃。
- **防止干扰文字注入**: 增加了对 Markdown 文件头部指引文字（如"您可以直接修改以下文字"）的静默拦截，避免其被误写到最终的海报里。

## [v1.0.0] - 2026-03-03

- 初始版本：支持 Gemini 文生图、1K/2K/4K 分辨率、垫图重绘
