"""
Singleton implementation for config objects
"""
import os

from my_tools import config_parser

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

CONFIG_PATH = "config.json"

conf = config_parser.parse(os.path.join(__location__, CONFIG_PATH))
