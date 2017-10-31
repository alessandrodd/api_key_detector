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
from strings_filter_singleton import s_filter

import string_classifier
from classifier_singleton import classifier


def detect_api_keys(strings):
    apikeys = [string for string in strings if s_filter.pre_filter(string)]
    classification = classifier.predict_strings(apikeys)
    apikeys = [apikeys[i] for i in range(len(apikeys)) if classification[i] > 0.5]
    apikeys = [string for string in apikeys if s_filter.post_filter(string)]
    return apikeys


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
                        default=False, help='Test mode; calculates all features for strings in stdin')
    parser.add_argument('--entropy', action="store_true", dest='boolean_entropy',
                        help='Calculates the charset-normalized Shannon Entropy for strings in stdin')
    parser.add_argument('--sequentiality', action="store_true", dest='boolean_sequentiality',
                        help='Calculates the Sequentiality Index for strings in stdin')
    parser.add_argument('--gibberish', action="store_true", dest='boolean_gibberish',
                        help='Calculates the Gibberish Index for strings in stdin')
    parser.add_argument('--charset-length', action="store_true", dest='boolean_charset',
                        help='Calculates the Induced Charset Length for strings in stdin')
    parser.add_argument('--words-percentage', action="store_true", dest='boolean_wordspercentage',
                        help='Calculates the percentage of dictionary words for each string in stdin')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--string', action="store", dest='string',
                       help='Calculate all features for a single string, to be used in conjunction with --test.')
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
                        help='Generate a 3d scatterplot for the training set. '
                             'Needs --api-key-files, --generic-text-files and --output-file to be specified ')
    group2.add_argument('--api-key-files', nargs='+',
                        help='List of files containing valid api-key examples, one for each line', dest='api_key_files')
    group2.add_argument('--generic-text-files', nargs='+',
                        help='List of files containing generic text examples that DOESN\'T contain any Api Key',
                        dest='generic_text_files')
    group2.add_argument('--output-file', action="store", dest='dump_file',
                        help='Where to output the training set file')
    group3 = parser.add_argument_group()
    group3.add_argument('--filter-apikeys', action='store_true', dest='boolean_detect',
                        help='Filter potential apikeys from strings in stdin.')
    results = parser.parse_args()

    # functions that don't need gibberish detector

    if results.boolean_debug:
        logging.basicConfig(level=logging.DEBUG)

    if results.boolean_test:
        if results.string:
            test_string(results.string)
            return
        else:
            test(results.sort_index)
            return

    if results.boolean_entropy or results.boolean_sequentiality or results.boolean_charset or \
            results.boolean_gibberish or results.boolean_wordspercentage or results.boolean_detect:
        print("Enter a list of string, one for each line. Press CTRL+D when finished")
        strings = []
        for line in sys.stdin:
            strings.append(line.strip())

        values = []
        if results.boolean_detect:
            values = detect_api_keys(strings)
            for string in values:
                print(string)
            return
        elif results.boolean_entropy:
            for string in strings:
                values.append(entropy.normalized_entropy(string, cset.get_narrower_charset(string)))
        elif results.boolean_sequentiality:
            for string in strings:
                values.append(sequentiality.string_sequentiality(string, cset.get_narrower_charset(string), True))
        elif results.boolean_gibberish:
            for string in strings:
                values.append(gib_detector.evaluate(string, True))
        elif results.boolean_charset:
            for string in strings:
                values.append(len(cset.get_narrower_charset(string)))
        elif results.boolean_wordspercentage:
            for string in strings:
                values.append(words_finder_singleton.finder.get_words_percentage(string))
        else:
            print("Unexpected ERROR")
            return
        for value, line in zip(values, strings):
            print("{0} {1}".format(value, line))
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
    parser.print_help()


if __name__ == '__main__':
    main()
