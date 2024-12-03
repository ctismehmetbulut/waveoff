import itertools


def pre_process_landmark(landmark_list):
    base_x, base_y = landmark_list[0]
    temp_landmark_list = [[x - base_x, y - base_y] for x, y in landmark_list]
    flattened = list(itertools.chain.from_iterable(temp_landmark_list))
    max_value = max(map(abs, flattened), default=1)
    return [v / max_value for v in flattened]


def pre_process_point_history(image, point_history):
    if not point_history or len(point_history) == 0:
        print("RAHMANIA - Point history is empty.")
        return []

    image_width, image_height = image.shape[1], image.shape[0]
    base_x, base_y = point_history[0]
    normalized_history = [(float(x - base_x) / image_width, float(y - base_y) / image_height)
                          for x, y in point_history]
    return list(itertools.chain.from_iterable(normalized_history))
