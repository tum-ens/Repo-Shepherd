import yaml
import re
import utils.llm_api as llm_api

def generate_general_prompt():
    '''
    Since there's prompts of Generation task and Improvement task have a lot in common. This function generate part in common to avoid duplicate
    '''
    with open("app/prompts/commit_message.yaml", 'r') as file:
        prompts_repo = yaml.safe_load(file)

    steps = prompts_repo["steps"]
    definition = prompts_repo["definition"]
    guideline = prompts_repo["guideline"]
    example_output = prompts_repo["example_output"]

    prompt = (steps + "\n\n" + 
              definition + "\n\n" + 
              guideline + "\n\n" + 
              example_output)
    
    return prompt

def generate_CM(code_diff, model):
    '''
    Generate CM from code diff.
    '''
    with open("app/prompts/commit_message.yaml", 'r') as file:
        prompts_repo = yaml.safe_load(file)

    meta_prompt = prompts_repo["meta-prompt_generate"]
    general_prompt = generate_general_prompt()
    instruction = prompts_repo["instruction_generate"]
    code_diff_instruction = prompts_repo["code_diff"]

    prompt = (meta_prompt + "\n\n" + 
              general_prompt + "\n\n"+ 
              code_diff_instruction + "\n\n" + 
              code_diff + "\n\n" +
              instruction
              )
    
    raw_result = llm_api.gemini_api(prompt, model)

    return extract_result(raw_result)

def improve_CM(code_diff, commit_message, model):
    '''
    Generate CM from code diff and original CM.
    '''
    with open("app/prompts/commit_message.yaml", 'r') as file:
        prompts_repo = yaml.safe_load(file)

    meta_prompt = prompts_repo["meta-prompt_improve"]
    general_prompt = generate_general_prompt()
    instruction = prompts_repo["instruction_improve"]
    original_CM = prompts_repo["original_CM"]

    prompt = (meta_prompt + "\n\n" + 
              general_prompt + "\n\n"+ 
              instruction + "\n\n" + 
              code_diff + "\n\n" +
              original_CM + "\n\n" +
              commit_message
              )
    
    raw_result = llm_api.gemini_api(prompt, model)

    return extract_result(raw_result)

def extract_result(raw_result):
    """
    There's useless information in refined CM, e.g. "Here is the commit message..."
    To avoid this, regex is used.
    """
    match = re.search(r"\[.*?\].*", raw_result, re.DOTALL)
    return match.group(0) if match else raw_result