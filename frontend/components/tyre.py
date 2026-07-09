import math

COMPOUND_COLOURS = {
    "SOFT":         "#e8002d",  
    "MEDIUM":       "#f5c842",
    "HARD":         "#f0f0f0",
    "INTERMEDIATE": "#39b54a",
    "WET":          "#0066cc",
}

def tyre_svg(compound: str, size: int = 52, active: bool = False) -> str:
    sidewall_colour = COMPOUND_COLOURS.get(compound, "#f0f0f0")
    glow_style = f'filter: drop-shadow(0 0 6px {sidewall_colour}99);' if active else ""
    
    # Generate spokes cleanly
    spokes = []
    for i in range(8):
        angle = math.radians(i * 45)
        x2 = f"{32 + 11 * math.cos(angle):.1f}"
        y2 = f"{32 + 11 * math.sin(angle):.1f}"
        spokes.append(f'<line x1="32" y1="32" x2="{x2}" y2="{y2}" stroke="#555" stroke-width="2.5" stroke-linecap="round" />')
    spokes_html = "".join(spokes)
    
    # CRITICAL: Keeping this entirely flat against the left margin removes the markdown "code block" trigger
    svg_string = (
        f'<svg width="{size}" height="{size}" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" style="{glow_style}">'
        f'<circle cx="32" cy="32" r="30" fill="#1a1a1a" stroke="#333" stroke-width="1" />'
        f'<circle cx="32" cy="32" r="25" fill="none" stroke="{sidewall_colour}" stroke-width="3.5" />'
        f'<circle cx="32" cy="32" r="20" fill="#111" stroke="#2a2a2a" stroke-width="1" />'
        f'<circle cx="32" cy="32" r="13" fill="#222" stroke="#444" stroke-width="1.5" />'
        f'{spokes_html}'
        f'<circle cx="32" cy="32" r="4" fill="#666" />'
        f'</svg>'
    )
    
    return svg_string