import cv2 as cv
from collections import deque, Counter
import numpy as np
from mediapipe_helpers.hand_processor import HandProcessor
from model import KeyPointClassifier, PointHistoryClassifier
from utils.cvfpscalc import CvFpsCalc
from utils.pre_processing import pre_process_landmark, pre_process_point_history
from mediapipe_helpers.utils import calc_bounding_rect, calc_landmark_list


# Initialize components
hand_processor = HandProcessor()
keypoint_classifier = KeyPointClassifier()
point_history_classifier = PointHistoryClassifier()
fps_calc = CvFpsCalc(buffer_len=10)

# Load labels
keypoint_labels = keypoint_classifier.load_labels()
gesture_labels = point_history_classifier.load_labels()

# Shared data structures
point_history = deque(maxlen=16)
finger_gesture_history = deque(maxlen=16)

def process_image(input_data, width=None, height=None):
    """
    Processes an image (either from byte data or camera frame) and detects gestures.

    Parameters:
        input_data: np.ndarray (camera frame) or bytes (byte data)
        width: int (optional) - Width of image (required for byte data)
        height: int (optional) - Height of image (required for byte data)

    Returns:
        dict: Hand sign, gesture type, bounding box, and FPS.
    """
    # Determine input type
    if isinstance(input_data, bytes):
        # Case: Byte data
        if width is None or height is None:
            raise ValueError("Width and height must be provided for byte data.")
        img_array = np.frombuffer(input_data, dtype=np.uint8)
        image = img_array.reshape((height, width, 3))

        # Flip image for mirroring effect
        image = cv.flip(image, 1)
        
    elif isinstance(input_data, (np.ndarray,)):
        # Case: Camera frame
        image = input_data
    else:
        raise TypeError("Unsupported input type. Must be bytes or numpy.ndarray.")

    # Process image with Mediapipe
    results = hand_processor.process(image)

    specific_gesture_type = 'None'
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Calculate bounding box and landmarks
            brect = calc_bounding_rect(image, hand_landmarks)
            landmark_list = calc_landmark_list(image, hand_landmarks)

            # Pre-process landmarks and point history
            pre_processed_landmark_list = pre_process_landmark(landmark_list)
            pre_processed_point_history_list = pre_process_point_history(image, point_history)

            if len(landmark_list) < 21:  # Ensure valid landmarks are present
                print("RAHMANIA - Insufficient landmarks detected.")
                continue

            # Hand sign classification
            hand_sign_id = keypoint_classifier(pre_processed_landmark_list)

            print(f"RAHMANIA - Before update: point_history = {list(point_history)}") # Debugging line

            # Update point history
            if hand_sign_id == 0:  # All fingers extended
                point_history.extend([landmark_list[i] for i in [4, 8, 12, 16, 20]])
            elif hand_sign_id == 3:  # Index finger extended
                point_history.append(landmark_list[8])
            else:
                point_history.append([0, 0])  # Placeholder

            print(f"RAHMANIA - After update: point_history = {list(point_history)}") # Debugging line

            # Before calling pre_process_point_history, ensure point_history is valid
            if len(point_history) == 0:
                print("RAHMANIA - Point history is empty. Skipping processing.")
                return {
                    "hand_sign": "None",
                    "gesture_type": "None",
                    "bounding_box": None,
                    "fps": fps_calc.get(),
                }

            # Gesture classification
            finger_gesture_id = 0
            if len(pre_processed_point_history_list) == (16 * 2):
                finger_gesture_id = point_history_classifier(pre_processed_point_history_list)
            finger_gesture_history.append(finger_gesture_id)
            most_common_fg_id = Counter(finger_gesture_history).most_common()

            # Map gesture ID to gesture type
            if finger_gesture_id == 0:
                specific_gesture_type = "Stop"
            elif finger_gesture_id == 1:
                specific_gesture_type = "Normal Wave"
            elif finger_gesture_id == 2:
                specific_gesture_type = "Index Wave"

            # Return results
            return {
                "hand_sign": keypoint_labels[hand_sign_id],
                #"gesture_type": specific_gesture_type,
                #"bounding_box": brect,
                #"fps": fps_calc.get(),
            }

    # If no hands are detected
    return {
        "hand_sign": "None",
        #"gesture_type": "None",
        #"bounding_box": None,
        #"fps": fps_calc.get(),
    }


def process_camera_stream(video_source=0):
    """
    Captures video frames from the local camera and processes them using the process_image function.
    """
    cap = cv.VideoCapture(video_source)

    # Set desired resolution
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 256)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 144)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip image if required (for mirroring effect)
        frame = cv.flip(frame, 1)

        # Process the frame
        result = process_image(frame)

        # Display results on the frame
        if result['bounding_box']:
            x1, y1, x2, y2 = result['bounding_box']
            cv.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv.putText(frame, f"Gesture: {result['gesture_type']}",
                       (x1, y1 - 10), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv.putText(frame, f"Sign: {result['hand_sign']}",
                       (x1, y2 + 20), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # Display FPS
        cv.putText(frame, f"FPS: {result['fps']}", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

        # Show the frame
        cv.imshow("Gesture Detection", frame)

        # Break on 'q' key
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    process_camera_stream()