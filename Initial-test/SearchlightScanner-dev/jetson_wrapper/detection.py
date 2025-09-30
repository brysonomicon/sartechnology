class Detection:
    """
    A class to simulate jetson_inference.detectNet.Detection functionalities.
    """
    def __init__(self, class_id, confidence, left, top, right, bottom):
        self.ClassID = class_id
        self.Confidence = confidence
        self.Left = left
        self.Top = top
        self.Right = right
        self.Bottom = bottom
