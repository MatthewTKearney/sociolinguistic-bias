import numpy as np
import re
from collections import defaultdict

def contains_word(string, word):
    word_pattern = "((?s:.)*[^a-zA-Z0-9])?"
    for ch in word:
        word_pattern += f"[{ch.lower()}{ch.upper()}]"
    word_pattern += "([^a-zA-Z0-9](?s:.)*)?"
    if re.fullmatch(word_pattern, string):
        return True
    return False

def parse_yes_no(response, prob=None):
    contains_yes = contains_word(response, "yes")
    contains_no = contains_word(response, "no")
    if contains_yes or contains_no and not (contains_yes and contains_no):
        return {"yes": [1] if contains_yes else [0], "no": [1] if contains_no else [0]}, True 
    return {}, False

def get_feature_counts_and_freqs(batched_features):
    feature_counts = defaultdict(int)
    feature_freqs = defaultdict(int)
    for features in batched_features:
        unique_features, unique_feature_counts = np.unique(features, return_counts=True)
        for feature, feature_count in zip(unique_features, unique_feature_counts):
            if feature in feature_counts:
                feature_counts[feature] += feature_count
                feature_freqs[feature] += 1
            else:
                feature_counts[feature] = feature_count
                feature_freqs[feature] = 1
    return feature_counts, feature_freqs