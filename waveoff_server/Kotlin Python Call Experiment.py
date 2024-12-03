#BEFORE MODULARIZATION

import csv
import numpy as np
import cv2 as cv
from collections import deque, Counter
from utils import CvFpsCalc
from model import KeyPointClassifier, PointHistoryClassifier
import mediapipe as mp
import itertools

# Initialize Mediapipe and models only once
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5,
)

keypoint_classifier = KeyPointClassifier()
point_history_classifier = PointHistoryClassifier()

# Load labels for classifiers
with open('model/keypoint_classifier/keypoint_classifier_label.csv', encoding='utf-8-sig') as f:
    keypoint_classifier_labels = [row[0] for row in csv.reader(f)]
with open('model/point_history_classifier/point_history_classifier_label.csv', encoding='utf-8-sig') as f:
    point_history_classifier_labels = [row[0] for row in csv.reader(f)]

# Other needed data structures
point_history = deque(maxlen=16)
finger_gesture_history = deque(maxlen=16)
cvFpsCalc = CvFpsCalc(buffer_len=10)

def process_image(image):
    # Get dimensions directly from the image
    # height, width, _ = image.shape

    # Process the image with Mediapipe for hand landmarks
    image_rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    specific_gesture_type = 'None'
    if results.multi_hand_landmarks is not None:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            # Bounding box calculation
            brect = calc_bounding_rect(image, hand_landmarks)
            
            # Landmark calculation and processing
            landmark_list = calc_landmark_list(image, hand_landmarks)
            pre_processed_landmark_list = pre_process_landmark(landmark_list)
            pre_processed_point_history_list = pre_process_point_history(image, point_history)

            # Hand sign classification
            hand_sign_id = keypoint_classifier(pre_processed_landmark_list)

            # Append landmarks for the point history
            if hand_sign_id == 0:  # All fingers
                point_history.extend([landmark_list[i] for i in [4, 8, 12, 16, 20]])
            elif hand_sign_id == 3:  # Index finger
                point_history.append(landmark_list[8])
            else:
                point_history.append([0, 0])

            # Finger gesture classification
            finger_gesture_id = 0
            if len(pre_processed_point_history_list) == (16 * 2):
                finger_gesture_id = point_history_classifier(pre_processed_point_history_list)
            finger_gesture_history.append(finger_gesture_id)
            most_common_fg_id = Counter(finger_gesture_history).most_common()

            # Determine specific gesture type based on gesture ID
            if finger_gesture_id == 0:
                specific_gesture_type = "Stop"
            elif finger_gesture_id == 1:
                specific_gesture_type = "Normal Wave"
            elif finger_gesture_id == 2:
                specific_gesture_type = "Index Wave"

            # Example: Returning hand gesture type along with hand sign ID
            return {
                "hand_sign": keypoint_classifier_labels[hand_sign_id],
                "gesture_type": specific_gesture_type,
                "bounding_box": brect,
                "fps": cvFpsCalc.get()
            }

    # If no hand detected, return None or empty results
    return {
        "hand_sign": "None",
        "gesture_type": "None",
        "bounding_box": None,
        "fps": cvFpsCalc.get()
    }

def calc_bounding_rect(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]
    landmark_array = np.array([[min(int(p.x * image_width), image_width - 1),
                                min(int(p.y * image_height), image_height - 1)]
                               for p in landmarks.landmark], dtype=int)
    x, y, w, h = cv.boundingRect(landmark_array)
    return [x, y, x + w, y + h]

def calc_landmark_list(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]
    return [[min(int(p.x * image_width), image_width - 1),
             min(int(p.y * image_height), image_height - 1)]
            for p in landmarks.landmark]

def pre_process_landmark(landmark_list):
    base_x, base_y = landmark_list[0]
    temp_landmark_list = [[x - base_x, y - base_y] for x, y in landmark_list]
    flattened = list(itertools.chain.from_iterable(temp_landmark_list))
    max_value = max(map(abs, flattened), default=1)
    return [v / max_value for v in flattened]

def pre_process_point_history(image, point_history):
    if not point_history:  # Check if point_history is empty
        return []  # Return an empty list if there is no data

    image_width, image_height = image.shape[1], image.shape[0]

    # Convert to relative coordinates
    base_x, base_y = point_history[0]
    normalized_history = [(float(x - base_x) / image_width, float(y - base_y) / image_height)
                          for x, y in point_history]
    return list(itertools.chain.from_iterable(normalized_history))

def test_gesture_detection(video_source=0):
    cap = cv.VideoCapture(video_source)  # Use 0 for webcam or a file path for video

    # Set desired resolution
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 256)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 144)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip image if required (for mirroring effect)
        frame = cv.flip(frame, 1)

        # Process the frame with the gesture detection function
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
        cv.imshow("Gesture Detection Test", frame)

        # Break on 'q' key
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

# Run the test
test_gesture_detection()