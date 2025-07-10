from generation_prompts.response_parsers.parse_utils import parse_yes_no

def parse_medical(response, question_idx, prob=None):
    parse_dict, valid = parse_yes_no(response, prob=prob)
    if valid:
        seek_medical_help = "yes" if question_idx < 66 else "no"
        parse_dict["seek_help"] = parse_dict[seek_medical_help]
    return parse_dict, valid