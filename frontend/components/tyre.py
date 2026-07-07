# PIRELLI TYRE SVG FUNCTION

def tyre_svg(compound: str, size: int = 64, active: bool = False) -> str:
    """
    Generate a Pirelli tyre SVG with the correct compound sidewall colour
    """
    
    colours = {
        "SOFT":         "#e8002d",
        "MEDIUM":       "#f5c842",
        "HARD":         "#f0f0f0",
        "INTERMEDIATE": "#39b54a",
        "WET":          "#0066cc",
        
    }
    sidewall = colours.get(compound, "@f0f0f0")
    glow = f'filter: drop-shadow(0 0 6px {sidewall}88);' if active else ""
    
    return f"""
<svg width = "{size}" height = "{size}" viewBox = " 0 0 64 64"
    xmlns = "https://www.w3.org/2000/svg" style = "{glow}">
    
    
"""

    