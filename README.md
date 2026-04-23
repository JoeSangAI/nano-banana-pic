# Nano Banana Pic

把专业广告公司的创意流程，封装进一个 AI Agent。

每次出图，不是碰运气，是一次有结构、有校验、有灵魂的完整创意执行。

> 英文版：[:english: English README](README_EN.md)

---

## 这是什么

Nano Banana Pic 是一家**没有人的 4A 广告公司**。

它把一位资深 **PM（客户经理）** 和一位 **Creative Director（视觉总监）** 的协作流程，用两个 AI Agent 完整还原。你只需要说出你的想法，剩下的——需求梳理、方向提案、Prompt 打磨、出图校验——全部自动完成。

底层支持 **Gemini** 和 **GPT Image** 双引擎，按需切换，出图质量更稳定。

**你不是在用 AI 画图，你是在委托一家广告公司。**

---

## 核心能力

### 🎯 PM + Creative Director 双 Agent 协作

两个 AI 像真正的创意团队一样工作：

- **PM Agent**：像资深客户经理一样追问，把模糊的想法翻译成精确的 Creative Brief——受众是谁、媒介是什么、要传达什么情绪、一个字都不能含糊
- **Creative Director Agent**：像视觉总监一样思考风格、构图、比例、出图方向，给你 2-3 个明确的设计提案供选择，而不是丢给你一张随机生成的图

整个过程**两轮确认**：先确认 Brief，再确认方向，最大程度避免返工。

### ✍️ 海报文字无损替换

AI 生成海报时，中文文字出问题是高频痛点——乱码、错字、翻译腔。

Nano Banana Pic 解决这个问题的思路不是"一次画对"，而是**允许画错，然后精准修**。

流程：提取文字 → 编辑 Markdown → 重新生成

画面完全不变，只有文字被替换。构图、人物、画风——全部原样保留。

### 🎨 海报 Prompt 模板

内置海报结构模板，一行调用即可生成符合专业版式的完整 prompt。

模板会持续增加——如果你有喜欢的海报风格，告诉 Nano Banana Pic，它会学习这种风格，并把它固化为一个可复用的模板。

```python
from prompt_templates import PosterTemplate

t = PosterTemplate()
prompt = t.build(
    product_name="你的品牌名",
    hook_line="钩子句子",
    slogan="标语",
    philosophy=["理念1", "理念2", "理念3"],
    services=[
        {"num": "01", "label": "【标签】", "title": "服务名", "desc": "一句话描述"}
    ],
    founder_cred=["创始人背书1", "创始人背书2"],
    team_cred="团队名称",
    audience=["受众1", "受众2", "受众3"],
    pricing={"original": "原价", "price": "现价", "badge": "标签"}
)
print(prompt)
```

### 🖼️ 垫图重绘 + 结构保护

当你要**保留原图构图，只改局部**时（换背景、调色、改天空），使用 `--edit-template` 模式。

系统会自动注入结构保护 prompt，指挥 AI 只改你要改的地方，其余保持像素级一致。

### 📊 信息图模式

一键切换到高密度数据可视化风格——Bento Grid 布局、图标、仪表盘式图表。适合需要专业感、数据感的高管汇报或社交媒体内容。

---

## 支持的比例

| 比例 | 场景 |
|------|------|
| `1:1` | 头像、封面 |
| `16:9` | PPT、横版 Banner |
| `9:16` | 手机壁纸、小红书封面 |
| `4:3` | 传统印刷 |
| `2:3` / `3:2` | 摄影风格 |
| `1:4` | 超长竖图（手机通知栏、全屏海报） |
| `4:1` | 超长横图 |
| `21:9` | 电影级宽银幕 |

---

## 推荐工作流

```
1K 草图  →  快速验证构图和风格（30秒出图）
    ↓ 满意
2K 调整  →  精细调色和元素（1-2分钟）
    ↓ 满意
4K 出图  →  最终交付级成品
```

**先低分辨率试错，再高分辨率出图**——这是专业设计师的工作方式，不是靠运气。

---

## 环境配置

```bash
# 克隆项目
git clone https://github.com/JoeSangAI/nano-banana-pic.git
cd nano-banana-pic

# 安装依赖
pip install requests pillow python-dotenv

# 配置密钥（从 DeerAPI 获取）
echo "DEER_API_KEY=your_key_here" > .env
```

---

## 命令行使用

```bash
# 基础文生图（默认 gpt-image-2）
python3 generate_image.py --prompt "夕阳下的海边小镇，暖色调"

# 切换模型为 Gemini
python3 generate_image.py --prompt "夕阳下的海边小镇，暖色调" --model gemini-3.1-flash-image-preview

# 指定分辨率
python3 generate_image.py --prompt "科技感会议室" --resolution 4K

# 指定比例
python3 generate_image.py --prompt "赛博朋克咖啡馆" --aspect-ratio 16:9

# 垫图重绘（仅 Gemini 支持）
python3 generate_image.py --prompt "把天空改成傍晚" --input-image 原图.png --model gemini-3.1-flash-image-preview

# 垫图 + 结构保护（仅 Gemini 支持）
python3 generate_image.py --prompt "把天空改成傍晚" --input-image 原图.png --edit-template --model gemini-3.1-flash-image-preview

# 一次生成多张
python3 generate_image.py --prompt "咖啡馆插画" --number 4

# 信息图模式
python3 generate_image.py --prompt "AI 增长数据信息图" --style infographic
```

### 模型对比

| 能力 | `gpt-image-2`（默认） | `gemini-3.1-flash-image-preview` |
|------|----------------------|--------------------------------|
| 基础文生图 | ✅ | ✅ |
| 垫图/参考图 | ❌ | ✅ |
| 1K/2K/4K 分辨率 | 部分重映射 | 原生支持 |
| 超长比例（1:4 / 21:9） | ❌ | ✅ |

---

## 两个 AI Agent 的协作流程

```
你（客户）
   ↓ 说出模糊想法
PM Agent（客户经理）
   ↓ 追问澄清，整理为结构化 Brief
   ↓ 你确认 Brief（第一轮确认）
Creative Director Agent（视觉总监）
   ↓ 输出 2-3 个设计方向提案
   ↓ 你确认方向（第二轮确认）
   ↓ 生成完整 Prompt
PM Agent（复核）
   ↓ 逐项 checklist 校验
   ↓ 全部通过 → 出图
```

这和找一个广告公司合作的过程完全一致——**需求对齐 → 方向确认 → 执行交付**，而不是 AI 直接给你一个黑箱结果。
