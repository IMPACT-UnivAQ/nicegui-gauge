"""
Generate background PNG images for gauges
Creates circular and semicircular gauge backgrounds
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("PIL/Pillow not available. Install with: pip install Pillow")
    print("Creating placeholder files instead...")


def generate_circular_background(size=220, output_path='assets/gauge_background_speed.png'):
    """Generate circular gauge background"""
    if not HAS_PIL:
        # Create empty file as placeholder
        with open(output_path, 'w') as f:
            pass
        return
    
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    center_x, center_y = size // 2, size // 2
    radius = size // 2 - 10
    
    # Draw outer circle
    draw.ellipse(
        [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
        fill=(240, 240, 240, 255),
        outline=(200, 200, 200, 255),
        width=2
    )
    
    # Draw inner circle (cutout)
    inner_radius = radius * 0.6
    draw.ellipse(
        [center_x - inner_radius, center_y - inner_radius,
         center_x + inner_radius, center_y + inner_radius],
        fill=(255, 255, 255, 255),
        outline=(200, 200, 200, 255),
        width=1
    )
    
    # Draw tick marks
    num_ticks = 12
    for i in range(num_ticks):
        angle = (i / num_ticks) * 360 - 90  # Start from top
        angle_rad = math.radians(angle)
        
        # Tick positions
        inner_tick = radius * 0.85
        outer_tick = radius * 0.95
        
        x1 = center_x + inner_tick * math.cos(angle_rad)
        y1 = center_y + inner_tick * math.sin(angle_rad)
        x2 = center_x + outer_tick * math.cos(angle_rad)
        y2 = center_y + outer_tick * math.sin(angle_rad)
        
        draw.line([(x1, y1), (x2, y2)], fill=(100, 100, 100, 255), width=2)
    
    # Draw major tick marks (every 3rd)
    for i in range(0, num_ticks, 3):
        angle = (i / num_ticks) * 360 - 90
        angle_rad = math.radians(angle)
        
        inner_tick = radius * 0.80
        outer_tick = radius * 0.98
        
        x1 = center_x + inner_tick * math.cos(angle_rad)
        y1 = center_y + inner_tick * math.sin(angle_rad)
        x2 = center_x + outer_tick * math.cos(angle_rad)
        y2 = center_y + outer_tick * math.sin(angle_rad)
        
        draw.line([(x1, y1), (x2, y2)], fill=(50, 50, 50, 255), width=3)
    
    # Save image
    img.save(output_path, 'PNG')
    print(f"Generated: {output_path}")


def generate_semicircular_background(size=220, output_path='assets/gauge_background_heading.png'):
    """Generate semicircular gauge background"""
    if not HAS_PIL:
        # Create empty file as placeholder
        with open(output_path, 'w') as f:
            pass
        return
    
    import math
    
    # Create image - height is half for semicircle
    img = Image.new('RGBA', (size, size // 2), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    center_x, center_y = size // 2, size // 2  # Center horizontally, but at bottom
    radius = size // 2 - 10
    
    # Draw semicircle arc
    # Create bounding box for arc
    bbox = [center_x - radius, center_y - radius, center_x + radius, center_y + radius]
    
    # Draw filled semicircle (bottom half)
    # We'll draw a path for the semicircle
    points = []
    for i in range(181):  # 180 degrees + 1
        angle = math.radians(i - 90)  # -90 to 90 degrees
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append((x, y))
    
    # Draw filled semicircle
    draw.polygon(points, fill=(240, 240, 240, 255))
    draw.line(points, fill=(200, 200, 200, 255), width=2)
    
    # Draw inner arc (cutout)
    inner_radius = radius * 0.6
    inner_points = []
    for i in range(181):
        angle = math.radians(i - 90)
        x = center_x + inner_radius * math.cos(angle)
        y = center_y + inner_radius * math.sin(angle)
        inner_points.append((x, y))
    
    draw.polygon(inner_points, fill=(255, 255, 255, 255))
    draw.line(inner_points, fill=(200, 200, 200, 255), width=1)
    
    # Draw tick marks (semicircle: 0-180 degrees)
    num_ticks = 9
    for i in range(num_ticks + 1):
        angle_deg = (i / num_ticks) * 180 - 90  # -90 to 90 degrees
        angle_rad = math.radians(angle_deg)
        
        inner_tick = radius * 0.85
        outer_tick = radius * 0.95
        
        x1 = center_x + inner_tick * math.cos(angle_rad)
        y1 = center_y + inner_tick * math.sin(angle_rad)
        x2 = center_x + outer_tick * math.cos(angle_rad)
        y2 = center_y + outer_tick * math.sin(angle_rad)
        
        draw.line([(x1, y1), (x2, y2)], fill=(100, 100, 100, 255), width=2)
    
    # Draw major tick marks
    for i in range(0, num_ticks + 1, 2):
        angle_deg = (i / num_ticks) * 180 - 90
        angle_rad = math.radians(angle_deg)
        
        inner_tick = radius * 0.80
        outer_tick = radius * 0.98
        
        x1 = center_x + inner_tick * math.cos(angle_rad)
        y1 = center_y + inner_tick * math.sin(angle_rad)
        x2 = center_x + outer_tick * math.cos(angle_rad)
        y2 = center_y + outer_tick * math.sin(angle_rad)
        
        draw.line([(x1, y1), (x2, y2)], fill=(50, 50, 50, 255), width=3)
    
    # Save image
    img.save(output_path, 'PNG')
    print(f"Generated: {output_path}")


if __name__ == '__main__':
    import math
    import os
    
    # Create assets directory if it doesn't exist
    os.makedirs('assets', exist_ok=True)
    
    # Generate backgrounds
    generate_circular_background()
    generate_semicircular_background()
    
    print("Background generation complete!")

