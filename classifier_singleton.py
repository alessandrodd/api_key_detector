"""
Singleton implementation for classifier object
"""
import os

import string_classifier
from detector_config import conf

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

api_learnsets = []
for path in conf.api_learnsets:
    api_learnsets.append(os.path.join(__location__, path))
text_learnsets = []
for path in conf.text_learnsets:
    text_learnsets.append(os.path.join(__location__, path))
good_test = []
for path in conf.good_test:
    good_test.append(os.path.join(__location__, path))
bad_test = []
for path in conf.bad_test:
    bad_test.append(os.path.join(__location__, path))
dump = os.path.join(__location__, conf.dump)

classifier = string_classifier.load_or_create_trained_instance(api_learnsets,
                                                               text_learnsets,
                                                               good_test,
                                                               bad_test,
                                                               dump,
                                                               conf.re_train)
