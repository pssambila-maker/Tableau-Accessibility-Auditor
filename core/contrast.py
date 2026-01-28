def get_relative_luminance(rgb):
    """
    Calculates the relative luminance of an RGB color.
    rgb: tuple of (R, G, B) in range 0-255.
    """
    srgb = [v / 255.0 for v in rgb]
    linear = []
    for v in srgb:
        if v <= 0.03928:
            linear.append(v / 12.92)
        else:
            linear.append(((v + 0.055) / 1.055) ** 2.4)
    
    r, g, b = linear
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def get_contrast_ratio(rgb1, rgb2):
    """
    Calculates the contrast ratio between two RGB colors.
    """
    l1 = get_relative_luminance(rgb1)
    l2 = get_relative_luminance(rgb2)
    
    if l1 < l2:
        l1, l2 = l2, l1
        
    return (l1 + 0.05) / (l2 + 0.05)

def check_compliance(rgb1, rgb2, level="AA", text_size="normal"):
    """
    Checks if the contrast ratio meets WCAG standards.
    """
    ratio = get_contrast_ratio(rgb1, rgb2)
    
    if level == "AA":
        target = 4.5 if text_size == "normal" else 3.0
    else: # AAA
        target = 7.0 if text_size == "normal" else 4.5
        
    return ratio >= target, ratio
