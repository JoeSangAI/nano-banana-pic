import argparse
import os
import sys
from pathlib import Path
import json

try:
    from google import genai
    from google.genai import types
    from PIL import Image
except ImportError:
    print("Error: 'google-genai' or 'pillow' not found.")
    sys.exit(1)

def extract_text(image_path, original_prompt=None, reference_images=None):
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        try:
            with open(env_path, "r") as f:
                for line in f:
                    if line.strip().startswith("GOOGLE_API_KEY=") and not api_key:
                        api_key = line.strip().split("=", 1)[1].strip('"').strip("'")
        except Exception:
            pass

    if not api_key:
        print("Error: API key not set.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    
    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"Error loading image '{image_path}': {e}")
        sys.exit(1)

    print(f"Extracting text from {image_path} using gemini-2.5-pro...")
    
    prompt = (
        "Extract all text from this image. Structure it logically "
        "(e.g., Main Title, Subtitle, Guest Info). "
        "Do not include any Markdown formatting blocks (like ```markdown), "
        "just return the raw text with clear section headers like [Main Title]."
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=[prompt, img]
        )
        extracted_text = response.text
    except Exception as e:
        print(f"Error during extraction: {e}")
        sys.exit(1)

    md_content = "---\n"
    md_content += f'base_image: "{image_path}"\n'
    if original_prompt:
        md_content += f'original_prompt: "{original_prompt}"\n'
    if reference_images:
        md_content += "reference_images:\n"
        for ref in reference_images:
            md_content += f'  - "{ref}"\n'
            
    # Save original text safely so it can be used for diffing later without breaking yaml
    # We must properly escape newlines and quotes to prevent YAML parsing errors
    safe_extracted = extracted_text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    md_content += f'original_text: "{safe_extracted}"\n'
    
    md_content += "---\n\n"
    md_content += "# 海报文本内容（您可以直接修改以下文字）\n\n"
    md_content += extracted_text

    out_path = Path(image_path).with_suffix(".md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    print(f"Successfully extracted text to {out_path}")

def main():
    parser = argparse.ArgumentParser(description="Extract text from an image into a Markdown file.")
    parser.add_argument("--image", required=True, help="Path to the generated image")
    parser.add_argument("--original-prompt", help="Original prompt used to generate the image")
    parser.add_argument("--reference-images", nargs='+', help="Path(s) to original input/reference image(s)")
    
    args = parser.parse_args()
    extract_text(args.image, args.original_prompt, args.reference_images)

if __name__ == "__main__":
    main()