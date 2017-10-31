"""
Singleton implementation for WordsFinder object
"""
import os

from detector_config import conf
from strings_filter import StringsFilter

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

blacklists = []
for path in conf.blacklists:
    blacklists.append(os.path.join(__location__, path))

s_filter = StringsFilter(conf.min_key_length, conf.word_content_threshold, blacklists)
