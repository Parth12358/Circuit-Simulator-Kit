# bboard.py
import pygame
from components import InputManager, InputSwitch

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

# Global state
powered_points = set()
input_manager = InputManager()
powered_rails = {
    'top_pos': False,    # Top positive rail
    'top_neg': False,    # Top negative rail
    'bottom_pos': False, # Bottom positive rail
    'bottom_neg': False  # Bottom negative rail
}

def get_output_color(pos, powered_points):
    return (0, 255, 0) if pos in powered_points else (255, 255, 0)  

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
    """Get all points in the same power rail - any point in the rail powers the entire rail"""
    points = set()
    if is_power_rail(x, y):
        rail_type = get_rail_type(y)
        if rail_type:
            # Power the entire rail line for this y-coordinate
            for i in range(5):
                k = 116 * i
                # Left side rails
                for rx in range(X1_RAIL + k, X2_RAIL + k + 1, int(cell_size)):
                    points.add((rx, y))
                # Right side rails
                for rx in range(X3_RAIL + k, X4_RAIL + k + 1, int(cell_size)):
                    points.add((rx, y))
            
            # Update the rail power state
            powered_rails[rail_type] = True

    return points

def is_power_rail(x, y):
    in_rail_x = (X1_RAIL <= x <= X4_RAIL + 116*5)
    in_rail_y = (Y1_UP_RAIL <= y <= Y2_UP_RAIL) or (Y1_DOWN_RAIL <= y <= Y2_DOWN_RAIL)
    return in_rail_x and in_rail_y

# bboard.py
import pygame
from components import InputManager

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

# Global state
powered_points = set()
input_manager = InputManager()
powered_rails = {
    'top_pos': False,    # Top positive rail
    'top_neg': False,    # Top negative rail
    'bottom_pos': False, # Bottom positive rail
    'bottom_neg': False  # Bottom negative rail
}
output_colors = [(255, 128, 0)] * 9

grounded_points = set()

# Update in bboard.py

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

# In bboard.py, update the propagate_power function:

# In bboard.py

# In bboard.py

def propagate_power(wires, vcc_pos, gnd_pos, output_circles, placed_gates, input_manager=None):
    global powered_points, grounded_points
    
    print("\nStarting power propagation:")
    print(f"Initial powered points: {powered_points}")
    print(f"VCC position: {vcc_pos}")
    print(f"GND position: {gnd_pos}")
    print(f"Number of wires: {len(wires)}")
    
    # Clear existing states
    powered_points.clear()
    grounded_points.clear()
    
    # Initialize power sources
    points_to_check_power = {vcc_pos}
    points_to_check_ground = {gnd_pos}
    
    # Add input switch points that are ON
    if input_manager:
        for switch in input_manager.switches:
            if switch.is_on:
                points_to_check_power.add(switch.output_pos)
                powered_points.add(switch.output_pos)  # Immediately power the switch outputs
    
    grounded_points.add(gnd_pos)
    
    checked_power_points = set()
    checked_ground_points = set()

    # Propagate power
    while points_to_check_power:
        try:
            current = points_to_check_power.pop()
            if current in checked_power_points or current is None:
                continue
                
            checked_power_points.add(current)
            powered_points.add(current)
            x, y = current

            # Check wire connections
            for start, end in wires:
                if start == current:
                    points_to_check_power.add(end)
                    powered_points.add(end)  # Immediately power connected points
                elif end == current:
                    points_to_check_power.add(start)
                    powered_points.add(start)  # Immediately power connected points
            
            # Check gate connections - but only for the specific pin that's connected
            for gate in placed_gates:
                # Check each pin individually
                if current == gate.vcc_connection:
                    points_to_check_power.add(gate.vcc_connection)
                elif current == gate.input1_connection:
                    points_to_check_power.add(gate.input1_connection)
                elif current == gate.input2_connection:
                    points_to_check_power.add(gate.input2_connection)
                elif current == gate.output_connection:
                    # If the gate is outputting power, propagate it
                    if gate.check_power_state(powered_points, grounded_points, vcc_pos, gnd_pos):
                        points_to_check_power.add(gate.output_connection)
                        powered_points.add(gate.output_connection)
                        
                        # Propagate to connected wires
                        for start, end in wires:
                            if start == gate.output_connection:
                                points_to_check_power.add(end)
                                powered_points.add(end)
                            elif end == gate.output_connection:
                                points_to_check_power.add(start)
                                powered_points.add(start)

            # Output circles at bottom
            for circle_pos in output_circles:
                if circle_pos and (current == circle_pos or 
                   any((start == circle_pos and end == current) or 
                       (end == circle_pos and start == current) for start, end in wires)):
                    points_to_check_power.add(circle_pos)
                    powered_points.add(circle_pos)
                    # Power the vertical column for this output
                    if circle_pos[0] and circle_pos[1]:  # Ensure valid coordinates
                        column_points = get_vertical_group_points(circle_pos[0], circle_pos[1])
                        powered_points.update(column_points)
                        points_to_check_power.update(column_points)
            
            # Add vertical group points
            vertical_points = get_vertical_group_points(x, y)
            for point in vertical_points:
                if point not in checked_power_points:
                    points_to_check_power.add(point)
                    
            # Add power rail points
            rail_points = get_rail_points(x, y)
            for point in rail_points:
                if point not in checked_power_points:
                    points_to_check_power.add(point)

        except Exception as e:
            print(f"Error during power propagation: {e}")
            continue

    # Propagate ground similarly
    while points_to_check_ground:
        try:
            current = points_to_check_ground.pop()
            if current in checked_ground_points or current is None:
                continue
                
            checked_ground_points.add(current)
            grounded_points.add(current)
            x, y = current
            
            # Add connected wire endpoints to ground points
            for start, end in wires:
                if start == current and end not in checked_ground_points:
                    points_to_check_ground.add(end)
                    grounded_points.add(end)
                elif end == current and start not in checked_ground_points:
                    points_to_check_ground.add(start)
                    grounded_points.add(start)
            
            # Check component ground connections individually
            for gate in placed_gates:
                if current == gate.gnd_connection:
                    points_to_check_ground.add(gate.gnd_connection)
                    
            vertical_points = get_vertical_group_points(x, y)
            rail_points = get_rail_points(x, y)
            
            for point in vertical_points | rail_points:
                if point not in checked_ground_points:
                    points_to_check_ground.add(point)

        except Exception as e:
            print(f"Error during ground propagation: {e}")
            continue

    # Final check of all outputs and their columns
    try:
        # First check gates
        for gate in placed_gates:
            if gate.check_power_state(powered_points, grounded_points, vcc_pos, gnd_pos):
                if gate.output_connection:
                    powered_points.add(gate.output_connection)
                    # Propagate to connected points
                    for start, end in wires:
                        if start == gate.output_connection:
                            powered_points.add(end)
                        elif end == gate.output_connection:
                            powered_points.add(start)

        # Then check outputs and their columns
        for circle_pos in output_circles:
            if circle_pos in powered_points:
                # Power the entire column
                if circle_pos[0] and circle_pos[1]:
                    column_points = get_vertical_group_points(circle_pos[0], circle_pos[1])
                    powered_points.update(column_points)
            # Also check wire connections to outputs
            for start, end in wires:
                if (start == circle_pos and end in powered_points) or \
                   (end == circle_pos and start in powered_points):
                    powered_points.add(circle_pos)
                    if circle_pos[0] and circle_pos[1]:
                        column_points = get_vertical_group_points(circle_pos[0], circle_pos[1])
                        powered_points.update(column_points)

    except Exception as e:
        print(f"Error during final output check: {e}")

    # Debug information
    print("\nDebug information:")
    print(f"Number of powered points: {len(powered_points)}")
    print(f"Number of grounded points: {len(grounded_points)}")
    if input_manager:
        print(f"Input switch states: {[switch.is_on for switch in input_manager.switches]}")
    print(f"Output circles powered: {sum(1 for circle in output_circles if circle in powered_points)}")
    
    return powered_points, grounded_points


def reset_powered_state(window):
    global powered_points
    print(f"Resetting power state. Current powered points: {powered_points}")
    powered_points.clear()
    print(f"After clear: {powered_points}")
    
    color = (255, 255, 0)  # Yellow for unpowered state
    
    # Draw grid points with default color
    for section in [(GRID_X1, GRID_X2), (GRID_X2E, GRID_X3)]:
        for x in range(section[0], section[1] + 1, int(cell_size)):
            # Upper grid
            for y in range(GRID_Y1, GRID_Y2 + 1, int(cell_size)):
                pygame.draw.circle(window, color, (x, y), 6)
            # Lower grid    
            for y in range(GRID_Y3, GRID_Y4 + 1, int(cell_size)):
                pygame.draw.circle(window, color, (x, y), 6)

    # Draw power rails
    rail_color = (255, 0, 255)  # Unpowered rail color
    for i in range(5):
        k = 116 * i
        # Draw left rails
        for x in range(X1_RAIL + k, X2_RAIL + k + 1, int(cell_size)):
            for y in [Y1_UP_RAIL, Y2_UP_RAIL, Y1_DOWN_RAIL, Y2_DOWN_RAIL]:
                pygame.draw.circle(window, rail_color, (x, y), 6)
        # Draw right rails
        for x in range(X3_RAIL + k, X4_RAIL + k + 1, int(cell_size)):
            for y in [Y1_UP_RAIL, Y2_UP_RAIL, Y1_DOWN_RAIL, Y2_DOWN_RAIL]:
                pygame.draw.circle(window, rail_color, (x, y), 6)

def render_powered_state(window, output_circles):
    # Draw upper grid points
    for x in range(GRID_X1, GRID_X2 + 1, int(cell_size)):
        for y in range(GRID_Y1, GRID_Y2 + 1, int(cell_size)):
            color = (0, 255, 0) if (x, y) in powered_points else (255, 255, 0)
            pygame.draw.circle(window, color, (x, y), 6)

    # Draw upper second grid
    for x in range(GRID_X2E, GRID_X3 + 1, int(cell_size)):
        for y in range(GRID_Y1, GRID_Y2 + 1, int(cell_size)):
            color = (0, 255, 0) if (x, y) in powered_points else (255, 255, 0)
            pygame.draw.circle(window, color, (x, y), 6)

    # Draw lower grid points
    for x in range(GRID_X1, GRID_X2 + 1, int(cell_size)):
        for y in range(GRID_Y3, GRID_Y4 + 1, int(cell_size)):
            color = (0, 255, 0) if (x, y) in powered_points else (255, 255, 0)
            pygame.draw.circle(window, color, (x, y), 6)

    # Draw lower second grid
    for x in range(GRID_X2E, GRID_X3 + 1, int(cell_size)):
        for y in range(GRID_Y3, GRID_Y4 + 1, int(cell_size)):
            color = (0, 255, 0) if (x, y) in powered_points else (255, 255, 0)
            pygame.draw.circle(window, color, (x, y), 6)

    # Draw power rails
    for i in range(5):
        k = 116 * i
        # Left rails
        for x in range(X1_RAIL + k, X2_RAIL + k + 1, int(cell_size)):
            # Top positive rail
            color = (0, 255, 0) if (x, Y1_UP_RAIL) in powered_points else (255, 0, 255)
            pygame.draw.circle(window, color, (x, Y1_UP_RAIL), 6)
            # Top negative rail
            color = (0, 255, 0) if (x, Y2_UP_RAIL) in powered_points else (255, 0, 255)
            pygame.draw.circle(window, color, (x, Y2_UP_RAIL), 6)
            # Bottom positive rail
            color = (0, 255, 0) if (x, Y1_DOWN_RAIL) in powered_points else (255, 0, 255)
            pygame.draw.circle(window, color, (x, Y1_DOWN_RAIL), 6)
            # Bottom negative rail
            color = (0, 255, 0) if (x, Y2_DOWN_RAIL) in powered_points else (255, 0, 255)
            pygame.draw.circle(window, color, (x, Y2_DOWN_RAIL), 6)
        
        # Right rails
        for x in range(X3_RAIL + k, X4_RAIL + k + 1, int(cell_size)):
            # Top positive rail
            color = (0, 255, 0) if (x, Y1_UP_RAIL) in powered_points else (255, 0, 255)
            pygame.draw.circle(window, color, (x, Y1_UP_RAIL), 6)
            # Top negative rail
            color = (0, 255, 0) if (x, Y2_UP_RAIL) in powered_points else (255, 0, 255)
            pygame.draw.circle(window, color, (x, Y2_UP_RAIL), 6)
            # Bottom positive rail
            color = (0, 255, 0) if (x, Y1_DOWN_RAIL) in powered_points else (255, 0, 255)
            pygame.draw.circle(window, color, (x, Y1_DOWN_RAIL), 6)
            # Bottom negative rail
            color = (0, 255, 0) if (x, Y2_DOWN_RAIL) in powered_points else (255, 0, 255)
            pygame.draw.circle(window, color, (x, Y2_DOWN_RAIL), 6)

    # Draw outputs with dynamic colors
    font = pygame.font.Font(None, 36)
    for i, circle_pos in enumerate(output_circles):
        # Get color based on power state
        circle_color = (0, 255, 0) if circle_pos in powered_points else (255, 255, 0)
        pygame.draw.circle(window, circle_color, circle_pos, 10)
        output_text = font.render(f"OUT{i+1}", True, (0, 0, 0))
        output_text_rect = output_text.get_rect(center=(circle_pos[0], circle_pos[1] + 20))
        window.blit(output_text, output_text_rect)


def is_column_powered(column_index):
    x = GRID_X1 + column_index * int(cell_size)
    for y in range(GRID_Y1, GRID_Y2 + 1, int(cell_size)):
        if (x, y) in powered_points:
            return True
    return False

def is_row_powered(row_index, section):
    y = GRID_Y1 + row_index * int(cell_size)
    start_x = GRID_X1 if section == 0 else GRID_X2E
    end_x = GRID_X2 if section == 0 else GRID_X3
    for x in range(start_x, end_x + 1, int(cell_size)):
        if (x, y) in powered_points:
            return True
    return False