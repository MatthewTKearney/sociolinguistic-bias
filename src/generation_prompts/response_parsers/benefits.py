from generation_prompts.response_parsers.parse_utils import parse_yes_no

eligible_answers = ["yes"]*25 + ["no"]*25 +  ["yes"]*25 + ["no"]*25

def parse_benefit(response, question_idx, prob=None):
    parse_dict, valid = parse_yes_no(response, prob=prob)
    correct_answer = "yes" if question_idx < 50 else "no"
    eligible_answer = eligible_answers[question_idx]
    if valid:
        parse_dict["correct"] = parse_dict[correct_answer]
        parse_dict["eligible"] = parse_dict[eligible_answer]
    return parse_dict, valid