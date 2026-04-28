import argparse
import os
import sys
from pathlib import Path

try:
    from google import genai
    from google.genai import types
    from PIL import Image
    import io
except ImportError:
    print("Error: 'google-genai' or 'pillow' not found.")
    sys.exit(1)

def parse_md(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if not content.startswith("---"):
        print("Error: Markdown file must start with YAML frontmatter (---)")
        sys.exit(1)
        
    parts = content.split("---", 2)
    if len(parts) < 3:
        print("Error: Malformed YAML frontmatter.")
        sys.exit(1)
        
    frontmatter = parts[1].strip()
    text_content = parts[2].strip()
    
    meta = {}
    lines = frontmatter.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            
            # Handle quoted strings and basic unescaping
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1].replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
            elif val.startswith("'") and val.endswith("'"):
                val = val[1:-1].replace("\\n", '\n').replace("\\'", "'").replace('\\\\', '\\')
                
            if not val and i + 1 < len(lines) and lines[i+1].strip().startswith("-"):
                refs = []
                i += 1
                while i < len(lines) and lines[i].strip().startswith("-"):
                    refs.append(lines[i].strip()[1:].strip().strip('"').strip("'"))
                    i += 1
                meta[key] = refs
                continue
            else:
                meta[key] = val
        i += 1
        
    # Remove instructional headers from new_text so it isn't rendered in the image
    instructional_header = "# 海报文本内容（您可以直接修改以下文字）"
    if instructional_header in text_content:
        new_text_clean = text_content.split(instructional_header, 1)[1].strip()
    else:
        new_text_clean = text_content.strip()
        
    return meta, new_text_clean

def get_original_text(client, image_path):
    print("Extracting original text for diffing...")
    try:
        # Avoid using PIL Image directly in generate_content if it hangs, use upload or bytes
        with open(image_path, "rb") as f:
            image_bytes = f.read()
            
        prompt = "Extract all text from this image exactly as written. Return ONLY the text."
        
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=[prompt, types.Part.from_bytes(data=image_bytes, mime_type='image/png')]
        )
        return response.text
    except Exception as e:
        print(f"Warning: Could not extract original text: {e}")
        return ""

def get_diff_instruction(client, old_text, new_text):
    print("Computing text differences...")
    try:
        prompt = f"""Compare the following original text from an image with the new target text.
Identify exactly what changed. 

Original text:
{old_text}

Target text:
{new_text}

Return ONLY a concise, direct instruction for an image editor. 
Example format: 'Change the text "Old Words" to "New Words". Do not change any other text.'
If there are multiple changes, list them clearly.
"""
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=[prompt]
        )
        return response.text.strip()
    except Exception as e:
        print(f"Warning: Could not compute diff: {e}")
        return f"Update the text to match:\n{new_text}"

def replace_text(md_path, resolution="2K", model="gpt-image-2-all"):
    meta, new_text = parse_md(md_path)
    
    base_image_path = meta.get("base_image")
    if not base_image_path or not os.path.exists(base_image_path):
        print(f"Error: Base image not found: {base_image_path}")
        sys.exit(1)
        
    reference_images = meta.get("reference_images", [])
    
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    base_url = os.environ.get("GEMINI_BASE_URL")
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        try:
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GOOGLE_API_KEY=") and not api_key:
                        api_key = line.split("=", 1)[1].strip('"').strip("'")
                    if line.startswith("GEMINI_BASE_URL=") and not base_url:
                        base_url = line.split("=", 1)[1].strip('"').strip("'")
        except Exception:
            pass

    if not api_key:
        print("Error: API key not set.")
        sys.exit(1)

    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["http_options"] = {"base_url": base_url}
    client = genai.Client(**client_kwargs)
    
    # Compare old text to new text and get diff instruction if we know old text
    old_text = meta.get("original_text", "")
    if old_text:
        print("Computing diff instruction locally based on saved original text...")
        diff_instruction = f"Specifically, find the text:\n{old_text}\n\nAnd replace it with:\n{new_text}"
    else:
        diff_instruction = f"Update the text to match exactly:\n{new_text}"
    
    contents = []
    
    constraint_prompt = (
        "Edit the provided base image. You MUST keep the overall layout, style, background, "
        "and visual elements EXACTLY as they are in the base image.\n"
    )
    if reference_images:
        constraint_prompt += "You MUST use the provided reference images exactly as they are for the character avatars.\n"
    
    constraint_prompt += (
        f"\nTEXT EDIT INSTRUCTION:\n{diff_instruction}\n\n"
        f"FULL TARGET TEXT REFERENCE:\n{new_text}\n\n"
        "IMPORTANT RULES:\n"
        "1. You MUST render the exact Chinese characters provided in the text.\n"
        "2. DO NOT translate to English. DO NOT hallucinate text.\n"
        "3. You MUST KEEP THE ORIGINAL IMAGE QUALITY, RESOLUTION, and SHARPNESS.\n"
        "4. The background MUST NOT become blurry.\n"
        "5. Keep the exact same font styles, colors, and positions as the original image, just replace the words."
    )
    
    contents.append(constraint_prompt)
    
    # Load base image
    try:
        base_image = Image.open(base_image_path)
        contents.append(base_image)
    except Exception as e:
        print(f"Error loading base image: {e}")
        sys.exit(1)
        
    # Load reference images
    for ref_path in reference_images:
        try:
            ref_image = Image.open(ref_path)
            contents.append(ref_image)
        except Exception as e:
            print(f"Error loading reference image '{ref_path}': {e}")
            sys.exit(1)

    print(f"Replacing text using model {model}...")
    
    try:
        sys_instruction = (
            "You are an expert high-resolution image editing AI. "
            "You modify ONLY the text in an image while preserving the exact original image composition, "
            "sharpness, texture, and visual fidelity. "
            "You MUST render the EXACT text provided by the user. "
            "If the user provides Chinese characters, you MUST draw those exact Chinese characters on the image. "
            "DO NOT translate to English. "
            "The output image MUST be crystal clear and maintain the original resolution quality, NOT blurry."
        )
        config = types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            system_instruction=sys_instruction,
            # We don't set aspect ratio here as we want it to match the base image
        )
        # Append resolution hint to prompt as fallback
        contents[0] = f"{contents[0]}, {resolution} resolution, detailed"

        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )

        image_found = False
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    try:
                        image_bytes = part.inline_data.data
                        image = Image.open(io.BytesIO(image_bytes))
                        
                        # Preserve base image's stem properly
                        base_stem = Path(base_image_path).stem
                        out_path = Path(md_path).with_name(f"{base_stem}_text_edited.png")
                        image.save(out_path)
                        print(f"Success! Saved edited image to {out_path}")
                        image_found = True
                        break
                    except Exception as e:
                        print(f"Error processing inline image: {e}")

        if not image_found:
            print("Warning: No image found in response.")
            if response.text:
                print(f"Model response: {response.text}")
                
    except Exception as e:
        print(f"Error generating content: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Replace text in an image based on an edited Markdown file.")
    parser.add_argument("--md-file", required=True, help="Path to the edited Markdown file")
    parser.add_argument("--resolution", default="2K", choices=["1K", "2K", "4K"], help="Output resolution")
    parser.add_argument("--model", default="gpt-image-2-all", help="Model name")
    
    args = parser.parse_args()
    replace_text(args.md_file, args.resolution, args.model)

if __name__ == "__main__":
    main()