from enum import Enum

import numpy as np
from PIL import Image


def png_file_to_rgb_np_array_converter(png_file_path: str) -> np.ndarray:
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
    with Image.open(png_file_path) as image:
        np_array = np.array(image.convert(mode='RGB'))
    return np_array


def np_array_to_png_file_converter(np_array: np.ndarray, path_to_save_png_file: str) -> None:
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
    Image.fromarray(np_array, mode='RGB').save(path_to_save_png_file)


def set_bit(value: int, bit_to_set: int, bit_index: int) -> int:
    if bit_to_set:
        return set_bit_1(value, bit_index)
    return set_bit_0(value, bit_index)


def set_bit_1(value: int, bit_index: int) -> int:
    return value | (1 << bit_index)


def set_bit_0(value: int, bit_index: int) -> int:
    return value & ~(1 << bit_index)


class Stage(Enum):
    HIDE = 1
    DECODE = 2


def get_output_path(image_path: str, stage: Stage) -> str:
    extension = {Stage.HIDE: "_hidden.png",
                 Stage.DECODE: "_decoded.txt"}

    if image_path[-4:] == '.png':
        image_path = image_path[0:-4]

    return f"{image_path}{extension[stage]}"
