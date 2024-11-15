import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import asyncio
from functools import partial
import os
from PIL import Image, ImageTk
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage
from dotenv import load_dotenv
import json
import base64
from openai import AsyncOpenAI
from typing import Optional

# Load environment variables
load_dotenv()

def load_components():
    try:
        with open("circuitCommandGen/data/components.json", 'r') as file:
            data = json.load(file)
            return "\n".join(
                f"{component['component']} ({component['code']}): {component['description']} - Inputs: {component['inputs']}, Outputs: {component['outputs']}"
                for component in data
            )
    except Exception as e:
        print(f"Error loading components: {e}")
        return ""

async def encode_image(image_path: str) -> Optional[str]:
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

async def analyze_circuit_image(image_path: str, components: str) -> str:
    try:
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        base64_image = await encode_image(image_path)
        
        if not base64_image:
            return "Error: Could not encode image"

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Analyze this image and describe it using preferably these components:\n{components}\n\nFormat the response as:\nIC Boards used:\n[IC PART#] - Gates: [GATE#]\n\nConnections:\n[FROM] to [TO]"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error during image analysis: {str(e)}"

async def process_circuit_design(prompt: str) -> str:
    try:
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        messages = [
            {
                "role": "system",
                "content": "You are a circuit design expert. Generate circuit designs using the specified components and format."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error in circuit design: {str(e)}"

class CircuitDesignerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Circuit Generator")
        self.root.geometry("800x600")
        
        # Configure root grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Load components
        self.components = load_components()
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Circuit Designer", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, pady=10)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew")
        
        # Text-based design tab
        self.text_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.text_tab, text="Text Design")
        self.setup_text_tab()
        
        # Image-based design tab
        self.image_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.image_tab, text="Image Design")
        self.setup_image_tab()
        
        # Output area
        self.setup_output_area(main_frame)
        
    def setup_text_tab(self):
        self.text_tab.grid_columnconfigure(0, weight=1)
        
        # Input label
        input_label = ttk.Label(self.text_tab, text="Enter your circuit design request:")
        input_label.grid(row=0, column=0, pady=(10,5), padx=10, sticky="w")
        
        # Input text area
        self.text_input = scrolledtext.ScrolledText(self.text_tab, height=5)
        self.text_input.grid(row=1, column=0, pady=5, padx=10, sticky="nsew")
        
        # Process button
        process_btn = ttk.Button(self.text_tab, text="Process Design",
                               command=self.process_text_design)
        process_btn.grid(row=2, column=0, pady=10)
        
    def setup_image_tab(self):
        self.image_tab.grid_columnconfigure(0, weight=1)
        
        # Image preview frame
        self.preview_frame = ttk.LabelFrame(self.image_tab, text="Image Preview")
        self.preview_frame.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")
        
        # Image preview label
        self.preview_label = ttk.Label(self.preview_frame, text="No image selected")
        self.preview_label.grid(row=0, column=0, pady=10, padx=10)
        
        # Browse button
        browse_btn = ttk.Button(self.image_tab, text="Browse Image",
                              command=self.browse_image)
        browse_btn.grid(row=1, column=0, pady=5)
        
        # Process button
        process_btn = ttk.Button(self.image_tab, text="Analyze Image",
                               command=self.process_image_design)
        process_btn.grid(row=2, column=0, pady=5)
        
        self.image_path = None
        
    def setup_output_area(self, parent):
        # Output frame
        output_frame = ttk.LabelFrame(parent, text="Output")
        output_frame.grid(row=2, column=0, pady=10, sticky="nsew")
        output_frame.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(2, weight=1)
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(output_frame, height=10)
        self.output_text.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")

         # Add clear button
        clear_btn = ttk.Button(output_frame, text="Clear Output", command=self.clear_output)
        clear_btn.grid(row=1, column=0, pady=(0, 5))


    def clear_output(self):
        """Clear the output text area"""
        self.output_text.delete("1.0", tk.END)
    def browse_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            self.image_path = file_path
            self.update_image_preview()
            
    def update_image_preview(self):
        if self.image_path:
            # Load and resize image for preview
            image = Image.open(self.image_path)
            image.thumbnail((300, 300))  # Resize for preview
            photo = ImageTk.PhotoImage(image)
            
            # Update preview label
            if hasattr(self, 'preview_photo'):
                self.preview_label.configure(image='')
            self.preview_photo = photo
            self.preview_label.configure(image=photo, text='')
            
    # Replace the process_text_design and related methods with these corrected versions:

    def process_text_design(self):
        """Prepare and initiate text design processing"""
        request = self.text_input.get("1.0", tk.END).strip()
        if not request:
            self.show_output("Please enter a circuit design request.")
            return
        
        prompt = f"""You are a circuit design instructor. Build digital circuits using ONLY: {self.components}
    Use standard naming:
    Inputs: IN1, IN2, IN3...
    Outputs: OUT1, OUT2, OUT3...
    Rules:
    Connect all inputs/outputs
    No floating inputs
    Last connection must go to output pin
    Don't generate any description

    Eg.
    IC Boards used:
    [IC 7400] - Gates: [NAND]
    [IC 7402] - Gates: [NOR]
    [IC 7404] - Gates: [NOT]

    Connections:
    [IN1] to [IC 7408 - AND1 Input 1]
    [IN2] to [IC 7408 - AND2 Input 1]
    [IN3] to [IC 7404 - NOT1 Input]
    [IN3] to [IC 7408 - AND2 Input 2]

    GENERATE ONLY:
    IC Boards used:
    [IC PART#] - Gates: [GATE#]
    Connections:
    [FROM] to [TO]
    -END-
    Current request: {request}"""
            
        # Create async task
        asyncio.run(self.run_text_design(prompt))

    async def run_text_design(self, request):
        """Run the async text design process"""
        self.show_output("Processing request...\n")
        try:
            result = await process_circuit_design(request)
            self.show_output(result)
        except Exception as e:
            self.show_output(f"Error: {str(e)}")
            
    def process_image_design(self):
        """Prepare and initiate image design processing"""
        if not self.image_path:
            self.show_output("Please select an image first.")
            return
            
        # Create async task
        asyncio.run(self.run_image_design())

    async def run_image_design(self):
        """Run the async image design process"""
        self.show_output("Analyzing image...\n")
        try:
            result = await analyze_circuit_image(self.image_path, self.components)
            self.show_output(result)
        except Exception as e:
            self.show_output(f"Error: {str(e)}")

    def show_output(self, text):
        """Display output and save to JSON"""
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, text)

        # Save the output as JSON
        try:
            # Format the circuit text into proper JSON structure
            circuit_json = self.format_circuit_json(text)
            
            # Save to file
            with open('circuit_output.json', 'w') as f:
                json.dump(circuit_json, f, indent=4)
            self.output_text.insert(tk.END, "\nOutput saved to circuit_output.json")
        except Exception as e:
            self.output_text.insert(tk.END, f"\nError saving JSON: {e}")
            
        def process_image_design(self):
            if not self.image_path:
                self.show_output("Please select an image first.")
                return
                
            # Create async task
            asyncio.run(self.run_image_design())

        def format_circuit_json(self, text: str) -> dict:
            """Format the circuit text into proper JSON structure"""
            try:
                # Split the text into sections
                sections = text.split('\n\n')
                ic_boards = []
                connections = []
                
                current_section = None
                for line in text.split('\n'):
                    line = line.strip()
                    if line == "IC Boards used:":
                        current_section = "ic_boards"
                    elif line == "Connections:":
                        current_section = "connections"
                    elif line and current_section == "ic_boards" and line != "IC Boards used:":
                        ic_boards.append(line)
                    elif line and current_section == "connections" and line != "Connections:":
                        connections.append(line)

                # Create proper JSON structure
                circuit_json = {
                    "IC Boards used": ic_boards,
                    "Connections": connections
                }
                return circuit_json
            except Exception as e:
                print(f"Error formatting JSON: {e}")
                return {"error": str(e)}

    def save_circuit_json(self):
        """Save the circuit description as JSON file"""
        text = self.output_text.get("1.0", tk.END).strip()
        if not text:
            self.show_output("No circuit to save!")
            return
            
        circuit_json = self.format_circuit_json(text)
        
        # Open file dialog for saving
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Save Circuit JSON"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(circuit_json, f, indent=4)
                self.output_text.insert(tk.END, f"\nCircuit saved to {file_path}")
            except Exception as e:
                self.output_text.insert(tk.END, f"\nError saving JSON: {e}")

    # Update the setup_output_area method to add the save button:
    def setup_output_area(self, parent):
        # Output frame
        output_frame = ttk.LabelFrame(parent, text="Output")
        output_frame.grid(row=2, column=0, pady=10, sticky="nsew")
        output_frame.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(2, weight=1)
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(output_frame, height=10)
        self.output_text.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")

        # Button frame
        button_frame = ttk.Frame(output_frame)
        button_frame.grid(row=1, column=0, pady=(0, 5))
        
        # Clear button
        clear_btn = ttk.Button(button_frame, text="Clear Output", command=self.clear_output)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Save JSON button
        save_btn = ttk.Button(button_frame, text="Save Circuit JSON", command=self.save_circuit_json)
        save_btn.pack(side=tk.LEFT, padx=5)
            
        async def run_text_design(self, request):
            self.show_output("Processing request...\n")
            try:
                result = await process_circuit_design(request)
                self.show_output(result)
            except Exception as e:
                self.show_output(f"Error: {str(e)}")
                
        async def run_image_design(self):
            self.show_output("Analyzing image...\n")
            try:
                result = await analyze_circuit_image(self.image_path, self.components)
                self.show_output(result)
            except Exception as e:
                self.show_output(f"Error: {str(e)}")
                
    def show_output(self, text):
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, text)

        # Save the entire output as a single string in JSON format
        data = {
            "Output": text
        }

        # Write to JSON file
        file_name = "circuit_output.json"
        try:
            with open(file_name, 'w') as json_file:
                json.dump(data, json_file, indent=4)
            self.output_text.insert(tk.END, f"\nOutput saved to {file_name}")
        except Exception as e:
            self.output_text.insert(tk.END, f"\nError saving to JSON: {e}")

def main():
    root = tk.Tk()
    app = CircuitDesignerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
