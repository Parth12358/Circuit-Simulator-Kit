import pygame
from typing import Optional, Set, Tuple

# Constants
GRID_X1 = 225
GRID_X2 = 794
GRID_X2E = 790
GRID_X3 = 1383
GRID_Y1 = 288
GRID_Y2 = 373
GRID_Y3 = GRID_Y1 + 143
GRID_Y4 = GRID_Y2 + 143

X1_RAIL = 225
X2_RAIL = 308
X3_RAIL = 833
X4_RAIL = 926
Y1_UP_RAIL = 207    # Top positive rail
Y2_UP_RAIL = 233    # Top negative rail
Y1_DOWN_RAIL = 566  # Bottom positive rail
Y2_DOWN_RAIL = 592  # Bottom negative rail
cell_size = 19.5

def get_vertical_group_points(x, y):
    """Get all points in the same vertical column within the same half"""
    points = set()
    
    # Check which half we're in based on y coordinate
    if GRID_Y1 <= y <= GRID_Y2:  # Upper half
        # LEFT UPPER HALF
        if GRID_X1 <= x <= GRID_X2:
            for grid_y in range(GRID_Y1, GRID_Y2 + 1, int(cell_size)):
                points.add((x, grid_y))
        
        # RIGHT UPPER HALF
        if GRID_X2E <= x <= GRID_X3:
            for grid_y in range(GRID_Y1, GRID_Y2 + 1, int(cell_size)):
                points.add((x, grid_y))
                
    elif GRID_Y3 <= y <= GRID_Y4:  # Lower half
        # LEFT LOWER HALF
        if GRID_X1 <= x <= GRID_X2:
            for grid_y in range(GRID_Y3, GRID_Y4 + 1, int(cell_size)):
                points.add((x, grid_y))
                
        # RIGHT LOWER HALF
        if GRID_X2E <= x <= GRID_X3:
            for grid_y in range(GRID_Y3, GRID_Y4 + 1, int(cell_size)):
                points.add((x, grid_y))
            
    return points

def get_rail_type(y):
    """Get the type of rail based on y-coordinate"""
    if y == Y1_UP_RAIL:
        return 'top_pos'
    elif y == Y2_UP_RAIL:
        return 'top_neg'
    elif y == Y1_DOWN_RAIL:
        return 'bottom_pos'
    elif y == Y2_DOWN_RAIL:
        return 'bottom_neg'
    return None

def get_rail_points(x, y):
    """Get all points in the same power rail"""
    points = set()
    if is_power_rail(x, y):
        rail_y = y  # Keep track of which rail we're on
        # Power the entire rail line for this y-coordinate
        for i in range(5):
            k = 116 * i
            # Left side rails
            for rx in range(X1_RAIL + k, X2_RAIL + k + 1, int(cell_size)):
                points.add((rx, rail_y))
            # Right side rails
            for rx in range(X3_RAIL + k, X4_RAIL + k + 1, int(cell_size)):
                points.add((rx, rail_y))
    return points

def is_power_rail(x, y):
    """Check if a point is on a power rail"""
    in_rail_x = (X1_RAIL <= x <= X4_RAIL + 116*5)
    in_rail_y = y in [Y1_UP_RAIL, Y2_UP_RAIL, Y1_DOWN_RAIL, Y2_DOWN_RAIL]
    return in_rail_x and in_rail_y


class NandGate:
    COLORS = {
        'body': (100, 100, 100),  # Gray for gate body
        'powered': (0, 255, 0),   # Green for powered state
        'unpowered': (255, 0, 0), # Red for unpowered state
        'border': (0, 0, 0)       # Black for borders
    }

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y  # Will be constrained in update_position
        self.width = 100  # Width of the AND gate body
        self.pin_spacing = 20  # Space between pins
        
        # Initialize all positions
        self.update_position(x, y)

        # Connection points to nearest grid (will be set when placed)
        self.vcc_connection = None
        self.input1_connection = None
        self.input2_connection = None
        self.output_connection = None
        self.gnd_connection = None


    def update_position(self, x: int, y: int):
        """Update the position of the AND gate while maintaining constraints"""
        self.x = x
        
        # Constrain y position to middle section (between GRID_Y2 and GRID_Y3)
        GRID_Y2 = 373  # Upper grid end
        GRID_Y3 = GRID_Y2 + 143  # Lower grid start
        middle_y = GRID_Y2 + (GRID_Y3 - GRID_Y2) // 2
        
        # Allow some movement up and down within the middle section
        max_offset = 40  # Maximum distance from middle
        self.y = min(max(y, middle_y - max_offset), middle_y + max_offset)
        
        # Update all pin positions (spread horizontally)
        self.vcc_pos = (x - 40, self.y)      # Leftmost
        self.input1_pos = (x - 20, self.y)    # Left middle
        self.input2_pos = (x, self.y)         # Center
        self.output_pos = (x + 20, self.y)    # Right middle
        self.gnd_pos = (x + 40, self.y)       # Rightmost


    def check_power_state(self, powered_points: Set[Tuple[int, int]], 
                         grounded_points: Set[Tuple[int, int]], 
                         vcc_pos: Tuple[int, int], 
                         gnd_pos: Tuple[int, int]) -> bool:
        """Simplified power check - returns True if AND condition is met"""
        # Check if inputs are powered
        input1_powered = self.input1_connection in powered_points if self.input1_connection else False
        input2_powered = self.input2_connection in powered_points if self.input2_connection else False
        
        # Check if VCC and GND are connected
        has_power = self.vcc_connection in powered_points
        has_ground = self.gnd_connection in grounded_points

        # Basic AND logic
        output_powered = not(input1_powered and input2_powered) and has_power and has_ground
        
        # If output is powered, also add inputs and output to powered points
        if output_powered:
            if self.input1_connection:
                powered_points.add(self.input1_connection)
            if self.input2_connection:
                powered_points.add(self.input2_connection)
            if self.output_connection:
                powered_points.add(self.output_connection)

        return output_powered
    

    def draw(self, window: pygame.Surface, powered_points: Set[Tuple[int, int]], 
            grounded_points: Set[Tuple[int, int]], 
            vcc_pos: Tuple[int, int], 
            gnd_pos: Tuple[int, int]):
        # Get output state
        output_powered = self.check_power_state(powered_points, grounded_points, vcc_pos, gnd_pos)

        # Draw gate body (horizontal line)
        pygame.draw.line(window, self.COLORS['body'], 
                        (self.x - 50, self.y), 
                        (self.x + 50, self.y), 4)
        
                # Draw gate label
        font = pygame.font.Font(None, 24)
        text = font.render("NAND", True, self.COLORS['border'])
        text_rect = text.get_rect(center=(self.x, self.y - 15))
        window.blit(text, text_rect)

        # Draw pins and connections with simplified coloring
        pin_states = {
            'vcc': self.vcc_connection in powered_points,
            'gnd': self.gnd_connection in grounded_points,
            'input1': self.input1_connection in powered_points,
            'input2': self.input2_connection in powered_points,
            'output': output_powered
        }

        # Draw all pins and their connections
        for pin_name, is_powered in pin_states.items():
            pin_pos = getattr(self, f"{pin_name}_pos")
            connection = getattr(self, f"{pin_name}_connection")
            
            color = self.COLORS['powered'] if is_powered else self.COLORS['unpowered']
            pygame.draw.circle(window, color, pin_pos, 4)
            
            if connection:
                pygame.draw.line(window, color, pin_pos, connection, 2)

        # Draw labels above the pins
        font = pygame.font.Font(None, 16)
        labels = [
            ("VCC", self.vcc_pos),
            ("IN1", self.input1_pos),
            ("IN2", self.input2_pos),
            ("OUT", self.output_pos),
            ("GND", self.gnd_pos)
        ]
        for text, pos in labels:
            surface = font.render(text, True, self.COLORS['border'])
            rect = surface.get_rect(center=(pos[0], pos[1] - 15))
            window.blit(surface, rect)

class DraggableNandGate:
    def __init__(self, initial_x: int, initial_y: int):
        self.gate = NandGate(initial_x, initial_y)
        self.is_dragging = False

    def update_position(self, x: int, y: int):
        # Constrain y position to middle section
        y = max(373, min(373 + 143, y))  # Constrain between GRID_Y2 and GRID_Y3
        self.gate.update_position(x, y)

    def draw(self, window: pygame.Surface, powered_points: Set[Tuple[int, int]], 
            grounded_points: Set[Tuple[int, int]], 
            vcc_pos: Tuple[int, int], 
            gnd_pos: Tuple[int, int]):
        self.gate.draw(window, powered_points, grounded_points, vcc_pos, gnd_pos)

class NandGatePalette:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y # Position below LED palette
        self.button_width = 100
        self.button_height = 40
        self.button_rect = pygame.Rect(self.x, self.y, self.button_width, self.button_height)
        self.dragging_gate: Optional[DraggableNandGate] = None

    def draw(self, window: pygame.Surface, powered_points: Set[Tuple[int, int]], 
            grounded_points: Set[Tuple[int, int]], 
            vcc_pos: Tuple[int, int], 
            gnd_pos: Tuple[int, int]):
        # Draw palette button
        pygame.draw.rect(window, (200, 200, 200), self.button_rect)
        pygame.draw.rect(window, (100, 100, 100), self.button_rect, 2)
        
        font = pygame.font.Font(None, 24)
        text = font.render("NAND", True, (0, 0, 0))
        text_rect = text.get_rect(center=self.button_rect.center)
        window.blit(text, text_rect)

        # Draw dragging gate if exists
        if self.dragging_gate:
            self.dragging_gate.draw(window, powered_points, grounded_points, vcc_pos, gnd_pos)

    def handle_click(self, pos: tuple) -> bool:
        if self.button_rect.collidepoint(pos):
            self.dragging_gate = DraggableNandGate(pos[0], pos[1])
            self.dragging_gate.is_dragging = True
            return True
        return False

    def handle_drag(self, pos: tuple):
        if self.dragging_gate:
            self.dragging_gate.update_position(pos[0], pos[1])

    def handle_release(self, grid_points: list) -> Optional[NandGate]:
        if self.dragging_gate:
            gate = self.dragging_gate.gate
            # Find nearest grid points for all pins
            for pin_name in ['vcc', 'input1', 'input2', 'output', 'gnd']:
                pin_pos = getattr(gate, f"{pin_name}_pos")
                # Find nearest grid point
                nearest_point = min(grid_points, 
                    key=lambda p: ((p[0] - pin_pos[0])**2 + (p[1] - pin_pos[1])**2)**0.5)
                setattr(gate, f"{pin_name}_connection", nearest_point)
            
            self.dragging_gate = None
            return gate
        return None