"""
Singleton implementation for WordsFinder object
"""
import os

from . import config
from .strings_filter import StringsFilter

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

blacklists = []
for path in config.blacklists:
    blacklists.append(os.path.join(__location__, path))

s_filter = StringsFilter(config.min_key_length, config.word_content_threshold, blacklists)
