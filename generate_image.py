import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Try importing the Google GenAI SDK
try:
    from google import genai
    from google.genai import types
    from PIL import Image
    import io
except ImportError:
    print("Error: 'google-genai' or 'pillow' not found. Please install them:")
    print("pip install google-genai pillow")
    sys.exit(1)

# 编辑类 prompt 模板：局部修改时保持其余不变
EDIT_PROMPT_TEMPLATE = (
    "Change ONLY: {user_instruction}. "
    "Keep identical: subject, composition/crop, pose, lighting, color palette, background, text, and overall style. "
    "Do not add new objects. If text exists, keep it unchanged."
)


def generate_image(prompt, model, aspect_ratio, output_path, number, input_image_paths=None, resolution="1K", use_edit_template=False):
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    
    # Check for .env file in script directory if env var not set
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        try:
            with open(env_path, "r") as f:
                for line in f:
                    if line.strip().startswith("GOOGLE_API_KEY=") and not api_key:
                        api_key = line.strip().split("=", 1)[1].strip('"').strip("'")
                    if line.strip().startswith("GEMINI_OUTPUT_DIR="):
                        val = line.strip().split("=", 1)[1].strip('"').strip("'")
                        if not os.environ.get("GEMINI_OUTPUT_DIR"):
                            os.environ["GEMINI_OUTPUT_DIR"] = val
        except Exception:
            pass

    if not api_key:
        print("Error: GOOGLE_API_KEY or GEMINI_API_KEY environment variable not set.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    resolution = (resolution or "1K").upper()
    if resolution not in ("1K", "2K", "4K"):
        resolution = "1K"

    effective_prompt = prompt
    if input_image_paths and use_edit_template:
        effective_prompt = EDIT_PROMPT_TEMPLATE.format(user_instruction=prompt)
        print("Using edit prompt template (preserve unchanged areas)")

    print(f"Generating {number} image(s) with model '{model}'...")
    print(f"Resolution: {resolution}")
    print(f"Prompt: {effective_prompt}")
    print(f"Aspect Ratio: {aspect_ratio}")
    if input_image_paths:
        print(f"Input Images: {input_image_paths}")
        for path in input_image_paths:
            if not os.path.exists(path):
                 print(f"Error: Input image file not found: {path}")
                 sys.exit(1)

    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    if ("imagen" in model.lower() or "veo" in model.lower()) and not input_image_paths:
        print(f"Using generate_images for {model}...")
        try:
            response = client.models.generate_images(
                model=model,
                prompt=effective_prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=number,
                    aspect_ratio=aspect_ratio,
                    image_size=resolution,
                    safety_filter_level="block_low_and_above",
                    person_generation="allow_adult",
                )
            )
            for i, generated_image in enumerate(response.generated_images):
                image = Image.open(io.BytesIO(generated_image.image.image_bytes))
                save_image(image, output_path, output_dir, number, i)
        except Exception as e:
            print(f"Error with generate_images: {e}")
            if hasattr(e, 'response'):
                 print(f"API Response: {e.response}")
            sys.exit(1)

    else:
        print(f"Using generate_content for {model} (Multimodal)...")
        contents = [effective_prompt]
        if input_image_paths:
            for path in input_image_paths:
                try:
                    img = Image.open(path)
                    contents.append(img)
                    print(f"Image loaded: {path}")
                except Exception as e:
                    print(f"Error loading input image '{path}': {e}")
                    sys.exit(1)

        for i in range(number):
            print(f"Generating image {i+1}/{number} using generate_content...")
            try:
                sys_instruction = "You are a creative AI that generates high-resolution, detailed images. If an input image is provided, use it as a strict reference for composition and style."
                config = None
                if hasattr(types, "ImageConfig"):
                    try:
                        config = types.GenerateContentConfig(
                            response_modalities=["IMAGE"],
                            image_config=types.ImageConfig(
                                aspect_ratio=aspect_ratio,
                                image_size=resolution,
                            ),
                            system_instruction=sys_instruction,
                        )
                    except (TypeError, AttributeError):
                        pass
                if config is None:
                    contents[0] = f"{contents[0]}, aspect ratio {aspect_ratio}, {resolution} resolution, detailed"
                    config = types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                        system_instruction=sys_instruction,
                    )

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
                                save_image(image, output_path, output_dir, number, i)
                                image_found = True
                                break
                            except Exception as e:
                                print(f"Error processing inline image: {e}")

                if not image_found:
                    print(f"Warning: No image found in response for generation {i+1}")
                    if response.text:
                        print(f"Model text response: {response.text}")
            except Exception as e:
                print(f"Error with generate_content: {e}")
                if hasattr(e, 'response'):
                     print(f"API Response: {e.response}")
                sys.exit(1)

def save_image(image, output_path, output_dir, number, index):
    if number > 1:
        base_name = Path(output_path).stem
        ext = Path(output_path).suffix or ".png"
        final_path = output_dir / f"{base_name}_{index+1}{ext}"
    else:
        final_path = output_path
    image.save(final_path)
    print(f"Image saved to: {final_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate images using Gemini API")
    parser.add_argument("--prompt", required=True, help="Text description of the image")
    parser.add_argument("--model", default="gemini-3.1-flash-image-preview", help="Model name")
    parser.add_argument("--aspect-ratio", default="1:1", choices=["1:1", "16:9", "9:16", "4:3", "3:4", "21:9"], help="Aspect ratio")
    parser.add_argument("--resolution", default="1K", choices=["1K", "2K", "4K"], help="Output resolution: 1K|2K|4K")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--input-image", nargs='+', help="Path(s) to input image(s)")
    parser.add_argument("--edit-template", action="store_true", help="Use edit template to preserve unchanged areas")
    parser.add_argument("--number", type=int, default=1, help="Number of images to generate (1-4)")

    args = parser.parse_args()

    if not args.output:
        date_str = datetime.now().strftime("%Y%m%d")
        safe_prompt = "".join(c for c in args.prompt[:50] if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
        filename = f"{date_str}_{safe_prompt}.png"
        output_base = os.environ.get("GEMINI_OUTPUT_DIR") or "output"
        output_dir = Path(output_base) / "images"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / filename
    else:
        output_path = Path(args.output)

    generate_image(
        args.prompt,
        args.model,
        args.aspect_ratio,
        output_path,
        args.number,
        args.input_image,
        resolution=args.resolution,
        use_edit_template=args.edit_template,
    )

if __name__ == "__main__":
    main()
