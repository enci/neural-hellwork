import pygame
import pygame.gfxdraw
import math

# Initialize pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

class ShapeRenderer:
    @staticmethod
    def draw_circle(screen, color, center, radius, width=0, antialiased=True):
        """Draw a circle. width=0 fills the circle, width>0 draws outline"""
        if antialiased and width == 0:
            # Filled antialiased circle
            pygame.gfxdraw.filled_circle(screen, int(center[0]), int(center[1]), radius, color)
            pygame.gfxdraw.aacircle(screen, int(center[0]), int(center[1]), radius, color)
        elif antialiased and width > 0:
            # Antialiased circle outline
            pygame.gfxdraw.aacircle(screen, int(center[0]), int(center[1]), radius, color)
            if width > 1:
                # Draw multiple circles for thickness
                for i in range(width):
                    r = radius - width//2 + i
                    if r > 0:
                        pygame.gfxdraw.aacircle(screen, int(center[0]), int(center[1]), r, color)
        else:
            # Standard pygame circle
            pygame.draw.circle(screen, color, center, radius, width)
    
    @staticmethod
    def draw_rectangle(screen, color, rect, width=0, antialiased=True):
        """Draw a rectangle. rect is (x, y, width, height)"""
        if antialiased and width == 0:
            # Filled antialiased rectangle (using polygon)
            x, y, w, h = rect
            points = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
            pygame.gfxdraw.filled_polygon(screen, points, color)
            pygame.gfxdraw.aapolygon(screen, points, color)
        elif antialiased and width > 0:
            # Antialiased rectangle outline
            x, y, w, h = rect
            points = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
            pygame.gfxdraw.aapolygon(screen, points, color)
            if width > 1:
                # Draw multiple rectangles for thickness
                for i in range(width):
                    offset = i
                    inner_rect = (x + offset, y + offset, w - 2*offset, h - 2*offset)
                    if inner_rect[2] > 0 and inner_rect[3] > 0:
                        inner_points = [(inner_rect[0], inner_rect[1]), 
                                      (inner_rect[0] + inner_rect[2], inner_rect[1]),
                                      (inner_rect[0] + inner_rect[2], inner_rect[1] + inner_rect[3]),
                                      (inner_rect[0], inner_rect[1] + inner_rect[3])]
                        pygame.gfxdraw.aapolygon(screen, inner_points, color)
        else:
            # Standard pygame rectangle
            pygame.draw.rect(screen, color, rect, width)
    
    @staticmethod
    def draw_polygon(screen, color, points, width=0, antialiased=True):
        """Draw a polygon from a list of points"""
        if antialiased and width == 0:
            # Filled antialiased polygon
            int_points = [(int(x), int(y)) for x, y in points]
            pygame.gfxdraw.filled_polygon(screen, int_points, color)
            pygame.gfxdraw.aapolygon(screen, int_points, color)
        elif antialiased and width > 0:
            # Antialiased polygon outline
            int_points = [(int(x), int(y)) for x, y in points]
            pygame.gfxdraw.aapolygon(screen, int_points, color)
            if width > 1:
                # For thick outlines, fall back to standard pygame
                pygame.draw.polygon(screen, color, points, width)
        else:
            # Standard pygame polygon
            pygame.draw.polygon(screen, color, points, width)
    
    @staticmethod
    def draw_triangle(screen, color, p1, p2, p3, width=0, antialiased=True):
        """Draw a triangle given three points"""
        points = [p1, p2, p3]
        ShapeRenderer.draw_polygon(screen, color, points, width, antialiased)
    
    @staticmethod
    def draw_star(screen, color, center, outer_radius, inner_radius, points=5, width=0, antialiased=True):
        """Draw a star shape"""
        star_points = []
        angle_step = math.pi / points
        
        for i in range(points * 2):
            angle = i * angle_step - math.pi / 2
            if i % 2 == 0:
                # Outer point
                x = center[0] + outer_radius * math.cos(angle)
                y = center[1] + outer_radius * math.sin(angle)
            else:
                # Inner point
                x = center[0] + inner_radius * math.cos(angle)
                y = center[1] + inner_radius * math.sin(angle)
            star_points.append((x, y))
        
        ShapeRenderer.draw_polygon(screen, color, star_points, width, antialiased)
    
    @staticmethod
    def draw_hexagon(screen, color, center, radius, width=0, antialiased=True):
        """Draw a regular hexagon"""
        points = []
        for i in range(6):
            angle = i * math.pi / 3
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))
        ShapeRenderer.draw_polygon(screen, color, points, width, antialiased)
    
    @staticmethod
    def draw_diamond(screen, color, center, width, height, outline=0, antialiased=True):
        """Draw a diamond shape"""
        x, y = center
        points = [
            (x, y - height // 2),  # Top
            (x + width // 2, y),   # Right
            (x, y + height // 2),  # Bottom
            (x - width // 2, y)    # Left
        ]
        ShapeRenderer.draw_polygon(screen, color, points, outline, antialiased)
    
    @staticmethod
    def draw_arrow(screen, color, start, end, arrow_head_size=20, width=3, antialiased=True):
        """Draw an arrow from start to end point"""
        if antialiased:
            # Use antialiased line for the shaft
            pygame.gfxdraw.line(screen, int(start[0]), int(start[1]), int(end[0]), int(end[1]), color)
            if width > 1:
                # Draw multiple lines for thickness
                for i in range(width):
                    offset = i - width // 2
                    # Calculate perpendicular offset
                    dx = end[0] - start[0]
                    dy = end[1] - start[1]
                    length = math.sqrt(dx**2 + dy**2)
                    if length > 0:
                        perp_x = -dy / length * offset
                        perp_y = dx / length * offset
                        start_offset = (start[0] + perp_x, start[1] + perp_y)
                        end_offset = (end[0] + perp_x, end[1] + perp_y)
                        pygame.gfxdraw.line(screen, int(start_offset[0]), int(start_offset[1]), 
                                          int(end_offset[0]), int(end_offset[1]), color)
        else:
            # Standard pygame line
            pygame.draw.line(screen, color, start, end, width)
        
        # Calculate arrow head (same for both antialiased and standard)
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.sqrt(dx**2 + dy**2)
        
        if length == 0:
            return
        
        # Normalize
        dx /= length
        dy /= length
        
        # Arrow head points
        head_length = arrow_head_size
        head_angle = math.pi / 6  # 30 degrees
        
        # Left arrow head line
        left_x = end[0] - head_length * (dx * math.cos(head_angle) + dy * math.sin(head_angle))
        left_y = end[1] - head_length * (dy * math.cos(head_angle) - dx * math.sin(head_angle))
        
        # Right arrow head line
        right_x = end[0] - head_length * (dx * math.cos(-head_angle) + dy * math.sin(-head_angle))
        right_y = end[1] - head_length * (dy * math.cos(-head_angle) - dx * math.sin(-head_angle))
        
        if antialiased:
            pygame.gfxdraw.line(screen, int(end[0]), int(end[1]), int(left_x), int(left_y), color)
            pygame.gfxdraw.line(screen, int(end[0]), int(end[1]), int(right_x), int(right_y), color)
        else:
            pygame.draw.line(screen, color, end, (left_x, left_y), width)
            pygame.draw.line(screen, color, end, (right_x, right_y), width)
    
    @staticmethod
    def draw_rounded_rect(screen, color, rect, border_radius, width=0):
        """Draw a rectangle with rounded corners"""
        x, y, w, h = rect
        
        if border_radius * 2 > min(w, h):
            border_radius = min(w, h) // 2
        
        # Draw the main rectangles
        pygame.draw.rect(screen, color, (x + border_radius, y, w - 2*border_radius, h), width)
        pygame.draw.rect(screen, color, (x, y + border_radius, w, h - 2*border_radius), width)
        
        # Draw the corner circles
        pygame.draw.circle(screen, color, (x + border_radius, y + border_radius), border_radius, width)
        pygame.draw.circle(screen, color, (x + w - border_radius, y + border_radius), border_radius, width)
        pygame.draw.circle(screen, color, (x + border_radius, y + h - border_radius), border_radius, width)
        pygame.draw.circle(screen, color, (x + w - border_radius, y + h - border_radius), border_radius, width)
    
    @staticmethod
    def draw_elongated_octagon(screen, color, center, width, height, outline_width=0, antialiased=True):
        """Draw an octagon that's elongated in one direction"""
        x, y = center
        w, h = width, height
        
        # Calculate the corner cut size (smaller of width/height divided by 4)
        corner_cut = min(w, h) // 4
        
        # Define the 8 points of the elongated octagon
        points = [
            (x - w//2 + corner_cut, y - h//2),      # Top-left corner
            (x + w//2 - corner_cut, y - h//2),      # Top-right corner
            (x + w//2, y - h//2 + corner_cut),      # Right-top corner
            (x + w//2, y + h//2 - corner_cut),      # Right-bottom corner
            (x + w//2 - corner_cut, y + h//2),      # Bottom-right corner
            (x - w//2 + corner_cut, y + h//2),      # Bottom-left corner
            (x - w//2, y + h//2 - corner_cut),      # Left-bottom corner
            (x - w//2, y - h//2 + corner_cut)       # Left-top corner
        ]
        
        ShapeRenderer.draw_polygon(screen, color, points, outline_width, antialiased)
    
    @staticmethod
    def draw_beveled_x(screen, color, center, size, bevel_size=None, width=0, antialiased=True):
        """Draw an X shape with beveled edges"""
        x, y = center
        
        if bevel_size is None:
            bevel_size = size // 8
        
        # Half size for easier calculation
        half_size = size // 2
        
        # Create the beveled X by drawing two beveled rectangles rotated 45 degrees
        # We'll approximate this with polygons
        
        # First arm of the X (top-left to bottom-right)
        arm1_points = [
            (x - half_size + bevel_size, y - bevel_size//2),
            (x - half_size, y - bevel_size//2 + bevel_size),
            (x + half_size - bevel_size, y + bevel_size//2 - bevel_size),
            (x + half_size, y + bevel_size//2),
            (x + half_size - bevel_size, y + bevel_size//2 + bevel_size),
            (x - half_size + bevel_size, y - bevel_size//2 - bevel_size)
        ]
        
        # Second arm of the X (top-right to bottom-left)
        arm2_points = [
            (x + half_size - bevel_size, y - bevel_size//2),
            (x + half_size, y - bevel_size//2 + bevel_size),
            (x - half_size + bevel_size, y + bevel_size//2 - bevel_size),
            (x - half_size, y + bevel_size//2),
            (x - half_size + bevel_size, y + bevel_size//2 + bevel_size),
            (x + half_size - bevel_size, y - bevel_size//2 - bevel_size)
        ]
        
        ShapeRenderer.draw_polygon(screen, color, arm1_points, width, antialiased)
        ShapeRenderer.draw_polygon(screen, color, arm2_points, width, antialiased)
    
    @staticmethod
    def draw_arc(screen, color, center, radius, start_angle, end_angle, thickness=1, antialiased=True):
        """
        Draw an arc with specified thickness
        
        Args:
            screen: pygame screen surface
            color: RGB color tuple
            center: (x, y) center point of the arc
            radius: radius of the arc
            start_angle: starting angle in radians (0 = right, π/2 = down)
            end_angle: ending angle in radians
            thickness: thickness of the arc line
            antialiased: whether to use antialiasing
        """
        x, y = center
        
        if thickness <= 1:
            if antialiased:
                # For thin arcs, draw individual pixels along the arc
                ShapeRenderer._draw_aa_thin_arc(screen, color, center, radius, start_angle, end_angle)
            else:
                # Use pygame's built-in arc function
                rect = (x - radius, y - radius, radius * 2, radius * 2)
                pygame.draw.arc(screen, color, rect, start_angle, end_angle, thickness)
        else:
            # For thick arcs, use polygon method (already smooth)
            ShapeRenderer._draw_thick_arc_polygon(screen, color, center, radius, start_angle, end_angle, thickness)
    
    @staticmethod
    def _draw_aa_thin_arc(screen, color, center, radius, start_angle, end_angle):
        """Helper method to draw thin antialiased arcs"""
        x, y = center
        
        # Normalize angles
        if end_angle < start_angle:
            end_angle += 2 * math.pi
        
        arc_length = end_angle - start_angle
        segments = max(8, int(arc_length * radius / 2))  # More segments for smoother arcs
        
        prev_point = None
        for i in range(segments + 1):
            angle = start_angle + (arc_length * i / segments)
            point_x = int(x + radius * math.cos(angle))
            point_y = int(y + radius * math.sin(angle))
            
            if prev_point is not None:
                pygame.gfxdraw.line(screen, prev_point[0], prev_point[1], point_x, point_y, color)
            
            prev_point = (point_x, point_y)
    
    @staticmethod
    def _draw_thick_arc_polygon(screen, color, center, radius, start_angle, end_angle, thickness):
        """Helper method to draw thick arcs using polygons"""
        x, y = center
        
        # Normalize angles
        if end_angle < start_angle:
            end_angle += 2 * math.pi
        
        # Calculate the number of segments based on arc length
        arc_length = end_angle - start_angle
        segments = max(8, int(arc_length * radius / 10))  # More segments for larger arcs
        
        # Calculate points for outer and inner arii
        outer_radius = radius + thickness // 2
        inner_radius = radius - thickness // 2
        
        if inner_radius <= 0:
            inner_radius = 1
        
        outer_points = []
        inner_points = []
        
        for i in range(segments + 1):
            angle = start_angle + (arc_length * i / segments)
            
            # Outer arc points
            outer_x = x + outer_radius * math.cos(angle)
            outer_y = y + outer_radius * math.sin(angle)
            outer_points.append((outer_x, outer_y))
            
            # Inner arc points (in reverse order for proper polygon)
            inner_x = x + inner_radius * math.cos(angle)
            inner_y = y + inner_radius * math.sin(angle)
            inner_points.insert(0, (inner_x, inner_y))
        
        # Combine points to form a closed polygon
        all_points = outer_points + inner_points
        
        if len(all_points) >= 3:
            # Use antialiased polygon drawing
            int_points = [(int(x), int(y)) for x, y in all_points]
            pygame.gfxdraw.filled_polygon(screen, int_points, color)
            pygame.gfxdraw.aapolygon(screen, int_points, color)
    
    @staticmethod
    def draw_arc_degrees(screen, color, center, radius, start_degrees, end_degrees, thickness=1, antialiased=True):
        """
        Draw an arc using degrees instead of radians
        
        Args:
            screen: pygame screen surface
            color: RGB color tuple
            center: (x, y) center point of the arc
            radius: radius of the arc
            start_degrees: starting angle in degrees (0 = right, 90 = down)
            end_degrees: ending angle in degrees
            thickness: thickness of the arc line
            antialiased: whether to use antialiasing
        """
        start_radians = math.radians(start_degrees)
        end_radians = math.radians(end_degrees)
        ShapeRenderer.draw_arc(screen, color, center, radius, start_radians, end_radians, thickness, antialiased)
    
    @staticmethod
    def draw_elongated_hexagon(screen, color, center, width, height, outline_width=0, antialiased=True):
        """Draw a hexagon that's elongated vertically (perfect for player ship)"""
        x, y = center
        w, h = width, height
        
        # For an elongated hexagon, we want the top and bottom to be angled
        # but the sides to be longer for the elongated effect
        
        # Define the 6 points of the elongated hexagon
        # Top and bottom points are closer to center for elongation
        angle_cut = h // 4  # How much to cut from top/bottom for angled edges
        
        points = [
            (x, y - h//2),                      # Top point
            (x + w//2, y - h//2 + angle_cut),   # Top-right
            (x + w//2, y + h//2 - angle_cut),   # Bottom-right  
            (x, y + h//2),                      # Bottom point
            (x - w//2, y + h//2 - angle_cut),   # Bottom-left
            (x - w//2, y - h//2 + angle_cut)    # Top-left
        ]
        
        ShapeRenderer.draw_polygon(screen, color, points, outline_width, antialiased)

# Example usage
def main():
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Pygame Shapes Demo")
    clock = pygame.time.Clock()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill(WHITE)
        
        # Draw various shapes using static methods
        ShapeRenderer.draw_circle(screen, RED, (100, 100), 50)
        ShapeRenderer.draw_rectangle(screen, GREEN, (200, 50, 100, 100))
        ShapeRenderer.draw_triangle(screen, BLUE, (400, 50), (350, 150), (450, 150))
        ShapeRenderer.draw_star(screen, YELLOW, (600, 100), 60, 30)
        
        ShapeRenderer.draw_hexagon(screen, PURPLE, (100, 300), 50)
        ShapeRenderer.draw_diamond(screen, ORANGE, (250, 300), 80, 100)
        ShapeRenderer.draw_arrow(screen, BLACK, (350, 250), (450, 350), 15, 5)
        ShapeRenderer.draw_rounded_rect(screen, BLUE, (500, 250, 120, 80), 15)
        
        # New shapes
        ShapeRenderer.draw_elongated_octagon(screen, RED, (650, 300), 100, 60)
        ShapeRenderer.draw_beveled_x(screen, GREEN, (100, 500), 80, 8)
        
        # Arc examples
        ShapeRenderer.draw_arc_degrees(screen, BLUE, (200, 500), 40, 0, 180, 8)  # Half circle
        ShapeRenderer.draw_arc_degrees(screen, PURPLE, (350, 500), 35, 45, 315, 12)  # 3/4 circle
        ShapeRenderer.draw_arc(screen, ORANGE, (500, 500), 30, 0, math.pi, 6)  # Half circle in radians
        
        # Draw some outlined shapes
        ShapeRenderer.draw_circle(screen, BLACK, (300, 450), 50, 3)
        ShapeRenderer.draw_rectangle(screen, RED, (400, 400, 100, 100), 3)
        ShapeRenderer.draw_star(screen, GREEN, (600, 450), 60, 30, width=3)
        ShapeRenderer.draw_elongated_octagon(screen, PURPLE, (650, 450), 80, 60, outline_width=3)
        ShapeRenderer.draw_beveled_x(screen, ORANGE, (750, 450), 50, 4, width=2)
        
        # More arc examples
        ShapeRenderer.draw_arc_degrees(screen, RED, (650, 500), 25, 90, 270, 4)  # Quarter circle
        ShapeRenderer.draw_arc_degrees(screen, GREEN, (750, 500), 30, 0, 90, 15)  # Thick quarter arc
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()