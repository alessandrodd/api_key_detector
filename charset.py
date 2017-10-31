import math
import sys
from enum import Enum

from my_tools.memoized import Memoized


class Charset(Enum):
    # characters order is important, should follow the ascii table index
    HEX_CHARS = "0123456789ABCDEFabcdef"
    HEX_CHARS_EXT = "-0123456789ABCDEFabcdef"  # for GUID
    BASE64_CHARS = "+/0123456789=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    BASE64_CHARS_EXT = "+-/0123456789=ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz"
    BASE64_CHARS_EXT2 = "+,-./0123456789;=ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz"
    BASE91_CHARS = "!\"#$%&()*+,./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
    BASE91_CHARS_EXT = "!\"#$%&()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
    PRINT_CHARS = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"

    def __str__(self):
        return str(self.value)


def get_narrower_charset(string):
    """
    Return the narrowest charset (among those defined) for the submitted string

    :param string: the string of which should be find the charset
    :return: the narrowest charset
    :rtype: str
    """
    for charset in Charset:
        charset = str(charset)
        charset_found = True
        for c in set(string):
            if c not in charset:
                charset_found = False
                break
        if charset_found:
            return charset
    return None


@Memoized
def get_charset_intervals(charset):
    """
    Given a charset, returns a list of INCLUSIVE (i.e. [a,b] in mathematical noation)
    intervals relative to the ascii table.
    For example, inserting 0123456789ABCDEFabcdef, the returned list will be
    [(48, 57), (65, 70), (97, 102)]

    :param charset: the charset as a string
    :return: a list of intervals
    :rtype: list
    """
    charset_set_list = sorted(set(charset), key=lambda char: ord(char))
    if len(charset_set_list) < 1:
        return None
    if len(charset_set_list) == 1:
        return [ord(charset[0])]

    left_index = ord(charset_set_list[0])
    latest_index = left_index
    intervals = []
    for c in charset_set_list[1:]:
        if ord(c) != (latest_index + 1):
            intervals.append((left_index, latest_index))
            left_index = ord(c)
        latest_index = ord(c)
    intervals.append((left_index, latest_index))
    return intervals


@Memoized
def get_char_distance_distribution(charset):
    """
    Calculates the distribution of the distance between characters. VERY slow, to be used with @Memoized
    for good performance (if only a predetermined set of charsets is needed)

    :param charset: the charset as a string
    :return: a (normalized) histogram with the distribution of distance
    :rtype: dict
    """
    if len(charset) <= 1:
        return {0: 1}
    buckets = {}
    counter = 0
    for i in range(0, len(charset)):
        for j in range(0, len(charset)):
            index = int(math.fabs(ord(charset[i]) - ord(charset[j])))
            buckets[index] = buckets.get(index, 0) + 1
            counter += 1
    # normalize histogram
    for key in buckets.keys():
        buckets[key] = buckets[key] / counter

    return buckets


def main(argv):
    if len(argv) != 2:
        print("Usage: python {0} charset_string".format(argv[0]))
        return
    print(str(get_char_distance_distribution(argv[1])))


if __name__ == '__main__':
    main(sys.argv)
