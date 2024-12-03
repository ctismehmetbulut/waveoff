class Observer:
    def __init__(self):
        self._observers = []  # List of subscribers
        self._last_result = None  # Cache for the last result
        self._count = 0  # Count of consecutive unchanged results

    def subscribe(self, observer):
        """
        Subscribe an observer to the notifications.
        :param observer: Function or object to be notified.
        """
        self._observers.append(observer)

    def unsubscribe(self, observer):
        """
        Unsubscribe an observer from the notifications.
        :param observer: Function or object to remove.
        """
        self._observers.remove(observer)

    def notify(self, result):
        """
        Notify all subscribers if the result has changed, with the count of unchanged results.
        :param result: The result to notify about.
        """
        if result == self._last_result:
            # Increment count for unchanged results
            self._count += 1
        else:
            # Notify observers about the new result and the count of the previous result
            if self._last_result is not None:
                for observer in self._observers:
                    observer({
                        "result": result,
                        "previous_result": self._last_result,
                        "unchanged_count": self._count
                    })
            # Update to the new result and reset count
            self._last_result = result
            self._count = 1  # Start counting the new result

    def flush(self):
        """
        Notify the final result count if the connection closes.
        """
        if self._last_result is not None:
            for observer in self._observers:
                observer({
                    "result": None,
                    "previous_result": self._last_result,
                    "unchanged_count": self._count
                })
            self._last_result = None
            self._count = 0


# class Observer:
#     def __init__(self):
#         self._observers = []  # List of subscribers
#         self._last_result = None  # Cache for the last result to avoid repetition

#     def subscribe(self, observer):
#         """
#         Subscribe an observer to the notifications.
#         :param observer: Function or object to be notified.
#         """
#         self._observers.append(observer)

#     def unsubscribe(self, observer):
#         """
#         Unsubscribe an observer from the notifications.
#         :param observer: Function or object to remove.
#         """
#         self._observers.remove(observer)

#     def notify(self, result):
#         """
#         Notify all subscribers if the result has changed.
#         :param result: The result to notify about.
#         """
#         if result != self._last_result:  # Avoid notifying the same result
#             for observer in self._observers:
#                 observer(result)  # Notify each observer
#                 print("RAHMAN - Notified observer.")
#             self._last_result = result  # Update the last result
