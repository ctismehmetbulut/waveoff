import base64
import binascii
import numpy as np
import cv2
import time

def base64_to_image(base64_data, output_image_folder, width, height):
    """
    Converts a Base64-encoded image stored in a text file into a PNG image file.

    Args:
        input_txt_file (str): Path to the input .txt file containing Base64 data.
        output_image_folder (str): Folder where the resulting PNG image will be saved.
        width (int): Width of the image in pixels.
        height (int): Height of the image in pixels.

    Returns:
        str: Path to the saved image file.
    """

    # Decode the Base64 data into raw bytes
    byte_data = base64.b64decode(base64_data)

    # Convert the raw bytes into a NumPy array
    image_data = np.frombuffer(byte_data, dtype=np.uint8).reshape((height, width, 3))

    # Create the output image file path with Unix timestamp
    output_image_path = f"{output_image_folder}/{int(time.time() * 1000)}.png"

    # Save the image as PNG using OpenCV
    cv2.imwrite(output_image_path, image_data)

    print(f"Image saved to: {output_image_path}")
    return output_image_path

def is_valid_base64(data):
    try:
        base64.b64decode(data, validate=True)
        return True
    except binascii.Error:
        return False
