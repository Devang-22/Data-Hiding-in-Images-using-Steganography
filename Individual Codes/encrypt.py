import cv2
import numpy as np

def encrypt_image(image_path, output_path, message, password):
    img = cv2.imread(image_path)

    if img is None:
        print("Error: Could not open image. Check file path.")
        return

    height, width, _ = img.shape

    # Convert message to ASCII values
    ascii_values = [ord(char) for char in message]
    msg_len = len(ascii_values)

    # Store password in a text file
    with open("password.txt", "w") as file:
        file.write(password)

    n, m, z = 1, 0, 0  # Start from second row to store actual message

    # Store message length in the first row (3 channels of 1st pixel)
    img[0, 0] = [msg_len % 256, (msg_len // 256) % 256, (msg_len // (256 * 256)) % 256]

    # Encrypt message into image
    for val in ascii_values:
        img[n, m, z] = val
        n += 1

        # Move within image bounds
        if n >= height:
            n = 1  # Start from second row
            m += 1
        if m >= width:
            print("Error: Message is too long for this image!")
            return

    # Save as PNG
    cv2.imwrite(output_path, img)
    print("Message encrypted and saved in", output_path)

if __name__ == "__main__":
    image_path = "car.png"  # Use PNG
    output_path = "encryptedImage.png"

    msg = input("Enter secret message: ")
    password = input("Enter a passcode: ")

    encrypt_image(image_path, output_path, msg, password)
