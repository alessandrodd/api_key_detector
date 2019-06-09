"""
Singleton implementation for WordsFinder object
"""
import os

from . import config
from .words_finder import WordsFinder

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

wordlists = []
for path in config.wordlists:
    wordlists.append(os.path.join(__location__, path))

finder = WordsFinder(wordlists)
