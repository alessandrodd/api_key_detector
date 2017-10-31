import argparse
import logging
import os
import sys
from logging.config import dictConfig

import numpy as np

import words_finder_singleton

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
sys.path.append(__location__)

from config import conf

dictConfig(conf.logging)

import entropy
import sequentiality
import charset as cset
from dataset_plotter import generate_3d_scatterplot
from gibberish_detector.gibberish_singleton import gib_detector

import string_classifier
from classifier_singleton import classifier


def classify_string(string):
    print("Value: {0}".format(classifier.predict_strings([string])))


def generate_training_set(api_key_files, generic_text_files, dump_file):
    matrix = string_classifier.generate_training_set(api_key_files, generic_text_files)
    np.save(dump_file, matrix)
    logging.info("Training set saved to {0}".format(dump_file))


def test_string(string):
    string = string.replace('\n', '').replace('\r', '')
    features = string_classifier.calculate_all_features(string)
    print(string, features)


def test(sort_index):
    if sort_index is None:
        sort_index = -1

    results = []
    for line in sys.stdin:
        line = line.replace('\n', '').replace('\r', '')
        features = string_classifier.calculate_all_features(line)
        if features:
            data = (line, *features)
            results.append(data)
    if sort_index != -1:
        results = sorted(results, key=lambda d: d[sort_index])
    for result in results:
        print(result)


def main():
    parser = argparse.ArgumentParser(
        description='A python program that detects API Keys', add_help=True
    )
    parser.add_argument('--debug', action="store_true", dest='boolean_debug',
                        default=False, help='Print debug information')
    parser.add_argument('--test', action="store_true", dest='boolean_test',
                        default=False, help='Test mode')
    parser.add_argument('--entropy', action="store", dest='entropy_string',
                        help='Calculates the charset-normalized Shannon Entropy for a string')
    parser.add_argument('--sequentiality', action="store", dest='sequentiality_string',
                        help='Calculates the sequentiality for a string')
    parser.add_argument('--gibberish', action="store", dest='gibberish_string',
                        help='Calculates the gibberish index for a string')
    parser.add_argument('--words-percentage', action="store_true", dest='boolean_wordspercentage',
                        help='Calculates the percentage of words inside strings from stdin')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--string', action="store", dest='string',
                       help='String to be tested. If not defined, waits for input from stdin.')
    group.add_argument('-a', action='store_const',
                       dest='sort_index',
                       const=0,
                       help='Sort in alphabetical order, ascending')
    group.add_argument('-e', action='store_const',
                       dest='sort_index',
                       const=1,
                       help='Sort by entropy, ascending')
    group.add_argument('-s', action='store_const',
                       dest='sort_index',
                       const=2,
                       help='Sort by sequentiality, ascending')
    group.add_argument('-g', action='store_const',
                       dest='sort_index',
                       const=3,
                       help='Sort by gibberish index, ascending')
    group2 = parser.add_argument_group()
    group2.add_argument('--generate-training-set', action="store_true", dest='boolean_generate_training',
                        default=False,
                        help='Generate training set for string classifier. '
                             'Needs --api-key-files, --generic-text-files and --output-file to be specified ')
    group2.add_argument('--plot-training-set', action="store_true", dest='boolean_generate_scatterplot',
                        default=False,
                        help='Generate a scatterplot for the training set. '
                             'Needs --api-key-files, --generic-text-files and --output-file to be specified ')
    group2.add_argument('--api-key-files', nargs='+',
                        help='List of files containing valid api-key examples, one for each line', dest='api_key_files')
    group2.add_argument('--generic-text-files', nargs='+',
                        help='List of files containing generic text examples that DOESN\'T contain any Api Key',
                        dest='generic_text_files')
    group2.add_argument('--output-file', action="store", dest='dump_file',
                        help='Where to output the training set file')
    group3 = parser.add_argument_group()
    group3.add_argument('--classify-string', action='store', dest='classify_string',
                        help='String to be classified.\n0 <- generic text, 1 <- API key')
    results = parser.parse_args()

    # functions that don't need gibberish detector

    if results.boolean_debug:
        logging.basicConfig(level=logging.DEBUG)

    if results.entropy_string:
        e = entropy.normalized_entropy(results.entropy_string, cset.get_narrower_charset(results.entropy_string))
        print(e)
        return

    if results.sequentiality_string:
        s = sequentiality.string_sequentiality(results.sequentiality_string,
                                               cset.get_narrower_charset(results.sequentiality_string), True)
        print(s)
        return
    if results.gibberish_string:
        g = gib_detector.evaluate(results.gibberish_string, True)
        print(g)
        return
    if results.boolean_wordspercentage:
        results = []
        for line in sys.stdin:
            r = words_finder_singleton.finder.get_words_percentage(line)
            results.append("{0:.2f} {1}".format(r, line.strip()))
        for r in reversed(sorted(results, key=str.lower)):
            print(r)
        return
    if results.boolean_test:
        if results.string:
            test_string(results.string)
            return
        else:
            test(results.sort_index)
            return
    elif results.boolean_generate_training:
        if results.api_key_files and results.generic_text_files and results.dump_file:
            generate_training_set(results.api_key_files, results.generic_text_files, results.dump_file)
            return
        elif results.dump_file:
            generate_training_set(conf.string_classifier['api_learnsets'], conf.string_classifier['text_learnsets'],
                                  results.dump_file)
            return
    elif results.boolean_generate_scatterplot:
        if results.api_key_files and results.generic_text_files and results.dump_file:
            generate_3d_scatterplot(results.api_key_files, results.generic_text_files, results.dump_file)
            return
        elif results.dump_file:
            generate_3d_scatterplot(conf.string_classifier['api_learnsets'], conf.string_classifier['text_learnsets'],
                                    results.dump_file)
            return
    elif results.classify_string is not None:
        classify_string(results.classify_string)
        return
    parser.print_help()


if __name__ == '__main__':
    main()
