"""
Singleton implementation for gibberish_detector object
"""
import os

from api_key_detector.gibberish_detector import gibberish_detector
from api_key_detector.gibberish_detector import config

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

learnsets = []
for path in config.learnsets:
    learnsets.append(os.path.join(__location__, path))
good_test = []
for path in config.good_test:
    good_test.append(os.path.join(__location__, path))
bad_test = []
for path in config.bad_test:
    bad_test.append(os.path.join(__location__, path))
dump = os.path.join(__location__, config.dump)

gib_detector = gibberish_detector.load_or_create_trained_instance(learnsets,
                                                                  good_test,
                                                                  bad_test,
                                                                  dump,
                                                                  config.re_train)
