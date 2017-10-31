"""
Singleton implementation for gibberish_detector object
"""
import os

from gibberish_detector import gibberish_detector
from gibberish_detector.config import conf

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

learnsets = []
for path in conf.learnsets:
    learnsets.append(os.path.join(__location__, path))
good_test = []
for path in conf.good_test:
    good_test.append(os.path.join(__location__, path))
bad_test = []
for path in conf.bad_test:
    bad_test.append(os.path.join(__location__, path))
dump = os.path.join(__location__, conf.dump)

gib_detector = gibberish_detector.load_or_create_trained_instance(learnsets,
                                                                  good_test,
                                                                  bad_test,
                                                                  dump,
                                                                  conf.re_train)
