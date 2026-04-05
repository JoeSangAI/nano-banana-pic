# Nano Banana Pic

使用 DeerAPI + Gemini API 进行高质量文生图、垫图重绘与海报文字无损替换。支持 1K/2K/4K 分辨率，多种比例（1:1、16:9、9:16、1:4、21:9 等）。

> 项目地址：[JoeSangAI/nano-banana-pic](https://github.com/JoeSangAI/nano-banana-pic)

## 环境配置

**密钥：** 在本目录下新建 `.env`，填入 `DEER_API_KEY=your_key_here`（请勿提交 `.env`）。

**依赖：**
```bash
pip install requests pillow python-dotenv
```

## 图像生成

### 命令行

```bash
# 基础文生图（默认 1K, 1:1）
python3 generate_image.py --prompt “夕阳下的海边小镇，暖色调”

# 指定分辨率（1K / 2K / 4K）
python3 generate_image.py --prompt “科技感会议室” --resolution 4K

# 指定比例（竖版横版方图外，还支持 1:4 竖长图、21:9 宽屏等）
python3 generate_image.py --prompt “赛博朋克咖啡馆” --aspect-ratio 16:9

# 垫图重绘（保留原图构图，AI 局部修改）
python3 generate_image.py --prompt “把天空改成傍晚” --input-image 原图.png

# 垫图 + 结构保护（智能保留主体、构图、光影）
python3 generate_image.py --prompt “把天空改成傍晚” --input-image 原图.png --edit-template

# 一次生成多张
python3 generate_image.py --prompt “咖啡馆插画” --number 4

# 信息图模式（高密度数据布局、Bento Grid 风格）
python3 generate_image.py --prompt “AI 增长数据信息图” --style infographic
```

### 支持的比例

| 比例 | 说明 |
|------|------|
| `1:1` | 方图（头像/封面） |
| `16:9` | 横图（PPT/宽屏） |
| `9:16` | 竖图（手机壁纸） |
| `4:3` / `3:4` | 传统比例 |
| `2:3` / `3:2` | 摄影比例 |
| `1:4` / `4:1` | 超长竖图/横图 |
| `1:2` / `2:1` | 宽幅 |
| `21:9` | 电影宽屏 |

### 推荐工作流

1. **1K 草图** → 快速试 prompt，确认构图和风格
2. **2K 调整** → 满意后提升分辨率做精细调整
3. **4K 最终出图** → 用于正式使用

---

## 海报文字无损替换

在不破坏原图画风、构图和人物特征的前提下，精准替换图中的指定文字。

### 步骤 1：提取文字

```bash
python3 extract_text.py --image 你的海报.png
```

脚本会自动调用 Gemini 识别图中所有文字，生成同目录下的 `.md` 文件。

### 步骤 2：编辑文字

打开 `.md` 文件，找到 `# 海报文本内容` 区域，直接修改文字，保存。

### 步骤 3：重新生成

```bash
python3 replace_text.py --md-file 你的海报.md --resolution 4K
```

生成一张 `_text_edited.png`，画面完全不变，文字已替换。

---

## 海报 Prompt 模板

项目内置 `poster_templates.py`，提供混沌风格（Chaos Style）的海报 prompt 模板：

```python
from prompt_templates import PosterTemplate

t = PosterTemplate()
prompt = t.build(
    product_name=”AI Master”,
    hook_line=”Master AI in 30 Days”,
    slogan=”AI Master · Future Skills”,
    philosophy=[“Deep Learning”, “Hands-on Projects”, “Real Results”],
    services=[
        {“num”: “01”, “label”: “【Day 1-10】”, “title”: “Foundations”, “desc”: “Build your AI fundamentals”}
    ],
    founder_cred=[“PhD in ML”, “Ex-Google Engineer”],
    team_cred=”AI Master Team”,
    audience=[“Engineers”, “Product Managers”, “Tech Enthusiasts”],
    pricing={“original”: “$299”, “price”: “$99”, “badge”: “Early Bird”}
)
print(prompt)
```

