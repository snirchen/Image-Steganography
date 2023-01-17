import copy
from datetime import datetime

import numpy as np

import config
import utils
from config import SPACE, EMPTY, MAX_HIDE_CHANNELS, VALID_UPPERCASE_LETTERS, LEFT_PUNCTUATIONS, RIGHT_PUNCTUATIONS


class Combination(object):
    def __init__(self, start_index: int, text: str):
        self.start_index = start_index
        self.text = text

    def clear(self):
        self.start_index = -1
        self.text = EMPTY


def get_valid_words_combinations_of_channel(channel: [str]) -> [[Combination]]:
    possible_letter_combinations = []
    current_combination = Combination(start_index=-1, text=EMPTY)

    for index, char in enumerate(channel):
        if char in config.VALID_TEXT_SYMBOLS_LETTERS:
            if char == SPACE:
                if not current_combination.text == EMPTY:
                    possible_letter_combinations.append(copy.deepcopy(current_combination))
                    current_combination.clear()
                possible_letter_combinations.append(Combination(index, SPACE))
            else:
                current_combination.text += char
                if current_combination.start_index == -1:
                    current_combination.start_index = index
        else:
            if not current_combination.text == EMPTY:
                possible_letter_combinations.append(copy.deepcopy(current_combination))
                current_combination.clear()

    if not current_combination.text == EMPTY:
        possible_letter_combinations.append(current_combination)

    return possible_letter_combinations


def remove_non_valid_one_letter_words(combinations: [Combination]) -> [Combination]:
    filtered_combinations = []
    for combination in combinations:
        if not len(combination.text) == 1:
            filtered_combinations.append(combination)
            continue
        elif combination.text.lower() in ['a', 'i', ' ']:
            filtered_combinations.append(combination)
    return filtered_combinations


def probably_english_word(combination: Combination) -> Combination or None:
    """
    This function is called when removing non-English words from the combinations.
    Notice - our MOST_COMMON_ENGLISH_WORDS list is lowercase.
    :param combination: Combination with text which is not '' and not  ' '.
    :return: What is most likely to be the word in english of the given text, or None if nothing was found.
    """
    text = combination.text
    text_lower = text.lower()
    start_index = combination.start_index

    if text_lower in config.MOST_COMMON_ENGLISH_WORDS_LOWERCASE:
        return combination

    for word in config.MOST_COMMON_ENGLISH_WORDS_LOWERCASE:
        if word == text_lower:
            return combination
        if word in text_lower:
            if len(text_lower) - len(word) <= 1:
                if text_lower[1:] == word:
                    return Combination(start_index + 1, text[1:])
                return Combination(start_index, text[:-1])
    return None


def remove_non_english_words(combinations: [Combination]) -> [Combination]:
    filtered_combinations = []

    for combination in combinations:
        if combination.text == SPACE:
            filtered_combinations.append(combination)
        english_word_combination = probably_english_word(combination)
        if english_word_combination:
            filtered_combinations.append(english_word_combination)

    return filtered_combinations


def remove_wrong_capital_letters_words(combinations: [Combination]) -> [Combination]:
    filtered_combinations = []
    for combination in combinations:
        if len(combination.text) == 1:
            filtered_combinations.append(combination)
            continue

        combination_is_valid = True
        for letter in combination.text[1:]:
            if letter in VALID_UPPERCASE_LETTERS:
                combination_is_valid = False
                break
        if combination_is_valid:
            filtered_combinations.append(combination)

    return filtered_combinations


def add_punctuations_if_exists(combinations: [Combination], symbols_of_channel: [str]) -> [Combination]:
    combinations_with_punctuations = []
    for combination in combinations:
        previous_index = combination.start_index - 1
        next_index = combination.start_index + len(combination.text)

        # Handling (
        if previous_index >= 0:
            if symbols_of_channel[previous_index] == LEFT_PUNCTUATIONS:
                combination.start_index = previous_index
                combination.text = symbols_of_channel[previous_index] + combination.text

        # Handling )!?.,
        if next_index < len(symbols_of_channel):
            if symbols_of_channel[next_index] in RIGHT_PUNCTUATIONS:
                combination.text = combination.text + symbols_of_channel[next_index]

        # Handling ...
        if next_index + 2 < len(symbols_of_channel):
            next_three_symbols = symbols_of_channel[next_index] + \
                                 symbols_of_channel[next_index + 1] + \
                                 symbols_of_channel[next_index + 2]
            if next_three_symbols == '...':
                # Because we already added one dot when handled )!?., we ignore it by combination.text[:-1]
                combination.text = combination.text[:-1] + next_three_symbols

        combinations_with_punctuations.append(combination)

    return combinations_with_punctuations


def longest_strike_from_combination(i: int, all_combinations: [Combination], should_be_space=False) -> [Combination]:
    current_combination = all_combinations[i]

    if all_combinations[i].text == SPACE and not should_be_space:
        return []
    if all_combinations[i].text != SPACE and should_be_space:
        return []

    # Because we combined 3 hidden channels (of 3 LSBs) we may have up to 3 options to continue the strike
    possible_options_to_continue = []
    next_start_index_should_be = all_combinations[i].start_index + len(all_combinations[i].text)

    for j in range(i + 1, len(all_combinations)):
        if all_combinations[j].start_index < next_start_index_should_be:
            continue
        if all_combinations[j].start_index > next_start_index_should_be:
            break
        possible_options_to_continue.append(j)

    possible_strikes = [longest_strike_from_combination(j, all_combinations, not should_be_space) for j in
                        possible_options_to_continue]

    return [current_combination] if possible_strikes == [] else [current_combination] + max(possible_strikes, key=len)


def longest_words_strike(all_combinations: [Combination]) -> str:
    max_strike_len = 0
    longest_strike = []

    for i in range(len(all_combinations)):
        current_longest_strike = longest_strike_from_combination(i, all_combinations)
        current_strike_len = len(current_longest_strike)
        if current_strike_len > max_strike_len:
            max_strike_len = current_strike_len
            longest_strike = copy.deepcopy(current_longest_strike)

    return ''.join([combination.text for combination in longest_strike])


def guess_hidden_text(symbols_of_channels: [[str]]) -> str:
    valid_words_combinations_channels = [[]] * len(symbols_of_channels)

    for i in range(len(valid_words_combinations_channels)):
        valid_words_combinations_channels[i] = get_valid_words_combinations_of_channel(symbols_of_channels[i])
        valid_words_combinations_channels[i] = remove_non_valid_one_letter_words(valid_words_combinations_channels[i])
        valid_words_combinations_channels[i] = remove_non_english_words(valid_words_combinations_channels[i])
        valid_words_combinations_channels[i] = remove_wrong_capital_letters_words(valid_words_combinations_channels[i])
        valid_words_combinations_channels[i] = \
            add_punctuations_if_exists(valid_words_combinations_channels[i], symbols_of_channels[i])

    all_combinations = []
    for channel_combination in valid_words_combinations_channels:
        for combination in channel_combination:
            all_combinations.append(combination)

    all_combinations.sort(key=lambda c: c.start_index)

    hidden_text = longest_words_strike(all_combinations)
    return hidden_text


def get_hidden_ascii_symbols_of_channels_from_image_as_np_array(image_as_np_array: np.ndarray, start_index) -> [[int]]:
    image_as_np_array = image_as_np_array.flatten()
    image_as_np_array = image_as_np_array[start_index:]

    # To make the array divisible by NUM_OF_BITS_IN_ASCII_SYMBOL
    num_of_colors_to_ignore_at_the_end = image_as_np_array.size % config.NUM_OF_BITS_IN_ASCII_SYMBOL
    if num_of_colors_to_ignore_at_the_end:
        image_as_np_array = image_as_np_array[:-num_of_colors_to_ignore_at_the_end]

    hidden_ascii_symbols_of_channels = [copy.deepcopy(image_as_np_array) for _ in range(MAX_HIDE_CHANNELS)]

    for i in range(MAX_HIDE_CHANNELS):
        # Get the LSB-i of each color (byte) in the image
        mask = utils.set_bit_1(0, i)
        hidden_ascii_symbols_of_channels[i] = (hidden_ascii_symbols_of_channels[i] & mask)
        # Combine each 8 bits to a uint-8
        hidden_ascii_symbols_of_channels[i] = np.packbits(hidden_ascii_symbols_of_channels[i])
        # Convert each uint-8 to its ascii representation
        hidden_ascii_symbols_of_channels[i] = list(map(chr, hidden_ascii_symbols_of_channels[i]))

    return hidden_ascii_symbols_of_channels


def decode(image_as_np_array: np.ndarray) -> str:
    max_words = 0
    best_guess = ''
    for i in range(8):
        symbols_of_channels = get_hidden_ascii_symbols_of_channels_from_image_as_np_array(image_as_np_array, i)
        guess = guess_hidden_text(symbols_of_channels)
        if len(guess.split(SPACE)) > max_words:
            max_words = len(guess.split(SPACE))
            best_guess = guess
    return best_guess


def main() -> None:
    print(datetime.now())
    PATH = r"hidden.png"
    image_as_np_array = utils.png_file_to_rgb_np_array_converter(PATH)
    hidden_text = decode(image_as_np_array)
    with open(f'{config.ID}.txt', 'w') as f:
        f.write(hidden_text)
    print(datetime.now())


if __name__ == '__main__':
    main()
