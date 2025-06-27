import pygame
import math
from globals import Globals

class ScrollingBackground:
    def __init__(self):
        # Background colors - two dark grays for striped pattern
        self.color1 = (35, 36, 30)   # Darker gray
        self.color2 = (50, 52, 45)   # Lighter gray
        
        # Stripe properties
        self.stripe_thickness = 40    # Thickness of each stripe
        self.slant_angle = math.radians(15)  # 15 degree slant
        self.scroll_speed = 1.0       # Speed of scrolling
        
        # Current scroll offset
        self.scroll_offset = 0
        
        # Calculate the diagonal distance we need to cover
        # to ensure full screen coverage with slanted stripes
        screen_diagonal = math.sqrt(Globals.screen_width**2 + Globals.screen_height**2)
        self.pattern_width = int(screen_diagonal + self.stripe_thickness * 2)
        
    def update(self):
        """Update the scrolling animation"""
        self.scroll_offset += self.scroll_speed
        
        # Reset offset to prevent overflow (cycle every 2 stripe widths)
        if self.scroll_offset >= self.stripe_thickness * 2:
            self.scroll_offset = 0
    
    def draw(self, surface):
        """Draw the scrolling striped background"""
        # Fill with base color first
        surface.fill(self.color1)
        
        # Calculate slant offset for creating diagonal stripes
        slant_offset_x = math.tan(self.slant_angle) * Globals.screen_height
        
        # Draw alternating stripes
        stripe_y_spacing = self.stripe_thickness * 2  # Space between stripes of same color
        
        # Start from a position that ensures full coverage
        start_y = -self.stripe_thickness * 2 + (self.scroll_offset % stripe_y_spacing)
        
        y = start_y
        while y < Globals.screen_height + self.stripe_thickness:
            # Calculate the slanted stripe as a polygon
            # Each stripe is a parallelogram
            
            # Calculate horizontal offset based on slant angle
            slant_offset = math.tan(self.slant_angle) * self.stripe_thickness
            
            # Define stripe as polygon points (clockwise)
            stripe_points = [
                (-slant_offset_x, y),                                    # Top-left
                (Globals.screen_width, y),                               # Top-right
                (Globals.screen_width + slant_offset, y + self.stripe_thickness),  # Bottom-right
                (slant_offset, y + self.stripe_thickness)                # Bottom-left
            ]
            
            # Draw the stripe
            pygame.draw.polygon(surface, self.color2, stripe_points)
            
            # Move to next stripe position
            y += stripe_y_spacing
    
    def draw_centered(self, surface, camera_offset):
        """
        Draw the background accounting for camera offset
        Note: For a scrolling background, camera offset typically doesn't affect it
        since backgrounds are usually fixed to the screen, but this method is provided
        for consistency with other drawing methods.
        """
        # For scrolling backgrounds, we typically ignore camera offset
        # since the background should stay fixed relative to the screen
        self.draw(surface)

# Example usage and test function
def main():
    """Test the scrolling background"""
    pygame.init()
    screen = pygame.display.set_mode((Globals.screen_width, Globals.screen_height))
    pygame.display.set_caption("Scrolling Background Test")
    clock = pygame.time.Clock()
    
    background = ScrollingBackground()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Update background animation
        background.update()
        
        # Draw background
        background.draw(screen)
        
        # Draw some test shapes to see the background effect
        pygame.draw.circle(screen, (255, 255, 255), (Globals.screen_width // 2, Globals.screen_height // 2), 50, 2)
        pygame.draw.rect(screen, (255, 0, 0), (100, 100, 100, 100), 3)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
