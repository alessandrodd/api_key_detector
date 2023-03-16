"""
Singleton implementation for config objects
"""
import os
import yaml

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

CONFIG_PATH = "config.yml"

with open(os.path.join(__location__, CONFIG_PATH), 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
    # Load the yaml content into this module global variables
    globals().update(cfg)
