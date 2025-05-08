import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import load_dotenv
import os
from time import sleep

# Load environment variables
load_dotenv()
API_KEY = os.getenv("HuggingFaceAPIKey")
if not API_KEY:
    raise ValueError("HuggingFaceAPIKey not found in .env file")

# Function to open and display images based on a given prompt
def open_images(prompt):
    folder_path = "Data"  # Folder where the images are stored
    prompt = prompt.replace(" ", "_")  # Replace spaces in prompt with underscores
    # Generate the filenames for the images
    files = [f"{prompt}{i}.jpg" for i in range(1, 5)]
    
    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)
        try:
            # Try to open and display the image
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)  # Pause for 1 second before showing the next image
        except IOError as e:
            print(f"Unable to open {image_path}: {e}")

# API details for the Hugging Face Stable Diffusion model
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0" 
headers = {"Authorization": f"Bearer {API_KEY}"} 

# Async function to send a query to the Hugging Face API
async def query(payload):
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

# Async function to generate images based on the given prompt
async def generate_images(prompt: str):
    # Create directory if it doesn't exist
    os.makedirs("Data", exist_ok=True)
    
    tasks = []
    # Create 4 image generation tasks
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness-maximum, Ultra High details, high resolution, seed = {randint(0, 1000000)}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)
    
    # Wait for all tasks to complete
    image_bytes_list = await asyncio.gather(*tasks)
    
    # Save the generated images to files
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:  # Only save if we got a valid response
            filename = os.path.join("Data", f"{prompt.replace(' ','_')}{i + 1}.jpg")
            with open(filename, "wb") as f:
                f.write(image_bytes)
                print(f"Saved image to {filename}")

# Wrapper function to generate and open images
def generate_images_sync(prompt: str):
    asyncio.run(generate_images(prompt))  # Run the async image generation
    open_images(prompt)  # Open the generated images
    return True

# Main loop to monitor for image generation requests
def main():
    data_file_path = os.path.join("Frontend", "Files", "ImageGeneration.data")
    
    # Check if the data file exists
    if not os.path.exists(data_file_path):
        parent_dir = os.path.dirname(data_file_path)
        os.makedirs(parent_dir, exist_ok=True)
        with open(data_file_path, "w") as f:
            f.write("False,False")
    
    print("Monitoring for image generation requests...")
    while True:
        try:
            # Read the status and prompt from the data file
            with open(data_file_path, "r") as f:
                data = f.read().strip()
            
            if ',' not in data:
                print(f"Invalid data format in file: {data}")
                sleep(1)
                continue
                
            prompt, status = data.split(",", 1)
            
            # If the status indicates an image generation request
            if status.strip().lower() == "true":
                print(f"Generating Images for prompt: {prompt}")
                success = generate_images_sync(prompt=prompt)
                
                # Reset the status in the file after generating images
                with open(data_file_path, "w") as f:
                    f.write("False,False")
                
                print("Image generation complete")
            else:
                sleep(1)  # Wait for 1 second before checking again
        except Exception as e:
            print(f"Error in main loop: {e}")
            sleep(5)  # Wait a bit longer when an error occurs

if __name__ == "__main__":
    main()