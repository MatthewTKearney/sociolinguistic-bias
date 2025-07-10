import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, DynamicCache
import os
from copy import deepcopy
from tqdm import tqdm

## Model Loaders 

model_name_to_model_key = {
    "llama3": f"meta-llama/Meta-Llama-3-70B-Instruct",
    "qwen3": "Qwen/Qwen3-32B",
}

def load_model(model_name):
    if not model_name in ["E5", "SFR"]:
        tokenizer = AutoTokenizer.from_pretrained(model_name_to_model_key[model_name], trust_remote_code=True)
        max_memory = {idx: '80GIB' for idx in range(torch.cuda.device_count())}
        model = AutoModelForCausalLM.from_pretrained(model_name_to_model_key[model_name],
                                                    trust_remote_code=True, 
                                                    device_map="auto",
                                                    max_memory=max_memory, 
                                                    torch_dtype=torch.float16,
                                                    low_cpu_mem_usage=True)
        
    return model, tokenizer

def load_tokenizer(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name_to_model_key[model_name], trust_remote_code=True)
    return tokenizer

def get_prompt_cache(model, tokenizer, prompt):
    prompt_cache = DynamicCache()
    with torch.no_grad():
        tokens = tokenizer.apply_chat_template(prompt, tokenize=True, add_generation_prompt=False, enable_thinking=False, return_tensors="pt")
        
        # fix annoying qwen tokenizer issue
        if "qwen3" in tokenizer.name_or_path.lower():
            think_idxs = torch.arange(tokens.shape[1])[tokens[0] == 151667] #find <think> tokens
            for think_idx in think_idxs.flip(0):
                tokens = torch.cat([tokens[:,:think_idx], tokens[:,think_idx+4:]], dim=1)
        
        tokens = tokens.to(model.device)
        prompt_cache = model(tokens, past_key_values = prompt_cache).past_key_values # this is the common prompt cached
    return prompt_cache
    
def expand_past_key_values(past_key_values, num_beams):
    expanded_past = []
    for layer in past_key_values:
        expanded_layer = tuple(
            [t.expand(num_beams, -1, -1, -1) for t in layer]
        )
        expanded_past.append(expanded_layer)
    return tuple(expanded_past)

def generate_model_responses(model, tokenizer, prompt, cache=None, max_new_tokens=5, num_beams=20, num_responses=1, do_sample=False, return_probs=True, return_tokens=True, temperature=1):
    ## If using cache, prompt should be ENTIRE prompt including part that is already cached
    if isinstance(prompt, str):
         prompt = [{
            'role': 'user',
            'content': prompt
        }]
    with torch.no_grad():
        inputs = tokenizer.apply_chat_template(prompt, tokenize=True, add_generation_prompt=True, enable_thinking=False, return_tensors="pt")
        inputs = inputs.to(model.device)
        outputs = model.generate(inputs, past_key_values=deepcopy(cache), max_new_tokens=max_new_tokens, num_beams=num_beams, num_return_sequences=num_responses, temperature=temperature, top_p=1, pad_token_id=tokenizer.eos_token_id, do_sample=do_sample, output_scores=True, return_dict_in_generate=True)
        response_tokens = outputs["sequences"][:, inputs.shape[1]:] #num_sequences x num_new_tokens
        response_tokens = [tokens[(tokens != tokenizer.eos_token_id) & (tokens != 128009)].cpu().tolist() for tokens in response_tokens]
        response_texts = tokenizer.batch_decode(response_tokens)
        return_vals = [response_texts] if return_tokens or return_probs else response_texts
        if return_tokens:
            return_vals.append(response_tokens)
        if return_probs:
            response_probs = torch.exp(outputs["sequences_scores"]).cpu().tolist()
            return_vals.append(response_probs)
    return return_vals

def get_single_token_response_probs(model, tokenizer, prompt, response_tokens, cache=None):
    ## If using cache, prompt should only be part that is not already cached
    with torch.no_grad():
        inputs = tokenizer.apply_chat_template(prompt, tokenize=True, add_generation_prompt=True, enable_thinking=False, return_tensors="pt")
        if not cache is None and "llama" in tokenizer.name_or_path.lower():
            inputs = inputs[:,1:]
        inputs = inputs.to(model.device)
        logits = model(inputs, past_key_values=deepcopy(cache))['logits']
        logits = logits[0,-1]
        probs = torch.nn.functional.softmax(logits, dim=-1)
        return probs[response_tokens].cpu().tolist()