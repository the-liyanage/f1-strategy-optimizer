# PIRELLI TYRE SVG FUNCTION
import math

# compound sidewall colours - official Pirelli colour coding
# these match the real tyre used in F1
COMPOUND_COLOURS = {
        "SOFT":         "#e8002d",  
        "MEDIUM":       "#f5c842",
        "HARD":         "#f0f0f0",
        "INTERMEDIATE": "#39b54a",
        "WET":          "#0066cc",
    }
    

def tyre_svg(compound: str,  size: int = 52,  active: bool = False) -> str:
    """
    generate an inline SVG of a Pirelli tyre with correct compound colours.
    
    HOW IT WORKS: 
    the tyre is built from four concentruc circles:
        1. outer tyre (dark grey)   - the rubber
        2. sidewall ring (compound colour)  - the colour coded stripe
        3. inner tyre wall (dark)   - seperates rubber from rim
        4. rim (medium gray)    - the wheel
        
        
    eight (8) spokes are drawn from the centre at 45 - degree intervals,
    calulated using trig (cos/sin for x/y coordinates)
    
    the viewBox is always 0 0 64 64 regardless of size 
    the size parameter just scaled the rendered output.
    this keeps the SVG coordinates simple and consistent
    
    
    Args:
        compound:   one of SOFT, MEDIUM, HARD, INTERMEDIATE, WET
        size:       pixel dimensions (width - height)
        active:     if True, adds a colour matched glow shadow 
                    used to highlight the recommended compound in the card
    """
    

    sidewall_colour = COMPOUND_COLOURS.get(compound, "#f0f0f0")
    
    # glow effwcr for active/ selected state
    # uses CSS drop-shadow filter 
    glow_style = (
        f'filter: drop-shadow(0 0 6px {sidewall_colour}99);'
        if active else ""
    )
    
    
    # generate 8 spokes evenly spaces at 45 intervals
    # each spoke does from the centre (32, 32) outward to radius 11
    # SPOKES ====
    spokes_html = "".join([
          f'line'
          f'x1="32" y1="32" '
          f'x2="{32 + 11* math.cos(math.radians(i*45)):.1f}"'
          f'y2="{32 + 12* math.sin(math.radians(i*45)):.1f}" '
          f'stroke="#555" stroke-width="2.5" stroke-linecap="round"/>'
          for i in range(8)
      ])
    
    
    return f"""
    <svg 
        width = "{size}"
        height = "{size}"
        viewBow = "0 0 64 64"
        xmlns = "http://www.w3.org/2000/svg"
        style = "{glow_style}"
    >
    
        <!-- outer tyre rubber -->
        <circle
        cx = "32"
        cy = "32"
        r = "30"
        fill = "1a1a1a"
        stroke = "#333"
        stroke-width = "1"
         />
    
        <!-- sidewall compound-colour ring -->
        <circle 
        cx = "32"
        cy = "32"
        r = "30"
        fill = "none"
        stroke = "{sidewall_colour}"
        stroke-width = "5"
        />
    
        <!-- inner tyre wall -->
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
        r = "13"
        fill = "#222"
        stroke = "#444"
        stroke-width = "1.5"
        />
    
    
        <!-- spokes -->
        {spokes_html}
      
      
    
         <!-- centre hub -->
        <circle 
        cx = "32"
        cy = "32"
        r = "4"
        fill = "#666"
    />
    </svg>
"""
    