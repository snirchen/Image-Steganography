import numpy as np

import steg_decode
import utils
from config import NUM_OF_BITS_IN_ASCII_SYMBOL

EXAMPLE_IMAGE = [[(27, 64, 164), (248, 244, 194), (174, 246, 250), (149, 95, 232)],
                 [(188, 156, 169), (71, 167, 127), (132, 173, 97), (113, 69, 206)],
                 [(255, 29, 213), (53, 153, 220), (246, 225, 229), (142, 82, 175)]]

# EXAMPLE_TEXT = 'Hey! How are you? (I am fine, Thanks)'
EXAMPLE_TEXT = 'IIIIIIIIIIIIIIIIIIIII   IIIIIIIIIIIIIIIIIIIII   IIIIIIIIIIIIIIIIIIIII'

PATH = "test.png"


def hide(image_path: str, text_to_hide: str) -> str:
    image_as_np_array = utils.png_file_to_rgb_np_array_converter(image_path)
    if image_as_np_array.size < len(text_to_hide) * 8:
        raise ValueError("The given text is too long for the given image.\n"
                         "Try a shorter text, or a bigger image.")
    ascii_values_of_chars = [ord(char) for char in text_to_hide]
    bits_to_hide = ''.join([f'{val:0{NUM_OF_BITS_IN_ASCII_SYMBOL}b}' for val in ascii_values_of_chars])
    for line_num, line in enumerate(image_as_np_array):
        for column_num, column in enumerate(line):
            # looping over all RGB values in image
            rgb_value = image_as_np_array[line_num][column_num]
            for color_index, color_value in enumerate(rgb_value):
                if bits_to_hide == '':
                    utils.np_array_to_png_file_converter(np.array(image_as_np_array), "test_hidden.png")
                    steg_decode.decode(image_as_np_array)
                    return r"C:\\BlaBla"
                bit_to_hide = bits_to_hide[0]
                bits_to_hide = bits_to_hide[1:]
                image_as_np_array[line_num][column_num][color_index] = utils.set_bit(
                    image_as_np_array[line_num][column_num][color_index], int(bit_to_hide), 0)

    return PATH


def main() -> None:
    hide(PATH, EXAMPLE_TEXT)


if __name__ == '__main__':
    main()
