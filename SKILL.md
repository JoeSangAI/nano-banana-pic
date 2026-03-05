---
name: nano-banana-pic
description: Generate images using Google's Gemini API (Imagen 3 / Nano Banana 2). Use when the user asks to generate images with Gemini, "Nano Banana 2", or "nano-banana-pic". Aligns with GitHub repo JoeSangAI/nano-banana-pic.
---

# Nano Banana Pic — Gemini Image Generation

Generate high-quality images using Google's Gemini API. Supports Imagen 3 / Nano Banana 2, text-to-image, image-to-image, and edit template. Repo: [nano-banana-pic](https://github.com/JoeSangAI/nano-banana-pic).

## When to use
- Generate images from text prompts using Google's models.
- When the user mentions "Nano Banana 2", "nano-banana-pic", "Gemini Image", or "Imagen".

## Workflow
1.  Collect inputs: prompt, aspect ratio (optional), and model name (default: `gemini-3.1-flash-image-preview`).
2.  Ensure `GEMINI_API_KEY` or `GOOGLE_API_KEY` is set in the environment（或在本机 `tools/nano_banana_pic/.env` 中配置，勿提交）。
3.  **从仓库根目录**运行本机工具：`tools/nano_banana_pic/generate_image.py`。
4.  Output 保存到 `GEMINI_OUTPUT_DIR` 或默认 `output/images/`。

## Usage

所有命令均在**工作区根目录**（即含 `tools/` 的目录）下执行：

```bash
# Basic usage
python3 tools/nano_banana_pic/generate_image.py --prompt "A futuristic city with flying cars"

# 指定分辨率 1K|2K|4K（默认 1K，4K 适合最终出图）
python3 tools/nano_banana_pic/generate_image.py --prompt "A serene Japanese garden" --resolution 4K

# Image-to-Image (Multi-shot / 垫图生成)
python3 tools/nano_banana_pic/generate_image.py --prompt "Transform into a cyberpunk style" --input-image "/path/to/image1.png" "/path/to/image2.png"

# 编辑模式：局部修改时保持其余不变（配合 --input-image 使用）
python3 tools/nano_banana_pic/generate_image.py --prompt "make the sky more dramatic" --input-image photo.png --edit-template --resolution 2K

# Specify model
python3 tools/nano_banana_pic/generate_image.py --prompt "A cute robot" --model "gemini-2.0-flash"
```

## Dependencies
- `google-genai` (preferred) or `google-generativeai`
- `Pillow` (for image saving/processing)

Install with:
```bash
uv pip install google-genai pillow
# or
python3 -m pip install google-genai pillow
```

## Environment
- `GOOGLE_API_KEY`: Required. Get it from Google AI Studio.

## Script: tools/nano_banana_pic/generate_image.py

脚本位于工作区 **tools/nano_banana_pic/** 下（与 nano_banana_ppt、feishu_sync 同级）。支持参数：
- `--prompt`: The text description of the image.
- `--model`: The model to use (default: `gemini-3.1-flash-image-preview`).
- `--aspect-ratio`: Aspect ratio (1:1, 16:9, 9:16, etc.).
- `--resolution`: Output resolution **1K**|**2K**|**4K** (default: 1K). 1K≈1024px, 2K≈2048px, 4K≈4096px. 推荐流程：1K 草图迭代 → 4K 最终出图。
- `--output`: Output filename (optional).
- `--style`: Force a specific generation style. Currently supports:
  - `infographic`: Uses a specialized system prompt for high-density information layouts (Bento Grids, Dashboards).
- `--number`: Number of images to generate (default: 1).
- `--input-image`: Path(s) to input image(s) for image-to-image or editing.
- `--edit-template`: When editing (with `--input-image`), use template to preserve unchanged areas (subject, composition, lighting, etc.).

# Infographic Generation (--style infographic)

Nano Banana Pic supports a dedicated **Infographic Mode** for generating high-density information graphics, Bento Grids, and data visualizations.

**Triggering Infographic Mode:**
1. **Automatic**: Include keywords like "infographic", "bento grid", "information map", "data visualization", or "信息图" in your prompt.
2. **Manual**: Use the `--style infographic` flag.

**Example:**
```bash
python3 tools/nano_banana_pic/generate_image.py --prompt "A futuristic bento grid showing AI growth statistics"
# or
python3 tools/nano_banana_pic/generate_image.py --prompt "AI Growth Stats" --style infographic
```

**Infographic Style Characteristics:**
- **Layout**: Modular Bento Grid or Dashboard.
- **Visuals**: Icons, stylized charts (donuts, bars), bold headers.
- **Aesthetic**: Liquid Glass (frosted cards) or Clean Flat Vector.
- **Density**: High information density with balanced negative space.

## Edit Prompt Template (--edit-template)

When editing existing images, use `--edit-template` to wrap user instructions in a structured prompt that preserves unchanged areas:

```
Change ONLY: {user_instruction}. Keep identical: subject, composition/crop, pose, lighting, color palette, background, text, and overall style. Do not add new objects. If text exists, keep it unchanged.
```

Use for: 局部改色、换背景、微调光影、保留主体只改细节等场景。

## 调用建议（给用户 / 对话时的指令示例）

**按用途选分辨率：**
- 「先 1K 出一张草图我看看」→ 用 `--resolution 1K`，快速试 prompt。
- 「这张满意了，用 4K 再出一版」→ 用 `--resolution 4K` 做最终大图。
- 「2K 就行，不用太高」→ 用 `--resolution 2K` 平衡速度与清晰度。

**按用途选宽高比：**
- 「竖图，手机屏」→ `--aspect-ratio 9:16`
- 「横图，PPT/宽屏」→ `--aspect-ratio 16:9`
- 「方图，头像/封面」→ `--aspect-ratio 1:1`

**纯文生图（直接描述画面）：**
- 「用 Gemini 生成一张：夕阳下的海边小镇，暖色调，插画风格」
- 「Nano Banana 生成：科技感会议室，大屏、白板、简约」

**垫图 / 风格迁移：**
- 「用这张图做参考，生成同样风格的一张：森林里的木屋」
- 「以这张为参考图，生成 16:9 横图，主题是……」（会用到 `--input-image`）

**编辑已有图（局部修改）：**
- 「在现有这张图基础上，只把天空改成傍晚晚霞，其它别动」→ 用 `--input-image` + `--edit-template`
- 「这张图保持人物和构图，只把背景换成办公室」→ `--input-image` + `--edit-template`，prompt 写「只改背景为办公室」

**推荐工作流：**
1. 先用 1K + 简短 prompt 出 1～2 张，确认构图和风格。
2. 微调文案后再跑一次 1K，满意后再用 4K 出最终图。

## Notes on "Nano Banana 2"
"Nano Banana 2" is often associated with Gemini's advanced image generation capabilities. If the user asks for it specifically, use the `imagen-3.0-generate-001` model as it is the underlying technology, unless a specific `nano-banana-2` model ID is known and valid in the API.
