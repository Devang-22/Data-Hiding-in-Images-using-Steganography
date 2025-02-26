import gradio as gr
import cv2
import numpy as np
import os

# Encryption function
def encrypt_image(image, message, password):
    img = cv2.imread(image)
    if img is None:
        return "Error: Could not open image."

    height, width, _ = img.shape

    ascii_values = [ord(char) for char in message]
    msg_len = len(ascii_values)

    with open("password.txt", "w") as file:
        file.write(password)

    img[0, 0] = [msg_len % 256, (msg_len // 256) % 256, (msg_len // (256 * 256)) % 256]

    n, m, z = 1, 0, 0
    for val in ascii_values:
        img[n, m, z] = val
        n += 1
        if n >= height:
            n = 1
            m += 1
        if m >= width:
            return "Error: Message is too long for this image!"

    output_path = "encryptedImage.png"
    cv2.imwrite(output_path, img)
    return output_path

# Decryption function
def decrypt_image(image, password):
    img = cv2.imread(image)
    if img is None:
        return "Error: Could not open image."

    try:
        with open("password.txt", "r") as file:
            stored_password = file.read().strip()
    except FileNotFoundError:
        return "Password file not found."

    if password != stored_password:
        return "YOU ARE NOT AUTHORIZED"

    msg_len = (img[0, 0, 0]) + (img[0, 0, 1] << 8) + (img[0, 0, 2] << 16)
    n, m, z = 1, 0, 0
    message = ""
    for _ in range(msg_len):
        message += chr(img[n, m, z])
        n += 1
        if n >= img.shape[0]:
            n = 1
            m += 1

    return message

# Gradio interface
encrypt_interface = gr.Interface(
    fn=encrypt_image,
    inputs=[gr.File(label="Select Image"), gr.Textbox(label="Secret Message"), gr.Textbox(label="Passcode", type="password")],
    outputs=gr.File(label="Encrypted Image"),
    title="Image Encryption"
)

decrypt_interface = gr.Interface(
    fn=decrypt_image,
    inputs=[gr.File(label="Select Encrypted Image"), gr.Textbox(label="Passcode", type="password")],
    outputs=gr.Textbox(label="Decrypted Message"),
    title="Image Decryption"
)

app = gr.TabbedInterface([encrypt_interface, decrypt_interface], ["Encrypt Image", "Decrypt Image"])

app.launch()
