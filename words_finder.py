import logging
import unicodedata

INVALID_CHARS = " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~\n\r"
MIN_WORD_LENGTH = 3


def filter_characters(string, invalid_chars=INVALID_CHARS):
    """
    Removes invalid characters from a string

    :param string: String to be sanitized
    :param invalid_chars: a string containing all invalid characters
    :return: the submitted string stripped from all the invalid characters
    :rtype: str
    """
    # remove invalid characters
    chars = []
    for c in string:
        if c in invalid_chars:
            continue
        chars.append(c)
    s = "".join(chars)
    # transform unicode to ascii
    s = ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))
    # transform everything to lowercase
    return s.lower()


class WordsFinder(object):
    def __init__(self, wordlists):
        # initializing dictionary set
        self.dictionary = None
        self.max_length = 0
        if wordlists:
            self.dictionary = set()
            for txt in wordlists:
                for line in open(txt, "r"):
                    word = filter_characters(line)
                    if len(word) > self.max_length:
                        self.max_length = len(word)
                    self.dictionary.add(word)

    def get_words_indexes(self, string):
        """
        Given a string, detects the largest substring that are dictionary words and returns
        the indices that identify them within the string

        :param string: string to analyze
        :return: 0 or more pairs (i, j, word), where  'word' is the
                 detected word, 'i' is the index of the first char of the word
                 and 'j' is the length of the word
        """
        string = filter_characters(string)
        if len(string) < MIN_WORD_LENGTH:
            return
        if not self.dictionary:
            logging.error("Dictionary uninitalized!")
            return
        i = 0
        while i < len(string) - (MIN_WORD_LENGTH - 1):
            chunk = string[i:i + self.max_length]
            found = False
            for j in range(len(chunk), MIN_WORD_LENGTH - 1, -1):
                candidate = chunk[:j]
                if candidate in self.dictionary:
                    yield (i, j, candidate)
                    found = True
                    i += j
                    break
            if not found:
                i += 1

    def get_words_percentage(self, string):
        """
        Returns the percentage of characters of the string that are part of valid dictionary words contained
        in the string.
        e.g.
        "zxHELLOyw" => 0.5 (50% of the string is composed of dictionary words, in this case "hello")

        :param string: string to be analyzed
        :return: the percentage of characters of the string that are part of valid dictionary words contained
                 in the string
        :rtype: float
        """
        word_length_count = 0
        for i in self.get_words_indexes(string):
            word_length_count += i[1]
        return word_length_count / len(string)
