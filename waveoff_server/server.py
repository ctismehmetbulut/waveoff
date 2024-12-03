import json
import cv2
from flask import Flask
from flask_sock import Sock
import numpy as np  # Import Sock from flask_sock for WebSocket support
from helper.Logger import Logger
import main as kpc
import base64
import time
from constants import WIDTH, HEIGHT  # Import constants
import os

from server_image_conversion import base64_to_image, is_valid_base64
from server_observer import Observer

app = Flask(__name__)
sock = Sock(app)  # Initialize Sock with the Flask app


# Create an instance of the Observer
result_observer = Observer()

# Define a notification function for the WebSocket
def notify_client_via_ws(ws):
    def send_result(notification):
        """
        Send the notification data to the WebSocket client.
        :param notification: The notification data to send.
        """
        ws.send(json.dumps(notification))

    return send_result

@sock.route('/opencv')
def ws_opencv(ws):
    logger = Logger()
    #logger.log("RAHMAN - WebSocket connection established.")
    
    # Subscribe the WebSocket notification function to the Observer
    ws_notifier = notify_client_via_ws(ws)
    result_observer.subscribe(ws_notifier)

    try:
        while True:
            try:
                # Receive the Base64-encoded message
                message = ws.receive()
                if not message:
                    break

                # Validate Base64 data
                if not is_valid_base64(message):
                    logger.log("RAHMANIA - Invalid Base64 data received.")
                    ws.send(json.dumps({"error": "Invalid Base64 data"}))
                    continue

                # Decode Base64 data
                byte_data = base64.b64decode(message)

                #Reshape into image
                try:
                    image_data = np.frombuffer(byte_data, dtype=np.uint8).reshape((HEIGHT, WIDTH, 3))
                    # logger.log(f"RAHMANIA - Image reshaped successfully: {image_data.shape}")
                except ValueError as e:
                    logger.log(f"RAHMANIA - Reshape error: {e}")
                    ws.send(json.dumps({"error": f"Reshape error: {e}"}))
                    continue

                # Save image
                output_folder = "data"
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                image_path = f"{output_folder}/{int(time.time() * 1000)}.png"
                cv2.imwrite(image_path, image_data)

                # Validate size
                expected_size = WIDTH * HEIGHT * 3
                if len(byte_data) != expected_size:
                    logger.log(f"RAHMANIA - Incorrect byte data size: {len(byte_data)} (expected {expected_size})")
                    ws.send(json.dumps({"error": f"Incorrect byte data size: {len(byte_data)}"}))
                    continue

                # Call the process_image function
                result = kpc.process_image(byte_data, WIDTH, HEIGHT)
                
                # Notify the observer with the result
                result_observer.notify(result)

            except Exception as e:
                logger.log("RAHMANIA - Error:" + str(e))
                ws.send(json.dumps({"error": f"Processing failed: {str(e)}"}))
    finally:
        # Unsubscribe the WebSocket notifier and flush pending notifications
        result_observer.unsubscribe(ws_notifier)
        result_observer.flush()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

# # Define a WebSocket route
# @sock.route('/reverse')
# def reverse(ws):
#     while True:
#         text = ws.receive()
#         ws.send(text[::-1])

# # Define a notification function for the WebSocket
# def notify_client_via_ws(ws):
#     def send_result(result):
#         """
#         Send the result to the WebSocket client.
#         :param result: The result to send.
#         """
#         ws.send(json.dumps(result))

#     return send_result

# @sock.route('/opencv')
# def ws_opencv(ws):
#     logger = Logger()
#     logger.log("RAHMAN - WebSocket connection established.")
    
#     # Subscribe the WebSocket notification function to the Observer
#     ws_notifier = notify_client_via_ws(ws)
#     result_observer.subscribe(ws_notifier)

#     try:
#         while True:
#             try:
#                 # Receive the Base64-encoded message
#                 message = ws.receive()
#                 if not message:
#                     break

#                 # Validate Base64 data
#                 if not is_valid_base64(message):
#                     logger.log("RAHMANIA - Invalid Base64 data received.")
#                     ws.send(json.dumps({"error": "Invalid Base64 data"}))
#                     continue

#                 # Decode Base64 data
#                 byte_data = base64.b64decode(message)

#                 # Validate size
#                 expected_size = WIDTH * HEIGHT * 3
#                 if len(byte_data) != expected_size:
#                     logger.log(f"RAHMANIA - Incorrect byte data size: {len(byte_data)} (expected {expected_size})")
#                     ws.send(json.dumps({"error": f"Incorrect byte data size: {len(byte_data)}"}))
#                     continue

#                 # Reshape into image
#                 try:
#                     image_data = np.frombuffer(byte_data, dtype=np.uint8).reshape((HEIGHT, WIDTH, 3))
#                 except ValueError as e:
#                     logger.log(f"RAHMANIA - Reshape error: {e}")
#                     ws.send(json.dumps({"error": f"Reshape error: {e}"}))
#                     continue

#                 # Save image
#                 # output_folder = "data"
#                 # if not os.path.exists(output_folder):
#                 #     os.makedirs(output_folder)
#                 # image_path = f"{output_folder}/{int(time.time() * 1000)}.png"
#                 # cv2.imwrite(image_path, image_data)
#                 # logger.log(f"RAHMANIA - Image saved at {image_path}")

#                 # Call the process_image function
#                 result = kpc.process_image(byte_data, WIDTH, HEIGHT)
                
#                 # Notify the observer with the result
#                 result_observer.notify(result)

#             except Exception as e:
#                 logger.log("RAHMANIA - Error:" + str(e))
#                 ws.send(json.dumps({"error": f"Processing failed: {str(e)}"}))
#     finally:
#         # Unsubscribe the WebSocket notifier when the connection closes
#         result_observer.unsubscribe(ws_notifier)


# Define a WebSocket route
# @sock.route('/opencv')
# def ws_opencv(ws):
#     logger = Logger()
#     logger.log("RAHMAN - WebSocket connection established.")
#     while True:
#         try:
#             # Receive the Base64-encoded message
#             message = ws.receive()
#             if not message:
#                 break

#             # Validate Base64 data
#             if not is_valid_base64(message):
#                 logger.log("RAHMANIA - Invalid Base64 data received.")
#                 ws.send(json.dumps({"error": "Invalid Base64 data"}))
#                 continue

#             # Decode Base64 data
#             byte_data = base64.b64decode(message)

#             # Validate size
#             expected_size = WIDTH * HEIGHT * 3
#             if len(byte_data) != expected_size:
#                 logger.log(f"RAHMANIA - Incorrect byte data size: {len(byte_data)} (expected {expected_size})")
#                 ws.send(json.dumps({"error": f"Incorrect byte data size: {len(byte_data)}"}))
#                 continue

#             # Reshape into image
#             try:
#                 image_data = np.frombuffer(byte_data, dtype=np.uint8).reshape((HEIGHT, WIDTH, 3))
#                 # logger.log(f"RAHMANIA - Image reshaped successfully: {image_data.shape}")
#             except ValueError as e:
#                 logger.log(f"RAHMANIA - Reshape error: {e}")
#                 ws.send(json.dumps({"error": f"Reshape error: {e}"}))
#                 continue

#             # Save image
#             output_folder = "data"
#             if not os.path.exists(output_folder):
#                 os.makedirs(output_folder)
#             image_path = f"{output_folder}/{int(time.time() * 1000)}.png"
#             cv2.imwrite(image_path, image_data)

#             logger.log(f"RAHMANIA - Image saved at {image_path}")

#             # Call the process_image function
#             result = kpc.process_image(byte_data, WIDTH, HEIGHT)
#             # Send the result back to the client
#             ws.send(json.dumps(result))
#             #ws.send(json.dumps({"success": True, "image_path": image_path}))

#         except Exception as e:
#             logger.log("RAHMANIA - Error:" + str(e))
#             ws.send(json.dumps({"error": f"Processing failed: {str(e)}"}))
