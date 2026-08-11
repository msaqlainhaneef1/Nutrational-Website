from PIL import Image, ImageDraw

def draw_round_line(draw, points, width, color):
    # Draw the lines
    draw.line(points, fill=color, width=width)
    # Draw circles at each point to round the joints and end caps
    r = width / 2
    for p in points:
        draw.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=color)

def create_favicon():
    # Create a high-res 2048x2048 transparent image
    hi_res = Image.new("RGBA", (2048, 2048), (0, 0, 0, 0))
    draw = ImageDraw.Draw(hi_res)

    # 1. Background Rounded Square (green #10b981)
    bg_color = (16, 185, 129, 255)
    draw.rounded_rectangle([64, 64, 1984, 1984], radius=448, fill=bg_color)

    # 2. Generate Leaf Points (Bezier curves)
    left_points = []
    right_points = []
    
    # Left curve: from top (1024, 192) to bottom (1024, 1856)
    p0 = (1024, 192)
    p1 = (448, 576)
    p2 = (448, 1472)
    p3 = (1024, 1856)
    
    for i in range(41):
        t = i / 40.0
        x = (1-t)**3 * p0[0] + 3*(1-t)**2*t * p1[0] + 3*(1-t)*t**2 * p2[0] + t**3 * p3[0]
        y = (1-t)**3 * p0[1] + 3*(1-t)**2*t * p1[1] + 3*(1-t)*t**2 * p2[1] + t**3 * p3[1]
        left_points.append((x, y))

    # Right curve: from bottom (1024, 1856) to top (1024, 192)
    p0_r = (1024, 1856)
    p1_r = (1600, 1472)
    p2_r = (1600, 576)
    p3_r = (1024, 192)
    
    for i in range(41):
        t = i / 40.0
        x = (1-t)**3 * p0_r[0] + 3*(1-t)**2*t * p1_r[0] + 3*(1-t)*t**2 * p2_r[0] + t**3 * p3_r[0]
        y = (1-t)**3 * p0_r[1] + 3*(1-t)**2*t * p1_r[1] + 3*(1-t)*t**2 * p2_r[1] + t**3 * p3_r[1]
        right_points.append((x, y))

    # Combine to make closed leaf polygon
    leaf_points = left_points + right_points + [left_points[0]]

    # 3. Draw Leaf Fill (semi-transparent white)
    draw.polygon(leaf_points, fill=(255, 255, 255, 38))

    # 4. Draw Leaf Outline (white)
    draw_round_line(draw, leaf_points, width=144, color=(255, 255, 255, 255))

    # 5. Draw Center Stem
    draw_round_line(draw, [(1024, 1856), (1024, 1408)], width=144, color=(255, 255, 255, 255))

    # 6. Draw Checkmark
    draw_round_line(draw, [(576, 960), (896, 1344), (1536, 576)], width=192, color=(255, 255, 255, 255))

    # Resize to 256x256 using Lanczos for perfect anti-aliased output
    icon_256 = hi_res.resize((256, 256), Image.Resampling.LANCZOS)
    
    # Save as multi-size ICO
    icon_256.save("public/favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (256, 256)])
    print("New high-quality favicon generated successfully.")

if __name__ == "__main__":
    create_favicon()
