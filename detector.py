import os
import sys

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
sys.path.append(__location__)
from classifier_singleton import classifier
from strings_filter_singleton import s_filter


def filter_api_keys(strings):
    apikeys = [string for string in strings if s_filter.pre_filter(string)]
    classification = classifier.predict_strings(apikeys)
    apikeys = [apikeys[i] for i in range(len(apikeys)) if classification[i] > 0.5]
    apikeys = [string for string in apikeys if s_filter.post_filter(string)]
    return apikeys


def detect_api_keys(strings):
    detection = []
    for string in strings:
        detection.append(s_filter.pre_filter(string))
    apikeys = [strings[i] for i in range(len(strings)) if detection[i]]
    classification = classifier.predict_strings(apikeys)
    j = 0
    for i in range(len(detection)):
        if detection[i]:
            detection[i] = classification[j] > 0.5
            j += 1
            if detection[i]:
                detection[i] = s_filter.post_filter(strings[i])
    return detection
