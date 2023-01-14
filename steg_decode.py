import copy

import numpy as np

import config
import utils
from config import SPACE, EMPTY, MAX_HIDE_CHANNELS, VALID_UPPERCASE_LETTERS, VALID_PUNCTUATIONS

PATH = "hidden.png"


class Combination(object):
    def __init__(self, start_index: int, value: str):
        self.start_index = start_index
        self.value = value

    def clear(self):
        self.start_index = -1
        self.value = EMPTY


def get_valid_words_combinations_of_channel(channel: [str]) -> [[Combination]]:
    possible_letter_combinations = []
    current_combination = Combination(start_index=-1, value=EMPTY)

    for index, char in enumerate(channel):
        if char in config.VALID_TEXT_SYMBOLS_LETTERS:
            if char == SPACE:
                if not current_combination.value == EMPTY:
                    possible_letter_combinations.append(copy.deepcopy(current_combination))
                    current_combination.clear()
                possible_letter_combinations.append(Combination(index, SPACE))
            else:
                current_combination.value += char
                if current_combination.start_index == -1:
                    current_combination.start_index = index
        else:
            if not current_combination.value == EMPTY:
                possible_letter_combinations.append(copy.deepcopy(current_combination))
                current_combination.clear()

    if not current_combination.value == EMPTY:
        possible_letter_combinations.append(current_combination)

    return possible_letter_combinations


def remove_non_valid_one_letter_words(combinations: [Combination]) -> [Combination]:
    filtered_combinations = []
    for combination in combinations:
        if not len(combination.value) == 1:
            filtered_combinations.append(combination)
            continue
        elif combination.value.lower() in ['a', 'i', ' ']:
            filtered_combinations.append(combination)
    return filtered_combinations


def remove_wrong_capital_letters_words(combinations: [Combination]) -> [Combination]:
    filtered_combinations = []
    for combination in combinations:
        if len(combination.value) == 1:
            continue
        combination_is_valid = True

        for letter in combination.value[1:]:
            if letter in VALID_UPPERCASE_LETTERS:
                combination_is_valid = False
                break
        if combination_is_valid:
            filtered_combinations.append(combination)
    return filtered_combinations


def y(word):
    for w in config.MOST_COMMON_ENGLISH_WORDS:
        if w.lower() in word.lower():
            if len(word) - len(w) <= 1 and len(w):
                return True
    return False


def remove_non_english_words(combinations: [Combination]) -> [Combination]:
    filtered_combinations = []
    common_english_words = config.MOST_COMMON_ENGLISH_WORDS

    for combination in combinations:
        # if combination.value.lower() in common_english_words or combination.value == SPACE:
        if y(combination.value) or combination.value == SPACE:
            filtered_combinations.append(combination)
    return filtered_combinations


def add_punctuations_if_exists(combinations: [Combination],
                               symbols_of_channel: [str]) -> [Combination]:
    combinations_with_punctuations = []
    for combination in combinations:
        previous_index = combination.start_index - 1
        next_index = combination.start_index + len(combination.value)
        if previous_index >= 0:
            if symbols_of_channel[previous_index] == '(':
                combination.start_index = previous_index
                combination.value = symbols_of_channel[previous_index] + combination.value
        if next_index < len(symbols_of_channel):
            if symbols_of_channel[next_index] in VALID_PUNCTUATIONS.replace('(', ''):
                combination.value = combination.value + symbols_of_channel[next_index]
        combinations_with_punctuations.append(combination)
    return combinations_with_punctuations


def longest_words_strike(all_combinations: [Combination]) -> str:
    current_strike_len = 0
    max_strike_len = 0
    current_longest_strike = []
    longest_strike = []
    for i, combination in enumerate(all_combinations):
        next_combination = i + 1
        if next_combination < len(all_combinations):
            next_combination_value = all_combinations[next_combination].value
            next_combination_start_index = all_combinations[next_combination].start_index
            if (combination.start_index + len(combination.value) == next_combination_start_index) \
                    and not (combination.value == next_combination_value == SPACE):
                current_strike_len += 1
                current_longest_strike.append(combination)
            else:
                current_longest_strike.append(combination)
                if current_strike_len > max_strike_len:
                    max_strike_len = current_strike_len
                    longest_strike = copy.deepcopy(current_longest_strike)
                    current_longest_strike = []
                current_strike_len = 0
    return ''.join([combination.value for combination in longest_strike])


def guess_hidden_text(symbols_of_channels: [[str]]) -> str:
    valid_words_combinations_channels = [[]] * len(symbols_of_channels)

    for i in range(len(valid_words_combinations_channels)):
        valid_words_combinations_channels[i] = get_valid_words_combinations_of_channel(symbols_of_channels[i])
        valid_words_combinations_channels[i] = remove_non_valid_one_letter_words(valid_words_combinations_channels[i])
        # valid_words_combinations_channels[i] = remove_wrong_capital_letters_words(valid_words_combinations_channels[i])
        valid_words_combinations_channels[i] = remove_non_english_words(valid_words_combinations_channels[i])
        valid_words_combinations_channels[i] = \
            add_punctuations_if_exists(valid_words_combinations_channels[i], symbols_of_channels[i])

    all_combinations = []
    for channel_combination in valid_words_combinations_channels:
        for combination in channel_combination:
            all_combinations.append(combination)

    all_combinations.sort(key=lambda c: c.start_index)

    hidden_text = longest_words_strike(all_combinations)
    print(hidden_text)
    return hidden_text


def get_hidden_ascii_symbols_of_channels_from_image_as_np_array(image_as_np_array: np.ndarray) -> [[int]]:
    hidden_ascii_symbols_of_channels = [[] for _ in range(MAX_HIDE_CHANNELS)]
    current_ascii_values = [0 for _ in range(MAX_HIDE_CHANNELS)]
    bits_counter = 0
    for line_num, line in enumerate(image_as_np_array):
        for column_num, column in enumerate(line):
            # looping over all RGB values in image
            rgb_value = image_as_np_array[line_num][column_num]
            for color_value in rgb_value:
                for channel_index in range(MAX_HIDE_CHANNELS):
                    current_ascii_values[channel_index] = \
                        utils.set_bit(current_ascii_values[channel_index],
                                      utils.get_bit(color_value, channel_index),
                                      (config.NUM_OF_BITS_IN_ASCII_SYMBOL - 1) - bits_counter)
                bits_counter += 1
                if bits_counter == config.NUM_OF_BITS_IN_ASCII_SYMBOL:
                    bits_counter = 0
                    for channel_index in range(MAX_HIDE_CHANNELS):
                        hidden_ascii_symbols_of_channels[channel_index].append(chr(current_ascii_values[channel_index]))
                        current_ascii_values[channel_index] = 0
    return hidden_ascii_symbols_of_channels


def decode(image_as_np_array: np.ndarray) -> str:
    symbols_of_channels = get_hidden_ascii_symbols_of_channels_from_image_as_np_array(image_as_np_array)
    best_guess = guess_hidden_text(symbols_of_channels)
    return best_guess


def main() -> None:
    image_as_np_array = utils.png_file_to_rgb_np_array_converter(PATH)
    print(decode(image_as_np_array))


if __name__ == '__main__':
    main()
