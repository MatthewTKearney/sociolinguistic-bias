import numpy as np
import re
import pandas as pd
from tqdm import tqdm
import os
from functools import partial
import argparse
import subprocess
import shutil

from data import load_prism, update_surveys
from file_structure import get_response_regression_analysis_fpath
from identity_categories import get_basic_regression_categories, get_user_id_category, get_limited_controls
from generation_prompts.response_parsers import parse_prompt_responses
from run_benchmark import load_prompt_responses

import warnings
warnings.filterwarnings("ignore", message="A value is trying to be set on a copy of a slice from a DataFrame.", category=RuntimeWarning)
warnings.filterwarnings("ignore", message="The default of observed=False is deprecated and will be changed to True", category=RuntimeWarning)

## LOAD IDENTITY DATA IN DF
def create_categorical_df(categories, surveys):
    identity_values = np.array([category.get_identity_values(surveys) for category in categories]).T
    identity_df = pd.DataFrame(identity_values, columns=[category.category_name for category in categories])
    for category in categories:
        category_values = category.identity_class_names.copy()
        reference = category.reference_value
        if reference in category_values:
            category_values.remove(reference)
            category_values = [reference] + category_values
        identity_df[category.category_name] = pd.Categorical(identity_df[category.category_name], categories=category_values, ordered=False)
    return identity_df

def get_categorical_variable_name(identity_category):
    return identity_category.category_name

def get_continuous_variable_name(identity_category, class_name):
    return re.sub(r'[^a-zA-Z0-9]', '_', f"{identity_category.category_name}_{class_name}")

def get_identity_data(identity_categories, user_id_category, surveys, label_type, generation_model=None):
    if label_type == "ground_truth":
        all_categories = identity_categories
        identity_df = create_categorical_df(all_categories, surveys)
    else:
        raise NotImplementedError
    user_id_df = create_categorical_df([user_id_category], surveys)
    identity_df = pd.concat([identity_df, user_id_df], axis=1)
    return identity_df

## PROCESS RESULTS FROM RUNNING R MODELS

def get_analysis_details(prompt_idx, valid_response_mask, response_feature_type, response_feature, model_variables, identity_categories, identity_df_valid, label_type, var_to_category_class):
    reference_vars = {f"{category.category_name}": category.reference_value for category in identity_categories for class_name in category.identity_class_names}
    category_names, class_names = zip(*[var_to_category_class[var] if var in var_to_category_class else (var, var) for var in model_variables])
    variable_details = {
        "prompt_idx": [prompt_idx]*len(category_names),
        "prompt_pct_valid": [np.mean(valid_response_mask)]*len(category_names),
        "response_feature_type": [response_feature_type]*len(category_names),
        "response_feature": [response_feature]*len(category_names),
        "response_feature_count": [np.sum(np.where(identity_df_valid[response_feature]>0, 1, 0))]*len(category_names), 
        "identity_variable": class_names,
        "classification_category": category_names,
    }
    if label_type == "ground_truth":
        variable_details["identity_mean"] = [np.mean(identity_df_valid[response_feature][identity_df_valid[category_name] == class_name]) for category_name, class_name in zip(category_names, class_names)]
        variable_details["identity_count"] = [len(identity_df_valid[response_feature][identity_df_valid[category_name] == class_name]) for category_name, class_name in zip(category_names, class_names)]
        variable_details["reference_mean"] = [np.mean(identity_df_valid[response_feature][identity_df_valid[category_name] == reference_vars[category_name]]) for category_name in category_names]
        variable_details["reference_count"] = [len(identity_df_valid[response_feature][identity_df_valid[category_name] == reference_vars[category_name]]) for category_name in category_names]
        variable_details["mean_difference"] = [id_mean - ref_mean for id_mean, ref_mean in zip(variable_details["identity_mean"], variable_details["reference_mean"])]
    return variable_details

def process_R_results(r_results_dir, analaysis_details_fxn):
    # convert R results to our standard format
    round_fxn = np.vectorize(lambda x: np.format_float_scientific(x, precision=3, unique=False, trim='k'))
    variable_estimates = pd.read_csv(os.path.join(r_results_dir, "estimates.csv"))
    model_fit = pd.read_csv(os.path.join(r_results_dir, "fit.csv"))
    variable_mask = (variable_estimates["effect"] == "fixed")&(variable_estimates["term"] != "(Intercept)")
    model_variables = variable_estimates["term"][variable_mask]
    analysis_details = analaysis_details_fxn(model_variables=model_variables)
    for col in variable_estimates.columns:
        if not col in ["term", "effect", "component", "group"]:
            analysis_details[col] = round_fxn(variable_estimates[col][variable_mask])
    for col in model_fit.columns:
        analysis_details[col] = model_fit[col].tolist()*len(model_variables)
    results_df = pd.DataFrame(analysis_details)
    return results_df

def remove_if_empty(dir):
    try:
        os.rmdir(dir)
    except OSError as e:
        pass

def fit_R_models(formulas, df, feature_types_and_names, fpath_kwargs, analysis_details_fxn, r_results_root="./r_results_temp"):
    fpath_kwargs_str = re.sub(r'[^a-zA-Z0-9]+', '', "_".join([str(v) for k, v in sorted(fpath_kwargs.items())]))
    df_root = os.path.join(r_results_root, fpath_kwargs_str)
    df_fpath = os.path.join(df_root, "df.csv")
    os.makedirs(df_root, exist_ok=True)
    df.to_csv(df_fpath)
    for control_variable, (fixed_effects, random_effects) in formulas.items():
        analysis_fpath = get_response_regression_analysis_fpath(**fpath_kwargs, formula_variable=control_variable)
        control_variable_results = []
        for feature_type, feature_name in feature_types_and_names:
            r_results_dir = os.path.join(df_root, f"{control_variable}_{feature_type}_{feature_name}")
            os.makedirs(r_results_dir, exist_ok=True)
            subprocess.run(["Rscript", "./src/glmm.R", df_fpath, feature_name, fixed_effects, random_effects, r_results_dir])
            try:
                feature_results = process_R_results(r_results_dir, partial(analysis_details_fxn, response_feature_type=feature_type, response_feature=feature_name))
                control_variable_results.append(feature_results)
            except FileNotFoundError:
                # Something happened in the R script and the results didn't save
                pass
        if len(control_variable_results) > 0:
            results = pd.concat(control_variable_results, axis=0).reset_index()
            results.to_csv(analysis_fpath)
    shutil.rmtree(df_root)
    remove_if_empty(r_results_root)

def get_formulas(identity_categories, combined=False):
    categorical_variables = identity_categories
    dummy_variables = []
    variables = []
    var_name_to_category_class = {}
    category_name_to_var_names = {}
    for categorical_variable in categorical_variables:
        variables.append(get_categorical_variable_name(categorical_variable)) #this is the variable used in the formula
        category_name_to_var_names[categorical_variable.category_name] = [categorical_variable.category_name]
        for class_name in categorical_variable.identity_class_names:
            var_name_to_category_class[f"{categorical_variable.category_name}{class_name}"] = (categorical_variable.category_name, class_name) #this is the variable name the model spits out
    for dummy_variable in dummy_variables:
        for class_name in dummy_variable.identity_class_names:
            if (not class_name == dummy_variable.reference_value): 
                variables.append(get_continuous_variable_name(dummy_variable, class_name))
                var_name_to_category_class[get_continuous_variable_name(dummy_variable, class_name)]=(dummy_variable.category_name, class_name)
                category_name_to_var_names[dummy_variable.category_name] = category_name_to_var_names.get(dummy_variable.category_name, []) + [get_continuous_variable_name(dummy_variable, class_name)]

    random_factors = "(1 | user_id)" if not combined else "(1 | prompt_idx)"
    random_factors += " + (1 | chosen_model)"
    limited_control_dict = get_limited_controls()
    formulas = {}
    for category_name, control_names in limited_control_dict.items():
        formula_vars = category_name_to_var_names[category_name].copy()
        for control_name in control_names:
            formula_vars += category_name_to_var_names[control_name]
        formulas[f"{category_name}_control"] = (" + ".join(formula_vars), random_factors)
    
    return formulas, var_name_to_category_class

def get_valid_response_mask(parsed_responses, combined, prompt_idx):
    if combined:
        valid_response_mask = np.concatenate(parsed_responses["valid_response_masks"],axis=0)
    else:
        valid_response_mask = np.array(parsed_responses["valid_response_masks"][prompt_idx])
    return valid_response_mask

def get_feature_values(parsed_responses, combined, feature_type, feature_name, prompt_idx):
    if combined:
        feature_values = np.concatenate([parsed_responses["features"][idx][feature_type][feature_name] for idx in range(len(parsed_responses["features"]))])
    else:
        feature_values = np.array(parsed_responses["features"][prompt_idx][feature_type][feature_name])
    return feature_values

def run_analysis(parsed_responses, prompt_idxs, identity_df, identity_categories, label_type, fpath_kwargs, combined=False):
    if combined:
        prompt_idx_labels = np.concatenate([[prompt_idx]*len(identity_df) for prompt_idx in prompt_idxs])
        identity_df = pd.concat([identity_df for _ in prompt_idxs])
        identity_df["prompt_idx"] = [f"prompt{idx}" for idx in prompt_idx_labels]
        prompt_idxs = ["all"]
    features = parsed_responses["features"] # len of prompt_idxs, not len of max(prompt_idxs)
    for idx, prompt_idx in tqdm(enumerate(prompt_idxs)):
        #Get formulas
        formulas, var_name_to_category_class = get_formulas(identity_categories, combined=combined)
        
        # Filter for valid Responses
        valid_response_mask = get_valid_response_mask(parsed_responses, combined, idx)
        identity_df_valid = identity_df[valid_response_mask]
        
        # Put feature_values in identity_df
        feature_types_and_names = []
        for feature_type in features[0].keys():
            for feature_name in features[0][feature_type]:
                feature_values = get_feature_values(parsed_responses, combined, feature_type, feature_name, idx)
                identity_df_valid[feature_name] = feature_values
                feature_types_and_names.append((feature_type, feature_name))

        # Fit model
        analysis_details_fxn = partial(get_analysis_details, prompt_idx=prompt_idx, valid_response_mask=valid_response_mask, identity_categories=identity_categories, identity_df_valid=identity_df_valid, label_type=label_type, var_to_category_class=var_name_to_category_class)
        fit_R_models(formulas, identity_df_valid, feature_types_and_names, {**fpath_kwargs, "prompt_idx":prompt_idx}, analysis_details_fxn)

def main(data_dir, generation_model, prompt_prefix_type, prompt_type, prompt_idxs_to_use, 
         combine_all_prompts, label_type, temperature):
    
    # Load Model Responses
    response_dict = load_prompt_responses(data_dir, prompt_prefix_type, generation_model, prompt_type, temperature)
    if prompt_idxs_to_use == "all":
        prompt_idxs_to_use = list(range(len(response_dict["prompts"])))
    else:
        prompt_idxs_to_use = [int(x.strip()) for x in prompt_idxs_to_use.split(",")]

    # Parse model responses 
    parsed_responses = parse_prompt_responses(response_dict, prompt_type, prompt_idxs=prompt_idxs_to_use)

    # Load PRISM
    conversations, surveys = load_prism()

    # Update surveys with conversation type, model type, and user_id
    additional_info = {
        "conversation_type": [conversation['conversation_type'] for conversation in conversations],
        "chosen_model": [conversation['chosen_model'] for conversation in conversations],
        "user_id": [conversation['user_id'] for conversation in conversations]
    }
    update_surveys(surveys, additional_info)

    # Load classification categories
    exclude_categories = []
    identity_categories = get_basic_regression_categories(surveys, exclude_counts_lt=1, exclude_categories=exclude_categories)
    user_id_category = get_user_id_category(surveys)

    # Get identity df
    identity_df = get_identity_data(identity_categories, user_id_category, surveys, label_type, generation_model=generation_model)

    # Fit model to data
    fpath_kwargs={"data_dir":data_dir, "prompt_prefix_type":prompt_prefix_type, "generation_model":generation_model, "prompt_type":prompt_type, "label_type":label_type}
    run_analysis(parsed_responses, prompt_idxs_to_use, identity_df, identity_categories, label_type, fpath_kwargs, combined=combine_all_prompts)

def parse_args_and_run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, type=str)
    parser.add_argument("--prompt_type", required=True, type=str)
    parser.add_argument("--prompt_prefix_type", required=False, default="prism", type=str)
    parser.add_argument("--combine_all_prompts", action='store_true')
    parser.add_argument("--label_type", required=False, default="ground_truth", type=str)
    parser.add_argument("--prompt_idxs_to_use", required=False, default="all", type=str)
    parser.add_argument("--data_dir", default="./data")
    parser.add_argument("--temperature", required=False, default=1, type=float)
    args = parser.parse_args()


    main(args.data_dir, args.model, args.prompt_prefix_type, args.prompt_type, args.prompt_idxs_to_use, 
         args.combine_all_prompts, args.label_type,
         args.temperature)

if __name__ == "__main__":
    parse_args_and_run()