import json
import pygame
from typing import Dict, List, Tuple, Set

class CircuitConverter:
    def __init__(self):
        self.GRID_X1 = 225
        self.GRID_Y1 = 288
        self.cell_size = 19.5
        self.gate_spacing = 100
        self.used_positions = set()
        self.component_positions = {}
        self.wires = []
        
    def load_circuit(self, json_path: str) -> dict:
        """Load circuit description from JSON file"""
        with open(json_path, 'r') as f:
            return json.load(f)
            
    def extract_gate_type(self, ic_name: str) -> str:
        """Extract gate type from IC name (e.g., 'AND7400' -> 'AND')"""
        if 'AND' in ic_name:
            return 'AND'
        elif 'NAND' in ic_name:
            return 'NAND'
        elif 'OR' in ic_name:
            return 'OR'
        elif 'NOR' in ic_name:
            return 'NOR'
        elif 'NOT' in ic_name:
            return 'NOT'
        return ic_name

    def parse_gate_id(self, component_str: str) -> tuple:
        """Parse gate ID and pin number from component string"""
        if component_str.startswith('IN') and len(component_str) <= 3:
            # Global input pin (e.g., 'IN1')
            return None, int(component_str[2:]), None
            
        if component_str.startswith('OUT'):
            # Global output pin (e.g., 'OUT1')
            return None, int(component_str[3:]), None
            
        # Handle gate components (e.g., 'AND1IN1', 'NOT1OUT')
        gate_type = ''
        numbers = []
        current_number = ''
        
        for char in component_str:
            if char.isalpha():
                if current_number:
                    numbers.append(int(current_number))
                    current_number = ''
                gate_type += char
            elif char.isdigit():
                current_number += char
                
        if current_number:
            numbers.append(int(current_number))
            
        gate_num = numbers[0] if numbers else 1
        pin_num = numbers[-1] if len(numbers) > 1 else None
        
        return gate_type, gate_num, pin_num

    def get_next_position(self, component_type: str) -> tuple:
        """Get next available grid position for a component"""
        base_x = self.GRID_X1 + len(self.used_positions) * self.gate_spacing
        base_y = self.GRID_Y1 + 50
        
        pos = (base_x, base_y)
        while pos in self.used_positions:
            base_x += self.cell_size
            pos = (base_x, base_y)
            
        self.used_positions.add(pos)
        return pos

    def create_gates(self, circuit_data: dict) -> dict:
        """Create gates based on circuit description"""
        gates = {}
        
        # Process IC boards and create gates
        for board in circuit_data['IC Boards used']:
            # Parse IC description (e.g., "AND7400 - Gates: 2")
            ic_name, count_part = board.split('-')
            gate_type = self.extract_gate_type(ic_name.strip())
            num_gates = int(count_part.split(':')[1].strip())
            
            # Create specified number of each gate type
            for i in range(num_gates):
                gate_id = f"{gate_type}{i+1}"
                pos = self.get_next_position(gate_type)
                self.component_positions[gate_id] = pos
                
                # Map gate types to simulator classes
                if gate_type == 'AND':
                    from AndGate import AndGate
                    gates[gate_id] = AndGate(*pos)
                elif gate_type == 'NAND':
                    from NandGate import NandGate
                    gates[gate_id] = NandGate(*pos)
                elif gate_type == 'OR':
                    from OrGate import OrGate
                    gates[gate_id] = OrGate(*pos)
                elif gate_type == 'NOR':
                    from NorGate import NorGate
                    gates[gate_id] = NorGate(*pos)
                elif gate_type == 'NOT':
                    from NotGate import NotGate
                    gates[gate_id] = NotGate(*pos)
                    
        return gates
        
    def create_connections(self, circuit_data: dict, gates: dict) -> list:
        """Create wire connections based on circuit description"""
        wires = []
        
        for connection in circuit_data['Connections']:
            from_component, to_component = connection.split(' to ')
            
            # Get source connection point
            if from_component.startswith('IN'):
                # Input switch connection
                input_num = int(from_component[2:]) - 1
                from_pos = (300 + input_num * 100, 80)
            else:
                # Gate output connection
                gate_type, gate_num, _ = self.parse_gate_id(from_component)
                gate_id = f"{gate_type}{gate_num}"
                if gate_id not in gates:
                    print(f"Warning: Gate {gate_id} not found")
                    continue
                from_pos = gates[gate_id].output_pos
                
            # Get destination connection point
            if to_component.startswith('OUT'):
                # Output connection
                output_num = int(to_component[3:]) - 1
                to_pos = (800 + output_num * 100, 750)
            else:
                # Gate input connection
                gate_type, gate_num, pin_num = self.parse_gate_id(to_component)
                gate_id = f"{gate_type}{gate_num}"
                if gate_id not in gates:
                    print(f"Warning: Gate {gate_id} not found")
                    continue
                    
                if pin_num == 1:
                    to_pos = gates[gate_id].input1_pos
                else:
                    to_pos = gates[gate_id].input2_pos
                    
            wires.append((from_pos, to_pos))
            
        return wires

    def setup_circuit(self, json_path: str) -> tuple:
        """Main function to set up circuit from JSON description"""
        try:
            circuit_data = self.load_circuit(json_path)
            gates = self.create_gates(circuit_data)
            wires = self.create_connections(circuit_data, gates)
            return gates, wires
        except Exception as e:
            print(f"Error setting up circuit: {e}")
            import traceback
            traceback.print_exc()
            return {}, []