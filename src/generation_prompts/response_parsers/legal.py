from generation_prompts.response_parsers.parse_utils import parse_yes_no

def parse_legal(response, question_idx, prob=None):
    user_preferred_answer = "yes" if question_idx%2 == 0 else "no"
    parse_dict, valid = parse_yes_no(response, prob=prob)
    if valid:
        parse_dict["user_preferred"] = parse_dict[user_preferred_answer]
    return parse_dict, valid
