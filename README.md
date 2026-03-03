# nano-banana-pic

使用 Google Gemini API（Imagen 3 / Nano Banana 2）文生图、垫图与编辑。支持 1K/2K/4K 分辨率与编辑模板。

**密钥：** 使用环境变量 `GOOGLE_API_KEY` 或在本目录下复制 `.env.example` 为 `.env` 填入（勿提交 .env）。密钥从 [Google AI Studio](https://aistudio.google.com/apikey) 获取。

**依赖：** `pip install google-genai pillow`

## 用法（在仓库根目录执行）

```bash
# 文生图
python3 generate_image.py --prompt "夕阳下的海边小镇，暖色调"

# 指定分辨率 1K|2K|4K
python3 generate_image.py --prompt "科技感会议室" --resolution 4K

# 垫图 / 编辑（--edit-template 保持其余不变）
python3 generate_image.py --prompt "把天空改成傍晚" --input-image 原图.png --edit-template
```

参数：`--resolution` 1K|2K|4K，`--aspect-ratio`，`--output`，`--number`，`--input-image`，`--edit-template` 等。
