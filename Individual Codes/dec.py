import cv2

import numpy as np

def decrypt_image(image_path):
    img = cv2.imread(image_path)

    if img is None:
        print("Error: Could not open image. Check file path.")
        return

    # Read stored password
    with open("password.txt", "r") as file:
        stored_password = file.read().strip()

    entered_password = input("Enter passcode for decryption: ")

    if entered_password == stored_password:
        n, m, z = 1, 0, 0  # Start from second row

        # Retrieve message length from the first pixel
        # Reconstruct the message length using bit shifts
        msg_len = (img[0, 0, 0]) + (img[0, 0, 1] << 8) + (img[0, 0, 2] << 16)

        message = ""

        # Decode message from image
        for _ in range(msg_len):
            message += chr(img[n, m, z])
            n += 1

            # Move within image bounds
            if n >= img.shape[0]:
                n = 1  # Start from second row
                m += 1

        print("Decrypted message:", message)
    else:
        print("YOU ARE NOT AUTHORIZED")

if __name__ == "__main__":
    image_path = "encryptedImage.png"
    decrypt_image(image_path)
