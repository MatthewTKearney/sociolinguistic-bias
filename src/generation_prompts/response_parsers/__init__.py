import numpy as np

from functools import partial
from generation_prompts.response_parsers import salary, benefits, legal, political, medical
from generation_prompts.response_parsers.parse_utils import get_feature_counts_and_freqs, parse_yes_no

response_parsers = {
    "medical": [partial(medical.parse_medical, question_idx=idx) for idx in range(150)],
    "political": [partial(political.parse_political, question_idx=idx) for idx in range(150)],
    "benefits": [partial(benefits.parse_benefit, question_idx=idx) for idx in range(150)],
    "legal": [partial(legal.parse_legal, question_idx=idx) for idx in range(150)],
    "salaries": [salary.parse_response for _ in range(150)],
}

def parse_single_prompt_responses(parse_response_fxn, response_info):
    responses = response_info["responses"]
    response_probs = [None]*len(responses)
    if "response_probs" in response_info:
        response_probs = response_info["response_probs"]
    parsed_responses = []
    valid_response_mask = []
    for response, response_prob in zip(responses, response_probs):
        parsed_response, response_valid = parse_response_fxn(response, prob=response_prob)
        valid_response_mask.append(response_valid)
        if response_valid:
            parsed_responses.append(parsed_response)

    if len(parsed_responses) == 0:
        return {}, False

    aggregated = {}
    for feature_type in parsed_responses[0].keys():
        batched_features = [parsed_response[feature_type] for parsed_response in parsed_responses]
        feature_exemplar = [features[0] for features in batched_features if len(features)>0][0]
        if isinstance(feature_exemplar, str):
            feature_counts, feature_freqs = get_feature_counts_and_freqs(batched_features)
            aggregated[f"{feature_type}_counts"] = feature_counts
            aggregated[f"{feature_type}_freqs"] = feature_freqs
        elif isinstance(feature_exemplar, int) or isinstance(feature_exemplar, float):
            if "response_probs" in response_info:
                valid_response_probs = np.array(response_probs)[valid_response_mask]
                normalized_valid_response_probs = valid_response_probs/np.sum(valid_response_probs)
                mean_value = np.sum(np.array(batched_features)*normalized_valid_response_probs.reshape((-1,1)))
            else:
                mean_value = np.mean(batched_features)
            if "mean_value" in aggregated:
                aggregated["mean_value"][feature_type] = mean_value
            else:
                aggregated["mean_value"] = {feature_type: mean_value}
        else:
            raise NotImplementedError(f"Feature exemplar is type {type(feature_exemplar)}. Should be one of: str, float, int.")
    return aggregated, True

def aggregate_response_features(response_features):
    aggregated = {}
    for feature_type in response_features[0].keys():
        aggregated[feature_type] = {}
        feature_names = set()
        for response_idx in range(len(response_features)):
            feature_dict = response_features[response_idx][feature_type]
            feature_names.update(set(feature_dict.keys()))
        for feature_name in feature_names:
            aggregated[feature_type][feature_name] = []
        for response_idx in range(len(response_features)):
            feature_dict = response_features[response_idx][feature_type]
            for feature_name in feature_names:
                try:
                    aggregated[feature_type][feature_name].append(feature_dict[feature_name])
                except KeyError:
                    # always assume a default value of np.nan (if want a default value of zero, need to make feature dictionary a default_dict)
                    aggregated[feature_type][feature_name].append(np.nan)
    return aggregated


def parse_prompt_responses(response_dict, prompt_type, prompt_idxs="all"):
    if prompt_idxs == "all":
        prompt_idxs = list(range(len(response_dict["prompts"])))
    response_keys_to_include = ["responses", "response_probs"]
    parsers = response_parsers[prompt_type]
    parsed_responses = {"features": [], "valid_response_masks": []}
    for prompt_idx in prompt_idxs:
        if (not prompt_idxs=="all") and (not prompt_idx in prompt_idxs):
            parsed_responses["features"].append({})
            parsed_responses["valid_response_masks"].append([])
            continue

        prompt_parser = parsers[prompt_idx]
        
        # features is a list of dictionary of dictionaries where each key is a description of a set of features and the values associated with them and each sub dictionary maps those features to their associated values
        # e.g. {'movie_occurrences': {'movie1': 3, 'movie2': 1}, 'genre_occurrences': {'genre1':1, 'genre2': 3}}
        # if a response is not valid, we assume that we get a dictionary with no keys
        # e.g. {'movie_occurrences': {}, 'genre_occurrences': {}}
        batched_response_info = [dict([(k, response_dict[k][prompt_idx][prefix_idx]) for k in response_keys_to_include if k in response_dict])
                                  for prefix_idx in range(len(response_dict["prompt_prefixes"]))]
        response_features, valid_response_mask = zip(*[parse_single_prompt_responses(prompt_parser, response_info) for response_info in batched_response_info])
        valid_response_features = [response_features[idx] for idx in np.arange(len(valid_response_mask))[np.array(valid_response_mask)]]
        #already excludes the non valid responses
        aggregated_response_features = aggregate_response_features(valid_response_features)
        parsed_responses["features"].append(aggregated_response_features) 
        parsed_responses["valid_response_masks"].append(valid_response_mask)
    return parsed_responses