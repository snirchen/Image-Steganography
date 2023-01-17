from datetime import datetime

import numpy as np
import argparse

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
    parser = argparse.ArgumentParser()

    parser.add_argument('--image',
                        type=str,
                        help='Path of a PNG image.',
                        required=True)
    parser.add_argument('--text',
                        type=str,
                        help='Path of a TXT file that contains the text you want to hide.',
                        required=True)

    args = parser.parse_args()
    text_path = args.text
    image_path = args.image

    print(f"\nThe hiding process started. The time is: {datetime.now()}\n")
    with open(text_path, 'r') as file:
        text = file.read().replace('\n', '')

    new_path = hide(image_path, text)
    print(f"The hiding process finished. The time is: {datetime.now()}\n")
    print(f'The text was hidden successfully in the image!\n'
          f'It was saved in {new_path}')


if __name__ == '__main__':
    main()
