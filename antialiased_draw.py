# Anti-aliased drawing utilities for pygame
import pygame
import pygame.gfxdraw

def draw_antialiased_circle(surface, color, center, radius):
    """
    Draw an anti-aliased circle using pygame.gfxdraw
    
    Args:
        surface: The surface to draw on
        color: RGB color tuple (r, g, b)
        center: Center position tuple (x, y)
        radius: Circle radius
    """
    x, y = int(center[0]), int(center[1])
    radius = int(radius)
    
    # Ensure color is a 3-tuple
    if len(color) == 4:
        color = color[:3]  # Remove alpha if present
    
    # Draw filled circle with anti-aliasing
    try:
        # Draw the filled circle
        pygame.gfxdraw.filled_circle(surface, x, y, radius, color)
        # Draw the anti-aliased edge
        pygame.gfxdraw.aacircle(surface, x, y, radius, color)
    except (ValueError, OverflowError):
        # Fallback to regular circle if gfxdraw fails (e.g., radius too large)
        pygame.draw.circle(surface, color, (x, y), radius)

def draw_antialiased_circle_outline(surface, color, center, radius, width=1):
    """
    Draw an anti-aliased circle outline
    
    Args:
        surface: The surface to draw on
        color: RGB color tuple (r, g, b)
        center: Center position tuple (x, y)
        radius: Circle radius
        width: Line width (note: gfxdraw doesn't support width, so this uses regular pygame for thick lines)
    """
    x, y = int(center[0]), int(center[1])
    radius = int(radius)
    
    # Ensure color is a 3-tuple
    if len(color) == 4:
        color = color[:3]  # Remove alpha if present
    
    try:
        if width == 1:
            # Use anti-aliased drawing for single pixel width
            pygame.gfxdraw.aacircle(surface, x, y, radius, color)
        else:
            # For thick lines, use regular pygame (no anti-aliasing available)
            pygame.draw.circle(surface, color, (x, y), radius, width)
    except (ValueError, OverflowError):
        # Fallback to regular circle
        pygame.draw.circle(surface, color, (x, y), radius, width)

def draw_antialiased_rect(surface, color, rect):
    """
    Draw an anti-aliased rectangle (filled)
    Note: gfxdraw doesn't have built-in anti-aliased rectangles,
    so this is a basic implementation
    
    Args:
        surface: The surface to draw on
        color: RGB color tuple (r, g, b)
        rect: Rectangle (x, y, width, height)
    """
    # For rectangles, we'll use regular pygame as gfxdraw doesn't provide
    # anti-aliased rectangles. We could implement our own, but it's complex.
    pygame.draw.rect(surface, color, rect)
