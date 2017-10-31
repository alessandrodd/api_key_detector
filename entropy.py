import math
import sys


def shannon_entropy(item, itemset):
    """
    Calculates the [String] Shannon Entropy of an item

    :param item: the item [string] of which should be computed the entropy
    :param itemset: an iterable representing the item set [charset as a string]
    :return: the item's entropy
    :rtype: float
    """
    if not item:
        return 0
    entropy = 0.0
    for x in itemset:
        p_x = float(item.count(x)) / len(item)
        if p_x > 0:
            entropy = entropy + (p_x * math.log(p_x, 2))
    return -entropy


def normalized_entropy(item, itemset, charset_normalization=False):
    """
    Calculates the [String] Shannon Entropy relative to the specific item length and set [charset]
    (i.e. weighted by the itemset's [charset's] complexity), if charset_normalization is True

    :param item: the item [string] of which should be computed the entropy
    :param itemset: an iterable representing the item set [charset as a string]
    :param charset_normalization: if True, normalize entropy with respect to the item length AND length of the charset
    :return: normalized entropy
    :rtype: float
    """
    if charset_normalization:
        return shannon_entropy(item, itemset) / (len(item) * len(itemset))
    return shannon_entropy(item, itemset) / len(item)


def main(argv):
    if len(argv) != 3:
        print("Usage: python {0} \"string to be classified\" charset".format(argv[0]))
        return
    print(shannon_entropy(argv[1], argv[2]))


if __name__ == '__main__':
    main(sys.argv)
