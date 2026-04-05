import argparse
import os
import sys
import time
import base64
import requests
from datetime import datetime
from pathlib import Path
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")


def main():
    parser = argparse.ArgumentParser(description="Generate images using DeerAPI + Gemini")
    parser.add_argument("--prompt", required=True, help="Text description")
    parser.add_argument("--model", default="gemini-3.1-flash-image-preview", help="Model name")
    parser.add_argument("--aspect-ratio", default="1:1", help="Aspect ratio (1:1, 16:9, 9:16, 1:4, 1:8, 4:3, 3:4, 2:3, 3:2, 4:1, 1:2, 2:1, 21:9)")
    parser.add_argument("--resolution", default="1K", help="Resolution: 512, 1K, 2K, 4K")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--input-image", nargs="+", help="Reference image paths")
    parser.add_argument("--number", type=int, default=1, help="Number of images")
    args = parser.parse_args()

    # 读取配置
    api_key = os.getenv("DEER_API_KEY")
    base_url = os.getenv("DEER_BASE_URL", "https://api.deerapi.com")
    api_version = os.getenv("DEER_API_VERSION", "v1beta")

    if not api_key:
        print("Error: DEER_API_KEY not found in .env")
        sys.exit(1)

    # 构建输出路径
    if not args.output:
        date_str = datetime.now().strftime("%Y%m%d")
        output_base = os.getenv("GEMINI_OUTPUT_DIR") or str(Path.home() / "Desktop" / "AI output")
        output_dir = Path(output_base) / "images"
        output_dir.mkdir(parents=True, exist_ok=True)
        safe = "".join(c for c in args.prompt[:40] if c.isalnum() or c in (" ", "_")).strip()
        output_path = output_dir / f"{date_str}_{safe}.png"
    else:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    # 构造 parts
    parts = [{"text": args.prompt}]

    if args.input_image:
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

    # 构建 payload
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": args.aspect_ratio,
                "imageSize": args.resolution.upper()
            }
        }
    }

    # 构建 URL
    url = f"{base_url.rstrip('/')}/{api_version}/models/{args.model}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    print(f"Model: {args.model}")
    print(f"Aspect Ratio: {args.aspect_ratio}")
    print(f"Resolution: {args.resolution}")
    print(f"Reference Images: {len(args.input_image) if args.input_image else 0}")

    for i in range(args.number):
        print(f"\nGenerating image {i+1}/{args.number}...")

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
                            if args.number > 1:
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


if __name__ == "__main__":
    main()
