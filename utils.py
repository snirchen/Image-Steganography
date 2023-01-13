import numpy as np
from PIL import Image


def png_file_to_rgb_np_array_converter(png_file_path: str) -> np.array:
    """
    This function gets a full path to an image, saved as a png file,
    and returns its representation as a np array of RGB values.

    Each pixel of an image has a representation as an RGB value: (R, G, B)

    R - Red: 0-255 value
    G - Green: 0-255 value
    B - Blue: 0-255 value

    With the combination of these 3 colors, and the strength of each one (0-255), it
    is possible to create many colors.

    Image can be represented as a 2D array of pixels, while each pixel can be represented
    as a color made of RGB values. That is what this function returns, and it looks
    like this:

    [(R,G,B), (R,G,B), ...
     (R,G,B), (R,G,B), ...
       ...   ,   ...  , ...
       ...   ,   ...  , ...
       ...   ,   ...  , ...]

    :param png_file_path: The full path to the file we want to convert.
    :return: The given image as a np array of RGB values
    """
    image = Image.open(png_file_path).convert('RGB')
    rgb_np_array = np.array(image)
    return rgb_np_array


def np_array_to_png_file_converter(np_array: np.array, path_to_save_png_file: str) -> None:
    """
    This function gets a np array, converts it to an RGB image, and saves it as a png file.

    Each pixel of an image has a representation as an RGB value: (R, G, B)

    R - Red: 0-255 value
    G - Green: 0-255 value
    B - Blue: 0-255 value

    With the combination of these 3 colors, and the strength of each one (0-255), it
    is possible to create many colors.

    Image can be represented as a 2D array of pixels, while each pixel can be represented
    as a color made of RGB values. This function gets a np array that should look like this:

    [(R,G,B), (R,G,B), ...
     (R,G,B), (R,G,B), ...
       ...   ,   ...  , ...
       ...   ,   ...  , ...
       ...   ,   ...  , ...]

    and saves it as a png file in the given path.

    :param np_array: The np array we want to convert to an image.
    :param path_to_save_png_file: Path for saving the image.
    :return: None
    """
    image = Image.fromarray(np_array, 'RGB')
    image.save(path_to_save_png_file)
