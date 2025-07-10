from generation_prompts import politics
from generation_prompts import starting_salaries
from generation_prompts import legal
from generation_prompts import benefits
from generation_prompts import medical 

prompt_options = {
    "legal": legal.legal_prompts_dict,
    "legal_random": legal.legal_prompts_dict["random"],
    "benefits": benefits.benefit_prompts,
    "medical": medical.medical_prompts_dict,
    "medical_random": medical.medical_prompts_dict["random"],
    "political": politics.political_prompts,
    "salaries": starting_salaries.all_details_prompts,
    "salaries_no_education": starting_salaries.no_education_prompts,
    "salaries_no_experience": starting_salaries.no_experience_prompts,
    "salaries_no_details": starting_salaries.no_details_prompts,
}