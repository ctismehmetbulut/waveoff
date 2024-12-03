class Logger:
    def __init__(self, log_file="terminal_output.log"):
        """
        Initializes the logger with the specified log file.
        :param log_file: Path to the log file (default is 'terminal_output.log')
        """
        self.log_file = log_file

    def log(self, message):
        """
        Logs a message to the terminal and appends it to the log file.
        :param message: The message to log
        """
        # Append message to the log file
        with open(self.log_file, 'a') as file:
            file.write(message + '\n')
        # Print the message to the terminal
        print(message)

# Example usage:
logger = Logger()

logger.log("This is the first log message.")
logger.log("Another message to log.")
