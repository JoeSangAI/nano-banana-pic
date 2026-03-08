# Gemini Image Gen / Nano Banana Pic

使用 Google Gemini API（Imagen 3 / Nano Banana 2）进行高质量的文生图、垫图与图片文字编辑。支持 1K/2K/4K 分辨率与原图结构保护。

**密钥：** 需使用环境变量 `GOOGLE_API_KEY` 或在本目录下新建 `.env` 填入（请勿提交 `.env`）。
**依赖：** `pip install google-genai pillow`

## 🌟 核心功能一：图像生成与重绘

在项目根目录（或 Cursor 终端）执行：

```bash
# 1. 基础文生图 (默认 1K 分辨率)
python3 tools/nano_banana_pic/generate_image.py --prompt "夕阳下的海边小镇，暖色调"

# 2. 指定高分辨率出图 (最高 4K)
python3 tools/nano_banana_pic/generate_image.py --prompt "科技感会议室" --resolution 4K

# 3. 垫图局部重绘 (利用 --edit-template 智能保护原图主体和构图)
python3 tools/nano_banana_pic/generate_image.py --prompt "把天空改成傍晚" --input-image 原图.png --edit-template
```
*Tip: 在 Cursor 中直接对 AI 说：“用 Nano Banana 帮我画一张赛博朋克风格的咖啡馆，比例 16:9” 即可自动执行。*

---

## 🌟 核心功能二：海报文字无损替换 (Advanced Text Editing)

这是专门针对“生成出来的海报文字不对/有拼写错误”的终极解决方案。它可以**在完全不破坏原图画风、构图和人物特征的前提下，精准替换图中的指定文字**。

### 工作流 (Cursor 中的交互方法)

你不需要手动敲代码，只需在 Cursor 中用自然语言按以下两步使唤 AI 即可：

**步骤 1：提取文字并编辑**
* **用户指令：** *"帮我把 `output/images/你的海报.png` 这张图的文字提取出来。"*
* AI 会自动运行 `extract_text.py`，并在同目录下生成一个 `.md` 文件。
* **你的操作：** 打开生成的这个 `.md` 文件，找到 `# 海报文本内容` 下方的文字，把你想要改的字直接改成新的内容，保存文件。

**步骤 2：执行精准替换**
* **用户指令：** *"我改好了那个 md 文件，按 4K 分辨率重新生成吧。"*
* AI 会自动运行 `replace_text.py`。
* **结果：** 脚本会自动进行文本差异对比 (Diff)，并生成一张带有 `_text_edited.png` 后缀的新图片。新图的画面完全不变，但文字已经完美替换为你修改后的内容！

---

## 📅 更新日志 (Changelog)

### [v1.1.0] - 2026-03-08
**🚀 新特性 (New Features)**
* **海报文字无损替换工作流**：新增 `extract_text.py` 与 `replace_text.py` 两个核心脚本。
* **智能 Diff 提示词系统**：文字替换时自动对比新旧文本差异，生成极度精确的局部重绘指令。
* **严格语言约束**：彻底解决了大模型重绘时强行将中文翻译为英文或出现乱码的问题，强制模型忠实渲染用户输入的各种语言（含中文）。

**🛠 优化与修复 (Improvements & Fixes)**
* **YAML 解析稳定性**：修复了提取文本中包含回车符、双引号等特殊字符时导致 Markdown Frontmatter 解析崩溃的问题。
* **分辨率锁定**：文本替换流程默认使用超清模式渲染，并加入“禁止模糊”和“保持锐度”的底层安全提示词。
