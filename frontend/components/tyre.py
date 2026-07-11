"""
components/tyre.py
Pirelli tyre SVG generator.
"""
import math

COMPOUND_COLOURS = {
    "SOFT":         "#e8002d",
    "MEDIUM":       "#f5c842",
    "HARD":         "#f0f0f0",
    "INTERMEDIATE": "#39b54a",
    "WET":          "#0066cc",
}

def tyre_svg(compound: str, size: int = 64, active: bool = False) -> str:
    colour = COMPOUND_COLOURS.get(compound, "#f0f0f0")
    glow = f"filter:drop-shadow(0 0 8px {colour}88);" if active else ""
    spokes = "".join([
        f'<line x1="32" y1="32" x2="{32+11*math.cos(math.radians(i*45)):.1f}" y2="{32+11*math.sin(math.radians(i*45)):.1f}" stroke="#666" stroke-width="2.5" stroke-linecap="round"/>'
        for i in range(8)
    ])
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" style="{glow}">'
        f'<circle cx="32" cy="32" r="30" fill="#1a1a1a" stroke="#2a2a2a" stroke-width="1"/>'
        f'<circle cx="32" cy="32" r="30" fill="none" stroke="{colour}" stroke-width="5"/>'
        f'<circle cx="32" cy="32" r="20" fill="#111" stroke="#222" stroke-width="1"/>'
        f'<circle cx="32" cy="32" r="13" fill="#252525" stroke="#444" stroke-width="1.5"/>'
        f'{spokes}'
        f'<circle cx="32" cy="32" r="4" fill="#777"/>'
        f'</svg>'
    )