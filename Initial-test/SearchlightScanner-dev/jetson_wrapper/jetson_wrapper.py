from jetson_wrapper.jetson_net import JetsonNet


"""
A wrapper module to simulate jetson_inference and jetson_utils functionalities.
"""


def cudaToNumpy(image):
    """
    Simulate conversion from CUDA image to NumPy array.
    """
    return image


def cudaFromNumpy(image):
    """
    Simulate conversion from NumPy array to CUDA image.
    """
    return image


def detectNet(model=None,
              labels=None,
              colors=None,
              input_blob=None,
              output_cvg=None,
              output_bbox=None,
              threshold=None):
    return JetsonNet(model, labels, colors, input_blob, output_cvg, output_bbox, threshold)

