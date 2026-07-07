# PIRELLI TYRE SVG FUNCTION

def tyre_svg(compound: str,  size: int = 64,  active: bool = False) -> str:
    """
    generate a pirelli tyre SVG with the corret compound
     sidewall color
    """
    
    colours = {
        "SOFT":         "#e8002d",
        "MEDIUM":       "#f5c842",
        "HARD":         "#f0f0f0",
        "INTERMEDIATE": "#39b54a",
        "WET":          "#0066cc",
    }
    
    sidewall = colours.get(compound, "#f0f0f0")
    glow = f'filter: drop-shadow(0 0 6px {sidewall}88);' if active else ""
    
    return f"""
    <svg 
        width = "{size}"
        height = "{size}"
        viewBow = "0 0 64 64"
        xmlns = "http://www.w3.org/2000/svg"
        style = "{glow}"
    >
    
    <!-- outer tyre -->
    <circle
        cx = "32"
        cy = "32"
        r = "30"
        fill = "1a1a1a"
        stroke = "#333"
        stroke-width = "1"
    />
    
    <!-- sidewall colour ring -->
    <circle 
        cx = "32"
        cy = "32"
        r = "30"
        fill = "none"
        stroke = "{sidewall}"
        stroke-width = "5"
    />
    
    <!-- inner tyre -->
    <circle
        cx = "32"
        cy = "32"
        r = "20"
        fill = "#111"
        stroke = "2a2a2a"
        stroke-width = "1"
    />
    
    <!-- rim -->
    <circle 
        cx = "32"
        cy = "32"
        r = "14"
        fill = "#111"
        stroke = "#444"
        stroke-width = "1.5"
    />
    
    
    <!-- spokes -->
      {"".join([
          f'<line x1="32" y1="32" x2="{32 + 12*__import__("math").cos(__import__("math").radians(i*45)):.1f}" '
          f'y2="{32 + 12*__import__("math").sin(__import__("math").radians(i*45)):.1f}" '
          f'stroke="#555" stroke-width="2.5" stroke-linecap="round"/>'
          for i in range(8)
      ])}
    
    <!-- centre hub -->
    <circle 
        cx = "32"
        cy = "32"
        r = "4"
        fill = "#666"
    />
"""
    