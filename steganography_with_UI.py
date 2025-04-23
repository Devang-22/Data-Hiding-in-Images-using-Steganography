import gradio as gr
import numpy as np
import os
import hashlib
import tempfile
from PIL import Image
import io

# Use PIL instead of OpenCV to avoid NumPy 2.x compatibility issues
def encrypt_image(image_file, message, password):
    try:
        # Handle file upload properly
        if isinstance(image_file, str):
            pil_image = Image.open(image_file)
        else:
            pil_image = Image.open(image_file.name)
        
        # Convert to numpy array (compatible with NumPy 2.x)
        img_array = np.array(pil_image)
        
        # Check if image has alpha channel and convert if needed
        if len(img_array.shape) == 2:  # Grayscale
            img_array = np.stack((img_array,) * 3, axis=-1)
        elif img_array.shape[2] == 4:  # RGBA
            img_array = img_array[:, :, :3]  # Strip alpha channel
            
        height, width, _ = img_array.shape
        max_bytes = height * width * 3 - 3  # Subtract 3 for header
        
        if len(message) > max_bytes:
            return None, f"Error: Message is too long for this image! Maximum capacity: {max_bytes} characters."
            
        # Create secure password hash
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Use secure temporary directory
        temp_dir = tempfile.gettempdir()
        hash_file = os.path.join(temp_dir, "password_hash.txt")
        with open(hash_file, "w") as file:
            file.write(password_hash)
            
        # Store message length in first pixel
        msg_len = len(message)
        img_array[0, 0] = [msg_len % 256, (msg_len // 256) % 256, (msg_len // (256 * 256)) % 256]
            
        # Encode message in the image
        n, m, z = 1, 0, 0
        for char in message:
            val = ord(char)
            img_array[n, m, z] = val
            n += 1
            if n >= height:
                n = 1
                m += 1
                if m >= width:
                    z += 1
                    if z >= 3:
                        return None, "Error: Message capacity exceeded!"
                    m = 0
                        
        # Save encrypted image
        output_path = os.path.join(temp_dir, "encrypted_image.png")
        Image.fromarray(img_array).save(output_path)
        
        return output_path, "Image encrypted successfully!"
    except Exception as e:
        return None, f"Error: {str(e)}"

def decrypt_image(image_file, password):
    try:
        # Handle file upload properly
        if isinstance(image_file, str):
            pil_image = Image.open(image_file)
        else:
            pil_image = Image.open(image_file.name)
            
        # Convert to numpy array (compatible with NumPy 2.x)
        img_array = np.array(pil_image)
        
        # Make sure we're working with RGB
        if len(img_array.shape) == 2:  # Grayscale
            return "Error: Invalid image format. Please use an encrypted RGB image."
        elif img_array.shape[2] == 4:  # RGBA
            img_array = img_array[:, :, :3]  # Strip alpha channel
            
        # Verify password using hash
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        temp_dir = tempfile.gettempdir()
        hash_file = os.path.join(temp_dir, "password_hash.txt")
        
        try:
            with open(hash_file, "r") as file:
                stored_hash = file.read().strip()
        except FileNotFoundError:
            return "Error: This image hasn't been encrypted with this application or password file is missing."
            
        if password_hash != stored_hash:
            return "ACCESS DENIED: Incorrect password"
            
        # Extract message length from first pixel
        msg_len = int(img_array[0, 0, 0] + (img_array[0, 0, 1] << 8) + (img_array[0, 0, 2] << 16))
        
        # Extract message from image
        height, width, _ = img_array.shape
        n, m, z = 1, 0, 0
        message = ""
        
        for _ in range(msg_len):
            message += chr(img_array[n, m, z])
            n += 1
            if n >= height:
                n = 1
                m += 1
                if m >= width:
                    z += 1
                    if z >= 3:
                        break
                    m = 0
                    
        return message
    except Exception as e:
        return f"Error: {str(e)}"

# Create a modern Gradio interface
with gr.Blocks(title="Secure Image Steganography") as app:
    gr.Markdown("# Secure Image Steganography")
    gr.Markdown("Hide secret messages within images - Compatible with NumPy 2.x")
    
    with gr.Tabs():
        with gr.Tab("Encrypt"):
            with gr.Row():
                with gr.Column():
                    input_image = gr.Image(type="filepath", label="Upload Image")
                    message = gr.Textbox(
                        label="Secret Message", 
                        placeholder="Type your secret message here...",
                        lines=5
                    )
                    password = gr.Textbox(
                        label="Password", 
                        type="password", 
                        placeholder="Enter a strong password"
                    )
                    encrypt_btn = gr.Button("Encrypt Image", variant="primary")
                
                with gr.Column():
                    output_image = gr.Image(label="Encrypted Image")
                    status_encrypt = gr.Textbox(
                        label="Status", 
                        interactive=False,
                        value="Ready to encrypt"
                    )
            
            encrypt_btn.click(
                fn=encrypt_image,
                inputs=[input_image, message, password],
                outputs=[output_image, status_encrypt]
            )

        with gr.Tab("Decrypt"):
            with gr.Row():
                with gr.Column():
                    encrypted_image = gr.Image(type="filepath", label="Upload Encrypted Image")
                    decrypt_password = gr.Textbox(
                        label="Password", 
                        type="password", 
                        placeholder="Enter the password"
                    )
                    decrypt_btn = gr.Button("Decrypt Message", variant="primary")
                
                with gr.Column():
                    decrypted_message = gr.Textbox(
                        label="Decrypted Message", 
                        interactive=False,
                        lines=5
                    )
            
            decrypt_btn.click(
                fn=decrypt_image,
                inputs=[encrypted_image, decrypt_password],
                outputs=decrypted_message
            )
    
    gr.Markdown("### Usage Instructions")
    gr.Markdown("1. **Encrypt:** Upload an image, enter your secret message and a password, then click 'Encrypt Image'")
    gr.Markdown("2. **Decrypt:** Upload an encrypted image, enter the correct password, then click 'Decrypt Message'")
    gr.Markdown("3. **Security:** The encrypted image looks normal but contains your hidden message")

# Launch the app
app.launch()