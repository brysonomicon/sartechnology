from PIL import ImageTk


class DisplayManager:
    @staticmethod
    def pil_to_tkinter(pil_image):
        """
        Convert a PIL image to a tkinter image.

        Args:
            pil_image (PIL Image): The PIL image to convert.

        Returns:
            Tkinter Image: The converted tkinter image.
        """
        return ImageTk.PhotoImage(pil_image)
