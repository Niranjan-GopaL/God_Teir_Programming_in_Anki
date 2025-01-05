import os
import subprocess

# Trying to do this for all
# ffmpeg -i input_image.jpg -vf scale=170:-1 output_image.jpg



directory = "path/to/your/directory"

for filename in os.listdir(directory):
    if filename.endswith(".jpg") or filename.endswith(".png"):  # Add other extensions as needed
        input_path = os.path.join(directory, filename)
        output_path = os.path.join(directory, f"resized_{filename}")
        
        # Use ffmpeg to resize the image
        subprocess.run([
            "ffmpeg", 
            "-i", input_path, 
            "-vf", "scale=170:-1", 
            output_path
        ])
        print(f"Resized: {filename} -> {output_path}")