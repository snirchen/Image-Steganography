import argparse
import copy
from datetime import datetime

import numpy as np

import config
import utils
from config import SPACE, EMPTY, MAX_HIDE_CHANNELS, VALID_UPPERCASE_LETTERS, LEFT_PUNCTUATIONS, RIGHT_PUNCTUATIONS


class Text(object):

    def __init__(self, start_index: int, text: str) -> None:
        """
        This class represents a text (sequence of symbols) that appears in the decoded image.
        :param start_index: The text start index of the ascii symbols that were hidden in LSB channel of the image.
        :param text: Sequence of symbols
        """
        self.start_index = start_index
        self.text = text

    def clear(self) -> None:
        self.start_index = -1
        self.text = EMPTY


def get_valid_symbol_combinations_of_channel(channel: [str]) -> [[Text]]:
    """
    :param channel: List of ascii symbols that were hidden in LSB channel of the image.
    :return: List of all the valid texts was found.
    """
    possible_letter_combinations = []
    current_combination = Text(start_index=-1, text=EMPTY)

    for index, char in enumerate(channel):
        if char in config.VALID_TEXT_SYMBOLS_LETTERS:
            if char == SPACE:
                if not current_combination.text == EMPTY:
                    possible_letter_combinations.append(copy.deepcopy(current_combination))
                    current_combination.clear()
                possible_letter_combinations.append(Text(index, SPACE))
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


def remove_non_valid_one_letter_words(words: [Text]) -> [Text]:
    """
    This function filter out all non-valid one-letter words from the given texts list.
    In English, there are only 2 one-letter words: "I" and "a".
    Each text that isn't one of those, or a space will be filtered out.
    """
    filtered_words = []
    for word in words:
        if not len(word.text) == 1:
            filtered_words.append(word)
            continue
        elif word.text.lower() in ['a', 'i', ' ']:
            filtered_words.append(word)
    return filtered_words


def probably_english_word(word: Text) -> Text or None:
    """
    Notice - our MOST_COMMON_ENGLISH_WORDS list is lowercase.
    :param word: Combination of readable symbols with text which is not '' and not  ' '.
    :return: What is most likely to be the word in english of the given text, or None if nothing was found.
    """
    text = word.text
    text_lower = text.lower()
    start_index = word.start_index

    if text_lower in config.MOST_COMMON_ENGLISH_WORDS_LOWERCASE:
        return word

    for word in config.MOST_COMMON_ENGLISH_WORDS_LOWERCASE:
        if word == text_lower:
            return word
        if word in text_lower:
            if len(text_lower) - len(word) <= 1:
                if text_lower[1:] == word:
                    return Text(start_index + 1, text[1:])
                return Text(start_index, text[:-1])
    return None


def remove_non_english_words(words: [Text]) -> [Text]:
    """
    This function filters out from the given list all the words that are not
    common words in English according to the dictionary in the config.py file.
    """
    filtered_words = []

    for word in words:
        if word.text == SPACE:
            filtered_words.append(word)

        english_word = probably_english_word(word)

        if english_word:
            # Capital letters can be only at the start of a word
            word_is_valid = True
            for letter in english_word.text[1:]:
                if letter in VALID_UPPERCASE_LETTERS:
                    word_is_valid = False
                    break
            if word_is_valid:
                filtered_words.append(english_word)

    return filtered_words


def add_punctuations_if_exists(words: [Text], symbols_of_channel: [str]) -> [Text]:
    """
    This function gets a list of all legal words in English that were hidden in an LSB channel.
    It also gets the list of symbols were hidden in this LSB channel.

    Based on these two, it adds to each word punctuations that were hidden in the channel,
    punctuations that are placed just before or after the word.
    """
    words_with_punctuations = []
    for word in words:
        previous_index = word.start_index - 1
        next_index = word.start_index + len(word.text)

        # Handling (
        if previous_index >= 0:
            if symbols_of_channel[previous_index] == LEFT_PUNCTUATIONS:
                word.start_index = previous_index
                word.text = symbols_of_channel[previous_index] + word.text

        # Handling )!?.,
        if next_index < len(symbols_of_channel):
            if symbols_of_channel[next_index] in RIGHT_PUNCTUATIONS:
                word.text = word.text + symbols_of_channel[next_index]

        # Handling ...
        if next_index + 2 < len(symbols_of_channel):
            next_three_symbols = symbols_of_channel[next_index] + \
                                 symbols_of_channel[next_index + 1] + \
                                 symbols_of_channel[next_index + 2]
            if next_three_symbols == '...':
                # Because we already added one dot when handled )!?., we ignore it by word.text[:-1]
                word.text = word.text[:-1] + next_three_symbols

        words_with_punctuations.append(word)

    return words_with_punctuations


# noinspection PyTypeChecker
def longest_sentence_from_word(i: int, all_words: [Text], should_be_space=False) -> [Text]:
    """
    This recursive function, returns the longest strike of words and spaces starting from a specific word.

    It looks at the start_index of the words, and based on the size of the word,
    calculates the index where the next word should be.

    Also, a check is made that after every English word there is a space,
    and after every space there is an English word (so that we get a proper sentence)
    """
    current_word = all_words[i]

    if all_words[i].text == SPACE and not should_be_space:
        return []
    if all_words[i].text != SPACE and should_be_space:
        return []

    # Because we combined 3 hidden channels (of 3 LSBs) we may have up to 3 options to continue the strike
    possible_options_to_continue = []
    next_start_index_should_be = all_words[i].start_index + len(all_words[i].text)

    for j in range(i + 1, len(all_words)):
        if all_words[j].start_index < next_start_index_should_be:
            continue
        if all_words[j].start_index > next_start_index_should_be:
            break
        possible_options_to_continue.append(j)

    possible_strikes = [longest_sentence_from_word(j, all_words, not should_be_space) for j in
                        possible_options_to_continue]

    return [current_word] if possible_strikes == [] else [current_word] + max(possible_strikes, key=len)


def longest_sentence(all_words: [Text]) -> str:
    """
    This function calculate and returns the longest sentence in English that
    was hidden in the image.
    """
    max_strike_len = 0
    longest_strike = []

    for i in range(len(all_words)):
        current_longest_strike = longest_sentence_from_word(i, all_words)
        current_strike_len = len(current_longest_strike)
        if current_strike_len > max_strike_len:
            max_strike_len = current_strike_len
            longest_strike = copy.deepcopy(current_longest_strike)

    return ''.join([word.text for word in longest_strike])


def guess_hidden_text(symbols_of_channels: [[str]]) -> str:
    """
    This function calculates and returns the longest sentence that was hidden in all relevant LSB channels.
    """
    valid_text_channels = [[]] * len(symbols_of_channels)

    for i in range(len(valid_text_channels)):
        valid_text_channels[i] = get_valid_symbol_combinations_of_channel(symbols_of_channels[i])
        valid_text_channels[i] = remove_non_valid_one_letter_words(valid_text_channels[i])
        valid_text_channels[i] = remove_non_english_words(valid_text_channels[i])
        valid_text_channels[i] = add_punctuations_if_exists(valid_text_channels[i], symbols_of_channels[i])

    all_texts = [text for valid_text_channel in valid_text_channels for text in valid_text_channel]
    all_texts.sort(key=lambda t: t.start_index)

    hidden_text = longest_sentence(all_texts)
    return hidden_text


def get_hidden_ascii_symbols_of_channels_from_image_as_np_array(image_as_np_array: np.ndarray, start_index) -> [[str]]:
    """
    This function creates and returns a list of all hidden ascii symbols were hidden in the image,
    in all relevant LSB channels.
    """
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
        # Convert each uint-8 to its ascii representation (string)
        hidden_ascii_symbols_of_channels[i] = list(map(chr, hidden_ascii_symbols_of_channels[i]))

    return hidden_ascii_symbols_of_channels


def decode(image_as_np_array: np.ndarray) -> str:
    """
    This is the main logic function of decoding an image with hidden text in it.
    It tries to find the best guess as if the text was hidden start from each byte in the image.
    """
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
    """
    The main function
    It gets arguments from the user while running the program and call the main logic.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--image',
                        type=str,
                        help='Path of a PNG image with hidden text.',
                        required=True)

    args = parser.parse_args()
    image_path = args.image

    print(f'\nThe decoding process started. The time is: {datetime.now()}\n')
    image_as_np_array = utils.png_file_to_rgb_np_array_converter(image_path)
    hidden_text = decode(image_as_np_array)

    decoded_image_path = utils.get_output_path(image_path, utils.Stage.DECODE)
    with open(decoded_image_path, 'w') as f:
        f.write(hidden_text)
    print(f'The text was found successfully! The time is {datetime.now()}\n'
          f'\nThe text is: {hidden_text}\n'
          f'And it was saved in {decoded_image_path}')


if __name__ == '__main__':
    main()
