# 海报 Prompt 模板 — 混沌风格最佳实践
# 用法: from prompt_templates import PosterTemplate; t = PosterTemplate(); print(t.build())

class PosterTemplate:
    """
    生成海报的 prompt 模板，内置混沌风格排版规则。
    自动保证：中文字清晰、层级分明、留白充足、无乱码。
    """

    # 排版规则（已验证有效的参数）
    TYPOGRAPHY_RULES = """
CRITICAL TYPOGRAPHY — always include these in every poster prompt:
1. Chinese text must be PERFECTLY CLEAR, no garbled characters, no乱码
2. Title text = BOLD or HEAVY weight (main visual anchor)
3. Body text = LIGHT weight (细体), NOT medium or bold — think 混沌 style
4. Line height = 2x for body text (generous breathing room)
5. Section spacing = 40px+ between major blocks
6. NO standalone words extracted from phrases (e.g. "理清" alone is wrong, only within "帮你理清生意")
7. NO background watermarks
8. Minimalist: high negative space, refined, clean

AESTHETIC: 混沌 style — minimalist, high negative space, breathable, refined.
"""

    @staticmethod
    def build(
        product_name: str,
        hook_line: str,
        slogan: str,
        philosophy: list[str],
        services: list[dict],  # [{"num": "01", "label": "【看懂方向】", "title": "xxx", "desc": "xxx"}, ...]
        founder_cred: list[str],
        team_cred: str,
        audience: list[str],
        pricing: dict,  # {"original": "¥2980", "price": "¥1980", "badge": "前50名限额特惠"}
        sections: list[str] = None,  # optional custom section descriptions
    ) -> str:
        """
        Build a complete poster prompt.
        """
        # Section 1 - Hook
        section1 = f"""SECTION 1 (~15%): {product_name} logo centered top. Below: {product_name} in large bold gold. Then: {hook_line} in extra-large bold gold. Gold divider line below."""

        # Section 2 - Philosophy
        phil_lines = "\n".join(f"{s} /" for s in philosophy)
        section2 = f"""SECTION 2 (~18%): {slogan} in medium white. Philosophy in LIGHT weight white, 2x line height, each on its own line: {phil_lines} Gold divider."""

        # Section 3 - Services
        service_cards = ""
        for svc in services:
            service_cards += f"/ {svc['num']} {svc['label']}{svc['title']} + description in LIGHT grey (not bold): {svc['desc']} /"
        section3 = f"""SECTION 3 (~27%): 服务内容 header in gold. 4 service cards with 30px+ spacing between: {service_cards} Cards: dark grey bg (#1A1A1A), thin gold border. Gold divider."""

        # Section 4 - Founder
        cred_lines = " / ".join(founder_cred)
        section4 = f"""SECTION 4 (~25%): Founder photo with gold border, rounded rect. Credentials in LIGHT weight white, 1.8x line height: {cred_lines}. Gold box: {team_cred}"""

        # Section 5 - Conversion
        aud_lines = " / ".join(audience)
        section5 = f"""SECTION 5 (~15%): 适合人群 header in gold. 4 items in LIGHT white, 2x line height: {aud_lines}. Pricing: {pricing['original']} grey strikethrough next to {pricing['price']} bold red with badge {pricing['badge']}. Bottom: logo small centered."""

        return f"""{PosterTemplate.TYPOGRAPHY_RULES}

5 SECTIONS top to bottom:

{section1}

{section2}

{section3}

{section4}

{section5}
"""
