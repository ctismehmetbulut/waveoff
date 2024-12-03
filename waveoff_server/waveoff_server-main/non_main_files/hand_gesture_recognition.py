import main_with_just_gesture_recognition

main_with_just_gesture_recognition.run_app()

# Modifying the original content with enumeration logic for detected gestures.
# We will insert enumeration code after gesture IDs are classified.

# Create a modified version of the file contents by adding gesture enumeration

modified_contents = []
gesture_counter = 0  # Starting counter variable for gesture enumeration

for line in main_with_just_gesture_recognition:
    # Insert gesture enumeration logic after gesture classification
    if 'hand_sign_id = keypoint_classifier(pre_processed_landmark_list)' in line:
        modified_contents.append(line)
        # Add enumeration logic after the hand sign classification
        modified_contents.append("                gesture_counter += 1\n")
        modified_contents.append("                print(f\"Gesture {gesture_counter}: Hand Sign ID {hand_sign_id}\")\n")
    elif 'finger_gesture_id = point_history_classifier(pre_processed_point_history_list)' in line:
        modified_contents.append(line)
        # Add enumeration logic after the finger gesture classification
        modified_contents.append("                    gesture_counter += 1\n")
        modified_contents.append("                    print(f\"Gesture {gesture_counter}: Finger Gesture ID {finger_gesture_id}\")\n")
    else:
        # Add lines without modification
        modified_contents.append(line)

# Save the modified content to a new file to preserve the original
modified_file_path = '/mnt/data/main_modified.py'
with open(modified_file_path, 'w') as file:
    file.writelines(modified_contents)

modified_file_path
