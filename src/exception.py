import os
import sys

# This function makes error messages more clear and useful
# It shows:
# - file name
# - line number
# - actual error

def error_message_detail(error, error_detail):

    # Gets full information about the error
    _, _, exc_tb = error_detail.exc_info()

    # Gets only the file name where error happened
    file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

    # Creates a custom error message
    error_message = "Error occurred in python script [{0}] line number [{1}] error message [{2}]".format(
        file_name,
        exc_tb.tb_lineno,
        str(error)
    )

    return error_message


# Creating our own custom error class
class CustomException(Exception):

    # Runs automatically when error object is created
    def __init__(self, error_message, error_detail):

        # Calls normal Exception class
        super().__init__(error_message)

        # Stores detailed error message
        self.error_message = error_message_detail(
            error_message,
            error_detail=error_detail
        )

    # Prints custom error message when we print the error
    def __str__(self):
        return self.error_message