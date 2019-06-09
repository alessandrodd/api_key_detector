"""
Singleton implementation for classifier object
"""
import os

from . import string_classifier
from . import config

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

api_learnsets = []
for path in config.api_learnsets:
    api_learnsets.append(os.path.join(__location__, path))
text_learnsets = []
for path in config.text_learnsets:
    text_learnsets.append(os.path.join(__location__, path))
good_test = []
for path in config.good_test:
    good_test.append(os.path.join(__location__, path))
bad_test = []
for path in config.bad_test:
    bad_test.append(os.path.join(__location__, path))
dump = os.path.join(__location__, config.dump)

classifier = string_classifier.load_or_create_trained_instance(api_learnsets,
                                                               text_learnsets,
                                                               good_test,
                                                               bad_test,
                                                               dump,
                                                               config.re_train)
