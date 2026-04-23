import argparse
import os
import sys
import time
import base64
import requests
import re
from datetime import datetime
from pathlib import Path
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# 模型配置
MODEL_CONFIGS = {
    "gemini-3.1-flash-image-preview": {
        "provider": "deerapi",
        "endpoint": "v1beta",
        "default_resolution": "1K",
        "supports_aspect_ratio": True,
    },
    "gpt-image-2": {
        "provider": "openai",
        "endpoint": "v1",
        "supports_aspect_ratio": True,  # 通过 size 参数控制
    },
}

# gpt-image-2 尺寸映射 (resolution + aspect-ratio → size)
GPT_IMAGE_SIZES = {
    # 1K
    ("1K", "1:1"): "1024x1024",
    ("1K", "16:9"): "1536x1024",
    ("1K", "9:16"): "1024x1536",
    ("1K", "4:3"): "1024x1024",
    ("1K", "3:4"): "1024x1024",
    # 2K
    ("2K", "1:1"): "2048x2048",
    ("2K", "16:9"): "2048x1024",
    ("2K", "9:16"): "1024x2048",
    ("2K", "4:3"): "2048x2048",
    ("2K", "3:4"): "1024x2048",
    # 4K
    ("4K", "1:1"): "4096x4096",
    ("4K", "16:9"): "4096x4096",  # DeerAPI 仅支持方形4K
    ("4K", "9:16"): "4096x4096",
    ("4K", "4:3"): "4096x4096",
    ("4K", "3:4"): "4096x4096",
}


def generate_gemini(model, prompt, parts, aspect_ratio, resolution, api_key, base_url, api_version, output_path, number):
    """Generate images using Gemini/deerapi v1beta endpoint"""
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio,
                "imageSize": resolution.upper()
            }
        }
    }
    url = f"{base_url.rstrip('/')}/{api_version}/models/{model}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    for i in range(number):
        print(f"\nGenerating image {i+1}/{number}...")
        for attempt in range(3):
            try:
                start = time.time()
                resp = requests.post(url, json=payload, headers=headers, timeout=300)
                elapsed = time.time() - start
                print(f"  Status: {resp.status_code}, Time: {elapsed:.1f}s")

                if resp.status_code == 200:
                    result = resp.json()
                    for part in result.get("candidates", [{}])[0].get("content", {}).get("parts", []):
                        if "inlineData" in part:
                            data = base64.b64decode(part["inlineData"]["data"])
                            final_path = output_path
                            if number > 1:
                                final_path = output_path.parent / f"{output_path.stem}_{i+1}{output_path.suffix}"
                            with open(final_path, "wb") as f:
                                f.write(data)
                            img = Image.open(BytesIO(data))
                            print(f"  ✅ Saved: {final_path} ({img.size[0]}x{img.size[1]}, {len(data)/1024/1024:.1f}MB)")
                            break
                    break
                elif resp.status_code == 503:
                    wait = (attempt + 1) * 10
                    print(f"  503 unavailable, retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    print(f"  Error: {resp.text[:200]}")
                    break
            except Exception as e:
                print(f"  Exception: {e}")
                if attempt < 2:
                    time.sleep(5)


def generate_gpt_image(api_key, base_url, prompt, size, output_path, number):
    """Generate images using OpenAI Images API endpoint with gpt-image-2"""
    url = f"{base_url.rstrip('/')}/v1/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    for i in range(number):
        print(f"\nGenerating image {i+1}/{number}...")
        for attempt in range(3):
            try:
                start = time.time()
                payload = {
                    "model": "gpt-image-2",
                    "prompt": prompt,
                    "size": size,
                    "n": 1,
                    "response_format": "b64_json"
                }
                resp = requests.post(url, json=payload, headers=headers, timeout=300)
                elapsed = time.time() - start
                print(f"  Status: {resp.status_code}, Time: {elapsed:.1f}s")

                if resp.status_code == 200:
                    result = resp.json()
                    b64_data = result.get("data", [{}])[0].get("b64_json", "")
                    if b64_data:
                        # Handle data URI format: data:image/webp;base64,...
                        if "," in b64_data:
                            b64_data = b64_data.split(",")[1]
                        img_bytes = base64.b64decode(b64_data)
                        final_path = output_path
                        if number > 1:
                            final_path = output_path.parent / f"{output_path.stem}_{i+1}{output_path.suffix}"
                        with open(final_path, "wb") as f:
                            f.write(img_bytes)
                        img = Image.open(BytesIO(img_bytes))
                        print(f"  ✅ Saved: {final_path} ({img.size[0]}x{img.size[1]}, {len(img_bytes)/1024/1024:.1f}MB)")
                    else:
                        print(f"  No b64_json in response: {result}")
                    break
                else:
                    print(f"  Error: {resp.text[:200]}")
                    break
            except Exception as e:
                print(f"  Exception: {e}")
                if attempt < 2:
                    time.sleep(5)


def main():
    parser = argparse.ArgumentParser(description="Generate images using DeerAPI + Gemini or GPT Image")
    parser.add_argument("--prompt", required=True, help="Text description")
    parser.add_argument("--model", default="gpt-image-2",
                        choices=list(MODEL_CONFIGS.keys()),
                        help="Model name")
    parser.add_argument("--aspect-ratio", default="1:1", help="Aspect ratio (1:1, 16:9, 9:16, 1:4, 1:8, 4:3, 3:4, 2:3, 3:2, 4:1, 1:2, 2:1, 21:9)")
    parser.add_argument("--resolution", default="1K", help="Resolution: 512, 1K, 2K, 4K")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--input-image", nargs="+", help="Reference image paths")
    parser.add_argument("--number", type=int, default=1, help="Number of images")
    args = parser.parse_args()

    # 读取配置
    api_key = os.getenv("DEER_API_KEY")
    base_url = os.getenv("DEER_BASE_URL", "https://api.deerapi.com")

    if not api_key:
        print("Error: DEER_API_KEY not found in .env")
        sys.exit(1)

    # 自动压缩参考图片（超过 500KB 则压缩）
    def compress_image(path, max_size_kb=500):
        size_kb = os.path.getsize(path) / 1024
        if size_kb <= max_size_kb:
            return path
        img = Image.open(path)
        ratio = (max_size_kb / size_kb) ** 0.5
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)
        buf = BytesIO()
        fmt = "PNG" if path.lower().endswith(".png") else "JPEG"
        img.save(buf, format=fmt, quality=85)
        compressed_path = path.rsplit(".", 1)[0] + "_compressed." + path.rsplit(".", 1)[1].lower()
        with open(compressed_path, "wb") as f:
            f.write(buf.getvalue())
        orig_size_kb = os.path.getsize(path) / 1024
        new_size_kb = os.path.getsize(compressed_path) / 1024
        print(f"  压缩: {orig_size_kb:.0f}KB → {new_size_kb:.0f}KB → {compressed_path}")
        return compressed_path

    # 构建输出路径
    if not args.output:
        date_str = datetime.now().strftime("%Y%m%d")
        output_base = os.getenv("GEMINI_OUTPUT_DIR") or "/Users/Joe_1/Desktop/AI output/pic"
        output_dir = Path(output_base)
        output_dir.mkdir(parents=True, exist_ok=True)
        safe = "".join(c for c in args.prompt[:40] if c.isalnum() or c in (" ", "_")).strip()
        output_path = output_dir / f"{date_str}_{safe}.png"
    else:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    # 获取模型配置
    model_config = MODEL_CONFIGS.get(args.model, MODEL_CONFIGS["gemini-3.1-flash-image-preview"])

    print(f"Model: {args.model}")
    print(f"Provider: {model_config['provider'].upper()}")
    print(f"Aspect Ratio: {args.aspect_ratio}")
    print(f"Resolution: {args.resolution}")

    # GPT Image 模型不支持参考图片
    if args.input_image and args.model == "gpt-image-2":
        print("Warning: gpt-image-2 不支持参考图片，将忽略 --input-image 参数")
        args.input_image = None

    # 根据模型类型选择生成方式
    if args.model == "gpt-image-2":
        # 查找对应的尺寸
        size_key = (args.resolution.upper(), args.aspect_ratio)
        size = GPT_IMAGE_SIZES.get(size_key, "1024x1024")
        print(f"Size: {size}")
        print(f"Reference Images: 0 (not supported)")
        generate_gpt_image(api_key, base_url, args.prompt, size, output_path, args.number)
    else:
        # 构建 parts（用于 Gemini 模型）
        parts = [{"text": args.prompt}]
        if args.input_image:
            args.input_image = [compress_image(p) for p in args.input_image]
            for path in args.input_image:
                if not os.path.exists(path):
                    print(f"Error: Image not found: {path}")
                    sys.exit(1)
                img = Image.open(path)
                buf = BytesIO()
                img.save(buf, format="PNG")
                parts.append({
                    "inlineData": {
                        "mimeType": "image/png",
                        "data": base64.b64encode(buf.getvalue()).decode()
                    }
                })

        print(f"Reference Images: {len(args.input_image) if args.input_image else 0}")
        api_version = model_config["endpoint"]
        generate_gemini(args.model, args.prompt, parts, args.aspect_ratio, args.resolution,
                        api_key, base_url, api_version, output_path, args.number)


if __name__ == "__main__":
    main()
