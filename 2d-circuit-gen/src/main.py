import pygame
import math
from bboard import propagate_power, render_powered_state, reset_powered_state
from bboard import powered_points, grounded_points  # Add grounded_points here
from components import InputManager
from LED import LEDPalette
from AndGate import AndGatePalette
from OrGate import OrGatePalette
from NandGate import NandGatePalette
from NorGate import NorGatePalette
from NotGate import NotGate, NotGatePalette
import argparse
# After initializing pygame, add:
from json_circ import CircuitConverter

# Add this after the imports but before pygame.init()
def parse_args():
    parser = argparse.ArgumentParser(description='Breadboard Circuit Simulator')
    parser.add_argument('--circuit-json', type=str, help='Path to circuit JSON file')
    return parser.parse_args()

# Initialize Pygame
pygame.init()

args = parse_args()

# Set up the window
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 800
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Breadboard Simulator")

# ic_manager = ICManager()
# ic_palette = ICPalette(50, 50)  # Position the palette on the left side
led_palette = LEDPalette(50, 200) 
and_gate_palette = AndGatePalette(50, 250)
nand_gate_palette = NandGatePalette(50,300)
or_gate_palette = OrGatePalette(50,350)
nor_gate_palette = NorGatePalette(50,400)
not_gate_palette = NotGatePalette(50,450)
placed_gates = []

input_manager = InputManager()
placed_leds = []  # Track placed LEDs

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

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WIRE_COLOR = (0, 0, 255)
VCC_COLOR = (0, 255, 0)
GND_COLOR = (255, 0, 0)

# Load and scale background image
try:
    #background_image = pygame.image.load("2d-circuit-gen/src/assets/bg.jpg")
    new_width = int(WINDOW_WIDTH * 0.9)
    new_height = int(WINDOW_HEIGHT * 0.75)
    #background_image = pygame.transform.smoothscale(background_image, (new_width, new_height))
except pygame.error:
    print("Warning: Could not load background image. Using white background.")
    background_image = None

# Setup positions
vcc_pos = (WINDOW_WIDTH // 2, 50)
gnd_pos = (WINDOW_WIDTH // 2, 100)
output_spacing = 100
output_circles = [(WINDOW_WIDTH // 2 - 4 * output_spacing + i * output_spacing, WINDOW_HEIGHT - 50) for i in range(9)]

def is_mouse_near_circle(mouse_pos, circle_pos, radius=8):
    distance = math.sqrt((mouse_pos[0] - circle_pos[0]) ** 2 + (mouse_pos[1] - circle_pos[1]) ** 2)
    return distance <= radius

def is_mouse_near_point(mouse_pos, point_pos, radius=8):
    """Helper function to check if mouse is near a point"""
    distance = math.sqrt((mouse_pos[0] - point_pos[0]) ** 2 + (mouse_pos[1] - point_pos[1]) ** 2)
    return distance <= radius

def get_grid_points():
    points = []
    # Upper grid points
    for x in range(GRID_X1, GRID_X2 + 1, int(cell_size)):
        for y in range(GRID_Y1, GRID_Y2 + 1, int(cell_size)):
            points.append((x, y))
    # Upper second grid points
    for x in range(GRID_X2E, GRID_X3 + 1, int(cell_size)):
        for y in range(GRID_Y1, GRID_Y2 + 1, int(cell_size)):
            points.append((x, y))
    # Lower grid points
    for x in range(GRID_X1, GRID_X2 + 1, int(cell_size)):
        for y in range(GRID_Y3, GRID_Y4 + 1, int(cell_size)):
            points.append((x, y))
    # Lower second grid points
    for x in range(GRID_X2E, GRID_X3 + 1, int(cell_size)):
        for y in range(GRID_Y3, GRID_Y4 + 1, int(cell_size)):
            points.append((x, y))
    # Power rails
    for i in range(0, 5):
        k = 116 * i
        for x in range(X1_RAIL + k, X2_RAIL + k + 1, int(cell_size)):
            for y in [Y1_UP_RAIL, Y2_UP_RAIL, Y1_DOWN_RAIL, Y2_DOWN_RAIL]:
                points.append((x, y))
        for x in range(X3_RAIL + k, X4_RAIL + k + 1, int(cell_size)):
            for y in [Y1_UP_RAIL, Y2_UP_RAIL, Y1_DOWN_RAIL, Y2_DOWN_RAIL]:
                points.append((x, y))
    return points

# Get all valid grid points
grid_points = get_grid_points()
wires = []  # Track all wires
# Main loop
running = True
start_point = None

# Initialize circuit from JSON if provided
if args.circuit_json:
    converter = CircuitConverter()
    new_gates, new_wires = converter.setup_circuit(args.circuit_json)
    placed_gates.extend(new_gates.values())
    wires.extend(new_wires)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                powered_points.clear()
                grounded_points.clear()
                reset_powered_state(window)
                wires.clear()
                placed_leds.clear()
                placed_gates.clear()
                output_colors = [(255, 255, 0)] * 9

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Check for input switch toggles first
            if input_manager.handle_click(mouse_pos):
                continue

            # Check for palette clicks
            if led_palette.handle_click(mouse_pos):
                continue
                
            
            if and_gate_palette.handle_click(mouse_pos):
                continue
            
            if nand_gate_palette.handle_click(mouse_pos):
                continue

            if or_gate_palette.handle_click(mouse_pos):
                continue
            
            if nor_gate_palette.handle_click(mouse_pos):
                continue

            if not_gate_palette.handle_click(mouse_pos):
                continue


            # Check if clicking on gate pins 
            gate_pin_clicked = False
            for gate in placed_gates:
                # Check if it's a NOT gate (has only 4 pins) or other type
                pin_names = ['vcc', 'input1', 'output', 'gnd'] if isinstance(gate, NotGate) else ['vcc', 'input1', 'input2', 'output', 'gnd']
                
                for pin_name in pin_names:
                    pin_pos = getattr(gate, f"{pin_name}_pos")
                    if is_mouse_near_point(mouse_pos, pin_pos):
                        if start_point is None:
                            start_point = pin_pos
                        else:
                            wires.append((start_point, pin_pos))
                            start_point = None
                        gate_pin_clicked = True
                        break
                if gate_pin_clicked:
                    break
            if gate_pin_clicked:
                continue

            # Check if clicking on LED terminals
            led_terminal_clicked = False
            for led in placed_leds:
                if is_mouse_near_point(mouse_pos, led.anode_pos):
                    if start_point is None:
                        start_point = led.anode_pos
                    else:
                        wires.append((start_point, led.anode_pos))
                        start_point = None
                    led_terminal_clicked = True
                    break
                elif is_mouse_near_point(mouse_pos, led.cathode_pos):
                    if start_point is None:
                        start_point = led.cathode_pos
                    else:
                        wires.append((start_point, led.cathode_pos))
                        start_point = None
                    led_terminal_clicked = True
                    break
            if led_terminal_clicked:
                continue

            # Check for input switch connection points
            switch = input_manager.get_switch_at_pos(mouse_pos)
            if switch:
                if start_point is None:
                    start_point = switch.output_pos
                else:
                    wires.append((start_point, switch.output_pos))
                    start_point = None
                continue
            
            # Check VCC and GND
            if is_mouse_near_point(mouse_pos, vcc_pos):
                if start_point is None:
                    start_point = vcc_pos
                else:
                    wires.append((start_point, vcc_pos))
                    start_point = None
                continue
            elif is_mouse_near_point(mouse_pos, gnd_pos):
                if start_point is None:
                    start_point = gnd_pos
                else:
                    wires.append((start_point, gnd_pos))
                    start_point = None
                continue
            
            # Check outputs
            for circle_pos in output_circles:
                if is_mouse_near_point(mouse_pos, circle_pos):
                    if start_point is None:
                        start_point = circle_pos
                    else:
                        wires.append((start_point, circle_pos))
                        start_point = None
                    break
            
            # Check grid points
            for point in grid_points:
                if is_mouse_near_point(mouse_pos, point):
                    if start_point is None:
                        start_point = point
                    else:
                        wires.append((start_point, point))
                        start_point = None
                    break

        if event.type == pygame.MOUSEMOTION:
            if led_palette.dragging_led:
                led_palette.handle_drag(pygame.mouse.get_pos())
            elif and_gate_palette.dragging_gate:
                and_gate_palette.handle_drag(pygame.mouse.get_pos())
            elif or_gate_palette.dragging_gate:  # Add this
                or_gate_palette.handle_drag(pygame.mouse.get_pos())
            elif nor_gate_palette.dragging_gate:  # Add this
                nor_gate_palette.handle_drag(pygame.mouse.get_pos())
            elif not_gate_palette.dragging_gate:  # Add this
                not_gate_palette.handle_drag(pygame.mouse.get_pos())
            elif nand_gate_palette.dragging_gate:  # Add this
                nand_gate_palette.handle_drag(pygame.mouse.get_pos())

        if event.type == pygame.MOUSEBUTTONUP:
            if led_palette.dragging_led:
                new_led = led_palette.handle_release()
                if new_led:
                    placed_leds.append(new_led)
            elif and_gate_palette.dragging_gate:
                new_gate = and_gate_palette.handle_release(grid_points)
                if new_gate:
                    placed_gates.append(new_gate)

            elif or_gate_palette.dragging_gate:  # Add this
                new_gate = or_gate_palette.handle_release(grid_points)
                if new_gate:
                    placed_gates.append(new_gate)

            elif nor_gate_palette.dragging_gate:  # Add this
                new_gate = nor_gate_palette.handle_release(grid_points)
                if new_gate:
                    placed_gates.append(new_gate)

            elif not_gate_palette.dragging_gate:  # Add this
                new_gate = not_gate_palette.handle_release(grid_points)
                if new_gate:
                    placed_gates.append(new_gate)

            elif nand_gate_palette.dragging_gate:
                new_gate = nand_gate_palette.handle_release(grid_points)
                if new_gate:
                    placed_gates.append(new_gate)

    # Clear window
    window.fill(WHITE)

    # Draw background if available
    #if background_image:
        #image_rect = background_image.get_rect()
        #image_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        #window.blit(background_image, image_rect)

    # Update power state
    powered_points = set()
    powered_inputs = input_manager.get_powered_points()
    powered_points, grounded_points = propagate_power(
    wires, 
    vcc_pos, 
    gnd_pos, 
    output_circles, 
    placed_gates,
    input_manager  # Pass the instance
)
    powered_points.update(powered_inputs)

    # Draw VCC and GND
    pygame.draw.circle(window, VCC_COLOR, vcc_pos, 10)
    pygame.draw.circle(window, GND_COLOR, gnd_pos, 10)

    # Draw labels
    font = pygame.font.Font(None, 36)
    vcc_text = font.render("VCC", True, BLACK)
    gnd_text = font.render("GND", True, BLACK)
    window.blit(vcc_text, (vcc_pos[0] + 20, vcc_pos[1] - 10))
    window.blit(gnd_text, (gnd_pos[0] + 20, gnd_pos[1] - 10))

    # Draw components and wires
    render_powered_state(window, output_circles)
    
    # Draw wires first (so they appear behind components)
    for start, end in wires:
        pygame.draw.line(window, WIRE_COLOR, start, end, 4)

    # Draw preview wire
    if start_point:
        pygame.draw.line(window, WIRE_COLOR, start_point, pygame.mouse.get_pos(), 4)

    # Draw inputs
    input_manager.draw(window)

    # Draw palettes and components
    led_palette.draw(window, powered_points, grounded_points, vcc_pos, gnd_pos)
    and_gate_palette.draw(window, powered_points, grounded_points, vcc_pos, gnd_pos)
    or_gate_palette.draw(window, powered_points, grounded_points, vcc_pos, gnd_pos)
    nor_gate_palette.draw(window, powered_points, grounded_points, vcc_pos, gnd_pos)
    nand_gate_palette.draw(window, powered_points, grounded_points, vcc_pos, gnd_pos)
    not_gate_palette.draw(window, powered_points, grounded_points, vcc_pos, gnd_pos)
    
    # Draw placed components
    for led in placed_leds:
        led.draw(window, powered_points, grounded_points, vcc_pos, gnd_pos)
    for gate in placed_gates:
        gate.draw(window, powered_points, grounded_points, vcc_pos, gnd_pos)

    pygame.display.flip()

pygame.quit()

