# Nano Banana Pic

把专业广告公司的创意流程，封装进一个 AI Agent。

每次出图，不是碰运气，是一次有结构、有校验、有灵魂的完整创意执行。

> 英文版：[:english: English README](README_EN.md)

---

## 这是什么

Nano Banana Pic 是一家**没有人的 4A 广告公司**。

它把一位资深 **PM（客户经理）** 和一位 **Creative Director（视觉总监）** 的协作流程，用两个 AI Agent 完整还原。你只需要说出你的想法，剩下的——需求梳理、方向提案、Prompt 打磨、出图校验——全部自动完成。

底层以 **GPT Image** 为主引擎，以 **Gemini** 为备选，按需切换，出图质量稳定可控。

**你不是在用 AI 画图，你是在委托一家广告公司。**

---

## 推荐使用 DeerAPI

本项目默认调用 **DeerAPI** 提供的 `gpt-image-2-all` 模型，稳定、快速、国内直连。

**为什么推荐 DeerAPI？**
- 聚合 OpenAI、Gemini 等主流模型，一个 Key 通用
- 国内网络直连，无需代理
- `gpt-image-2-all` 出图质量优秀，支持文生图 + 垫图编辑
- 支持 `gemini-3.1-flash-image-preview` 作为备选（4K + 超长比例）

👉 [获取 DeerAPI Key](https://api.deerapi.com)

---

## 核心能力

### 🎯 PM + Creative Director 双 Agent 协作

两个 AI 像真正的创意团队一样工作：

- **PM Agent**：像资深客户经理一样追问，把模糊的想法翻译成精确的 Creative Brief——受众是谁、媒介是什么、要传达什么情绪、一个字都不能含糊
- **Creative Director Agent**：像视觉总监一样思考风格、构图、比例、出图方向，给你明确的设计方向提案供选择，而不是丢给你一张随机生成的图

整个过程**两轮确认**：先确认 Brief，再确认方向，最大程度避免返工。

**Prompt 策略**：我们相信模型的审美能力。提案只定方向（情绪板），不定实现（线框图）。在满足核心约束的前提下，让模型发挥训练数据中海量优秀设计案例的创造力。

### 🖼️ 垫图生成（Image-to-Image）

支持以产品图、参考图为素材，让模型在保留原图核心元素的基础上生成新画面。

底层通过 DeerAPI 的 `/v1/images/edits` 端点调用 `gpt-image-2-all`，支持单张主图 + 多张附加参考图。

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

### 📊 信息图模式

一键切换到高密度数据可视化风格——Bento Grid 布局、图标、仪表盘式图表。适合需要专业感、数据感的高管汇报或社交媒体内容。

---

## 模型能力对比

| 能力 | `gpt-image-2-all`（默认，推荐） | `gemini-3.1-flash-image-preview`（备选） |
|------|-------------------------------|----------------------------------------|
| **文生图** | ✅ 1024×1024 / 1536×1024 / 1024×1536 | ✅ 原生多尺寸，支持 4K |
| **垫图/参考图** | ✅ 支持 `image` + `additional_images[]` | ✅ 支持多图参考 |
| **超长比例** | ❌ 不支持（最长 9:16） | ✅ 支持 1:4 / 1:8 / 21:9 等 |
| **中文文字渲染** | ✅ 较好 | ⚠️ 一般 |
| **API 稳定性** | ✅ DeerAPI 国内直连 | ✅ DeerAPI 国内直连 |

**使用建议**：
- 日常出图、产品海报、电商详情页 → **默认用 `gpt-image-2-all`**
- 需要 4K 大图、超长比例、或复杂多图垫图 → **切换 `gemini-3.1-flash-image-preview`**

---

## 环境配置

```bash
# 克隆项目
git clone https://github.com/JoeSangAI/nano-banana-pic.git
cd nano-banana-pic

# 安装依赖
pip install requests pillow python-dotenv

# 配置密钥（推荐从 DeerAPI 获取）
echo "DEER_API_KEY=your_key_here" > .env
echo "DEER_BASE_URL=https://api.deerapi.com" >> .env

# （可选）如果需要通过 Google genai SDK 调用，也一并配置
echo "GOOGLE_API_KEY=your_key_here" >> .env
echo "GEMINI_BASE_URL=https://api.deerapi.com" >> .env
```

> 💡 **提示**：`.env` 文件已加入 `.gitignore`，不会意外提交到 Git。

---

## 命令行使用

```bash
# 基础文生图（默认 gpt-image-2-all，通过 DeerAPI）
python3 generate_image.py --prompt "夕阳下的海边小镇，暖色调"

# 垫图生成（以产品图为参考，生成电商海报）
python3 generate_image.py --prompt "干净的电商详情页，产品参考附图" \
  --input-image product.png \
  --aspect-ratio 9:16

# 指定分辨率
python3 generate_image.py --prompt "科技感会议室" --resolution 1K

# 指定比例
python3 generate_image.py --prompt "赛博朋克咖啡馆" --aspect-ratio 16:9

# 切换模型为 Gemini（支持 4K 和超长比例）
python3 generate_image.py --prompt "发布会主视觉，大留白" \
  --model gemini-3.1-flash-image-preview \
  --resolution 4K \
  --aspect-ratio 21:9

# 一次生成多张
python3 generate_image.py --prompt "咖啡馆插画" --number 4

# 信息图模式
python3 generate_image.py --prompt "AI 增长数据信息图" --style infographic
```

---

## 推荐工作流

```
1K 草图  →  快速验证构图和风格（约 1-2 分钟出图）
    ↓ 满意
2K 调整  →  精细确认元素和氛围
    ↓ 满意
最终出图  →  交付级成品
```

**先低分辨率试错，再高分辨率出图**——这是专业设计师的工作方式，不是靠运气。

> 注：`gpt-image-2-all` 的 2K/4K 为 DeerAPI 的扩展映射，实际输出尺寸由模型端决定。如需真 4K，请切换至 `gemini-3.1-flash-image-preview`。

---

## 两个 AI Agent 的协作流程

```
你（客户）
   ↓ 说出模糊想法
PM Agent（客户经理）
   ↓ 追问澄清，整理为结构化 Brief
   ↓ 你确认 Brief（第一轮确认）
Creative Director Agent（视觉总监）
   ↓ 输出设计方向提案（情绪板，不定实现细节）
   ↓ 你确认方向（第二轮确认）
   ↓ 生成完整 Prompt（意图翻译 + 关键约束）
PM Agent（复核）
   ↓ 检查核心约束是否满足
   ↓ 全部通过 → 出图
```

这和找一个广告公司合作的过程完全一致——**需求对齐 → 方向确认 → 执行交付**，而不是 AI 直接给你一个黑箱结果。
