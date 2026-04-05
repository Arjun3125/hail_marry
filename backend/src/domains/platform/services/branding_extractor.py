from colorthief import ColorThief
import io

def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    """Convert an RGB tuple to a hex string."""
    return "#{:02x}{:02x}{:02x}".format(*rgb).upper()

def get_luminance(rgb: tuple[int, int, int]) -> float:
    """Calculate the relative luminance of a color according to WCAG 2.1."""
    a = [c / 255.0 for c in rgb]
    for i, c in enumerate(a):
        if c <= 0.03928:
            a[i] = c / 12.92
        else:
            a[i] = ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2]

def get_contrast_ratio(color1: tuple[int, int, int], color2: tuple[int, int, int]) -> float:
    """Calculate the contrast ratio between two colors."""
    lum1 = get_luminance(color1)
    lum2 = get_luminance(color2)
    brightest = max(lum1, lum2)
    darkest = min(lum1, lum2)
    return (brightest + 0.05) / (darkest + 0.05)

def suggest_text_color(bg_rgb: tuple[int, int, int]) -> str:
    """
    Returns either white or dark gray depending on the background color luminance
    to ensure WCAG AA compliant contrast ratio (>= 4.5:1).
    """
    white = (255, 255, 255)
    dark_gray = (31, 41, 55)  # Tailwind gray-800
    
    if get_contrast_ratio(bg_rgb, white) >= 4.5:
        return rgb_to_hex(white)
    return rgb_to_hex(dark_gray)

def extract_brand_palette(image_bytes: bytes) -> dict:
    """
    Given an image file byte stream, uses colorthief to extract the dominant
    color (primary) and an additional color from the palette for secondary/accent.
    Returns suggested text colors that mathematically contrast well.
    """
    # ColorThief requires a file-like object
    img_stream = io.BytesIO(image_bytes)
    
    try:
        color_thief = ColorThief(img_stream)
        
        # 1. Primary (Dominant Color)
        primary_rgb = color_thief.get_color(quality=1)
        
        # 2. Get a palette to select secondary/accent
        # A quality of 1 means highest accuracy (slowest but fine for logos)
        palette = color_thief.get_palette(color_count=5, quality=1)
        
        # Determine Secondary
        # Pick the most distinct color from primary by calculating distance
        # For simplicity, we just pick the second item in the palette if it's there
        secondary_rgb = palette[1] if len(palette) > 1 else primary_rgb
        
        # Background fallback (usually a light/white color if present)
        # We assume the user wants standard brand colors.
        
        primary_hex = rgb_to_hex(primary_rgb)
        secondary_hex = rgb_to_hex(secondary_rgb)
        
        return {
            "primary": primary_hex,
            "primary_content": suggest_text_color(primary_rgb),
            "secondary": secondary_hex,
            "secondary_content": suggest_text_color(secondary_rgb)
        }
    except Exception as e:
        print(f"Error extracting colors: {e}")
        # Return fallback default colors
        return {
            "primary": "#4f46e5",
            "primary_content": "#ffffff",
            "secondary": "#10b981",
            "secondary_content": "#ffffff"
        }
