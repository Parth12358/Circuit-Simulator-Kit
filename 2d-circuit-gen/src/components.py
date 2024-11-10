from dataclasses import dataclass
from typing import List, Tuple, Dict, Set
import math
import pygame
from typing import Optional, Tuple

# Constants
cell_size = 19.5
GRID_X1 = 225
GRID_Y1 = 288
GRID_X2 = 794
GRID_X2E = 790
GRID_X3 = 1383
GRID_Y2 = 373
X1_RAIL = 225
X2_RAIL = 308
X3_RAIL = 833
X4_RAIL = 926
Y1_UP_RAIL = 207
Y2_UP_RAIL = 233
Y1_DOWN_RAIL = 566
Y2_DOWN_RAIL = 592
GRID_Y3 = GRID_Y1 + 143  # Y coordinate for lower grid start
GRID_Y4 = GRID_Y2 + 143  # Y coordinate for lower grid end
GRID_Y5 = GRID_Y1 + (5 * cell_size)  # Row 5 y-coordinate
GRID_Y6 = GRID_Y1 + (6 * cell_size)  # Row 6 y-coordinate
WIRE_COLOR = (0, 255, 0)

@dataclass
class Pin:
    number: int
    x: int
    y: int
    is_input: bool
    is_output: bool
    is_power: bool
    is_ground: bool
    
def is_mouse_near_point(mouse_pos: Tuple[int, int], point_pos: Tuple[int, int], radius: int = 8) -> bool:
        """Helper function to check if mouse is near a point"""
        distance = math.sqrt((mouse_pos[0] - point_pos[0]) ** 2 + (mouse_pos[1] - point_pos[1]) ** 2)
        return distance <= radius

class InputSwitch:
    # Class-level color definitions
    COLORS = {
        'on': (0, 255, 0),    # Green when on
        'off': (255, 0, 0),   # Red when off
        'border': (0, 0, 0),  # Black border
        'text': (0, 0, 0)     # Black text
    }

    def __init__(self, x: int, y: int, label: str):
        self.x = x
        self.y = y
        self.label = label
        self.is_on = True
        self.output_pos = (x, y + 30)
        self.switch_radius = 15
        self.connection_radius = 6
        # No need to recreate colors dictionary for each instance
        
    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        return is_mouse_near_point(pos, (self.x, self.y), self.switch_radius)

    def toggle(self):
        self.is_on = not self.is_on
        print(self.is_on)

    def is_vcc(self):
        return self.is_on

    def draw(self, window: pygame.Surface):
        # Draw the switch circle
        color = self.COLORS['on'] if self.is_on else self.COLORS['off']
        pygame.draw.circle(window, color, (self.x, self.y), self.switch_radius)
        pygame.draw.circle(window, self.COLORS['border'], (self.x, self.y), self.switch_radius, 2)

        # Draw labels
        font = pygame.font.Font(None, 24)
        text = font.render(f"Input {self.label}", True, self.COLORS['text'])
        text_rect = text.get_rect(center=(self.x, self.y - 25))
        window.blit(text, text_rect)

        state_text = font.render(str(int(self.is_on)), True, self.COLORS['text'])
        state_rect = state_text.get_rect(center=(self.x, self.y))
        window.blit(state_text, state_rect)

        # Draw connection point with better visibility
        connection_color = self.COLORS['on'] if self.is_on else self.COLORS['border']
        pygame.draw.circle(window, connection_color, self.output_pos, self.connection_radius)
        pygame.draw.circle(window, self.COLORS['border'], self.output_pos, self.connection_radius, 2)
        
# Also update InputManager class:
class InputManager:
    def __init__(self):
        # Create 4 input switches evenly spaced at the top
        spacing = 100
        base_x = 300  # Starting X position
        base_y = 50   # Y position
        
        self.switches = [
            InputSwitch(base_x + i * spacing, base_y, chr(65 + i))  # Labels A, B, C, D
            for i in range(4)
        ]
        
    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """Returns True if a switch was clicked"""
        for switch in self.switches:
            if switch.is_clicked(pos):
                switch.is_on = not switch.is_on
                return True
        return False
    
    def draw(self, window: pygame.Surface):
        for switch in self.switches:
            switch.draw(window)
            
    def get_powered_points(self) -> Set[Tuple[int, int]]:
        """Returns the set of powered output points from the switches"""
        return {switch.output_pos for switch in self.switches if switch.is_on}
    
    def get_switch_at_pos(self, pos: Tuple[int, int]) -> Optional[InputSwitch]:
        """Returns the switch at the given position, if any"""
        for switch in self.switches:
            # Use distance check instead of exact position
            if is_mouse_near_point(pos, switch.output_pos):
                return switch
        return None

