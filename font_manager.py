"""Font management utilities for Neural Hellwork"""
import pygame
import os
from typing import Dict, Optional

class FontManager:
    """Manages font loading and caching"""
    
    def __init__(self):
        self._fonts: Dict[str, pygame.font.Font] = {}
        self._font_path = os.path.join("assets", "Fonts", "Pulsewidth-1.0.0.otf")
        # Font size scaling - Pulsewidth font renders much larger than default pygame font
        self._size_scale = 0.5  # Scale down by 50% to match default font appearance
    
    def get_scaled_size(self, desired_size: int) -> int:
        """
        Get the scaled font size for the Pulsewidth font
        
        Args:
            desired_size: The size you want the text to appear as
            
        Returns:
            The actual font size to use for loading
        """
        return max(8, int(desired_size * self._size_scale))  # Minimum size of 8px
        
    def get_font(self, size: int = 36) -> pygame.font.Font:
        """
        Get the Pulsewidth font at the specified size
        
        Args:
            size: Font size in pixels (will be automatically scaled for Pulsewidth font)
            
        Returns:
            pygame.font.Font object
        """
        # Scale the size for the Pulsewidth font
        actual_size = self.get_scaled_size(size)
        font_key = f"mayhem_{actual_size}"
        
        if font_key not in self._fonts:
            try:
                # Try to load the custom font
                if os.path.exists(self._font_path):
                    self._fonts[font_key] = pygame.font.Font(self._font_path, actual_size)
                    print(f"Loaded custom font: {self._font_path} at size {actual_size} (scaled from {size})")
                else:
                    # Fallback to default font if custom font not found
                    self._fonts[font_key] = pygame.font.Font(None, size)  # Use original size for default font
                    print(f"Custom font not found at {self._font_path}, using default font")
            except pygame.error as e:
                # Fallback to default font if loading fails
                print(f"Failed to load custom font: {e}")
                self._fonts[font_key] = pygame.font.Font(None, size)  # Use original size for default font
                
        return self._fonts[font_key]
    
    def render_text(self, text: str, size: int = 36, color: tuple = (255, 255, 255), antialias: bool = True) -> pygame.Surface:
        """
        Render text using the Pulsewidth font
        
        Args:
            text: Text to render
            size: Font size
            color: Text color (r, g, b)
            antialias: Whether to use anti-aliasing
            
        Returns:
            pygame.Surface with rendered text
        """
        font = self.get_font(size)
        return font.render(text, antialias, color)
    
    def get_text_size(self, text: str, size: int = 36) -> tuple:
        """
        Get the size of rendered text
        
        Args:
            text: Text to measure
            size: Font size
            
        Returns:
            (width, height) tuple
        """
        font = self.get_font(size)
        return font.size(text)

# Global font manager instance
font_manager = FontManager()
