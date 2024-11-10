class LogicGate:
    def __init__(self, ic_name, number):
        self.ic_name = ic_name
        self.number = number
        # Pin mappings for AND, OR, NOT gates
        self.pin_mappings = {
            '7408': {  # AND Gate (Quad 2-input)
                1: {'A': 1, 'B': 2, 'Y': 3},
                2: {'A': 4, 'B': 5, 'Y': 6},
                3: {'A': 9, 'B': 10, 'Y': 8},
                4: {'A': 12, 'B': 13, 'Y': 11},
                'VCC': 14,
                'GND': 7
            },
            '7432': {  # OR Gate (Quad 2-input)
                1: {'A': 1, 'B': 2, 'Y': 3},
                2: {'A': 4, 'B': 5, 'Y': 6},
                3: {'A': 9, 'B': 10, 'Y': 8},
                4: {'A': 12, 'B': 13, 'Y': 11},
                'VCC': 14,
                'GND': 7
            },
            '7404': {  # NOT Gate (Hex inverter)
                1: {'A': 1, 'Y': 2},
                2: {'A': 3, 'Y': 4},
                3: {'A': 5, 'Y': 6},
                4: {'A': 9, 'Y': 8},
                5: {'A': 11, 'Y': 10},
                6: {'A': 13, 'Y': 12},
                'VCC': 14,
                'GND': 7
            }
        }
        
    def get_pin_number(self, pin_type):
        """Get the actual pin number for a given gate input/output"""
        gate_pins = self.pin_mappings[self.ic_name][self.number]
        if pin_type not in gate_pins:
            raise ValueError(f"Invalid pin type '{pin_type}' for IC {self.ic_name}")
        return gate_pins[pin_type]

class BreadboardParser:
    def __init__(self):
        self.ics = {}
        self.connections = []
        
    def parse_input(self, input_text):
        lines = input_text.strip().split('\n')
        ic_section = True
        
        for line in lines:
            line = line.strip()
            if line == "-END-":
                break
            elif line.startswith("Connections:"):
                ic_section = False
                continue
            elif line == "" or line.startswith("IC Boards used:"):
                continue
                
            if ic_section:
                # Parse IC line
                parts = line.split('-')
                ic_number = parts[0].split('.')[1].strip()
                gates_used = parts[1].split(':')[1].strip()
                
                gates = [int(g.strip()) for g in gates_used.split(',')]
                for gate in gates:
                    key = f"{ic_number}-{gate}"
                    self.ics[key] = LogicGate(ic_number, gate)
            else:
                # Parse connection line
                if not line[0].isdigit():
                    continue
                    
                conn = line.split('.')[1].strip()
                source, dest = [x.strip() for x in conn.split(' to ')]
                self.connections.append((source, dest))
    
    def get_gate_type(self, ic_number):
        mapping = {
            '7408': 'AND',
            '7432': 'OR',
            '7404': 'NOT'
        }
        return mapping.get(ic_number, ic_number)
    
    def generate_breadboard_layout(self):
        result = []
        result.append("Breadboard Layout Instructions:")
        result.append("==============================")
        
        # Add IC placement instructions
        result.append("\nIC Placement:")
        placed_ics = set()
        for ic_key in self.ics:
            ic_number = ic_key.split('-')[0]
            if ic_number not in placed_ics:
                gate_type = self.get_gate_type(ic_number)
                result.append(f"- Place {ic_number} ({gate_type}) in the breadboard")
                result.append(f"  * Connect pin {self.ics[ic_key].pin_mappings[ic_number]['VCC']} to +5V")
                result.append(f"  * Connect pin {self.ics[ic_key].pin_mappings[ic_number]['GND']} to GND")
                placed_ics.add(ic_number)
        
        # Add connection instructions
        result.append("\nConnections:")
        for source, dest in self.connections:
            try:
                if '-' in source:  # Source is an IC pin
                    ic_name_src, pin_info_src = source.split('-')
                    gate_num_src = int(pin_info_src[0])
                    pin_type_src = pin_info_src[1:]
                    ic_gate_src = self.ics[f"{ic_name_src}-{gate_num_src}"]
                    source_pin = ic_gate_src.get_pin_number(pin_type_src)
                    source_text = f"{source} (pin {source_pin})"
                else:
                    source_text = source

                if '-' in dest:  # Destination is an IC pin
                    ic_name_dest, pin_info_dest = dest.split('-')
                    gate_num_dest = int(pin_info_dest[0])
                    pin_type_dest = pin_info_dest[1:]
                    ic_gate_dest = self.ics[f"{ic_name_dest}-{gate_num_dest}"]
                    dest_pin = ic_gate_dest.get_pin_number(pin_type_dest)
                    dest_text = f"{dest} (pin {dest_pin})"
                else:
                    dest_text = dest

                result.append(f"- Connect {source_text} to {dest_text}")
            except ValueError as e:
                result.append(f"- Error with connection {source} to {dest}: {str(e)}")
                continue

        return '\n'.join(result)

def main():
    input_text = """IC Boards used:
1. 7408 - Using gates: 1,2
2. 7404 - Using gates: 1
Connections:
1. A to 7408-1A
2. B to 7408-1B
3. 7408-1Y to 7404-1A
4. C to 7408-2A
5. 7408-2Y to 7404-1B
6. 7404-1Y to OUT1
-END-"""

    parser = BreadboardParser()
    parser.parse_input(input_text)
    layout = parser.generate_breadboard_layout()
    print(layout)

if __name__ == "__main__":
    main()