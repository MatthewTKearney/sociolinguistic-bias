# sociolinguistic-bias

## Reproducing Paper Results
1. Set up your Hugging Face api key and request access to Meta-Llama-3-70B-Instruct and Qwen3-32B if necessary.
2. Set up the conda environment by running

```
conda env create -f env.yml
conda activate bias-env
```
   
3. Generate model responses to the prompts of interest by running the following from the root directory.

```
python src/run_benchmark.py --model MODEL --prompt_type PROMPT_TYPE 
```
Where MODEL can be either "llama3" or "qwen3" and prompt_type must be one of ["salaries", "legal", "medical", "political", "benefits"]

4. Fit statistical models to LLM responses by running the following from the root directory.

```
python src/response_analysis.py --model MODEL --prompt_type PROMPT_TYPE
python src/response_analysis.py --model MODEL --prompt_type PROMPT_TYPE --combine_all_prompts
```

5. Create figures by running the following in the root directory.

```
python src/plots.py --models llama3 qwen3 --prompt_types salaries legal medical political benefits
```
