import math
from PIL import Image, ImageDraw, ImageFilter

def create_liquid_glass_insta_icon(output_path, size=1024):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Base dark rounded background (OLED True Black #08080A)
    corner_radius = int(size * 0.225) # Standard Apple squircle approx
    draw.rounded_rectangle([0, 0, size, size], radius=corner_radius, fill=(8, 8, 12, 255))

    # 2. Subtle Liquid Glass Gradient glow behind the icon
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    
    # Sunset-magenta / Electric violet / Cyan liquid glow
    center_x, center_y = size // 2, size // 2
    for r in range(int(size * 0.45), int(size * 0.15), -4):
        alpha = int(35 * (1.0 - (r - size * 0.15) / (size * 0.30)))
        # Radial blend from vibrant pink-orange to deep violet
        glow_draw.ellipse(
            [center_x - r, center_y - r, center_x + r, center_y + r],
            fill=(230, 60, 140, max(0, alpha))
        )
    glow = glow.filter(ImageFilter.GaussianBlur(radius=30))
    img.alpha_composite(glow)

    # 3. Translucent frosted glass card in center
    card_margin = int(size * 0.14)
    card_radius = int(size * 0.18)
    glass_card = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glass_draw = ImageDraw.Draw(glass_card)

    glass_draw.rounded_rectangle(
        [card_margin, card_margin, size - card_margin, size - card_margin],
        radius=card_radius,
        fill=(255, 255, 255, 18),
        outline=(255, 255, 255, 70),
        width=int(size * 0.008)
    )

    # Specular glass reflection top highlight
    highlight = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    high_draw = ImageDraw.Draw(highlight)
    high_draw.chord(
        [card_margin - 40, card_margin - 80, size - card_margin + 40, size // 2 + 30],
        start=0, end=180,
        fill=(255, 255, 255, 24)
    )
    # Mask highlight to stay within card
    card_mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(card_mask)
    mask_draw.rounded_rectangle(
        [card_margin, card_margin, size - card_margin, size - card_margin],
        radius=card_radius,
        fill=255
    )
    glass_card.paste(highlight, (0, 0), card_mask)
    img.alpha_composite(glass_card)

    # 4. Modern Minimalist Camera Glyph (Frosted White with Soft Glow)
    glyph = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glyph)

    cam_margin = int(size * 0.28)
    cam_radius = int(size * 0.11)
    line_w = int(size * 0.038)

    # Outer camera squircle
    gdraw.rounded_rectangle(
        [cam_margin, cam_margin, size - cam_margin, size - cam_margin],
        radius=cam_radius,
        outline=(255, 255, 255, 240),
        width=line_w
    )

    # Center lens circle
    lens_r = int(size * 0.13)
    gdraw.ellipse(
        [center_x - lens_r, center_y - lens_r, center_x + lens_r, center_y + lens_r],
        outline=(255, 255, 255, 240),
        width=line_w
    )

    # Camera flash dot
    dot_x = int(size * 0.655)
    dot_y = int(size * 0.345)
    dot_r = int(size * 0.024)
    gdraw.ellipse(
        [dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r],
        fill=(255, 255, 255, 240)
    )

    # Add soft drop shadow to glyph for float effect
    shadow = glyph.filter(ImageFilter.GaussianBlur(radius=8))
    img.alpha_composite(shadow)
    img.alpha_composite(glyph)

    # Save 1024x1024 icon
    img.save(output_path, "PNG")
    print(f"Generated Liquid Glass icon at {output_path}")

if __name__ == '__main__':
    create_liquid_glass_insta_icon(r'C:\Users\gusta\.gemini\antigravity\scratch\lucid-insta\AppIcon1024.png')
