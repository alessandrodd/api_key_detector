import math
import sys

import matplotlib

matplotlib.use('Agg')  # Avoid tkinter dependency
import matplotlib.pyplot as plt

import charset as cset


def string_sequentiality(string, charset, plot_scatterplot=False):
    """
    Computes how much a string contains sequence of consecutive or distance-fixed characters

    :param string: the string
    :param charset: a charset as a string
    :param plot_scatterplot: optional boolean, if true plots a scatterplot

    :return: sequentiality index, 0 (low sequentiality) to 1 (high sequentiality)
    :rtype: float
    """
    if len(string) <= 2:
        return 0
    string_length = len(string)
    window_size = math.floor(math.log(string_length))
    window_size = int(window_size)
    counter = 0
    buckets = {}
    for j in range(1, len(string)):
        for i in range(max(j - window_size, 0), j):
            diff = math.fabs((ord(string[j]) - ord(string[i])))
            buckets[diff] = buckets.get(diff, 0) + 1
            counter += 1

    # normalize histogram
    for key in buckets.keys():
        buckets[key] = buckets[key] / counter

    # Calculate MSE
    charset_buckets = cset.get_char_distance_distribution(charset)
    mse = 0
    for key in charset_buckets.keys():
        diff = buckets.get(key, 0) - charset_buckets.get(key, 0)
        square_diff = diff ** 2
        mse += square_diff / len(charset_buckets.keys())

    if plot_scatterplot:
        # Plot the scatterplot
        subplot = plt.subplot(111)
        subplot.set_xlabel("Average distance from other characters")
        subplot.set_ylabel("% of chars at distance x from the others")
        s1 = s2 = None
        for v in charset_buckets.items():
            x = v[0]
            y = v[1]
            s1 = plt.scatter(x, y * 100, alpha=0.6, color='r', label='charset')

        for v in buckets.items():
            x = v[0]
            y = v[1]
            s2 = plt.scatter(x, y * 100, alpha=0.6, color='g', label='string')

        plt.legend(handles=[s1, s2])
        plt.show()

    return mse


def weighted_sequentiality(string, charset):
    """
    Returns the string sequentiality weighted by the string length. I.e.
    ABC is less meaningful than ABCDEFGHIJKLMNO

    :param string:
    :param charset:
    :return:
    """
    return string_sequentiality(string, charset) * len(string)


def multiple_string_sequentiality(item_charset_dict):
    """
    Calculates the sequentiality for a list of strings

    :param item_charset_dict: list of string:charset
    :return: string:sequentiality dictionary
    :rtype: dict
    """
    items = {}
    for item in item_charset_dict:
        items[item] = (string_sequentiality(item[0], item[1]))
    return items


def main(argv):
    if len(argv) != 2:
        print("Usage: python {0} string_to_be_computed".format(argv[0]))
        return
    else:
        print(
            "Sequentiality index: {0}".format(string_sequentiality(argv[1], cset.get_narrower_charset(argv[1]), True)))


if __name__ == '__main__':
    main(sys.argv)
