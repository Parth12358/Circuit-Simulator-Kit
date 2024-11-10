from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage
from dotenv import load_dotenv
import json
import os
import asyncio
import base64
from openai import AsyncOpenAI
from typing import Optional

# Load environment variables
load_dotenv()

def load_components():
    try:
        with open("data/components.json", 'r') as file:
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
        # Create OpenAI client directly
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

async def main():
    while True:
        print("\nOptions:")
        print("1. Circuit Design from Text")
        print("2. Circuit Design from Image")
        print("3. Quit")
        
        choice = input("Choose an option (1-3): ")
        
        if choice == "3":
            break
            
        components = load_components()
        
        if choice == "1":
            user_input = input("\nEnter your circuit design request: ")
            prompt = f"""You are a circuit design instructor. Build digital circuits using ONLY:
{components}
Use standard naming:
Inputs: IN1, IN2, IN3...
Outputs: OUT1, OUT2, OUT3...
Rules:
Connect all inputs/outputs
No floating inputs
Last connection must go to output pin
GENERATE ONLY:
IC Boards used:
[IC PART#] - Gates: [GATE#]
Connections:
[FROM] to [TO]
-END-
Example:
IC Boards used:
7408 - Gates: 1
7404 - Gates: 1
Connections:
IN1 to 7408-1A
IN2 to 7408-1B
7408-1Y to 7404-1A
7404-1Y to OUT1
Current request: {user_input}"""

            response = await process_circuit_design(prompt)
            print("\nGenerated Circuit:")
            print(response)
            
        elif choice == "2":
            image_path = input("\nEnter the path to your circuit diagram image: ")
            if not os.path.exists(image_path):
                print("Error: Image file not found")
                continue
                
            print("\nAnalyzing circuit diagram...")
            circuit_description = await analyze_circuit_image(image_path, components)
            
            if circuit_description.startswith("Error"):
                print(circuit_description)
                continue
                
            print("\nAnalysis Result:")
            print(circuit_description)
            
            # Process the analysis through circuit design
            prompt = f"""You are a circuit design instructor. Build digital circuits using ONLY:
{components}
Use standard naming:
Inputs: IN1, IN2, IN3...
Outputs: OUT1, OUT2, OUT3...
Rules:
Use each gate once
Connect all inputs/outputs
No floating inputs
Last connection must go to output pin

GENERATE ONLY:
IC Boards used:
[IC PART#] - Gates: [GATE#]
Connections:
[FROM] to [TO]
-END-
Example:
IC Boards used:
7408 - Gates: 1
7404 - Gates: 1
Connections:
IN1 to 7408-1A
IN2 to 7408-1B
7408-1Y to 7404-1A
7404-1Y to OUT1
Current request: {circuit_description}"""

            final_design = await process_circuit_design(prompt)
            print("\nFinal Circuit Design:")
            print(final_design)
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    asyncio.run(main())