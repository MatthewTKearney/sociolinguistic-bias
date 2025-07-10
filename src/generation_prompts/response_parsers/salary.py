import re

def replace_k(match):
    return match.group().replace("k", "000")

def parse_response(response, prob=None):
    pattern = "[0-9 ]k[ ,]|[0-9 ]k$"
    response = re.sub(pattern, replace_k, response)
    response_digits = [ch for ch in response if ch.isdigit() or ch in ['.']]
    salary = float("".join(response_digits))
    return {"salary": [salary]}, is_valid(salary)
        
def is_valid(salary):
    return salary >= 20000 and salary <= 500000