import pygame
from typing import Optional, Set, Tuple

class LED:
    COLORS = {
        'off': (100, 0, 0),  # Dark red when off
        'on': (255, 0, 0),   # Bright red when on
        'border': (0, 0, 0)  # Black border
    }

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.radius = 10
        self.anode_pos = (x, y - 15)    # Positive terminal (longer leg)
        self.cathode_pos = (x, y + 15)  # Negative terminal (shorter leg)
        self.is_on = False

    def update_position(self, x: int, y: int):
        self.x = x
        self.y = y
        self.anode_pos = (x, y - 15)
        self.cathode_pos = (x, y + 15)

    def check_power_state(self, powered_points: Set[Tuple[int, int]], 
                         grounded_points: Set[Tuple[int, int]], 
                         vcc_pos: Tuple[int, int], 
                         gnd_pos: Tuple[int, int]) -> bool:
        """Returns True if LED should be lit (anode connected to VCC and cathode to GND)"""
        anode_powered = self.anode_pos in powered_points or self.anode_pos == vcc_pos
        cathode_grounded = self.cathode_pos in grounded_points or self.cathode_pos == gnd_pos
        return anode_powered and cathode_grounded

    def draw(self, window, powered_points: Set[Tuple[int, int]], 
            grounded_points: Set[Tuple[int, int]], 
            vcc_pos: Tuple[int, int], 
            gnd_pos: Tuple[int, int]):
        # Update LED state
        self.is_on = self.check_power_state(powered_points, grounded_points, vcc_pos, gnd_pos)
        
        # Draw LED body
        color = self.COLORS['on'] if self.is_on else self.COLORS['off']
        pygame.draw.circle(window, color, (self.x, self.y), self.radius)
        pygame.draw.circle(window, self.COLORS['border'], (self.x, self.y), self.radius, 2)
        
        # Draw terminals
        pygame.draw.line(window, self.COLORS['border'], 
                        (self.x, self.y - self.radius), 
                        self.anode_pos, 2)  # Anode (longer)
        pygame.draw.line(window, self.COLORS['border'], 
                        (self.x, self.y + self.radius), 
                        self.cathode_pos, 2)  # Cathode (shorter)
        
        # Draw connection points
        pygame.draw.circle(window, self.COLORS['border'], self.anode_pos, 4)
        pygame.draw.circle(window, self.COLORS['border'], self.cathode_pos, 4)
        
        # Draw + and - labels
        font = pygame.font.Font(None, 20)
        plus_text = font.render('+', True, self.COLORS['border'])
        minus_text = font.render('-', True, self.COLORS['border'])
        window.blit(plus_text, (self.x + 8, self.y - 20))
        window.blit(minus_text, (self.x + 8, self.y + 10))

class DraggableLED:
    def __init__(self, initial_x: int, initial_y: int):
        self.led = LED(initial_x, initial_y)
        self.is_dragging = False

    def update_position(self, x: int, y: int):
        self.led.update_position(x, y)

    def draw(self, window, powered_points: Set[Tuple[int, int]], 
            grounded_points: Set[Tuple[int, int]], 
            vcc_pos: Tuple[int, int], 
            gnd_pos: Tuple[int, int]):
        self.led.draw(window, powered_points, grounded_points, vcc_pos, gnd_pos)

class LEDPalette:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y   # Position below IC palette
        self.button_width = 100
        self.button_height = 40
        self.button_rect = pygame.Rect(self.x, self.y, self.button_width, self.button_height)
        self.dragging_led: Optional[DraggableLED] = None

    def draw(self, window: pygame.Surface, powered_points: Set[Tuple[int, int]], 
            grounded_points: Set[Tuple[int, int]], 
            vcc_pos: Tuple[int, int], 
            gnd_pos: Tuple[int, int]):
        # Draw palette button
        pygame.draw.rect(window, (200, 200, 200), self.button_rect)
        pygame.draw.rect(window, (100, 100, 100), self.button_rect, 2)
        
        font = pygame.font.Font(None, 24)
        text = font.render("LED", True, (0, 0, 0))
        text_rect = text.get_rect(center=self.button_rect.center)
        window.blit(text, text_rect)

        # Draw dragging LED if exists
        if self.dragging_led:
            self.dragging_led.draw(window, powered_points, grounded_points, vcc_pos, gnd_pos)

    def handle_click(self, pos: tuple) -> bool:
        if self.button_rect.collidepoint(pos):
            self.dragging_led = DraggableLED(pos[0], pos[1])
            self.dragging_led.is_dragging = True
            return True
        return False

    def handle_drag(self, pos: tuple):
        if self.dragging_led:
            self.dragging_led.update_position(pos[0], pos[1])

    def handle_release(self) -> Optional[LED]:
        if self.dragging_led:
            led = self.dragging_led.led
            self.dragging_led = None
            return led
        return None