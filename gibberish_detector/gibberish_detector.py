"""
Based on Gibberish-Detector by Rob Renaud: https://github.com/rrenaud/Gibberish-Detector

MIT License included:

The MIT License (MIT)

Copyright (c) 2015 Rob Renaud

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import logging
import math
import os
import pickle

# ACCEPTED_CHARSET = 'abcdefghijklmnopqrstuvwxyz '
# ACCEPTED_CHARSET = " +-/0123456789=ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz"
# ACCEPTED_CHARSET = " !#+,-./0123456789:;=ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz"
ACCEPTED_CHARSET = "0123456789abcdefghijklmnopqrstuvwxyz"

pos = dict([(char, idx) for idx, char in enumerate(ACCEPTED_CHARSET)])

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


class GibberishDetector(object):
    def __init__(self):
        self.log_prob_mat = None
        self.threshold = None

    def train(self, learnset, good_test, bad_test):
        """
        Trains the Gibberish Detector, i.e. creates the transition probability matrix

        :param learnset: list of file paths containing non-gibberish lines of text (e.g. books, stories...)
        :param good_test: set of file paths where each line doesn't contain gibberish, used for testing
        :param bad_test: set of file paths where each line contains gibberish, used for testing
        """
        logging.info("Training the gibberish detector module...")

        k = len(ACCEPTED_CHARSET)
        # Assume we have seen 10 of each character pair.  This acts as a kind of
        # prior or smoothing factor.  This way, if we see a character transition
        # live that we've never observed in the past, we won't assume the entire
        # string has 0 probability.
        self.log_prob_mat = [[10 for i in range(k)] for i in range(k)]

        # Count transitions from big text files, taken
        # from http://norvig.com/spell-correct.html
        for document in learnset:
            for line in open(document):
                for a, b in ngram(2, line):
                    self.log_prob_mat[pos[a]][pos[b]] += 1

        # Normalize the probability_mat so that they become log probabilities.
        # We use log probabilities rather than straight probabilities to avoid
        # numeric underflow issues with long texts.
        # This contains a justification:
        # http://squarecog.wordpress.com/2009/01/10/dealing-with-underflow-in-joint-probability-calculations/
        for i, row in enumerate(self.log_prob_mat):
            s = float(sum(row))
            for j in range(len(row)):
                row[j] = math.log(row[j] / s)

        # Find the probability of generating a few arbitrarily choosen good and
        # bad phrases.
        good_probs = []
        for good_test_file in good_test:
            with open(good_test_file) as f:
                for l in f:
                    good_probs.append(self.evaluate(l))

        bad_probs = []
        for bad_test_file in bad_test:
            with open(bad_test_file) as f:
                for l in f:
                    bad_probs.append(self.evaluate(l))

        # Assert that we actually are capable of detecting the junk.
        assert min(good_probs) > max(bad_probs)

        # And pick a threshold halfway between the worst good and best bad inputs.
        self.threshold = (min(good_probs) + max(bad_probs)) / 2
        logging.info("Training complete.")

    def evaluate(self, l, default_to_0=False):
        """
        Return the average transition prob from l through log_prob_mat.

        :param l: string to be evaluated
        :param default_to_0: if True, whenever the submitted string it's made of just one or zero
                             accepted characters, returns 0.
        :return: a value which indicates how likely is the string to be composed of natural language words.
                 Recognized languages depends on the training set. The lower the value, the more probable is that
                 the string is gibberish.
        :rtype: float
        """
        if default_to_0 and len(normalize(l)) <= 1:
            return 0
        log_prob = 0.0
        transition_ct = 0
        for a, b in ngram(2, l):
            log_prob += self.log_prob_mat[pos[a]][pos[b]]
            transition_ct += 1
        # The exponentiation translates from log probs to probs.
        return math.exp(log_prob / (transition_ct or 1))


def normalize(line):
    """ Return only the subset of chars from accepted_chars.
    This helps keep the  my_model relatively small by ignoring punctuation,
    infrequenty symbols, etc. """
    return [c.lower() for c in line if c.lower() in ACCEPTED_CHARSET]


def ngram(n, l):
    """ Return all n grams from l after normalizing """
    filtered = normalize(l)
    for start in range(0, len(filtered) - n + 1):
        yield ''.join(filtered[start:start + n])


def load_or_create_trained_instance(learnset, good_test, bad_test, dump_file, rebuild=False):
    """
    Initializes a GibberishDetector if not available in dump_file, otherwise it simply loads it from storage
    :param learnset: list of file paths containing non-gibberish lines of text (e.g. books, stories...)
    :param good_test: set of file paths where each line doesn't contain gibberish, used for testing
    :param bad_test: set of file paths where each line contains gibberish, used for testing
    :param dump_file: path of the dump file
    :param rebuild: if the instance should be re-created even if a dump file is available
    :return:a ready-to-be-used GibberishDetector instance
    :rtype: GibberishDetector
    """
    if os.path.exists(dump_file):
        if rebuild:
            try:
                os.remove(dump_file)
            except OSError:
                pass
        else:
            logging.info("Restoring dump file '{0}'. There is no need to re-train the algorithm".format(dump_file))
            detector = pickle.load(open(dump_file, 'rb'))
            logging.info("Dump restored")
            return detector
    detector = GibberishDetector()
    detector.train(learnset, good_test, bad_test)
    pickle.dump(detector, open(dump_file, 'wb'))
    logging.info("Object saved to {0}".format(dump_file))
    return detector
