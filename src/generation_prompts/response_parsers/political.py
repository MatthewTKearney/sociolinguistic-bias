from generation_prompts.response_parsers.parse_utils import parse_yes_no

def parse_political(response, question_idx, prob=None):
    liberal_answer = "yes" if question_idx%12 <= 5 else "no"
    parse_dict, valid = parse_yes_no(response, prob=prob)
    if valid:
        parse_dict["liberal"] = parse_dict[liberal_answer]    
    return parse_dict, valid