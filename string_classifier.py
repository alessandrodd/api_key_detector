import logging
import os
import pickle

import numpy as np
from sklearn.neural_network import MLPClassifier

import charset
from entropy import normalized_entropy
from gibberish_detector.gibberish_singleton import gib_detector
from sequentiality import string_sequentiality


class StringBinaryClassifier(object):
    """
    Wrapper object for a Neural Network.
    Used to classify strings based on entropy, sequentiality and gibberish
    """

    def __init__(self, max_iter=100):
        """
        :param max_iter: max iterations for wrapped Neural Network
        """
        self.__neural_network = MLPClassifier(hidden_layer_sizes=(100, 100), solver='lbfgs', max_iter=max_iter)
        self.input_mean = None
        self.input_stdev = None

    def calculate_normalization_parameters(self, matrix):
        """
        Calculates train set mean and standard deviation to normalize input
        :param matrix: input train set
        """
        self.input_mean = matrix.mean(axis=0)
        self.input_stdev = matrix.std(axis=0)

    def train(self, matrix_learn_set, good_test, bad_test):
        """
        Trains the wrapped neural network

        :param matrix_learn_set: input train set, where each row contains the already-computed input features
        :param good_test:  set of file paths where each line is a class 1 string, used for testing
        :param bad_test: set of file paths where each line is a class 0 string, used for testing
        """
        # always better to shuffle data before feeding to a NN
        np.random.shuffle(matrix_learn_set)
        # separate expected outputs and inputs features
        train_outputs = np.array(matrix_learn_set[:, -1])
        train_inputs = matrix_learn_set[:, 0:-1]
        self.calculate_normalization_parameters(train_inputs)
        if self.input_mean is not None and self.input_stdev is not None:
            train_inputs -= self.input_mean
            train_inputs /= self.input_stdev

        # train the NN
        logging.info("Started training NN...")
        self.__neural_network.fit(train_inputs, train_outputs)
        logging.info("Training finished.")

        tot_count = 0
        err_count = 0
        for good_test_file in good_test:
            for line in open(good_test_file):
                tot_count += 1
                line = line.replace('\n', '').replace('\r', '')
                prediction = self.predict_strings([line])
                if prediction[0] != 1:
                    logging.warning("String {0} was not detected as an API key.".format(line))
                    err_count += 1
        for bad_test_file in bad_test:
            for line in open(bad_test_file):
                tot_count += 1
                line = line.replace('\n', '').replace('\r', '')
                prediction = self.predict_strings([line])
                if prediction[0] != 0:
                    logging.warning("String {0} was wrongly detected as an API key.".format(line))
                    err_count += 1
        score = (tot_count - err_count) / tot_count
        logging.info("Test finished. Classifier score: {0}".format(score))

    def train_from_text_files(self, class_one_files, class_zero_files, good_test, bad_test):
        """
        Trains the wrapped neural network

        :param class_one_files: path of files where each line is a class 1 string, used for training
        :param class_zero_files: path of files where each line is a class 0 string, used for training
        :param good_test:  set of file paths where each line is a class 1 string, used for testing
        :param bad_test: set of file paths where each line is a class 0 string, used for testing        """
        matrix = generate_training_set(class_one_files, class_zero_files)
        self.train(matrix, good_test, bad_test)

    def predict(self, inputs):
        """
        Predicts the class for the inserted inputs

        :param inputs: matrix where each row contains input features
        :return: a list of class predictions, one element for each input
        :rtype: list
        """
        # normalization
        if self.input_mean is not None and self.input_stdev is not None:
            inputs = inputs - self.input_mean
            inputs = inputs / self.input_stdev
        return self.__neural_network.predict(inputs)

    def predict_strings(self, strings):
        """
        Predicts the class for the inserted inputs

        :param strings: a list of string whose class should be predicted
        :return: a list of class predictions, one element for each input
        :rtype: list
        """
        inputs = []
        for string in strings:
            inputs.append(calculate_all_features(string))
        return self.predict(np.array(inputs))


def generate_all_features(list_of_strings):
    """
    Python Generator version of calculate_all_features

    :param list_of_strings: a list of strings
    :return: a tuple containing charset-normalized entropy, sequentiality and gibberish for the string
    """
    for string in list_of_strings:
        yield calculate_all_features(string)


def calculate_all_features(string):
    """
    Computes all the string features, like the normalized entropy, sequentiality and gibberish, for a given string

    :param string: string to be analyzed
    :return: a tuple containing charset-normalized entropy, sequentiality and gibberish for the string
    :rtype: (float, float, float, float)
    """
    if not string:
        return None
    relative_charset = charset.get_narrower_charset(string)
    if not relative_charset:
        return None
    entropy = normalized_entropy(string, relative_charset, False)
    sequentiality = string_sequentiality(string, relative_charset)
    gibberish = gib_detector.evaluate(string, True)
    return entropy, sequentiality, gibberish, float(len(relative_charset))


def generate_training_set(class_one_files, class_zero_files, return_strings=False):
    """
    Generates a matrix containing rows of string features

    :param class_one_files: path of files where each line is a class 1 string, used for training
    :param class_zero_files: path of files where each line is a class 0 string, used for training
    :param return_strings: if True, returns a list with the original strings too
    :return: a matrix containg the training set and (if return_strings is True) the list of strings
             that corresponds to each row of the matrix (order compatible, i.e. the i-th string was
             used to generate the values in the i-th row of the matrix
    :rtype: Union[np.array, (np.array, list)]
    """
    rows = []
    strings = []
    for file_path in class_one_files:
        for line in open(file_path):
            line = line.replace('\n', '').replace('\r', '')
            features = calculate_all_features(line)
            if features is not None:
                array = list(features)
                array.append(1.0)
                if return_strings:
                    strings.append(line)
                rows.append(array)
            else:
                print("Invalid line: {0}".format(line))
    for file_path in class_zero_files:
        for line in open(file_path):
            line = line.replace('\n', '').replace('\r', '')
            features = calculate_all_features(line)
            if features is not None:
                array = list(features)
                array.append(0.0)
                if return_strings:
                    strings.append(line)
                rows.append(array)
            else:
                print("Invalid line: {0}".format(line))
    matrix = np.array(rows)
    if return_strings:
        if len(matrix) != len(strings):
            logging.error("Something went wrong")
        return matrix, strings
    return matrix


def load_or_create_trained_instance(class_one_files, class_zero_files, good_test, bad_test, dump_file, rebuild=False):
    """
    Initializes a StringClassifier if not available in dump_file, otherwise it simply loads it from storage

    :param class_one_files: path of files where each line is a class 1 string, used for training
    :param class_zero_files: path of files where each line is a class 0 string, used for training
    :param good_test:  set of file paths where each line is a class 1 string, used for testing
    :param bad_test: set of file paths where each line is a class 0 string, used for testing
    :param dump_file: path of the dump file
    :param rebuild: if the instance should be re-created even if a dump file is available
    :return: a ready-to-be-used StringClassifier instance
    :rtype: StringBinaryClassifier
    """
    if os.path.exists(dump_file):
        if rebuild:
            try:
                os.remove(dump_file)
            except OSError:
                pass
        else:
            logging.info("Restoring dump file '{0}'. There is no need to re-train the algorithm".format(dump_file))
            classifier = pickle.load(open(dump_file, 'rb'))
            logging.info("Dump restored")
            return classifier
    classifier = StringBinaryClassifier()
    classifier.train_from_text_files(class_one_files, class_zero_files, good_test, bad_test)
    pickle.dump(classifier, open(dump_file, 'wb'))
    logging.info("Object saved to {0}".format(dump_file))
    return classifier
