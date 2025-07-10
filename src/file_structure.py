import os
from os.path import join
import numpy as np

def get_generation_dir(data_dir, prompt_prefix_dataset, generation_model):
    directory = join(data_dir, "generations", f"{generation_model}_{prompt_prefix_dataset}")
    os.makedirs(directory, exist_ok=True)
    return directory

def get_generation_fpath(data_dir, prompt_prefix_dataset, generation_model, prompt_tag, temperature):
    temperature_str = f"_T{np.round(temperature, 2)}" if temperature != 1.0 else ""
    return join(get_generation_dir(data_dir, prompt_prefix_dataset, generation_model), f"{prompt_tag}{temperature_str}_prompt_responses.json")

def get_response_analysis_dir(data_dir, prompt_prefix_type, generation_model, prompt_type, label_type):
    directory = join(data_dir, "response_analysis", f"{generation_model}_{prompt_prefix_type}", prompt_type, f"{label_type}")
    os.makedirs(directory, exist_ok=True)
    return directory

def get_response_regression_analysis_fpath(data_dir, prompt_prefix_type, generation_model, prompt_type, prompt_idx, label_type, formula_variable):
    return join(get_response_analysis_dir(data_dir, prompt_prefix_type, generation_model, prompt_type, label_type), f"{formula_variable}_prompt_{prompt_idx}_regression_stats.csv")