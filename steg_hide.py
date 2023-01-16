import argparse

import numpy as np

import utils
from config import NUM_OF_BITS_IN_ASCII_SYMBOL


def new_path_name(image_path: str) -> str:
    # Given image has png extension
    if image_path[-4:] == '.png':
        return rf"{image_path[0:-4]}_hidden.png"

    # Given image has no png extension
    return rf"{image_path}_hidden.png"


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
                    new_name = new_path_name(image_path)
                    utils.np_array_to_png_file_converter(np.array(image_as_np_array), new_name)
                    return new_name
                bit_to_hide = bits_to_hide[0]
                bits_to_hide = bits_to_hide[1:]
                image_as_np_array[line_num][column_num][color_index] = utils.set_bit(
                    image_as_np_array[line_num][column_num][color_index], int(bit_to_hide), 0)
    raise Exception("Unexpected error occurred.")


def main() -> None:
    EXAMPLE_TEXT_PATH = r'Example\example_text.txt'
    EXAMPLE_IMAGE_PATH = r'Example\cubes.png'

    with open(EXAMPLE_TEXT_PATH, 'r') as file:
        text = file.read().replace('\n', '')

    new_path = hide(EXAMPLE_IMAGE_PATH, text)
    print(f'The text was hidden successfully in the image, and saved in {new_path}')


if __name__ == '__main__':
    main()
