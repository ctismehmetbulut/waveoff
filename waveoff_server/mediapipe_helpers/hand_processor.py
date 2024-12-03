import mediapipe as mp
import cv2 as cv

mp_hands = mp.solutions.hands


class HandProcessor:
    def __init__(self):
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
        )

    def process(self, image):
        """
        Processes the image with Mediapipe to extract hand landmarks.

        Args:
            image (np.ndarray): Input image.

        Returns:
            mediapipe.python.solutions.hands.Hands.process: Mediapipe result object.
        """
        image_rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        return self.hands.process(image_rgb)