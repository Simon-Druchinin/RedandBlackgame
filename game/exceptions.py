class NotCorrectColorIndex(Exception):
    def __init__(self, text):
        self.txt = text

class UserValidationError(Exception):
    def __init__(self, text):
        self.txt = text