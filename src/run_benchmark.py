import argparse
from tqdm import tqdm
import asyncio
import numpy as np

from models import generate_model_responses, load_model, get_prompt_cache, expand_past_key_values, get_single_token_response_probs
from data import conversation_to_prompt, load_prism
from generation_prompts import prompt_options
from utils import json_load, json_save
from file_structure import get_generation_fpath

def get_prompt_prefixes(prompt_prefix_type):
    if prompt_prefix_type == "None":
        return [[]]
    elif prompt_prefix_type == "prism":
        conversations, surveys = load_prism()
        return conversation_to_prompt(conversations, use_model_responses=True, remove_final_response=False)
    raise NotImplementedError

def init_generations_dict(data_dir, prompt_prefix_type, generation_model, prompt_type, responses_per_prompt, max_new_tokens, prompts, prompt_prefixes, binary_prompt, load_from_checkpoint=False, temperature=1):
    return_probs = False
    if load_from_checkpoint:
        try:
            prompt_responses = load_prompt_responses(data_dir, prompt_prefix_type, generation_model, prompt_type, temperature)
            n_original_prompts = len(prompt_responses["prompts"])
            assert prompt_responses["prompts"] == prompts[:n_original_prompts]
            assert prompt_responses["responses_per_prompt"] == responses_per_prompt
            prompt_responses["prompts"] = prompts
            prompt_responses["responses"] += [[] for _ in range(len(prompts)-n_original_prompts)]
            if "response_probs" in prompt_responses:
                prompt_responses["response_probs"] += [[] for _ in range(len(prompts)-n_original_prompts)]
            return_probs = "response_probs" in prompt_responses
            prefixes_responses_by_prompt = np.array([len(responses) for responses in prompt_responses["responses"]])
            prompt_start_idx = np.arange(len(prompts))[prefixes_responses_by_prompt != len(prompt_prefixes)][0]
            prefix_start_idx = np.min(prefixes_responses_by_prompt)
        except FileNotFoundError:
            load_from_checkpoint = False
    if not load_from_checkpoint:
        prompt_responses = {"prompts": prompts, "prompt_prefixes": prompt_prefixes, "responses": [[] for _ in range(len(prompts))], "responses_per_prompt": responses_per_prompt}   
        prompt_start_idx, prefix_start_idx = 0, 0
        if binary_prompt or (max_new_tokens <= 10 and responses_per_prompt > 1):
            prompt_responses["response_probs"] = [[] for _ in range(len(prompts))]
            return_probs = True
    return prompt_responses, prompt_start_idx, prefix_start_idx, return_probs

def compute_prompt_responses(data_dir, prompt_prefix_type, prompt_type, generation_model, responses_per_prompt=1, max_new_tokens=None, load_from_checkpoint=False, batch_size=50, temperature=1.0):
    results_path = get_generation_fpath(data_dir, prompt_prefix_type, generation_model, prompt_type, temperature)
    prompts_to_use = prompt_options[prompt_type]
    if isinstance(prompts_to_use, dict):
        prompts_to_use = prompts_to_use[generation_model]
    prompts_to_use = [[{'role': 'user', 'content': prompt}] for prompt in prompts_to_use]
    prompt_prefixes = get_prompt_prefixes(prompt_prefix_type)
    
    binary_prompt = not prompt_type == "salaries"
    generations, prompt_start_idx, prefix_start_idx, return_probs = init_generations_dict(data_dir, prompt_prefix_type, generation_model, prompt_type, responses_per_prompt, max_new_tokens, prompts_to_use, prompt_prefixes, binary_prompt, load_from_checkpoint=load_from_checkpoint)        
    lens = np.array([len(generations["responses"][idx]) for idx in range(len(generations["responses"]))])
    
    model, tokenizer = load_model(generation_model)
    if binary_prompt:
        response_words = ["Yes", "yes", "YES", "No", "no", "NO"]
        response_tokens = [tokenizer.encode(word) for word in response_words]
        if generation_model in ["llama3", "deepseek70B"]:
            assert all([len(tokens) == 2 for tokens in response_tokens]), "Some of the response words are not single tokens"
            response_tokens = [tokens[1] for tokens in response_tokens]
        else:
            assert all([len(tokens) == 1 for tokens in response_tokens]), "Some of the response words are not single tokens"
            response_tokens = [tokens[0] for tokens in response_tokens]
    for prefix_idx, prompt_prefix in tqdm(enumerate(prompt_prefixes[prefix_start_idx:]), total=len(prompt_prefixes[prefix_start_idx:])):
        if len(prompt_prefix) > 0:
            context_cache = get_prompt_cache(model, tokenizer, prompt_prefix)
            if not binary_prompt:
                context_cache = expand_past_key_values(context_cache, responses_per_prompt)
        else:
            context_cache=None
        for prompt_idx, base_prompt in enumerate(prompts_to_use[prompt_start_idx:]):
            prompt_idx = prompt_idx + prompt_start_idx
            prompt = prompt_prefix + base_prompt
            if binary_prompt:
                response_texts = response_words
                response_probs = get_single_token_response_probs(model, tokenizer, base_prompt, response_tokens, cache=context_cache)
                generations["response_probs"][prompt_idx].append(response_probs)
            else:
                response_texts = generate_model_responses(model, tokenizer, prompt, cache=context_cache, max_new_tokens=max_new_tokens, num_beams=responses_per_prompt, num_responses=responses_per_prompt, return_probs=return_probs, return_tokens=False, temperature=temperature)
                if return_probs:
                    response_texts, response_probs = response_texts
                    generations["response_probs"][prompt_idx].append(response_probs)
            generations["responses"][prompt_idx].append(response_texts)
        if prefix_idx % 10 == 0:
            json_save(results_path, generations)
        lens = np.array([len(generations["responses"][idx]) for idx in range(len(generations["responses"]))])

    json_save(results_path, generations)

def load_prompt_responses(data_dir, prompt_prefix_type, generation_model, prompt_type, temperature):
    results_path = get_generation_fpath(data_dir, prompt_prefix_type, generation_model, prompt_type, temperature)
    return json_load(results_path)
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", help="Model to use for response generation", default="llama3", type=str)
    parser.add_argument("--prompt_type", required=True, type=str)
    parser.add_argument("--prompt_prefix_type", required=False, default="prism", type=str)
    parser.add_argument("--data_dir", default="./data/")
    parser.add_argument("--temperature", default=1.0, type=float)
    parser.add_argument("--responses_per_prompt", default=1, type=int)
    parser.add_argument("--max_new_tokens", default=1000, type=int)
    args = parser.parse_args()

    compute_prompt_responses(args.data_dir, args.prompt_prefix_type, args.prompt_type, args.model, responses_per_prompt=args.responses_per_prompt, max_new_tokens=args.max_new_tokens, load_from_checkpoint=True, temperature=args.temperature)

if __name__ == "__main__":
    main()